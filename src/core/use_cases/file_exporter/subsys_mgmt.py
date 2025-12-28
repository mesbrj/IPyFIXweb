import pickle
import logging
import os
import signal
import asyncio
from multiprocessing import Manager, get_context
from multiprocessing.managers import SharedMemoryManager
from concurrent.futures import ProcessPoolExecutor

from pydantic import BaseModel, validate_call

from core.entities.file_exporter_task import FileExporterTask

logger = logging.getLogger(__name__)


class _ProcessPoolSemaphore:
    """Singleton (single-process wide) asyncio semaphore for each Gunicorn uvicorn-worker
    (Only single process can use asyncio semaphore, not threads)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_ProcessPoolSemaphore, cls).__new__(cls)
            logger.info(" ****** Creating new ProcessPoolSemaphore instance")
        else:
            logger.info(" ****** Using existing ProcessPoolSemaphore instance")
        return cls._instance

    def __init__(self, max_workers=2):
        if not hasattr(self, '_initialized'):
            self._max_workers = max_workers
            self._semaphore = asyncio.Semaphore(max_workers)
            _ProcessPoolSemaphore._instance = self
            self._initialized = True
            logger.info(f"  ******  Created process pool semaphore with {max_workers} permits [{hex(id(self))} - {os.getpid()}]")
        else:
            logger.info(f"  ******  Skipping re-initialization of existing ProcessPoolSemaphore instance [{hex(id(self))} - {os.getpid()}]")
            return

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def semaphore(self):
        return self._semaphore

    async def acquire(self, timeout=30):
        """Acquire semaphore with timeout"""
        try:
            await asyncio.wait_for(self._semaphore.acquire(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Failed to acquire process pool semaphore within {timeout}s")
            return False

    def release(self):
        """Release semaphore"""
        try:
            self._semaphore.release()
        except ValueError:
            logger.warning("Attempted to release semaphore more times than acquired")


class _ProcPool:
    """Singleton (single-process/local-threads wide) process pool manager for each Gunicorn uvicorn-worker 
    (threads can start separated new process in a pool)"""
    _instance = {}

    def __new__(cls):
        current_pid = os.getpid()
        if current_pid in cls._instance:
            logger.info(f" ****** info: Using EXISTING instance for PID {current_pid}")
            return cls._instance[current_pid]

        logger.info(f" ****** info: Creating NEW instance for PID {current_pid}")
        instance = super(_ProcPool, cls).__new__(cls)
        cls._instance[current_pid] = instance
        return instance

    def __init__(self, max_workers=2):
        if hasattr(self, '_initialized'):
            logger.info(f" ****** SKIPPING re-initialization of existing instance {hex(id(self))} for PID {os.getpid()}")
            return

        logger.info(f" ****** INITIALIZING NEW instance {hex(id(self))} for PID {os.getpid()}")
        self._max_workers = max_workers
        self._executor = ProcessPoolExecutor(max_workers=max_workers, mp_context=get_context('forkserver'))
        self._worker_pid = os.getpid()
        self._initialized = True
        logger.info(f" ****** Created process pool executor with {max_workers} workers for worker PID {self._worker_pid}")

    @property
    def executor(self):
        # Check if executor is still healthy before returning it
        try:
            if hasattr(self._executor, '_broken') and self._executor._broken:
                logger.warning("Process pool is broken, attempting to recreate...")
                self._recreate_executor()
        except Exception as e:
            logger.warning(f"Error checking executor health: {e}, attempting to recreate...")
            self._recreate_executor()
        return self._executor

    def _recreate_executor(self):
        """Recreate the process pool when it becomes broken"""
        try:
            # Force kill only child processes from THIS executor (not other workers)
            logger.info("Force killing child processes from current executor...")
            try:
                if hasattr(self, '_executor') and self._executor:
                    processes = getattr(self._executor, '_processes', {})
                    killed_count = 0
                    if processes is not None and hasattr(processes, 'values'):
                        for process in processes.values():
                            try:
                                if process is not None and hasattr(process, 'pid'):
                                    os.kill(process.pid, signal.SIGKILL)
                                    killed_count += 1
                                    logger.info(f"Force killed process {process.pid}")
                            except (ProcessLookupError, OSError):
                                pass
                        logger.info(f"Killed {killed_count} processes from current executor")
                    else:
                        logger.info("Current executor has no processes to kill")
            except Exception as e:
                logger.warning(f"Error during child process cleanup: {e}")

            # Shutdown the old executor
            if hasattr(self, '_executor') and self._executor:
                try:
                    self._executor.shutdown(wait=False, cancel_futures=True)
                except Exception as e:
                    logger.info(f"Error shutting down old executor: {e}")

            # Create new executor
            self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
            logger.info(f"Successfully recreated process pool executor with {self._max_workers} workers")

        except Exception as e:
            logger.error(f"Failed to recreate process pool: {e}")
            raise

    @classmethod
    def get_instance(cls, only_id: bool = False):
        current_pid = os.getpid()
        logger.info(f" ****** Get_instance info: Current PID {current_pid}, _instance keys: {list(cls._instance.keys())}")
        if current_pid not in cls._instance:
            logger.info(f" ****** Get_instance info: Creating NEW instance for PID {current_pid}")
            cls._instance[current_pid] = cls()
        else:
            logger.info(f" ****** Get_instance info: Using EXISTING instance for PID {current_pid}")
        instance = cls._instance[current_pid]
        logger.info(f" ****** Get_instance info: Returning instance {hex(id(instance))} for PID {current_pid}")
        if only_id:
            return hex(id(instance))
        return instance

    def proc_pool_release(self) -> None:
        logger.info("Starting shutdown...")
        killed_count = 0
        try:
            processes = getattr(self._executor, '_processes', {})
            if processes is not None and hasattr(processes, 'values'):
                for process in processes.values():
                    try:
                        if process is not None and hasattr(process, 'pid'):
                            os.kill(process.pid, signal.SIGKILL)
                            killed_count += 1
                            logger.info(f"SIGKILL process {process.pid}")
                    except:
                        pass
            else:
                logger.info(f"Has no processes to send SIGKILL")

            # Shutdown executor (non-blocking)
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except:
                pass

            logger.info(f"Shutdown completed - SIGKILL {killed_count} processes")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


class _SharedMemoryList:
    """
    System Wide Singleton, for all child process, Gunicorn uvicorn-worker and threads.
    Shared memory list for task management synchronization. Shared Resource initialized
    exclusively in the main process before Gunicorn start/fork workers (--preload).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_SharedMemoryList, cls).__new__(cls)
            logger.info(" ****** Creating new SharedMemoryList instance")
        else:
            logger.info(" ****** Using existing SharedMemoryList instance")
        return cls._instance

    @validate_call
    def __init__(
        self,
        value_model: BaseModel = FileExporterTask().model_dump(mode='python'),
        max_items: int = 15
        ):
        if not hasattr(self, '_initialized'):
            self._shared_memory_manager = SharedMemoryManager()
            self._shared_memory_manager.start()
            self._max_items = max_items
            byte_serialized_data = pickle.dumps(value_model)
            self._shared_list = self._shared_memory_manager.ShareableList(
                [byte_serialized_data] * self._max_items
            )
            self._shared_list_name = self._shared_list.shm.name
            self._shared_list_lock = Manager().Lock()
            _SharedMemoryList._instance = self
            self._initialized = True

    @property
    def shared_list(self):
        return self._shared_list
    @shared_list.setter
    def shared_list(self):
        pass
    @shared_list.deleter
    def shared_list(self):
        pass

    @property
    def shared_list_name(self):
        return self._shared_list_name
    @shared_list_name.setter
    def shared_list_name(self):
        pass
    @shared_list_name.deleter
    def shared_list_name(self):
        pass

    @property
    def shared_list_lock(self):
        return self._shared_list_lock
    @shared_list_lock.setter
    def shared_list_lock(self):
        pass
    @shared_list_lock.deleter
    def shared_list_lock(self):
        pass

    @property
    def max_items(self):
        return self._max_items
    @max_items.setter
    def max_items(self):
        pass
    @max_items.deleter
    def max_items(self):
        pass

    @classmethod
    def get_instance(cls, only_id: bool = False):
        if cls._instance is not None and isinstance(cls._instance, _SharedMemoryList):
            if only_id:
                return hex(id(cls._instance))
            return cls._instance
        else:
            return cls()

    def instance_release(self):
        """Shared memory cleanup"""
        if self._instance is not None:
            logger.info("Starting shared memory cleanup...")
            
            try:
                # Force shutdown shared memory manager
                if hasattr(self, '_shared_memory_manager'):
                    self._shared_memory_manager.shutdown()
                
                # Clear all references
                for attr in ['_shared_list', '_shared_list_name', '_shared_list_lock', 
                            '_max_items', '_shared_memory_manager']:
                    setattr(self, attr, None)
                
                logger.info("Shared memory cleanup completed")
            except Exception as e:
                logger.warning(f"Shared memory cleanup error: {e}")
            finally:
                _SharedMemoryList._instance = None

def proc_pool() -> _ProcPool:
    return _ProcPool().get_instance()

def simultaneous_tasks_list() -> _SharedMemoryList:
    return _SharedMemoryList.get_instance()

def get_process_pool_semaphore() -> _ProcessPoolSemaphore:
    return _ProcessPoolSemaphore.get_instance()

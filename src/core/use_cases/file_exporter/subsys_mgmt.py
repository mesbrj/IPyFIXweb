import pickle
import logging
import os
import signal
import asyncio
from multiprocessing import Lock
from multiprocessing.managers import SharedMemoryManager
from concurrent.futures import ProcessPoolExecutor

from pydantic import BaseModel, validate_call

from core.entities.file_exporter_task import FileExporterTask

logger = logging.getLogger(__name__)


class _ProcessPoolSemaphore:
    """Singleton semaphore for each Gunicorn worker to control process pool access"""
    _instance = None
    
    def __init__(self, max_workers=2):
        self._max_workers = max_workers
        self._semaphore = asyncio.Semaphore(max_workers)
        logger.info(f"Created process pool semaphore with {max_workers} permits")
    
    @classmethod
    def get_instance(cls, max_workers=2):
        if cls._instance is None:
            cls._instance = cls(max_workers)
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
    _instance = None
    # Class-level list shared across all workers (preloaded Gunicorn workers)
    _all_executors = []
    
    def __init__(self, max_workers=2):
        # Only create executor if this is a new instance (singleton per worker)
        self._max_workers = max_workers
        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        _ProcPool._all_executors.append(self._executor)
        logger.info(f"Created executor #{len(_ProcPool._all_executors)} with {max_workers} max workers for process coordination")

    @property
    def executor(self):
        # Check if executor is still healthy before returning it
        try:
            # Try to submit a simple test task to verify executor health
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
                                    logger.debug(f"Force killed process {process.pid}")
                            except (ProcessLookupError, OSError):
                                pass
                        logger.info(f"Killed {killed_count} processes from current executor")
                    else:
                        logger.debug("Current executor has no processes to kill")
            except Exception as e:
                logger.warning(f"Error during child process cleanup: {e}")
            
            # Shutdown the old executor
            if hasattr(self, '_executor') and self._executor:
                try:
                    self._executor.shutdown(wait=False, cancel_futures=True)
                except Exception as e:
                    logger.debug(f"Error shutting down old executor: {e}")
            
            # Create new executor
            self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
            _ProcPool._all_executors.append(self._executor)
            logger.info(f"Successfully recreated process pool executor with {self._max_workers} workers")
            
        except Exception as e:
            logger.error(f"Failed to recreate process pool: {e}")
            raise

    @classmethod
    def get_instance(cls, only_id: bool = False):
        # Proper singleton: only create one instance per worker process
        if cls._instance is None:
            cls._instance = cls()
        if only_id:
            return hex(id(cls._instance))
        return cls._instance

    def proc_pool_release(self) -> None:
        """Ultra-simple brutal shutdown - kill everything, ignore errors"""
        logger.info("Starting brutal shutdown...")
        killed_count = 0
        
        try:
            # Kill all processes from all executors
            for i, executor in enumerate(_ProcPool._all_executors, 1):
                logger.info(f"Force-killing executor #{i}")
                
                # Get processes and kill them - handle None case
                processes = getattr(executor, '_processes', {})
                if processes is not None and hasattr(processes, 'values'):
                    for process in processes.values():
                        try:
                            if process is not None and hasattr(process, 'pid'):
                                os.kill(process.pid, signal.SIGKILL)
                                killed_count += 1
                                logger.debug(f"Killed process {process.pid}")
                        except:
                            pass
                else:
                    logger.debug(f"Executor #{i} has no processes to kill")
                
                # Shutdown executor (non-blocking)
                try:
                    executor.shutdown(wait=False, cancel_futures=True)
                except:
                    pass
            
            logger.info(f"Brutal shutdown completed - killed {killed_count} processes")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
        finally:
            # Always clear everything no matter what
            _ProcPool._all_executors.clear()


class _SharedMemoryList:
    _instance = None
    @validate_call
    def __init__(
        self,
        value_model: BaseModel = FileExporterTask().model_dump(mode='python'),
        max_items: int = 15
        ):
        if _SharedMemoryList._instance is None:
            self._shared_memory_manager = SharedMemoryManager()
            self._shared_memory_manager.start()
            self._max_items = max_items
            byte_serialized_data = pickle.dumps(value_model)
            self._shared_list = self._shared_memory_manager.ShareableList(
                [byte_serialized_data] * self._max_items
            )
            self._shared_list_name = self._shared_list.shm.name
            self._shared_list_lock = Lock()
            _SharedMemoryList._instance = self

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
        """Ultra-simple shared memory cleanup"""
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


proc_pool_exec = _ProcPool()
current_tasks_list = _SharedMemoryList()
process_pool_semaphore = _ProcessPoolSemaphore()

def proc_pool() -> _ProcPool:
    return proc_pool_exec.get_instance()

def simultaneous_tasks_list() -> _SharedMemoryList:
    return current_tasks_list.get_instance()

def get_process_pool_semaphore() -> _ProcessPoolSemaphore:
    return process_pool_semaphore.get_instance()

import pickle
import logging
import os
import signal
from multiprocessing import Lock
from multiprocessing.managers import SharedMemoryManager
from concurrent.futures import ProcessPoolExecutor

from pydantic import BaseModel, validate_call

from core.entities.file_exporter_task import FileExporterTask

logger = logging.getLogger(__name__)


class _ProcPool:
    _instance = None
    # Class-level list shared across all workers (preloaded Gunicorn workers)
    _all_executors = []
    
    def __init__(self, max_workers=2):
        # Only create executor if this is a new instance (singleton per worker)
        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        _ProcPool._all_executors.append(self._executor)
        logger.info(f"Created executor #{len(_ProcPool._all_executors)} with {max_workers} max workers for process coordination")

    @property
    def executor(self):
        return self._executor

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
                
                # Get processes and kill them
                processes = getattr(executor, '_processes', {})
                for process in processes.values():
                    try:
                        os.kill(process.pid, signal.SIGKILL)
                        killed_count += 1
                        logger.debug(f"Killed process {process.pid}")
                    except:
                        pass
                
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

def proc_pool() -> _ProcPool:
    return proc_pool_exec.get_instance()

def simultaneous_tasks_list() -> _SharedMemoryList:
    return current_tasks_list.get_instance()

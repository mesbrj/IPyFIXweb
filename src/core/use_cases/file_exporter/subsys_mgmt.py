from pydantic import BaseModel, validate_call

from multiprocessing import Lock
from multiprocessing.managers import SharedMemoryManager
from concurrent.futures import ProcessPoolExecutor

from core.entities.file_exporter_task import FileExporterTask

class _ProcPool:
    _instance = None
    def __init__(self):
        if _ProcPool._instance is None:
            self._executor = ProcessPoolExecutor()
            _ProcPool._instance = self
        elif isinstance(_ProcPool._instance, _ProcPool):
            pass
        else:
            raise RuntimeError(
                "Unexpected instance type for _ProcPool. Need improvements "
                "and more checks (instances memory address, ..., ...)."
            )
    @property
    def _instance(self):
        return _ProcPool._instance
    @_instance.setter
    def _instance(self):
        pass
    @_instance.deleter
    def _instance(self):
        pass

    @property
    def executor(self):
        return self._executor
    @executor.setter
    def executor(self):
        pass
    @executor.deleter
    def executor(self):
        pass

    @classmethod
    def get_instance(cls, only_id: bool = False) -> '_ProcPool' | str | None:
        if cls._instance is not None and isinstance(cls._instance, _ProcPool):
            if only_id:
                return hex(id(cls._instance))
            return cls._instance

    def proc_pool_release(self) -> None:
        if self._instance is not None and isinstance(self._instance, _ProcPool):
            self._executor.shutdown(wait=True)
            self._executor = None
            _ProcPool._instance = None


class _SharedMemoryList:
    _instance = None
    @validate_call
    def __init__(self, value_model: BaseModel, max_items: int = 2):
        if _SharedMemoryList._instance is None:
            self._shared_memory_manager = SharedMemoryManager()
            self._shared_memory_manager.start()
            self._max_items = max_items
            self._shared_list = self._shared_memory_manager.ShareableList(
                [value_model().model_dump(mode='python')] * self._max_items
                )
            self._shared_list_name = self._shared_list.name
            self._shared_list_lock = Lock()
            _SharedMemoryList._instance = self
        elif isinstance(_SharedMemoryList._instance, _SharedMemoryList):
            pass
        else:
            raise RuntimeError(
                "Unexpected instance type for _SharedMemoryList. Need improvements "
                "and more checks (instances memory address, ..., ...)."
            )
    @property
    def _instance(self):
        return _SharedMemoryList._instance
    @_instance.setter
    def _instance(self):
        pass
    @_instance.deleter
    def _instance(self):
        pass

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
    def get_instance(cls, only_id: bool = False) -> '_SharedMemoryList' | str | None:
        if cls._instance is not None and isinstance(cls._instance, _SharedMemoryList):
            if only_id:
                return hex(id(cls._instance))
            return cls._instance

    def instance_release(self):
        if self._instance is not None and isinstance(self._instance, _SharedMemoryList):
            self._shared_list = None
            self._shared_list_name = None
            self._shared_list_lock = None
            self._max_items = None
            self._shared_memory_manager.shutdown()
            self._shared_memory_manager = None
            _SharedMemoryList._instance = None


proc_pool_exec = _ProcPool()
current_tasks_list = _SharedMemoryList(
    value_model=FileExporterTask(),
    max_items=10
)

@validate_call
def simultaneous_tasks_list(value_model: BaseModel, max_items: int) -> _SharedMemoryList:
    return current_tasks_list.get_instance()

def proc_pool() -> _ProcPool:
    return proc_pool_exec.get_instance()
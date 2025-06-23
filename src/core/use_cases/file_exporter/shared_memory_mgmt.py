from pydantic import BaseModel, validate_call

from multiprocessing import Lock
from multiprocessing.managers import SharedMemoryManager


class _SharedMemoryList:
    _instance = None
    @validate_call
    def __init__(self, value_model: BaseModel, max_items: int = 10):
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
            raise RuntimeWarning(
                "SharedMemoryList already initialized. Use get_instance() to access it "
                "or instance_release() to release it."
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
        else:
            raise RuntimeWarning("SharedMemoryList not initialized.")

    def instance_release(self) -> None:
        if self._instance is not None and isinstance(self._instance, _SharedMemoryList):
            self._shared_memory_manager.shutdown()
            self._shared_memory_manager = None
            self._shared_list = None
            self._shared_list_name = None
            self._shared_list_lock = None
            self._max_items = None
            _SharedMemoryList._instance = None

@validate_call
def get_shared_memory_list(value_model: BaseModel, max_items: int) -> _SharedMemoryList:
    return _SharedMemoryList(
        value_model=value_model, max_items=max_items
    ).get_instance()
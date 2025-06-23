from multiprocessing import Lock
from multiprocessing.managers import SharedMemoryManager

from core.entities.file_exporter_task import FileExporterTask

class QueueSubsystem:
    _instance = None

    def __init__(self, max_parallel_tasks: int = 10):
        if QueueSubsystem._instance is None:
            QueueSubsystem._instance = self
        elif isinstance(QueueSubsystem._instance, QueueSubsystem):
            raise ValueError(
                "QueueSubsystem already initialized. Use get_instance() to access it "
                "or instance_release() to release it."
            )
        self._shared_memory_manager = SharedMemoryManager()
        self._shared_memory_manager.start()
        self._parallel_tasks = max_parallel_tasks
        self._tasks = self._shared_memory_manager.ShareableList(
            [FileExporterTask().model_dump(mode='python')] * self._parallel_tasks
        )
        self._tasks_list_name = self._tasks.name
        self._tasks_lock = Lock()

    @property
    def tasks_list(self):
        return self._tasks
    @tasks_list.setter
    def tasks_list(self):
        pass
    @tasks_list.deleter
    def tasks_list(self):
        pass

    @property
    def tasks_list_name(self):
        return self._tasks_list_name
    @tasks_list_name.setter
    def tasks_list_name(self):
        pass
    @tasks_list_name.deleter
    def tasks_list_name(self):
        pass

    @property
    def tasks_lock(self):
        return self._tasks_lock
    @tasks_lock.setter
    def tasks_lock(self):
        pass
    @tasks_lock.deleter
    def tasks_lock(self):
        pass

    @property
    def max_parallel_tasks(self):
        return self._parallel_tasks
    @max_parallel_tasks.setter
    def max_parallel_tasks(self):
        pass
    @max_parallel_tasks.deleter
    def max_parallel_tasks(self):
        pass

    @classmethod
    def get_instance(cls, only_id: bool = False) -> 'QueueSubsystem' | str | None:
        if cls._instance is not None:
            if only_id:
                return hex(id(cls._instance))
            return cls._instance
        else:
            QueueSubsystem()
            return cls._instance

    def instance_release(self) -> None:
        self._shared_memory_manager.shutdown()
        self._shared_memory_manager = None
        self._tasks = None
        self._tasks_list_name = None
        self._tasks_lock = None
        self._parallel_tasks = None
        QueueSubsystem._instance = None
        

queue_subsys = QueueSubsystem()

def get_subsystem() -> QueueSubsystem:
    return queue_subsys
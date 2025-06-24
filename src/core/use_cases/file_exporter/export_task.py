import asyncio
from multiprocessing import Queue

from core.use_cases.file_exporter.subsys_mgmt import proc_pool, simultaneous_tasks_list


class ExportService:
    def __init__(self, pcap_files: list[str], output_ipfix_file: str, **kwargs):
        self.pcap_files = pcap_files
        self.ipfix_file = output_ipfix_file
        self.tasks_definitions = kwargs
        self.shared_task_queue = Queue(maxsize=0)
        self.shared_status_queue = Queue(maxsize=0)
        self.current_tasks = simultaneous_tasks_list()


async def execute_export_task(*args, **kwargs):
    task = ExportService(*args, **kwargs)

    #with task.current_tasks.shared_list_lock:
    #    ... export_service.current_tasks.shared_list
    #task.shared_task_queue.put('...',block=False)

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(
        proc_pool().executor,
        export_task,
        task
    )
    result = asyncio.wrap_future(future, loop=loop)
    await result

    # result ...
    #task.shared_status_queue.get_nowait()
    #with task.current_tasks.shared_list_lock:
    #    ... export_service.current_tasks.shared_list

    task.shared_task_queue.shutdown(immediate=True)
    task.shared_status_queue.shutdown(immediate=True)

    return 


def export_task(export_service: ExportService):
    """
    Run the export task using multiprocessing pool.
    """
    ...
    #with export_service.current_tasks.shared_list_lock:
    #    ... export_service.current_tasks.shared_list
    #export_service.shared_task_queue.get_nowait()
    # ...
    #export_service.shared_status_queue..put('...',block=False)
    #with export_service.current_tasks.shared_list_lock:
    #    ... export_service.current_tasks.shared_list


def file_export_service():
    proc_pool_exec = proc_pool()
    shared_mem_list = simultaneous_tasks_list()
    return (proc_pool_exec, shared_mem_list)

import asyncio
from multiprocessing import Process, Queue
from concurrent.futures import ProcessPoolExecutor

from core.use_cases.file_exporter.shared_memory_mgmt import get_shared_memory_list

process_executor = ProcessPoolExecutor()

class ExportService:
    def __init__(self, pcap_files: list[str], output_ipfix_file: str, **kwargs):
        self.pcap_files = pcap_files
        self.ipfix_file = output_ipfix_file
        self.tasks_definitions = kwargs
        self.shared_task_queue = Queue()
        self.shared_status_queue = Queue()


async def execute_export_task(export_service: ExportService):
    future = process_executor.submit(export_task, export_service)
    result = await asyncio.wrap_future(future)
    process_executor.shutdown(wait=True)
    return result


def export_task(export_service: ExportService):
    """
    Run the export task using multiprocessing.
    """
    ...


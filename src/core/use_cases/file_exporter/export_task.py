import multiprocessing as parallel

from core.use_cases.file_exporter.queue_subsys import get_subsystem as queue_subsys


class ExportService:
    def __init__(self, pcap_files: list[str], output_ipfix_file: str, **kwargs):
        self.pcap_files = pcap_files
        self.ipfix_file = output_ipfix_file
        self.tasks_definitions = kwargs
        self.shared_list = queue_subsys().get_instance()
        self.shared_task_queue = parallel.Queue()
        self.shared_status_queue = parallel.Queue()

def execute_export_task(export_service: ExportService):
    
    with export_service.shared_list.tasks_lock:
        ...

def export_task():
    """
    Run the export task using multiprocessing.
    """
    process = parallel.Process(target=execute_export_task, args=(ExportService(
        pcap_files=["example1.pcap", "example2.pcap"],
        output_ipfix_file="output.ipfix",
        task_id="1234567890abcdef1234567890abcdef",
        epoch_timestamp="1700000000.000000",
        status="pending"
    ),))
    process.start()
    ...
    process.join()
    
    return process.exitcode
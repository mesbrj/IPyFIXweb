from pydantic import BaseModel, RootModel
from typing import List

class FileExporterTask(BaseModel):
    task_id: str = "#" * 32
    pcap_files: List[str] = []
    output_ipfix_file: str = "output.ipfix"
    epoch_start_timestamp: str = "0" * 19 + '.'
    DPI: bool = False
    analysis_list: List[str] = []
    status: str = "_" * 10

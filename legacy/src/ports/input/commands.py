from abc import ABC, abstractmethod
from typing import Any

class FileExportTask(ABC):
    @abstractmethod
    def export_task(self, pacap_files: list[str], output_ipfix_path: str, **kwargs):
        pass





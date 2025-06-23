from pydantic import BaseModel


class FileExporterTask(BaseModel):
    task_info = {
        "task_id": "#" * 32,
        "epoch_timestamp": "0" * 19 + '.',
        "status": "_" * 10,
        }
    task_id: str
    epoch_timestamp: str
    status: str
    def __init__(self, **data):
        data["task_id"] = data.get("task_id", self.task_info["task_id"])
        data["epoch_timestamp"] = data.get("epoch_timestamp", self.task_info["epoch_timestamp"])
        data["status"] = data.get("status", self.task_info["status"])
        super().__init__(**data)

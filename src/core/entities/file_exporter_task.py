from pydantic import BaseModel

task_info = {
    "task_id": "#" * 32,
    "epoch_timestamp": "0" * 19 + '.',
    "status": "_" * 10,
    }

class FileExporterTask(BaseModel):
    task_id: str
    epoch_timestamp: str
    status: str
    def __init__(self, **data):
        data["task_id"] = data.get("task_id", task_info["task_id"])
        data["epoch_timestamp"] = data.get("epoch_timestamp", task_info["epoch_timestamp"])
        data["status"] = data.get("status", task_info["status"])
        super().__init__(**data)

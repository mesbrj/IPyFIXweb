from pydantic import BaseModel

list_item = {
    "task_id": "#" * 32,
    "epoch_timestamp": "0" * 19 + '.',
    "status": "_" * 10,
    }
class TaskSharedListItem(BaseModel):
    task_id: str
    epoch_timestamp: str
    status: str
    def __init__(self, **data):
        data["task_id"] = data.get("task_id", list_item["task_id"])
        data["epoch_timestamp"] = data.get("epoch_timestamp", list_item["epoch_timestamp"])
        data["status"] = data.get("status", list_item["status"])
        super().__init__(**data)

class CurrentTasksSharedList(BaseModel):
    __root__: list[TaskSharedListItem]
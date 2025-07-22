from fastapi import APIRouter, BackgroundTasks
import logging
import pickle
import time

from adapters.web_api.fastapi.controllers.time_series import get_time_series_info
# "Hurting" the hexagonal architecture here:
from core.use_cases.file_exporter.export_task import execute_export_task
from core.use_cases.file_exporter.subsys_mgmt import simultaneous_tasks_list

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_router = APIRouter()

@test_router.get("/time_series/{ts_service_uuid}")
async def time_series_info(ts_service_uuid: str):
    return await get_time_series_info(ts_service_uuid, type="time-series")

@test_router.get("/time_series/{ts_service_uuid}/{measurement_uuid}")
def time_series_fetch(ts_service_uuid: str, measurement_uuid: str, start: int = 0, end: int = 0):
    if start or end:
        return {"start": start, "end": end, "uuid": ts_service_uuid, "measurement_uuid": measurement_uuid}
    else:
        return {"uuid": ts_service_uuid, "measurement_uuid": measurement_uuid}


@test_router.post("/file_exporter/export_task")
async def file_exporter_export_task(background_tasks: BackgroundTasks):
    
    # Generate unique task ID for each request (not hardcoded!)
    import uuid
    import time
    task_id = f"api_task_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    pcap_files = ["example1.pcap", "example2.pcap"]
    output_ipfix_path = "output.ipfix"
    
    kwargs = {
        "task_id": task_id,  # Now unique for each request!
        "epoch_start_timestamp": str(time.time()),
        "DPI": True,
        "analysis_list": ["Model_analysis1", "Model_analysis2"],
        "status": "pending"
    }
    
    logger.info(f"Starting export task with unique ID: {task_id}")
    
    # Add the background task with unique ID
    background_tasks.add_task(execute_export_task, pcap_files, output_ipfix_path, **kwargs)
    
    return {"task_id": task_id, "status": "export task started", "timestamp": time.time()}


@test_router.get("/file_exporter/tasks")
async def get_current_tasks():
    """Get current tasks - with Gunicorn --preload, shared memory works across all workers!"""
    try:
        # Get tasks from shared memory (now works across all workers!)
        tasks_list = simultaneous_tasks_list()
        current_tasks = []
        
        with tasks_list.shared_list_lock:
            for i in range(tasks_list.max_items):
                try:
                    task_data = pickle.loads(tasks_list.shared_list[i])
                    if not task_data.get("task_id", "").startswith("#"):  # Skip empty slots
                        current_tasks.append({
                            "index": i,
                            "task_data": task_data
                        })
                except Exception as e:
                    logger.warning(f"Error reading task at index {i}: {e}")
                    continue
        
        return {
            "storage_type": "shared_memory_with_gunicorn_preload",
            "total_tasks": len(current_tasks),
            "tasks": current_tasks
        }
        
    except Exception as e:
        logger.error(f"Error getting current tasks: {e}")
        return {"error": str(e)}


@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}
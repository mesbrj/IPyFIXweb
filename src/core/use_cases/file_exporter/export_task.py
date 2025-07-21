"""Export Task Manager - Ultra-compact task orchestrator"""

import asyncio
import logging
import time
import uuid

from core.use_cases.file_exporter.subsys_mgmt import proc_pool, simultaneous_tasks_list
from .task_manager import create_task_manager
from .worker_handler import ExportTaskData, export_task

logger = logging.getLogger(__name__)


async def execute_export_task(pcap_files: list[str], output_ipfix_path: str, **kwargs) -> dict:
    """Ultra-compact task execution with bulletproof synchronization"""
    # Generate unique task ID
    task_id = kwargs.get("task_id") or f"task_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    logger.info(f"Starting task {task_id}: {len(pcap_files)} files → {output_ipfix_path}")
    
    # Get task manager and create task data
    current_tasks = simultaneous_tasks_list()
    task_manager = create_task_manager(current_tasks.shared_list, current_tasks.shared_list_lock, current_tasks.max_items)
    task_data = {
        "task_id": task_id, "status": "starting", "created_at": time.time(),
        "file_count": len(pcap_files), "output_path": output_ipfix_path[:50] + "..." if len(output_ipfix_path) > 50 else output_ipfix_path
    }
    
    # Try to add task - handle rejections inline
    if not task_manager.add_task(task_data):
        # Check if duplicate or server busy
        is_duplicate = any(t.get('task_id') == task_id for t in task_manager.get_current_tasks())
        reason = "duplicate_task_id" if is_duplicate else "server_busy"
        msg = f"Task {task_id} already exists" if is_duplicate else "Server busy - all slots full"
        logger.warning(msg)
        return {"status": "rejected", "task_id": task_id, "reason": reason, "message": msg}
    
    # Execute task
    try:
        task_manager.update_task_status(task_id, "running")
        export_data = ExportTaskData(pcap_files, output_ipfix_path, kwargs)
        
        # Run in process pool
        loop = asyncio.get_event_loop()
        await asyncio.wrap_future(loop.run_in_executor(proc_pool().executor, export_task, export_data))
        
        task_manager.complete_task(task_id, success=True)
        logger.info(f"Task {task_id} completed successfully")
        return {"status": "completed", "task_id": task_id}
        
    except Exception as e:
        task_manager.complete_task(task_id, success=False)
        logger.error(f"Task {task_id} failed: {e}")
        return {"status": "failed", "task_id": task_id, "error": str(e)}


def file_export_service():
    """Legacy compatibility function"""
    return (proc_pool(), simultaneous_tasks_list())

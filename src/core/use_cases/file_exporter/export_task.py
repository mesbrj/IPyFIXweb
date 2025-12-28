"""Export Task Manager - Ultra-compact task orchestrator"""

import os
import asyncio
import logging
import time
import uuid
from concurrent.futures import BrokenExecutor

from core.use_cases.file_exporter.subsys_mgmt import proc_pool, simultaneous_tasks_list, get_process_pool_semaphore
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
    
    # Execute task with semaphore-controlled access to process pool
    semaphore_manager = get_process_pool_semaphore()
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        # Try to acquire semaphore with retry logic
        semaphore_acquired = False
        try:
            logger.info(f"Task {task_id}: Attempting to acquire process pool semaphore (attempt {attempt + 1}/{max_retries + 1})")
            semaphore_acquired = await semaphore_manager.acquire(timeout=30)
            
            if not semaphore_acquired:
                if attempt < max_retries:
                    logger.warning(f"Task {task_id}: Failed to acquire semaphore, retrying...")
                    task_manager.update_task_status(task_id, f"semaphore_retry_attempt_{attempt + 2}")
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                else:
                    # Final attempt failed
                    logger.error(f"Task {task_id}: Failed to acquire semaphore after {max_retries + 1} attempts")
                    task_manager.complete_task(task_id, success=False)
                    return {"status": "failed", "task_id": task_id, "error": "semaphore_timeout", "details": "Could not acquire process pool access"}
            
            # Semaphore acquired, execute task
            try:
                task_manager.update_task_status(task_id, "running")
                export_data = ExportTaskData(pcap_files, output_ipfix_path, kwargs)
                
                # Run in process pool
                logger.info(f" ****** [before asyncio.wrap_future] Current process pool instances: {proc_pool()._instance}")
                loop = asyncio.get_event_loop()
                await asyncio.wrap_future(loop.run_in_executor(proc_pool().executor, export_task, export_data))
                logger.info(f" ****** [after asyncio.wrap_future] Current process pool instances: {proc_pool()._instance}")

                # Worker process handles completion, just log success here
                logger.info(f"Task {task_id} completed successfully")
                return {"status": "completed", "task_id": task_id}
                
            except BrokenExecutor as e:
                # Handle process pool being terminated/broken
                if attempt < max_retries:
                    logger.warning(f"Task {task_id} failed due to broken process pool (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    logger.info(f"Task {task_id}: Retrying with new process pool...")
                    task_manager.update_task_status(task_id, f"retrying_attempt_{attempt + 2}")
                    # Force recreation of process pool on next call
                    continue
                else:
                    logger.error(f"Task {task_id} failed after {max_retries + 1} attempts: Process pool consistently broken - {e}")
                    task_manager.complete_task(task_id, success=False)
                    return {"status": "failed", "task_id": task_id, "error": "process_pool_consistently_broken", "details": str(e)}
                
            except asyncio.CancelledError as e:
                # Handle task cancellation
                logger.warning(f"Task {task_id} was cancelled: {e}")
                task_manager.complete_task(task_id, success=False)
                return {"status": "cancelled", "task_id": task_id, "error": "task_cancelled", "details": str(e)}
                
            except asyncio.TimeoutError as e:
                # Handle task timeout
                logger.error(f"Task {task_id} timed out: {e}")
                task_manager.complete_task(task_id, success=False)
                return {"status": "failed", "task_id": task_id, "error": "task_timeout", "details": str(e)}
                
            except Exception as e:
                # Handle worker handler exceptions (shared memory failures)
                if "shared memory connection failed" in str(e):
                    logger.error(f"Task {task_id} failed due to shared memory connection failure: {e}")
                    task_manager.complete_task(task_id, success=False)
                    return {"status": "failed", "task_id": task_id, "error": "shared_memory_failure", "details": str(e)}
                
                # Handle all other exceptions
                if attempt < max_retries and "process" in str(e).lower():
                    logger.warning(f"Task {task_id} failed with process-related error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    logger.info(f"Task {task_id}: Retrying...")
                    task_manager.update_task_status(task_id, f"retrying_attempt_{attempt + 2}")
                    continue
                else:
                    logger.error(f"Task {task_id} failed: {e}")
                    task_manager.complete_task(task_id, success=False)
                    return {"status": "failed", "task_id": task_id, "error": str(e)}
            
        finally:
            # Always release semaphore if acquired
            if semaphore_acquired:
                semaphore_manager.release()
                logger.info(f"Task {task_id}: Released process pool semaphore")


def file_export_service(only_shm: bool):
    if only_shm:
        return simultaneous_tasks_list()
    else:
        return (proc_pool(), simultaneous_tasks_list())

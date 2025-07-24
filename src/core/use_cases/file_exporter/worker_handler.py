"""Ultra-compact worker process handler - Maximum efficiency"""
import os
import time
import logging

logger = logging.getLogger(__name__)


class ExportTaskData:
    """Ultra-compact data class for worker processes"""
    def __init__(self, pcap_files: list[str], output_ipfix_file: str, task_definitions: dict):
        self.pcap_files = pcap_files
        self.ipfix_file = output_ipfix_file
        self.tasks_definitions = task_definitions


def export_task(task_data: ExportTaskData):
    """Ultra-compact worker task execution with bulletproof shared memory"""
    logger.info("Starting export task in worker process")
    
    try:
        task_id = task_data.tasks_definitions.get("task_id", "unknown")
        logger.info(f"Processing {len(task_data.pcap_files)} files → {task_data.ipfix_file} (DPI: {task_data.tasks_definitions.get('DPI', False)})")
        
        # Try shared memory connection (CRITICAL - must succeed)
        task_manager = None
        try:
            from core.use_cases.file_exporter.subsys_mgmt import simultaneous_tasks_list
            from .task_manager import TaskSlotManager
            current_tasks = simultaneous_tasks_list()
            if current_tasks.shared_list and current_tasks.shared_list_lock:
                task_manager = TaskSlotManager(current_tasks.shared_list, current_tasks.shared_list_lock, current_tasks.max_items)
                logger.info("Worker connected to shared memory")
            else:
                raise Exception("Shared memory not available")
        except Exception as e:
            logger.error(f"CRITICAL: Worker failed to connect to shared memory: {e}")
            raise Exception(f"Task cancelled - shared memory connection failed: {e}")

        # Execute processing steps
        steps = ["Loading PCAP", "Parsing packets", "Applying DPI", "Converting IPFIX", "Writing output", "Analysis"]

        logger.info(f" ****** Export task {task_id} started in worker process {os.getpid()} ########## {task_id}")

        for i, step in enumerate(steps, 1):
            logger.info(f"Step {i}/6: {step} - Task {task_id}")
            time.sleep(1)  # Simulate processing
            if task_manager:
                    if i == len(steps):
                        task_manager.update_task_status(task_id, "completed_all_steps")
                    else:
                        task_manager.update_task_status(task_id, f"step_{i}_{step.lower().replace(' ', '_')}")
        # Mark task as completed and free the slot
        if task_manager:
            try:
                task_manager.complete_task(task_id, success=True)
                logger.info(f"Task {task_id} marked as completed and slot freed")
            except Exception as completion_error:
                logger.warning(f"Failed to mark task {task_id} as completed: {completion_error}")
        else:
            logger.error(f"Task {task_id} 'completed'/failed but no task_manager to free slot")
        
        logger.info("Export task completed successfully")
        return {"status": "success", "output_file": task_data.ipfix_file}

    except KeyboardInterrupt:
        # Handle process termination gracefully
        logger.warning(f"Export task {task_id} interrupted by system shutdown")
        if 'task_manager' in locals() and task_manager:
            try:
                task_manager.complete_task(task_id, success=False)
                logger.info(f"Interrupted task {task_id} marked as completed and slot freed")
            except Exception as completion_error:
                logger.warning(f"Failed to mark interrupted task {task_id} as completed: {completion_error}")
        raise
        
    except MemoryError as e:
        # Handle memory exhaustion
        logger.error(f"Export task {task_id} failed due to memory exhaustion: {e}")
        if 'task_manager' in locals() and task_manager:
            try:
                task_manager.complete_task(task_id, success=False)
                logger.info(f"Memory-failed task {task_id} marked as completed and slot freed")
            except Exception as completion_error:
                logger.warning(f"Failed to mark memory-failed task {task_id} as completed: {completion_error}")
        raise
        
    except Exception as e:
        logger.error(f"Export task {task_id} failed: {e}")
        # Mark task as failed and free the slot
        if 'task_manager' in locals() and task_manager:
            try:
                task_manager.complete_task(task_id, success=False)
                logger.info(f"Failed task {task_id} marked as completed and slot freed")
            except Exception as completion_error:
                logger.warning(f"Failed to mark failed task {task_id} as completed: {completion_error}")
        raise e

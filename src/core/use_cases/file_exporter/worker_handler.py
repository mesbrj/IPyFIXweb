"""Ultra-compact worker process handler - Maximum efficiency"""

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
        
        # Try shared memory connection (optional for status updates)
        task_manager = None
        try:
            from core.use_cases.file_exporter.subsys_mgmt import simultaneous_tasks_list
            from .task_manager import TaskSlotManager
            current_tasks = simultaneous_tasks_list()
            if current_tasks.shared_list and current_tasks.shared_list_lock:
                task_manager = TaskSlotManager(current_tasks.shared_list, current_tasks.shared_list_lock, current_tasks.max_items)
                logger.info("Worker connected to shared memory")
        except Exception as e:
            logger.debug(f"Shared memory connection failed: {e}")
        
        # Execute processing steps
        steps = ["Loading PCAP", "Parsing packets", "Applying DPI", "Converting IPFIX", "Writing output", "Analysis"]
        
        for i, step in enumerate(steps, 1):
            logger.info(f"Step {i}/6: {step} - Task {task_id}")
            time.sleep(1)  # Simulate processing
            
            # Update status if possible
            if task_manager:
                try:
                    task_manager.update_task_status(task_id, f"step_{i}_{step.lower().replace(' ', '_')}")
                except:
                    pass  # Continue even if status update fails
        
        logger.info("Export task completed successfully")
        return {"status": "success", "output_file": task_data.ipfix_file}
        
    except Exception as e:
        logger.error(f"Export task failed: {e}")
        if 'task_manager' in locals() and task_manager:
            try:
                task_manager.update_task_status(task_id, "processing_failed")
            except:
                pass
        raise e

"""Ultra-compact bulletproof task manager - Maximum efficiency"""

import time
import pickle
import logging

logger = logging.getLogger(__name__)


class TaskSlotManager:
    """Ultra-compact bulletproof shared memory manager"""
    
    def __init__(self, shared_list, shared_lock, max_items):
        self.shared_list = shared_list
        self.shared_lock = shared_lock
        self.max_items = max_items
    
    def _safe_op(self, func):
        """Ultra-compact safe operation wrapper"""
        try:
            if self.shared_lock.acquire(timeout=0.1):
                try:
                    return func()
                finally:
                    self.shared_lock.release()
        except:
            pass
        return None
    
    def _get_data(self, i):
        """Get slot data safely"""
        try:
            return pickle.loads(self.shared_list[i])
        except:
            return None
    
    def _set_data(self, i, data):
        """Set slot data safely"""
        try:
            self.shared_list[i] = pickle.dumps(data)
            return True
        except:
            return False
    
    def add_task(self, task_data: dict) -> bool:
        """Add task - ultra-compact"""
        def _add():
            task_id = task_data.get('task_id', 'unknown')
            free_slot = -1
            
            # Single pass: check duplicates and find free slot
            for i in range(self.max_items):
                data = self._get_data(i)
                if data:
                    if data.get("task_id") == task_id and not data.get("task_id", "").startswith("#"):
                        logger.warning(f"Task {task_id} already exists")
                        return False
                    elif data.get("task_id", "").startswith("#") and free_slot == -1:
                        free_slot = i
            
            if free_slot != -1 and self._set_data(free_slot, task_data):
                logger.info(f"Task {task_id} → slot {free_slot}")
                return True
            
            logger.warning("All slots full")
            return False
        
        return self._safe_op(_add) or False
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update status - ultra-compact"""
        def _update():
            for i in range(self.max_items):
                data = self._get_data(i)
                if data and data.get("task_id") == task_id:
                    data.update({"status": status, "updated_at": time.time()})
                    return self._set_data(i, data)
            return False
        
        return self._safe_op(_update) or False
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Complete task - ultra-compact"""
        def _complete():
            for i in range(self.max_items):
                data = self._get_data(i)
                if data and data.get("task_id") == task_id:
                    # Log completion
                    try:
                        from .task_logger import log_task_completion
                        log_task_completion(data, success)
                    except:
                        pass
                    
                    # Free slot
                    empty = {"task_id": f"#empty_slot_{i}", "status": "empty", "epoch_timestamp": str(time.time())}
                    if self._set_data(i, empty):
                        logger.info(f"Task {task_id} completed, slot {i} freed")
                        return True
            return False
        
        return self._safe_op(_complete) or False
    
    def get_current_tasks(self) -> list:
        """Get active tasks - ultra-compact"""
        def _get_tasks():
            return [data for i in range(self.max_items) 
                   if (data := self._get_data(i)) and not data.get("task_id", "").startswith("#")]
        
        return self._safe_op(_get_tasks) or []
    
    def get_task_count(self) -> dict:
        """Get task counts - ultra-compact"""
        def _count():
            counts = {"running": 0, "completed": 0, "failed": 0, "empty": 0}
            for i in range(self.max_items):
                data = self._get_data(i)
                if data:
                    status = data.get("status", "unknown")
                    counts[status if status in counts else ("empty" if data.get("task_id", "").startswith("#") else "running")] += 1
                else:
                    counts["empty"] += 1
            return counts
        
        return self._safe_op(_count) or {"running": 0, "completed": 0, "failed": 0, "empty": self.max_items}


def create_task_manager(shared_list, shared_lock, max_items):
    """Factory function"""
    return TaskSlotManager(shared_list, shared_lock, max_items)

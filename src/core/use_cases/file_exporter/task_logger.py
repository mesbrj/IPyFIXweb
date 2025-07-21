"""Ultra-compact JSON task logging - Maximum efficiency"""

import time
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Ultra-compact log setup
LOG_DIR = Path("/var/log/IPyFIXweb")
LOG_DIR.mkdir(parents=True, exist_ok=True)
SUCCESS_LOG = LOG_DIR / "successful_tasks.jsonl"
FAILED_LOG = LOG_DIR / "failed_tasks.jsonl"


def log_task_completion(task_data: dict, success: bool = True):
    """Ultra-compact task logging"""
    try:
        task_data.update({'completed_at': time.time(), 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})
        (SUCCESS_LOG if success else FAILED_LOG).open('a').write(json.dumps(task_data) + '\n')
        logger.info(f"Task {task_data.get('task_id')} logged as {'success' if success else 'failed'}")
    except Exception as e:
        logger.error(f"Logging failed: {e}")


def get_recent_logs(success_logs: bool = True, max_lines: int = 100) -> list:
    """Get recent logs - ultra-compact"""
    try:
        log_file = SUCCESS_LOG if success_logs else FAILED_LOG
        if not log_file.exists():
            return []
        return [json.loads(line.strip()) for line in log_file.open('r').readlines()[-max_lines:] if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return []

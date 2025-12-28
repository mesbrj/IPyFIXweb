"""
Pure Python multi-worker web server - no external dependencies
Container-optimized for production use with Gunicorn
"""
from gunicorn.app.base import BaseApplication
from fastapi import FastAPI
import atexit
import signal
import os
import logging

from cmds.shutdown import file_exporter_shutdown
from adapters.web_api.fastapi.routes import test_router

# FastAPI application setup
web_app = FastAPI()
web_app.add_event_handler("shutdown", file_exporter_shutdown)
web_app.include_router(
    test_router, prefix="/api/v1/test", tags=["test"]
)

# Register atexit handler for graceful shutdown
atexit.register(file_exporter_shutdown)

# Signal handlers for container environments
def signal_handler(signum, frame):
    """Handle container shutdown signals"""
    logging.info(f"Received signal {signum}, initiating graceful shutdown...")
    
    try:
        file_exporter_shutdown()
    except Exception as e:
        logging.error(f"Error during signal shutdown: {e}")
    finally:
        # Force exit if needed
        os._exit(0)

# Register signal handlers for container environments
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


class GunicornServer(BaseApplication):
    """
    Custom Gunicorn server for multi-worker FastAPI deployment
    Optimized for containerized environments
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


async def async_multi_worker_web_server(workers: int = 2, host: str = "0.0.0.0", port: int = 8000):
    """
    Start multi-worker FastAPI server using Gunicorn
    
    Args:
        workers: Number of worker processes (minimum 2 for shared memory)
        host: Host to bind to
        port: Port to bind to
    """
    
    # Enforce minimum workers for multiprocessing.Queue avoidance
    if workers < 2:
        workers = 2
        logging.warning(f"Minimum 2 workers required for proper multiprocessing. Setting workers to {workers}")
    
    # Limit maximum workers to prevent resource exhaustion
    elif workers > 4:
        workers = 4
        logging.warning(f"Limiting workers to {workers} to prevent resource exhaustion")
    
    logging.info(f"Starting IPyFIXweb server with {workers} workers...")
    
    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "preload_app": True,  # Critical for shared memory across workers
        "timeout": 120,
        "keepalive": 2,
        "max_requests": 1000,
        "max_requests_jitter": 100,
        "graceful_timeout": 30,  # Extended timeout for proper cleanup
        "worker_tmp_dir": "/dev/shm",  # Use tmpfs for better performance
    }
    await GunicornServer(web_app, options).run()

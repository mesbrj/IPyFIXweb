"""
Pure Python shutdown module - no external dependencies
Container-optimized for production use
"""
from core.use_cases.file_exporter.export_task import file_export_service


def file_exporter_shutdown() -> None:
    """
    Clean shutdown sequence using pure Python only.
    Optimized for containerized environments.
    """
    import logging
    import os

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting file exporter shutdown sequence...")

    try:
        # Get the service components
        proc_pool_instance, shared_mem_instance = file_export_service()
        
        # Normal shutdown sequence
        logger.info("Shutting down process pool...")
        proc_pool_instance.proc_pool_release()
        
        logger.info("Shutting down shared memory...")
        shared_mem_instance.instance_release()
        
        logger.info("File exporter shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        # If normal shutdown fails, force exit immediately
        # In containers, this allows the container runtime to clean up
        logger.warning("Normal shutdown failed, exiting...")
        os._exit(1)

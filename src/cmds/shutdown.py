from core.use_cases.file_exporter.export_task import file_export_service

def file_exporter_shutdown() -> None:
    proc_pool, shared_mem = file_export_service()
    proc_pool.proc_pool_release()
    shared_mem.instance_release()
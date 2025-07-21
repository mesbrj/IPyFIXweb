from pydantic import validate_call

from adapters.web_api.fastapi.web_server import async_multi_worker_web_server
from core.use_cases.file_exporter.export_task import file_export_service

def init_app():
    file_export_service()
    # ipfix_collector_service()

@validate_call
def webapp_startup(
    workers: int = 2,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    return async_multi_worker_web_server(workers, host, port)


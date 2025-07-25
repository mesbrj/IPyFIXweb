from pydantic import validate_call

from adapters.web_api.fastapi.web_server import async_multi_worker_web_server
from core.use_cases.file_exporter.export_task import file_export_service

def init_app():
    file_export_service(only_shm=True)
    # ipfix_collector_service()

@validate_call
async def webapp_startup(
    workers: int = 2,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    await async_multi_worker_web_server(workers, host, port)


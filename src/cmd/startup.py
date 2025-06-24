import asyncio

from pydantic import validate_call

from core.use_cases.file_exporter.export_task import file_export_service
from adapters.web_api.flask.web_server import startup_sync_not_implemented
from adapters.web_api.fastapi.web_server import (
    async_multi_worker_web_server,
    async_single_worker_web_server
)

def file_exporter_startup() -> None:
    return file_export_service()


@validate_call
def webframework_startup(
    framework: str,
    workers: int | None,
    reload: bool = False) -> None:
    '''
    Only one web framework can be started at a time.
    :param framework: The web framework to use.
    :param workers: Number of workers for the web server.
    :param reload: Use web-server auto-reload.
    '''
    if framework == "fastapi":
        if reload or workers:
            async_multi_worker_web_server(workers,reload)
        else:
            asyncio.run(async_single_worker_web_server())
    elif framework == "flask":
        startup_sync_not_implemented()

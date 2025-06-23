import asyncio

from pydantic import validate_call

from adapters.web_api.flask.web_server import startup_sync_not_implemented
from adapters.web_api.fastapi.web_server import (
    async_multi_worker_web_server,
    async_single_worker_web_server
)

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

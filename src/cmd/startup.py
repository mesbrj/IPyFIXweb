
import asyncio
from adapters.web_api.fastapi.web_server import start_web_server

async def startup_async():
    """
    Start asynchronous web server: uvicorn + FastApi
    """
    await start_web_server()

def startup_sync():
    """
    Start synchronous web server: gunicorn + Flask (default sync)
    """
    import sys
    import logging
    msg = (
        " Synchronous startup is not implemented yet. "
        "Please use the fastapi web_api adapter."
    )
    logging.warning(msg)
    sys.exit(1)

def webframework_startup(framework: str = "fastapi"):
    '''
    Only one web framework can be started at a time.
    :param framework: The web framework to use.
    '''
    if framework == "fastapi":
        asyncio.run(startup_async())
    elif framework == "flask":
        startup_sync()

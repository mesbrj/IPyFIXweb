
import asyncio
from adapters.web_api.web_server import start_web_server

async def startup_async():
    """
    Start assynchronous web server: uvicorn + FastApi
    """
    await start_web_server()

def startup_sync():
    """
    Start synchronous web server: gunicorn + Flask
    """
    import sys
    import logging
    msg = (
        " Synchronous startup is not implemented yet. "
        "Please use the fastapi web_api adapter."
    )
    logging.warning(msg)
    sys.exit(1)

def webframework_startup(framework="fastapi"):
    if framework == "fastapi":
        asyncio.run(startup_async())
    elif framework == "flask":
        startup_sync()

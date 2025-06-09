from adapters.web_api.web_server import start_web_server

async def startup():
    """
    Start the web server.
    """
    await start_web_server()
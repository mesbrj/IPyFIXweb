from fastapi import FastAPI
import uvicorn

from adapters.web_api.routes import test_router

web_server = FastAPI()
web_server.include_router(test_router, prefix="/api/v1/test", tags=["test"])

async def start_web_server():
    config = uvicorn.Config(web_server, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

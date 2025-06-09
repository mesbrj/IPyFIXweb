from fastapi import FastAPI
import uvicorn

from adapters.web_api.fastapi.routes import test_router

web_server = FastAPI()

web_server.include_router(test_router, prefix="/api/v1/test", tags=["test"])

async def start_web_server():

    server = uvicorn.Server(
        uvicorn.Config(
            web_server,
            host="0.0.0.0",
            port=8000
        )
    )
    await server.serve()

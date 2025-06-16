import logging 
from fastapi import FastAPI
import uvicorn

from adapters.web_api.fastapi.routes import test_router

web_app = FastAPI()
web_app.include_router(
    test_router, prefix="/api/v1/test", tags=["test"]
)

def async_multi_worker_web_server(workers: int = 2, reload: bool = False):
    if not workers:
        workers = 2
    elif workers > 4:
        workers = 4
        logging.warning(f"Limiting workers to {workers}")
    if workers > 1 and reload:
        logging.warning(
            "Reloading is not supported with multiple workers. "
            "Setting workers to 1."
        )
    uvicorn.run(
        "adapters.web_api.fastapi.web_server:web_app",
        host="0.0.0.0",
        port=8000,
        workers=workers if not reload else 1,
        lifespan="on",
        reload=reload if reload else False,
    )

async def async_single_worker_web_server():
    server = uvicorn.Server(
        uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=8000,
            lifespan="on",
        )
    )
    await server.serve()

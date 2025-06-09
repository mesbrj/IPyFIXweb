from fastapi import APIRouter

from adapters.web_api.fastapi.controllers.time_series import get_time_series_info


test_router = APIRouter()

# async routes:

@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# sync routes:

@test_router.get("/time_series/{uuid}/info")
def time_series_info(uuid: str):
    return get_time_series_info(uuid)

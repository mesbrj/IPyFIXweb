from fastapi import APIRouter

from adapters.web_api.fastapi.controllers.time_series import get_time_series_info


test_router = APIRouter()

# async routes:

@test_router.get("/time_series/{ts_service_uuid}")
async def time_series_info(ts_service_uuid: str, ts_type: str = "time-series"):
    return await get_time_series_info(ts_service_uuid, ts_type)

# sync routes:

@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@test_router.get("/time_series/{ts_service_uuid}/{ts_service_measurement_uuid}")
def time_series_info(ts_service_uuid: str, ts_service_measurement_uuid: str):
    pass
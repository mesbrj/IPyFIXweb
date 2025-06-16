from fastapi import APIRouter

from adapters.web_api.fastapi.controllers.time_series import get_time_series_info


test_router = APIRouter()

# async routes:

# sync routes:

@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@test_router.get("/time_series/{ts_service_uuid}/")
def time_series_info(ts_service_uuid: str):
    return get_time_series_info(ts_service_uuid)

@test_router.get("/time_series/{ts_service_uuid}/{ts_service_measurement_uuid}/")
def time_series_info(ts_service_uuid: str, ts_service_measurement_uuid: str):
    return {ts_service_measurement_uuid: "measurements details and fetch not implemented yet"}
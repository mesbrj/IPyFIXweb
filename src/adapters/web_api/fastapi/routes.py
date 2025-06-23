from fastapi import APIRouter

from adapters.web_api.fastapi.controllers.time_series import get_time_series_info


test_router = APIRouter()

@test_router.get("/time_series/{ts_service_uuid}")
async def time_series_info(ts_service_uuid: str):
    return await get_time_series_info(ts_service_uuid, type="time-series")

@test_router.get("/time_series/{ts_service_uuid}/{measurement_uuid}")
def time_series_fetch(ts_service_uuid: str, measurement_uuid: str, start: int = 0, end: int = 0):
    if start or end:
        return {"start": start, "end": end, "uuid": ts_service_uuid, "measurement_uuid": measurement_uuid}
    else:
        return {"uuid": ts_service_uuid, "measurement_uuid": measurement_uuid}

@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}
'''
This Adapter module is a controllers (FastApi) for the time-series analyses. This module will interact with the input ports/interfaces and are completely decoupled from the use cases and related business logic.
'''
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ports.input.analysis import analysisService

async def get_time_series_info(uuid: str, type: str) -> JSONResponse:
    time_series_info = await analysisService(type=type).instance_info(ts_uuid=uuid)
    if time_series_info:
        return JSONResponse(content=time_series_info)
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Time series instance not found",
                "uuid": uuid
            })
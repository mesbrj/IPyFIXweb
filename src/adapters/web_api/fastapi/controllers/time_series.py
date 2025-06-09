'''
This Adapter module is a controllers (FastApi) for the time-series analyses. This module will interact with the input ports/interfaces and are completely decoupled from the use cases and related business logic.
'''
from fastapi import HTTPException
from ports.input.analysis import analysisService

def get_time_series_info(uuid: str):

    # Mock implementation for testing purposes
    if uuid == "1164a4ac-1415-4316-a455-1f8d650348b2":
        instance_ts_id = "tests/flowFile34_Rec15_HTTPS_bits_packets_sec.rrd"
        info = analysisService(type="time-series").instance_info(ts_id=instance_ts_id)
        return info
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Time series instance not found",
                "uuid": uuid
            })
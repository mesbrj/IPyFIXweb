from fastapi import APIRouter, BackgroundTasks

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


@test_router.post("/file_exporter/export_task")
async def file_exporter_export_task(BackgroundTasks: BackgroundTasks):

    id = "1234567890abcdef1234567890abcdef"
    kwargs = {
        "pcap_files": ["example1.pcap", "example2.pcap"],
        "output_ipfix_file": "output.ipfix",
        "task_id": id,
        "epoch_start_timestamp": "1700000000.000000",
        "DPI": True,
        "analysis_list": ["Model_analysis1", "Model_analysis2"],
        "status": "pending"
    }
    fnc = "core.use_cases.file_exporter.export_task.execute_export_task"
    if not callable(eval(fnc)):
        raise ValueError(f"{fnc} is not callable")

    BackgroundTasks.add_task(fnc, **kwargs)
    return {"task_id": id, "status": "export task started"}


@test_router.get("/health")
async def health_check():
    return {"status": "healthy"}
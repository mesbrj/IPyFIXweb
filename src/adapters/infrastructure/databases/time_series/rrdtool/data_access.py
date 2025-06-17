'''
RRDTool Databases (File System) Adapter
This module provides an implementation of the interface:
"ports.repositories.time_series.DbPort" for RRDTool.
Data-Access implementation for local and S3 storage.
https://oss.oetiker.ch/rrdtool/doc/rrdtool.en.html
'''
import re
from typing import Any
from aiofile import AIOFile, LineReader
from aiopath import AsyncPath

import rrdtool

from ports.repositories.time_series import DbPort


## Without core management service and tenant features.
## Only one user and one tenant. Only one "Instancies Server" of
## RRDTool database for the entire system.
service_tenant_uuid = "73861fb6-feb7-5bf2-a6ce-8fee04d1919b"
service_tenant_path = "/var/ipyfix/tenants/rrdtool/"
service_tenant_test_path = "tests/tenant_test/rrdtool/"
rdd_instances_dir_path = service_tenant_test_path
class rrdb:
    """
    Base class for IPyFIXweb RRDTool Instance.
    """
    def __init__(self, ts_uuid: str, path: str = rdd_instances_dir_path) -> None:
        if path and ts_uuid:
            self._path = path
            self._ts_uuid= ts_uuid
        else:
            raise rrdb_error("path_or_id_not_set")
        self._rrd_local_instance = None
        self._rrd_ts_service_instance_uuid = None
    @property
    def tenant_path(self) -> str:
        return self._path
    @tenant_path.setter
    def tenant_path(self) -> None:
        pass
    @tenant_path.deleter
    def tenant_path(self) -> None:
        pass
    @property
    def local_instance(self) -> str:
        return self._rrd_local_instance
    @local_instance.setter
    def local_instance(self) -> None:
        pass
    @local_instance.deleter
    def local_instance(self) -> None:
        pass
    @property
    def service_instance(self) -> str:
        return self._rrd_ts_service_instance_uuid
    @service_instance.setter
    def service_instance(self) -> None:
        pass
    @service_instance.deleter
    def service_instance(self) -> None:
        pass
    async def fill_instance_infos(self) -> bool:
        async for entry in AsyncPath(self.tenant_path).iterdir():
            if await entry.is_dir():
                async with AIOFile(f"{entry}/rrd_meta", 'r') as f:
                    async for line in LineReader(f):
                        if ":" in line and self._ts_uuid == line.split(":")[1].strip():
                            self._rrd_local_instance = f"{entry}/"
                            self._rrd_ts_service_instance_uuid = self._ts_uuid
                            break
            if self._rrd_local_instance:
                break
        if self._rrd_local_instance:
            return True

class rrdb_local(DbPort, rrdb):
    """
    Class for interacting with a local RRDTool database (read/write mode).
    This class implements the DbPort interface (port) for local storage
    """

    async def info(self, options: Any = None) -> dict:
        if not await self.fill_instance_infos():
            return None

        measurements_list = []
        ts_instance_info = {
            "tenant_uuid": service_tenant_uuid,
            "ts_uuid": self.service_instance,
            "ts_backend": "rrdtool-local-file-system",
            "measurements_list": [],
            "measurements": [],
        }

        async with AIOFile(f"{self.local_instance}rrd_meta", 'r') as f:
            async for line in LineReader(f):
                if not line.startswith("service_uuid"):
                    measurements_list.append(line.strip())
        if not measurements_list:
            return ts_instance_info

        for measurement in measurements_list:
            uuid = measurement.split(",")[1].split(":")[1]
            ts_instance_info["measurements_list"].append(uuid)
            measurement_data = {f"{uuid}": {
                "tags": [],
                "fields": {},
                "data_sources_info": [],
                "ids": {}
            }}
            for entry in measurement.split(","):
                if ":" in entry:
                    if not re.match(r"^.*_(id|uuid)", entry):
                        key, value = entry.split(":")
                        measurement_data[uuid]["fields"][key] = value
                    else:
                        key, value = entry.split(":")
                        measurement_data[uuid]["ids"][key] = value
                else:
                    measurement_data[uuid]["tags"].append(entry)

            for key, value in rrdtool.info(
                f"{self.local_instance}{measurement.split(',')[0].split(':')[1]}.rrd").items():
                ds_name = re.match(r"^ds\[(?P<ds_name>.*)\].index$", key)
                rra_info = re.match(r"^rra\[(?P<rra_index>\d+)\].cf$", key)
                if ds_name and value == 0:
                    ds_index = value
                    measurement_data[uuid]["data_sources_info"].append([])
                    measurement_data[uuid]["data_sources_info"][ds_index].append(ds_name.group("ds_name"))
                elif ds_name and value != 0:
                    ds_index = value
                    measurement_data[uuid]["data_sources_info"].append([])
                    measurement_data[uuid]["data_sources_info"][ds_index].append(ds_name.group("ds_name"))
                elif re.match(r"^ds\[.*\].type$", key):
                    measurement_data[uuid]["data_sources_info"][ds_index].append(value)
                elif re.match(r"^ds\[.*\].minimal_heartbeat$", key):
                    measurement_data[uuid]["data_sources_info"][ds_index].append(str(value))
                elif rra_info and rra_info.group("rra_index") == "0":
                    rra_index = ds_index + 1
                    measurement_data[uuid]["data_sources_info"].append([])
                    measurement_data[uuid]["data_sources_info"][rra_index].append(value)
                elif rra_info and rra_info.group("rra_index") != "0":
                    rra_index = ds_index + 1
                    measurement_data[uuid]["data_sources_info"].append([])
                    measurement_data[uuid]["data_sources_info"][rra_index].append(value)
                elif re.match(r"^rra\[\d+\].pdp_per_row$", key):
                    measurement_data[uuid]["data_sources_info"][rra_index].append(str(value))
                elif re.match(r"^rra\[\d+\].rows$", key):
                    measurement_data[uuid]["data_sources_info"][rra_index].append(str(value))
                elif re.match(r"^rra\[\d+\].cur_row$", key):
                    measurement_data[uuid]["data_sources_info"][rra_index].append(str(value))
                elif re.match(r"^rra\[\d+\].xff$", key):
                    measurement_data[uuid]["data_sources_info"][rra_index].append(str(value))

            ts_instance_info["measurements"].append(measurement_data[uuid])
        return ts_instance_info

    def create(self, options) -> bool:
        if not self.path:
            raise rrdb_error("path_not_set")

    def update(self, data) -> bool:
        if not self.path:
            raise rrdb_error("path_not_set")

    def fetch(self, start: int, end: int, options):
        if not self.path:
            raise rrdb_error("path_not_set")

    def export(self, start: int, end: int, options, output_type):
        if not self.path:
            raise rrdb_error("path_not_set")

    def delete(self, options):
        if not self.path:
            raise rrdb_error("path_not_set")


class rrdb_s3(DbPort, rrdb):
    """
    Class for interacting with a RRDTool database on S3 (read only mode).
    This class implements the DbPort interface (port) for S3 storage.
    """

    def info(self, options) -> dict:
        if not self.path:
            raise rrdb_error("path_not_set")

    def create(self, options) -> bool:
        if not self.path:
            raise rrdb_error("path_not_set")

    def update(self, data) -> bool:
        if not self.path:
            raise rrdb_error("path_not_set")

    def fetch(self, start: int, end: int, options):
        if not self.path:
            raise rrdb_error("path_not_set")

    def export(self, start: int, end: int, options, output_type):
        if not self.path:
            raise rrdb_error("path_not_set")

    def delete(self, options):
        if not self.path:
            raise rrdb_error("path_not_set")


class rrdb_error(Exception):
    """
    Custom exception class for RRDTool
    """
    def __init__(self, exception_type = None, message =None):
        if exception_type == "path_or_id_not_set":
            raise ValueError("Path or UUID time-series service is not set for the RRDTool database/instance. Please provide a valid path or UUID.")
        elif exception_type == "no_instance_found":
            raise ValueError("No RRDTool instance found for the given time-series UUID. Please ensure the instance exists.")
        elif exception_type == "no_measurements_found":
            raise ValueError("No measurements found in the RRDTool database. Please ensure the database is initialized and contains data.")
        elif message:
            super().__init__(message)
        else:
            super().__init__("An unknown error occurred in RRDTool database operations.")

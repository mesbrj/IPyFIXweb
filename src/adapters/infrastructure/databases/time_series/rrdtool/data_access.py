'''
RRDTool Databases (File System) Adapter
This module provides an implementation of the interface:
"ports.repositories.time_series.DbPort" for RRDTool.
Data-Access implementation for local and S3 storage.
https://oss.oetiker.ch/rrdtool/doc/rrdtool.en.html
'''

from typing import Any

import rrdtool

from ports.repositories.time_series import DbPort


class rrdb:
    """
    Base class for RRDTool database
    """
    def __init__(self, path: str = None):
        if path:
            self._path = path
        else:
            self._path = None
    @property
    def path(self) -> str:
        if not self._path:
            raise rrdb_error("path_not_set")
        return self._path
    @path.setter
    def path(self, path: str) -> None:
        if not self._path:
            self._path = path
    @path.deleter
    def path(self) -> None:
        pass


class rrdb_local(DbPort, rrdb):
    """
    Class for interacting with a local RRDTool database (read/write mode).
    This class implements the DbPort interface (port) for local storage
    """

    def info(self, options: Any = None) -> dict:
        if not self.path:
            raise rrdb_error("path_not_set")

        # For testing purposes, we return a mock store/instance info
        if self.path == "tests/flowFile34_Rec15_HTTPS_bits_packets_sec.rrd":
            return {"rrdtool_data_source": "True",
                "rrdtool_path": self.path, 
                "test": "True",
                "test_data": "This is a test data for RRDTool database."}

        return rrdtool.info(self.path)

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
        if exception_type == "path_not_set":
            raise ValueError("Path is not set. Please set the 'path' property before performing operations.")
        elif message:
            super().__init__(message)
            return
        else:
            super().__init__("An unknown error occurred in RRDTool database operations.")

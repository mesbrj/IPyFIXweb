'''
Time Series Database Port - Interface Module
This module defines the interface for time series database operations.
'''

from abc import ABC, abstractmethod
from typing import Any


class timeSeriesDbPort(ABC):
    """
    Abstract base class for time series database operations.
    This class defines the interface for interacting with a time series database.
    """
    @abstractmethod
    def info(self, options: Any) -> dict:
        """
        Get information about the time series database.
        :param options: Additional options for retrieving information (e.g., metadata, statistics).
        :return: Dictionary containing database information such as schema, retention policy, and other metadata.
        """
        ...
    @abstractmethod
    def create(self, options: Any) -> bool:
        """
        Create a new time series database.
        :param options: Additional options for database creation (e.g., schema, retention policy).
        :return: True if creation is successful, False otherwise.
        """
        ...
    @abstractmethod
    def update(self, data: Any) -> bool:
        """
        Update time series data to the database.
        :param data: Data to be updated.
        :return: True if update is successful, False otherwise.
        """
        ...
    @abstractmethod
    def fetch(self, start: int, end: int, options: Any) -> Any:
        """
        Fetch time series data from the database.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :param options: Additional options for fetching data (e.g., aggregation, filters).
        :return: Time series data for the specified range.
        """
        ...
    @abstractmethod
    def export(self, start: int, end: int, options: Any, output_type: str) -> Any:
        """
        Export the time series database to a file.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :param options: Additional options for exporting data (e.g., steps, filters).
        :param output_type: Type of output file/format (e.g., 'csv', 'json').
        :return: Path to the exported file or the exported data object.
        """
        ...
    @abstractmethod
    def delete(self, options: Any) -> bool:
        """
        Delete the time series database.
        :param options: Additional options for deletion (e.g., backup, archiving options).
        :return: True if deletion is successful, False otherwise.
        """ 
        ...


def timeSeriesDb(
        db_type: str = "rrd",
        ts_id: Any = None,
        storage: str = None
    ) -> timeSeriesDbPort:
    """
    Factory function to get the appropriate time series database instance.
    At this moment only RRDTool is supported, but this function can be extended to support other timeseries.
    
    The ts_id argument is used to identify the specific time series instance. Now only RRDTool is supported and this argument value is a string path (formats: fs, s3) to the RRDTool database file. If InfluxDB is added, this argument value will be the Bucket-ID (and Org-ID if needed).
    
    The supported RRDTool values to the storage argument are:
    - 'local': stored on the local filesystem (read/write mode).
    - 's3': stored on S3 (read only mode).

    :param db_type: Type of the database (default is 'rrd').
    :param ts_id: Identifier for the time series instance.
    :param storage: Type of the storage ('s3', 'local').
    :return: Instance of the specified time series database.
    """
    from adapters.infrastructure.databases.time_series.rrdtool.data_access import (
        rrdb_s3,
        rrdb_local,
    )
    if db_type != "rrd":
        raise ValueError(f"Unknown time-series DB type: {db_type}")
    if not ts_id:
        raise ValueError("ts_id must be provided to identify the time-series instance.")
    if storage == 'local' or storage == None:
        return rrdb_local(ts_id)
    elif storage == 's3':
        return rrdb_s3(ts_id)
    else:
        raise ValueError(
            f"Unknown storage type: {storage}. "
            "Supported types are 'local' or 's3'."
            )

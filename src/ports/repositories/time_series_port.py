from abc import ABC, abstractmethod

class timeSeriesDbPort(ABC):
    """
    Abstract base class for time series database operations.
    This class defines the interface for interacting with a time series database.
    """
    @abstractmethod
    def create(self) -> bool:
        """
        Create a new time series database.
        :return: True if creation is successful, False otherwise.
        """
        ...
    @abstractmethod
    def get(self, start: int, end: int) -> list:
        """
        Get time series data from the database.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :return: List of time series data.
        """
        ...
    @abstractmethod
    def update(self, data: list) -> bool:
        """
        Update time series data to the database.
        :param data: List of time series data to be updated.
        :return: True if update is successful, False otherwise.
        """
        ...

def timeSeriesDb(db_type: str) -> timeSeriesDbPort:
    """
    Factory function to get the appropriate time series database instance.
    :param db_type: Type of the database ('memory', 's3', 'local').
    :return: Instance of the specified time series database.
    """
    from adapters.infrastructure.databases.time_series.rrdtool.data_access import (
        rrdb_memory,
        rrdb_s3,
        rrdb_local,
    )
    if db_type == 'memory':
        return rrdb_memory()
    elif db_type == 's3':
        return rrdb_s3()
    elif db_type == 'local':
        return rrdb_local()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
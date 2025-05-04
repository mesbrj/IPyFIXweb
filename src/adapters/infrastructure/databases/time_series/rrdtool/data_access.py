from core.repositories.time_series_port import timeSeriesDbPort


class rrdb_local(timeSeriesDbPort):
    """
    Class for interacting with a local RRDTool database.
    This class implements the timeSeriesDb interface for RRDTool.
    """
    def time_series_create(self) -> bool:
        """
        Create a new RRDTool database locally.
        :return: True if creation is successful, False otherwise.
        """
        # Implementation for creating a new RRDTool database 
        ...

    
    def get_time_series(self, start: int, end: int) -> list:
        """
        Get time series data from the RRDTool database locally.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :return: List of time series data.
        """
        # Implementation for fetching time series data from RRDTool
        print(f"(local) Fetching time series data from {start} to {end}")


    def update_time_series(self, data: list) -> bool:
        """
        Update time series data to the RRDTool database locally.
        :param data: List of time series data to be updated.
        :return: True if update is successful, False otherwise.
        """
        # Implementation for updating time series data to RRDTool
        ...

class rrdb_s3(timeSeriesDbPort):
    """
    Class for interacting with a RRDTool database on S3.
    This class implements the timeSeriesDb interface for S3 storage.
    """
    def time_series_create(self) -> bool:
        """
        Create a new RRDTool database on S3.
        :return: True if creation is successful, False otherwise.
        """
        # Implementation for creating a new S3 RRDTool database
        ...


    def get_time_series(self, start: str, end: str) -> list:
        """
        Get time series data from the RRDTool database on S3.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :return: List of time series data.
        """
        # Implementation for fetching time series data from RRDTool on S3
        print(f"(s3) Fetching time series data from {start} to {end}")


    def update_time_series(self, data: list) -> bool:
        """
        Update time series data to the RRDTool database on S3.
        :param data: List of time series data to be updated.
        :return: True if update is successful, False otherwise.
        """
        # Implementation for updating time series data to RRDTool on S3
        ...

class rrdb_memory(timeSeriesDbPort):
    """
    Class for interacting with a RRDTool database in memory.
    This class implements the timeSeriesDb interface for in-memory storage.
    """
    def time_series_create(self) -> bool:
        """
        Create a new in-memory RRDTool database.
        :return: True if creation is successful, False otherwise.
        """
        # Implementation for creating a new in-memory RRDTool database
        ...


    def get_time_series(self, start: str, end: str) -> list:
        """
        Get time series data from the in-memory RRDTool database.
        :param start: Start date in epoch format.
        :param end: End date in epoch format.
        :return: List of time series data.
        """
        # Implementation for fetching time series data from in-memory RRDTool
        print(f"(memory) Fetching time series data from {start} to {end}")


    def update_time_series(self, data: list) -> bool:
        """
        Update time series data to the in-memory RRDTool database.
        :param data: List of time series data to be updated.
        :return: True if update is successful, False otherwise.
        """
        # Implementation for updating time series data to in-memory RRDTool
        ...
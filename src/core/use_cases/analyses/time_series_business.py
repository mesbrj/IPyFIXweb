'''
This module implements the use cases for the time-series analyses business logic. This module will interact with the repositories ports/interfaces and are completely decoupled from the infrastructure and related adapters.
'''

from typing import Any
from ports.repositories.time_series import timeSeriesDb


class timeSeries:
    def __init__(self, ts_id: Any):
        if ts_id:
            self._ts_id = ts_id
            try:
                self._ts_db = timeSeriesDb(ts_id=self._ts_id)
            except Exception as error:
                raise Exception(
                    "Unknown error occurred while accessing and or connecting the time-series database. "
                    f"ts_id '{ts_id}': {error}"
                ) from error
        else:
            raise ValueError(
                "ts_id must be provided to identify the time-series instance."
            )
    @property
    def ts_id(self):
        return self._ts_id
    @ts_id.setter
    def ts_id(self):
        pass
    @ts_id.deleter
    def ts_id(self):
        pass
    @property
    def ts_db(self):
        return self._ts_db
    @ts_db.setter
    def ts_db(self):
        pass
    @ts_db.deleter
    def ts_db(self):
        pass

    def store_info(self):
        return self._ts_db.info()
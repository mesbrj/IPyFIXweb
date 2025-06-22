'''
This module implements the use cases for the time-series analyses business logic. This module will interact with the repositories ports/interfaces and are completely decoupled from the infrastructure and related adapters.
'''

from typing import Any

from ports.repositories.time_series import timeSeriesDb
from core.entities.time_series import Instance


class timeSeries:
    def __init__(self, ts_uuid: Any):
        if ts_uuid:
            self._ts_uuid = ts_uuid
            self._ts_db = timeSeriesDb(ts_uuid=self._ts_uuid)
        else:
            raise ValueError(
                "ts_uuid must be provided to identify the time-series instance."
            )
    @property
    def ts_uuid(self):
        return self._ts_uuid
    @ts_uuid.setter
    def ts_uuid(self, value: Any):
        pass
    @ts_uuid.deleter
    def ts_uuid(self):
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

    async def store_info(self):
        info = await self._ts_db.info()
        if not info:
            return None
        return Instance(**info).model_dump()

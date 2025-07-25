'''
Time-Series Analyses Service
This module provides an implementation of the interface:
"ports.input.analysis.timeSeriesPort"
'''

from typing import Any
from ports.input.analysis import timeSeriesPort
from core.use_cases.analyses.time_series_business import timeSeries as ts_analyses

class service(timeSeriesPort):
    """
    Service class for time series analyses,
    implementing the timeSeriesPort interface.
    """

    async def instance_info(self, ts_uuid: Any = None):
        if ts_uuid:
            return await ts_analyses(ts_uuid).store_info()
        return None








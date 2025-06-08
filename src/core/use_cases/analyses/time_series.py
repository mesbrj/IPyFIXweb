'''
Analyses Services
This module provides an implementation of the interfaces:
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

    def instance_info(self, ts_id: Any = None):
        if ts_id:
            return ts_analyses(ts_id).store_info()








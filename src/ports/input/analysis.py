'''
IPFIX, PCAP and Time Series Analysis and Queries Ports - Interfaces Module
This module defines the interfaces to perform IPFIX, PCAP and Time Series analyses and queries.
'''

from abc import ABC, abstractmethod
from typing import Any

class timeSeriesPort(ABC):
    @abstractmethod
    def instance_info(self, ts_id: Any = None):
        ...


class ipfixPort(ABC):
    @abstractmethod
    def record_info(self):
        ...


class pcapPort(ABC):
    ...


def analysisService(type: str = "time-series") -> ipfixPort | pcapPort | timeSeriesPort:
    """
    Factory function to create an instance of analysisService.
    :param type: Type of analysis service to create. Default is "ipfix".
    Other options can be added in the future.
    :return: An instance of ipfixService or pcapService analysis service.
    """
    from core.use_cases.analyses.time_series import service as ts_service
    if type == "time-series":
        return ts_service()
    else:
        raise ValueError(f"Unknown analysis service type: {type}")
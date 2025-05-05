import sys
import os
import rrdtool

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from core.repositories.time_series_port import timeSeriesDb 

a = timeSeriesDb('local')
a.get(2024, 2025)

a.update([10])
a.update(["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"])
a.update(["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z", "2024-01-03T00:00:00Z"])


rrdtool.create(
    'test.rrd',
    '--step', '300',
    '--start', '0',
    'DS:temperature:GAUGE:600:-50:50',
    'RRA:AVERAGE:0.5:1:600',
    'RRA:AVERAGE:0.5:6:700',
    'RRA:AVERAGE:0.5:24:775',
    'RRA:AVERAGE:0.5:288:797'
)



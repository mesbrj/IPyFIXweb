from core.repositories.time_series_port import timeSeriesDb
import rrdtool

a = timeSeriesDb('local')
b = timeSeriesDb('s3')
c = timeSeriesDb('memory')

a.get(2024, 2025)
b.get(2026, 2027)
c.get(2028, 2029)

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



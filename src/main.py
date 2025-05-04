from core.repositories.time_series_port import timeSeriesDb

a = timeSeriesDb('local')
b = timeSeriesDb('s3')
c = timeSeriesDb('memory')

a.get(2024, 2025)
b.get(2026, 2027)
c.get(2028, "2029")






**Some info about rrdtool and analysis services** 

Example of one real use case (focusing on the RRD/Time-Series):

- PCAP file(s) generated (in a router for example). PCAP file(s) uploaded (to IPyFIXweb service). PCAP "convert" executed (YAF with deep packet inspection), will export the uploaded PCAP(s) to IPFIX file(s) (RFC-5655). Next the following analysis will be performed:
- Packets and bytes per second for SSH (specific server IP).
- Packets and bytes per second for HTTPS (specific server IP).

This analysis needs perform *"some searches for infos"* in the IPFIX file(s) and related data: what records in the flows/recs matches to the analysis filter and next, in the PCAP file(s): what packets (and related data) belong to each record identified before (ipfix files).

For example, following the above analysis: Two records of HTTPS for the specific server IP (two different clients) and one record of SSH for the specific server IP were found.

To persist the analysis results (packets and bytes per second), the following 3 RRD files will be created (one per IPFIX record):

DB/instance: time_series service UUID: ***1164a4ac-1415-4316-a455-1f8d650348b2***

- ts_id (implementation id - rrd file-system): /tenat_folder_id/pcap_export_id/rrd

    - *https1 data_sources/data_fields_sets/table: rdd file 1* - **714db67f8406f33e6dc69e8eff9f343e.rrd**
        https_bytes_secs (data + step epoch)
        https_packets_secs (data + step epoch)

    - *https2 data_sources/data_fields_sets/table: rdd file 2* - **Se39dfb5169058449f8aa457faecdc17.rrd**
        https_bytes_secs (data + step epoch)
        https_packets_secs (data + step epoch)

    - *ssh data_sources/data_fields_sets/table: rdd file 3* - **9ef377b830807cbc237a2dfe7536fc1f.rrd**
        ssh_bytes_secs (data + step epoch)
        ssh_packets_secs (data + step epoch)

- The DB/instance, in this implementation, is a folder with rrd files. One text file will be used to store additional info (metering sources, tags, fileds, ...).
    - rrd_meta (easy read and parse):
    >ts_instance_service_UUID:***1164a4ac-1415-4316-a455-1f8d650348b2***
    >**rdd_id**:714db67f8406f33e6dc69e8eff9f343e,**measurement_service_uuid**:afdb16a0-00db-51eb-b9ec-7d8aebd5243a,**FlowsFile**:34,**REC**:54,**HTTPS**,server_ip:10.1.96.15,client_ip:192.168.1.148
    >**rdd_id**:Se39dfb5169058449f8aa457faecdc17,**measurement_service_uuid**:f30e8b1c-baea-5204-89df-069e25f039ca,**FlowsFile**:34,**REC**:624,**HTTPS**,server_ip:10.1.96.15,client_ip:192.168.1.72
    >**rdd_id**:9ef377b830807cbc237a2dfe7536fc1f,**measurement_service_uuid**:sa8589cb3-724e-5102-b9b8-d57783637a70**FlowsFile**:34,**REC**:19,**SSH**,server_ip:10.1.32.4,client_ip:172.16.0.25

Individual size RRD file (2 data_sources for 2 hours): **114 KB**
**Total size** of these 3 RRD files and meta_rrd: **342 KB (meta file: 540 bytes)**.
If some future analysis against the same server/clients pair and protocol infos are needed, new data can update the existent rrd files, without increase the file size (circular data archive, in this case for 2 hours in 1 sec steps).

---

**Some info about rrdtool manipulation:**

```python
# create a new RRD file with two data sources
tenant_path = "tests/tenant_testID/pcap_export1"
rrd_file_path = "9ef377b830807cbc237a2dfe7536fc1f.rrd"
ssh_bytesDataSource = "tcp22_bytes"
ssh_packetsDataSource = "tcp22_packets"
start_time_epoch = 1656562235-1
data_source_type = 'GAUGE'  # GAUGE, COUNTER, DERIVE, DCOUNTER, DDERIVE, ABSOLUTE
consolidation_function = 'AVERAGE'  # AVERAGE, MIN, MAX, LAST, TOTAL or specialized functions (via the Holt-Winters forecasting algorithm): HWPREDICT, MHWPREDICT, SEASONAL, DEVSEASONAL, DEVPREDICT, FAILURES (OBS: All specialized functions with own RRA formmat)
step_time_sec = 1
row_size_hours = 2
dataSource_confs, roundRobin_archives = list(), list()
dataSource_confs.append(f'DS:{ssh_bytesDataSource}:{data_source_type}:600:U:U')
dataSource_confs.append(f'DS:{ssh_packetsDataSource}:{data_source_type}:600:U:U')
roundRobin_archives.append(f'RRA:{consolidation_function}:0.5:{step_time_sec}s:{row_size_hours}h')
rrdtool.create(
    f'{tenant_path}/{rrd_file_path}',
    '--start', f'{start_time_epoch}',
    '--step', f'{step_time_sec}',
    dataSource_confs,
    roundRobin_archives
)
# very simple update example (update two ds same time / random values)
epoch_time = 1656562235
for _ in range(1656569408 - 1656562235):
    random_packets_sec = random.randint(11, 14)
    random_bytes_sec = random_packets_sec * 1500
    rrdtool.update(
        f'{tenant_path}/{rrd_file_path}',
        f'{epoch_time}:{random_bytes_sec}:{random_packets_sec}'
    )
    epoch_time += 1
```
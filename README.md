# IPFIXServices 

![](/docs/IPFIXservices.png)

## Instrumentation and Telemetry Guidelines

### General Instrumentation and Telemetry
- Opentelemetry (Python and Go) API and SDKs for metrics, traces and logs

### Custom instrumentation for detailed OS Process telemetry
**Only specific OS processes (from Python *process-pool-executor*) need custom instrumentation to capture detailed telemetry, and at the same time these OS processes need to be correlated with the business of the service:**
- **Background tasks from frontend WEB-API service**.
    - Only the OS processes (worker processes) that execute the tasks (data processing, report generation and etc...) need to be instrumented.
- **Collector instances from IPFIX Collector service**.
    - Each OS process corresponds to a specific Collector instance and needs to be correlated with the specific Collector service configuration.
- **Mediator instances from IPFIX Mediator service**.
    - Each OS process corresponds to a specific Mediator instance (record export or record ingestion) and needs to be correlated with the specific Mediator service configuration.

This will be achieved using the `psutil` library to gather CPU usage metrics and statistics for each specifically identified OS process. The detailed telemetry will be captured and exported using the OpenTelemetry SDK and APIs for Python using the OpenTelemetry metrics capabilities.

With the detailed telemetry captured for each specifically identified OS process, we are able to identify adjustment needs:
- Increase or decrease the number of CPUs defined for the containers running the services (K8s CPU requests and limits).
- Increase or decrease the number of worker processes in the Python *process-pool-executor* of the services.

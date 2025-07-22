# IPyFIXweb

**Enterprise-grade IPFIX traffic analysis and PCAP processing system with bulletproof multi-worker coordination.**

## Overview

IPyFIXweb is a high-performance, production-ready system for network traffic analysis, featuring PCAP to IPFIX conversion, DPI (Deep Packet Inspection), and real-time task management with cross-process synchronization.

## Architecture

- **Framework**: FastAPI with Gunicorn multi-worker deployment
- **Concurrency**: ProcessPoolExecutor with semaphore-based flow control and shared memory coordination
- **Flow Control**: Per-worker semaphore system preventing process pool overwhelming
- **Process Management**: Self-healing process pools with automatic broken pool recovery
- **Storage**: Cross-process task management with timeout-based locking and fail-safe cleanup
- **Container Optimization**: Signal-based graceful shutdown with extended timeout handling
- **Fault Isolation**: Cross-worker isolation ensuring one worker's failures don't affect others


## Key Features

- ✅ **Multi-worker coordination** with shared memory synchronization
- ✅ **Bulletproof task management** with duplicate prevention and timeout handling
- ✅ **High-throughput processing** with configurable worker pools
- ✅ **Real-time status tracking** across process boundaries
- ✅ **Semaphore-based flow control** preventing process pool overwhelming
- ✅ **Container-optimized deployment** with graceful shutdown handling
- ✅ **Self-healing process pools** with automatic broken pool recovery
- ✅ **Cross-worker isolation** ensuring fault containment


## Quick Start

### Prerequisites
- Python 3.13+
- Linux environment (WSL not recommended, issues with container image builds)

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Start development server
python src/cmds/main.py
```

### API Endpoints
```bash
# Submit PCAP export task (test example)
curl -X POST http://172.16.0.102:8000/api/v1/test/file_exporter/export_task

POST /api/export-task
{
  "pcap_files": ["/path/to/file.pcap"],
  "output_path": "/path/to/output.ipfix",
  "DPI": true,
  "analysis_list": ["tcp", "udp"]
}

# Get task status
GET /api/task-status/{task_id}

# List active tasks
GET /api/tasks
```

## Configuration

System behavior is controlled through:
- **Worker count**: Configurable via `workers` parameter (default: 2)
- **Task slots**: Maximum concurrent tasks per worker
- **Timeout settings**: Lock acquisition and task completion timeouts
- **Log directory**: `/var/log/IPyFIXweb/` for structured logging

## Architecture Components

| Component | Purpose | Location | Key Features |
|-----------|---------|----------|--------------|
| Task Manager | Bulletproof shared memory coordination | `src/core/use_cases/file_exporter/task_manager.py` | Thread-safe operations, brute-force cleanup, slot management |
| Worker Handler | Process pool task execution | `src/core/use_cases/file_exporter/worker_handler.py` | Critical shared memory validation, comprehensive exception handling |
| Export Orchestrator | Main task lifecycle management | `src/core/use_cases/file_exporter/export_task.py` | Semaphore-controlled access, timeout-based rejection |
| System Management | Process pools and shared resources | `src/core/use_cases/file_exporter/subsys_mgmt.py` | Semaphore singletons, self-healing executors, shared memory manager, selective process cleanup |
| Web Server | FastAPI application with signal handling | `src/adapters/web_api/fastapi/web_server.py` | Container-optimized shutdown, SIGTERM/SIGINT handlers |
| Shutdown Handler | Graceful cleanup orchestration | `src/cmds/shutdown.py` | Pure Python shutdown, container-friendly exit |

## Characteristics

- **Startup time**: < 3 seconds for multi-worker deployment
- **Shutdown time**: < 0.3 seconds with ultra-fast termination
- **Throughput**: Optimized for high-volume concurrent processing
- **Memory efficiency**: Shared memory coordination with minimal overhead
- **Fault tolerance**: Comprehensive error handling with graceful degradation
- **Process Pool Overflow Prevention**: Implemented per-worker semaphore system to prevent process pool overwhelming during high-volume loads
- **Cross-Worker Isolation**: Enhanced process management to ensure one worker's failures don't affect other Gunicorn workers
- **Intelligent Rate Limiting**: Automatic task rejection with timeout-based semaphore acquisition to maintain system stability
- **Memory Management**: Improved shared memory cleanup with fail-safe mechanisms
- **Broken Pool Recovery**: Automatic process pool recreation when BrokenProcessPool exceptions occur
- **Selective Process Cleanup**: Workers now only terminate their own child processes, preventing cross-contamination
- **Comprehensive Exception Coverage**: Enhanced handling for MemoryError, KeyboardInterrupt, and process termination scenarios

## Production Considerations

- Configure appropriate worker count based on CPU cores and workload
- Monitor `/var/log/IPyFIXweb/` for task completion tracking
- Implement log rotation for high-volume environments
- Use reverse proxy (nginx/Apache) for production deployments

## Testing & Volume Tests

### Basic Functionality Test
```bash
# Start the server
python src/cmds/main.py

# Submit single task
curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task
```

### Simultaneous Load Testing
```bash
# Test semaphore-based flow control with simultaneous submissions
# This tests the new prevention-based architecture

# High-volume concurrent test (10 simultaneous tasks)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task &
done
wait

# Extended volume test (50 tasks in batches)
for batch in {1..5}; do
  echo "Starting batch $batch..."
  for i in {1..10}; do
    curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task &
  done
  wait
  echo "Batch $batch completed, waiting 2s..."
  sleep 2
done

# Stress test - rapid fire submissions (tests semaphore limits)
for i in {1..25}; do
  curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task &
  if [ $((i % 5)) -eq 0 ]; then
    echo "Submitted $i tasks..."
    sleep 1
  fi
done
wait
```

### Container Testing
```bash
# Build and test container deployment
podman build -t ipyfixweb-test .
podman run --name ipyfixweb-test -p 8000:8000 -d ipyfixweb-test

# Test container stability under load
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task &
done
wait

# Test graceful shutdown (should complete in ~30s)
time podman stop ipyfixweb-test

# Check logs for clean shutdown
podman logs ipyfixweb-test | grep -E "(shutdown|cleanup|killed.*processes)"
```

### Process Pool Resilience Test
```bash
# Test process pool self-healing capabilities
# Submit tasks to trigger potential BrokenProcessPool scenarios

# Rapid concurrent submissions to stress process pool
seq 1 30 | xargs -n1 -P10 -I{} curl -X POST http://localhost:8000/api/v1/test/file_exporter/export_task

# Monitor logs for process pool recreation events
tail -f /var/log/IPyFIXweb/*.log | grep -E "(recreat|broken|semaphore|killed.*process)"
```

### Expected Test Results
- **Semaphore Control**: Tasks should be queued/rejected when pool is full, not cause freezing 
- **Process Isolation**: Worker failures shouldn't affect other workers
- **Container Stability**: Graceful shutdown within 30 seconds
- **Self-Healing**: Automatic recovery from BrokenProcessPool exceptions

### Performance Benchmarks
```bash
# Measure baseline performance
time seq 1 20 | xargs -n1 -P5 -I{} curl -s -X POST http://localhost:8000/api/v1/test/file_exporter/export_task

# Expected results:
# - No server freezing under high load
# - Consistent response times even when pool is saturated
# - Graceful task rejection instead of timeouts
```

## Documentation

- **Legacy documentation**: [`docs/legacy/`](docs/legacy/)
- **API examples**: [`docs/examples/`](docs/examples/)
- **Configuration samples**: [`samples/`](samples/)

## License

See [LICENSE](LICENSE) file for details.

---

*Enterprise-grade network analysis for production environments.*
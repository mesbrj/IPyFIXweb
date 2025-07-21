# IPyFIXweb

**Enterprise-grade IPFIX traffic analysis and PCAP processing system with bulletproof multi-worker coordination.**

## Overview

IPyFIXweb is a high-performance, production-ready system for network traffic analysis, featuring PCAP to IPFIX conversion, DPI (Deep Packet Inspection), and real-time task management with cross-process synchronization.

## Architecture

- **Framework**: FastAPI with Gunicorn multi-worker deployment
- **Concurrency**: ProcessPoolExecutor with bulletproof shared memory coordination
- **Storage**: Cross-process task management with timeout-based locking


## Key Features

- ✅ **Multi-worker coordination** with shared memory synchronization
- ✅ **Bulletproof task management** with duplicate prevention and timeout handling
- ✅ **High-throughput processing** with configurable worker pools
- ✅ **Real-time status tracking** across process boundaries


## Quick Start

### Prerequisites
- Python 3.13+
- Linux/Unix environment (WSL not recommended, issues with shared memory and image builds)

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Start development server
python src/cmds/main.py

# Production deployment with Gunicorn
gunicorn --workers 3 --preload --bind 0.0.0.0:8000 app:app
```

### API Endpoints
```bash
# Submit PCAP export task
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

| Component | Purpose | Location |
|-----------|---------|----------|
| Task Manager | Bulletproof shared memory coordination | `src/core/use_cases/file_exporter/task_manager.py` |
| Worker Handler | Process pool task execution | `src/core/use_cases/file_exporter/worker_handler.py` |
| Export Orchestrator | Main task lifecycle management | `src/core/use_cases/file_exporter/export_task.py` |
| System Management | Process pools and shared resources | `src/core/use_cases/file_exporter/subsys_mgmt.py` |

## Performance Characteristics

- **Startup time**: < 3 seconds for multi-worker deployment
- **Shutdown time**: < 0.3 seconds with ultra-fast termination
- **Throughput**: Optimized for high-volume concurrent processing
- **Memory efficiency**: Shared memory coordination with minimal overhead
- **Fault tolerance**: Comprehensive error handling with graceful degradation

## Production Considerations

- Configure appropriate worker count based on CPU cores and workload
- Monitor `/var/log/IPyFIXweb/` for task completion tracking
- Implement log rotation for high-volume environments
- Use reverse proxy (nginx/Apache) for production deployments

## Documentation

- **Legacy documentation**: [`docs/legacy/`](docs/legacy/)
- **API examples**: [`docs/examples/`](docs/examples/)
- **Configuration samples**: [`samples/`](samples/)

## License

See [LICENSE](LICENSE) file for details.

---

*Enterprise-grade network analysis for production environments.*
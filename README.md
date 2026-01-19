# IPFIXServices 

![](/docs/IPFIXservices.png)

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [POD Structures and Deployment Strategy](#pod-structures-and-deployment-strategy)
- [Session Affinity and State Management](#session-affinity-and-state-management)

## Architecture Overview

### System Components

1. **FrontEnd Web-API Service** (ReplicaSet POD)
   - FastAPI/Uvicorn server for HTTP REST API
   - Background task execution for CPU-intensive operations
     - Multiple worker processes for concurrent request handling

2. **IPFIX Collector/Mediator Service** (StatefulSet POD)
   - Multi-container pod with three components:
     - **D-Bus Container** (Go): Local IPC coordinator for inter-container communication
     - **Collector Container** (Python): IPFIX flow collection services
     - **Mediator Container** (Python): IPFIX flow mediation and export

3. **Data and external Layer**
   - Redis cluster for caching and state management
   - Integration with [IPFIXgraph](https://github.com/mesbrj/IPFIXgraph) project
   - External IPFIX collectors and exporters
   - Kubernetes Web-API for interactions

### Communication Patterns

- **FrontEnd Web API → D-bus Controller: Collector/Mediator**: HTTP REST API calls
- **Within StatefulSet POD**: D-Bus IPC for inter-container coordination
- **Within Web API POD**: ZeroMQ IPC for high-speed process communication
- **External**: 
  - Loadbalancer service for IPFIX (collector) TCP protocol (with session affinity via Gateway API TCPRoute)
  - Loadbalancer service for FrontEnd Web-API (Ingress / Gateway API HTTPRoute)
  - Loadbalancer service for D-Bus controller Web-API (Ingress / Gateway API HTTPRoute)

## ReplicaSet POD: FrontEnd Web-API

**Purpose**: Scalable HTTP API layer that handles user requests and orchestrates background processing.

**Deployment Characteristics**:
- **Type**: ReplicaSet (horizontal scaling)
- **CPU Requests**: 2+ cores recommended
- **Exposed Service**: LoadBalancer (HTTP)
- **Scaling Behavior**: Automatically scales based on load

## StatefulSet POD: Collector/Mediator Service

**Purpose**: Active-active horizontal scaling for IPFIX flow collection and mediation with stable network identities.

**Deployment Characteristics**:

- **Type**: StatefulSet (stable network identity)
- **CPU Requests**: 2+ cores (for Mediator and Collector containers)
- **Exposed Services**:
  - LoadBalancer (HTTP) for D-Bus controller API
  - LoadBalancer (TCP) for Collector service with session affinity
- **Active Pods**: All pods active simultaneously (active-active HA)
- **Scaling**: Horizontal scaling based on flow volume (HPA support)

**Stable Network Identity**:
   - Predictable pod names: collector-0, collector-1, collector-2
   - Stable hostname for DNS resolution
   - Ordered, graceful scaling (add/remove replicas sequentially)

**Active-Active High Availability**:
   - All pods process flows simultaneously
   - Horizontal scaling distributes load across instances
   - Better throughput and latency under high load

**Multi-Container Sidecar Pattern**:
   - **Efficient IPC**: D-Bus provides microsecond latency for local coordination
   - **Internal management**: D-Bus manages Mediator/Collector integration
   - **Separation of concerns**: Clear division between control plane (D-Bus) and data plane (IPFIX Collector/Mediator)
   - **Process isolation**: Each service maintains security boundaries

### Session Affinity and State Management

IPFIX is an inherently stateful protocol where exporters send **templates** separately from **data records**:

1. **Template Message**: Defines the structure of flow data (field types, lengths, order)
2. **Data Records**: Reference template IDs without repeating the structure

If data records arrive at a different collector than the template, they cannot be parsed.

#### State Management Strategy

**Redis-Based Template Cache**: Share IPFIX templates across all collector pods for resilience.

**Template Re-transmission Handling**: IPFIX Standard Behavior: Exporters periodically retransmit templates (typically every 5-10 minutes).

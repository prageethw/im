# Gurobi Deployment Architecture Analysis
# Recommendation for API-Driven Business Optimization Platform

## Executive Summary

This paper evaluates Gurobi's deployment options for building an API-driven optimization platform that serves multiple business units with scalable compute capacity. Based on the requirements for elastic scaling with additional CPU licenses and multi-tenant API access, **Gurobi Compute Server with Web License Service (WLS) on Kubernetes** is the recommended solution.

This architecture provides:
- Automatic horizontal scaling based on demand
- Thread-level load balancing across cluster nodes
- Containerized deployment for infrastructure flexibility
- API-driven integration supporting multiple business units
- Pay-per-use CPU licensing without machine binding

---

## 1. Business Requirements Analysis

### Core Requirements
1. **Centralized optimization service**: Build models once, expose via well-defined APIs
2. **Multi-tenant usage**: Different business units executing models through API calls
3. **Elastic scalability**: Scale compute resources as demand increases
4. **CPU-based licensing**: Add licenses incrementally to match capacity needs
5. **Production-grade reliability**: High availability and load balancing

### Architecture Pattern
The desired pattern follows a **client-server** model where:
- Business applications use Gurobi API to define/submit models
- Optimization engine runs on separate compute infrastructure
- Models are queued, distributed, and solved by a managed cluster
- Results are returned to calling applications via API responses

---

## 2. Gurobi Deployment Options Evaluated

### 2.1 On-Premises Compute Server

**Architecture**: Self-hosted cluster of Gurobi Compute Server instances on physical or virtual machines.

**Key Features**:
- Installed on Windows, Linux, or macOS servers
- Multiple instances form a cluster with shared job queue
- Automatic load balancing across nodes
- Thread-based resource allocation (introduced in Gurobi v12)

**Licensing**:
- Traditional node-locked or floating licenses
- CPU-based licenses available (core count determines capacity)
- Requires license server infrastructure

**Scalability**:
- Vertical: Add more cores/memory to existing nodes
- Horizontal: Add new server nodes to cluster
- Manual infrastructure provisioning required

**Pros**:
- Full control over infrastructure and data residency
- No external internet dependency for solving
- Predictable performance on dedicated hardware

**Cons**:
- Manual infrastructure management (provisioning, patching, monitoring)
- License server administration overhead
- Slower scaling response compared to container orchestration
- Higher operational complexity for multi-environment deployments

---

### 2.2 Kubernetes (Container-Based with WLS)

**Architecture**: Containerized Gurobi Compute Server deployed on Kubernetes clusters with Web License Service.

**Key Features**:
- Docker containers running Gurobi Compute Server nodes
- Kubernetes orchestration for auto-scaling and self-healing
- Web License Service (WLS) for dynamic license token retrieval
- Supports AWS EKS, Azure AKS, and on-premises K8s clusters

**Licensing**:
- Web License Service (WLS) - cloud-based license token distribution
- Containers request JWT tokens from Gurobi's WLS servers via HTTPS
- No machine-binding; licenses follow workload elastically
- CPU/thread-based capacity allocation
- Requires internet connectivity to token.gurobi.com:443

**Scalability**:
- Native Kubernetes horizontal pod autoscaling (HPA)
- Dynamic cluster expansion based on job queue depth
- Thread-limit configuration per node (NODE_THREADLIMIT parameter)
- Greedy load balancing: jobs allocated to nodes with most available threads

**Pros**:
- **Best-in-class elastic scaling**: K8s HPA responds automatically to demand
- **Infrastructure agnostic**: Deploy on any K8s cluster (on-prem, AWS, Azure, hybrid)
- **Simplified licensing**: WLS eliminates license file management in dynamic environments
- **DevOps-friendly**: Infrastructure-as-code, CI/CD integration, GitOps compatibility
- **Multi-environment support**: Easily replicate across dev/test/prod with same configs
- **Self-healing**: Kubernetes automatically restarts failed containers
- **Resource efficiency**: Share K8s cluster with other workloads; isolate with namespaces

**Cons**:
- Requires Kubernetes expertise for initial setup
- Internet dependency for WLS token retrieval (tokens cached, limited offline operation)
- WLS license types may have different pricing structure than traditional licenses

---

### 2.3 Gurobi Instant Cloud

**Architecture**: Fully managed Gurobi environment on AWS or Azure, operated by Gurobi.

**Key Features**:
- Gurobi manages infrastructure, updates, and scaling
- Choose machine types (compute capacity) via Cloud Manager
- Built-in Compute Server capabilities with automatic queuing
- HTTPS encryption and load balancing included

**Licensing**:
- Cloud-specific licenses managed via Cloud Manager
- Pay-as-you-go or reserved capacity pricing
- License tied to Gurobi's managed cloud instances

**Scalability**:
- Gurobi handles machine provisioning
- Limited control over scaling logic compared to self-managed K8s

**Pros**:
- Zero infrastructure management
- Fast time-to-value (no setup overhead)
- Automatic updates and security patching by Gurobi

**Cons**:
- **Reduced control**: Cannot customize infrastructure, scaling policies, or deployment topology
- **Vendor lock-in**: Tied to Gurobi's cloud offering and pricing model
- **Limited integration**: More difficult to integrate with existing CI/CD, monitoring, or security infrastructure
- **Cost opacity**: Less predictable costs compared to managing own compute resources
- **Compliance constraints**: Data processed on Gurobi-managed infrastructure may not meet regulatory requirements

---

## 3. Detailed Comparison Matrix

| Criterion | On-Prem Compute Server | Kubernetes + WLS | Gurobi Instant Cloud |
|-----------|------------------------|------------------|----------------------|
| **Scalability** | Manual horizontal scaling | Automatic K8s HPA | Managed by Gurobi |
| **Operational Overhead** | High (manual patching, monitoring) | Medium (K8s expertise required) | Low (fully managed) |
| **Infrastructure Control** | Full | Full | Limited |
| **License Model** | Node/floating licenses | WLS (token-based) | Cloud licenses |
| **Elastic CPU Licensing** | Add license capacity manually | Dynamic token retrieval | Managed capacity |
| **Multi-Environment Support** | Separate infrastructure per env | IaC duplication across clusters | Separate cloud instances |
| **Integration Flexibility** | Full API/network control | Full API/network control | Limited to Gurobi APIs |
| **Cost Predictability** | High (owned infrastructure) | High (K8s + WLS pricing) | Variable (managed service) |
| **Data Residency** | Complete control | Complete control (if on-prem K8s) | Gurobi-managed AWS/Azure |
| **Internet Dependency** | None (local license server) | WLS requires internet | Required |
| **Time to Production** | Weeks (infrastructure setup) | Days (K8s deployment) | Hours (sign up + configure) |

---

## 4. Technical Architecture: Kubernetes + WLS (Recommended)

### 4.1 Logical Architecture

![Logican View](Gurobi_Component_Architecture.svg)



### 4.2 API Integration Pattern

1. **Model Development**: Data scientists/analysts build optimization models using Gurobi APIs (Python, Java, C++, etc.)
2. **Service Wrapper**: Models are wrapped in microservices with REST/gRPC APIs exposing business-specific endpoints
3. **Job Submission**: Business applications call API endpoints, which create Gurobi environments and submit models to Compute Server cluster
4. **Distributed Solving**: Cluster Manager distributes jobs to available nodes based on thread availability
5. **Result Retrieval**: Solutions are returned to calling service and formatted for business consumption

### 4.3 Load Balancing and Scaling

**Thread-Based Load Balancing** (Gurobi v12+):
- Each node configured with NODE_THREADLIMIT (e.g., 32 threads)
- Jobs specify ThreadLimit parameter (threads required)
- Cluster Manager allocates jobs to nodes with most available threads
- Greedy algorithm ensures efficient resource utilization

**Kubernetes Auto-Scaling**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gurobi-compute-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gurobi-compute-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: gurobi_queue_depth
      target:
        type: AverageValue
        averageValue: "5"
```

### 4.4 WLS Licensing Configuration

**License Setup**:
1. Obtain WLS license from Gurobi (commercial or evaluation)
2. Create API key via Web License Manager
3. Configure Kubernetes Secret with credentials:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gurobi-wls-credentials
type: Opaque
stringData:
  WLSACCESSID: "203dec48-e3f8-46ac-0184-92d7d6ded944"
  WLSSECRET: "a080cce8-4e01-4e36-955e-61592c5630db"
  LICENSEID: "12127"
```

**Container Environment**:
- Containers retrieve license tokens automatically on startup
- Tokens are JWT-based, time-limited, and automatically renewed
- No license file management or manual activation required
- Supports dynamic scaling without pre-provisioning licenses

---

## 5. Cost and Resource Considerations

### Licensing Costs
- **WLS Pricing**: Contact Gurobi sales for specific pricing; typically based on:
  - Maximum concurrent CPU cores/threads
  - Annual subscription model
  - Volume discounts for larger deployments

- **Capacity Planning**:
  - Analyze typical job concurrency and thread requirements
  - Size license capacity 20-30% above average peak demand
  - Use Kubernetes autoscaling to optimize resource utilization

### Infrastructure Costs
- **Compute**: K8s node costs (on-prem hardware amortization or cloud VM pricing)
- **Network**: Egress costs for WLS token requests (minimal - ~1 KB per token request)
- **Storage**: Minimal for Gurobi containers; model data stored in application layer

### Operational Costs
- **Kubernetes Management**: Platform team or managed K8s service (EKS, AKS, GKE)
- **Monitoring**: Observability tools (Prometheus, Grafana, Datadog)
- **DevOps**: CI/CD pipeline maintenance and infrastructure-as-code management

---

## 6. Implementation Roadmap

### Phase 1: Proof of Concept (2-3 weeks)
1. **Week 1**: 
   - Request Gurobi WLS evaluation license
   - Set up development Kubernetes cluster (Minikube or cloud dev cluster)
   - Deploy single Gurobi Compute Server container
   - Test sample optimization model via API

2. **Week 2**:
   - Deploy multi-node cluster (3 nodes)
   - Configure load balancing and job queuing
   - Integrate first business model (e.g., supply chain optimization)
   - Build REST API wrapper service

3. **Week 3**:
   - Performance testing with concurrent jobs
   - Validate WLS token retrieval and renewal
   - Document API specifications and integration patterns

### Phase 2: Production Deployment (4-6 weeks)
1. **Infrastructure Setup**:
   - Provision production Kubernetes cluster (on-prem or cloud)
   - Configure networking, security policies, and service mesh
   - Set up monitoring and alerting (Prometheus/Grafana)

2. **Gurobi Cluster Deployment**:
   - Deploy Gurobi Compute Server Deployment with 5-10 initial replicas
   - Configure HPA policies based on queue depth and CPU metrics
   - Implement health checks and readiness probes

3. **API Gateway and Authentication**:
   - Deploy API gateway (Kong, AWS API Gateway, Azure API Management)
   - Implement OAuth2/JWT authentication for business units
   - Configure rate limiting and quota management per tenant

4. **Model Migration**:
   - Convert existing optimization models to API-compatible services
   - Deploy model microservices to Kubernetes
   - Integrate with Gurobi Compute Server cluster

5. **Testing and Validation**:
   - Load testing with realistic workload patterns
   - Failover testing (node failures, network interruptions)
   - Security audit and penetration testing

### Phase 3: Optimization and Expansion (Ongoing)
1. **Performance Tuning**:
   - Optimize ThreadLimit settings per model type
   - Fine-tune HPA scaling thresholds
   - Implement job prioritization for critical business processes

2. **Multi-Region Deployment** (if required):
   - Replicate architecture to additional regions for latency reduction
   - Implement job routing based on geography

3. **Advanced Features**:
   - Distributed optimization for extremely large models
   - Real-time optimization dashboards for business users
   - Integration with data pipelines (Kafka, Airflow)

---

## 7. Risk Mitigation

### Internet Dependency for WLS
**Risk**: WLS requires HTTPS connectivity to token.gurobi.com; network outages could disrupt license validation.

**Mitigation**:
- WLS tokens are cached locally and renewed automatically; temporary outages tolerated
- Implement network redundancy (multiple internet uplinks)
- Monitor WLS endpoint reachability and alert on failures
- Negotiate SLA with Gurobi for WLS uptime guarantees
- Consider hybrid approach: WLS for primary, node-locked licenses for critical failover capacity

### Kubernetes Operational Complexity
**Risk**: Kubernetes requires specialized expertise; misconfigurations could cause outages.

**Mitigation**:
- Use managed Kubernetes services (EKS, AKS, GKE) to reduce operational burden
- Implement infrastructure-as-code (Terraform, Pulumi) for reproducible deployments
- Invest in team training or hire Kubernetes expertise
- Start with simple deployment; add complexity incrementally

### License Cost Overruns
**Risk**: Unpredictable usage growth could exceed licensed capacity.

**Mitigation**:
- Implement job quotas per business unit
- Monitor license utilization via Gurobi WLS Manager dashboard
- Set up alerts when approaching capacity thresholds (e.g., 80% utilization)
- Negotiate flexible licensing terms with Gurobi (e.g., burst capacity options)

---

## 8. Alternative Scenarios

### When On-Prem Compute Server Makes Sense
- **Regulatory constraints**: Data cannot leave on-premises environment AND internet connectivity is restricted
- **Stable, predictable workloads**: No need for elastic scaling; constant capacity requirements
- **Existing VM infrastructure**: Already have virtualization platform; Kubernetes overhead not justified

### When Gurobi Instant Cloud Makes Sense
- **Rapid prototyping**: Need to validate optimization approach quickly without infrastructure investment
- **Small-scale deployments**: Limited user base; managed service overhead acceptable
- **Variable workloads**: Occasional optimization needs; don't want to maintain standby infrastructure

---

## 9. Conclusion and Recommendation

For building an API-driven optimization platform serving multiple business units with elastic scaling requirements, **Gurobi Compute Server on Kubernetes with Web License Service (WLS)** is the optimal architecture.

### Key Decision Factors

1. **Scalability**: Kubernetes HPA provides automatic horizontal scaling; WLS licensing follows workload elastically without machine binding constraints
2. **Operational Efficiency**: Infrastructure-as-code and containerization enable consistent multi-environment deployments with minimal operational overhead
3. **Cost Control**: Pay for actual compute capacity used; scale down during off-peak periods
4. **Integration Flexibility**: Full control over API gateway, authentication, and service mesh integrations
5. **Future-Proof**: Kubernetes is industry-standard platform; easy to integrate with evolving cloud-native ecosystem

### Recommended Next Steps

1. **Immediate (Week 1-2)**:
   - Contact Gurobi sales to request WLS evaluation license and discuss commercial pricing
   - Identify pilot business model for initial deployment (preferably well-understood, medium complexity)
   - Assess Kubernetes readiness (existing K8s platform vs. need to provision)

2. **Short-Term (Month 1-2)**:
   - Execute Phase 1 proof-of-concept on development Kubernetes cluster
   - Validate WLS performance and cost model with actual workloads
   - Design API specifications for first 2-3 business models

3. **Medium-Term (Month 3-6)**:
   - Production deployment with initial model suite
   - Onboard first business units as API consumers
   - Establish monitoring, alerting, and SLA tracking

4. **Long-Term (6+ months)**:
   - Expand model catalog based on business demand
   - Optimize performance and cost based on production metrics
   - Explore advanced features (distributed optimization, real-time APIs)

---

## Appendices

### Appendix A: Gurobi API Languages Supported
- Python (gurobipy)
- Java
- C++
- C#/.NET
- R
- MATLAB
- Command-line interface

### Appendix B: Kubernetes Requirements
- **Minimum Cluster**: 3 worker nodes (for HA)
- **Node Resources**: 8+ CPU cores, 16+ GB RAM per node (adjust based on model complexity)
- **Kubernetes Version**: 1.24+ (for latest HPA features)
- **Networking**: Service mesh optional but recommended (Istio, Linkerd)

### Appendix C: Monitoring Metrics
- **Gurobi-Specific**: Job queue depth, active jobs, thread utilization per node, solve times
- **Kubernetes**: Pod CPU/memory utilization, HPA scaling events, pod restart counts
- **Application**: API latency, request throughput, error rates, business model-specific KPIs

### Appendix D: Reference Documentation
- Gurobi Compute Server Documentation: https://docs.gurobi.com/projects/remoteservices/
- Web License Service Setup: https://support.gurobi.com/hc/en-us/articles/13232844297489
- Gurobi Docker Images: https://github.com/Gurobi/docker-compute
- Kubernetes HPA Guide: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

---

**Document Version**: 1.0  
**Date**: May 28, 2026  
**Author**: Optimiser Team  
**Classification**: Internal Use

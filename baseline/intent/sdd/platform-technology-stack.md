# Intent Platform Technology Stack

**Document status:** Baseline technology stack for SDD implementation.

## 1. Purpose:

This document defines the mandatory implementation stack for the Intent Management Platform.

The stack applies to all service implementation slices unless a later Architecture Decision Record changes the baseline.

This document is tool-neutral. GPT Codex, Claude Code or any other approved coding agent must follow this stack when generating implementation code.

## 2. Stack baseline:

| Area | Baseline |
|---|---|
| Service language | Java 21 |
| Service framework | Spring Boot 3.x |
| Build tool | Maven |
| API framework | Spring Web |
| Validation | Jakarta Bean Validation |
| Persistence | Spring Data JPA |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Spring Kafka |
| Local Kafka runtime | Redpanda or Apache Kafka through Docker Compose |
| API documentation | OpenAPI 3.x |
| Testing | JUnit 5, Mockito, Spring Boot Test |
| Integration testing | Testcontainers |
| Containerisation | Docker |
| Local runtime | Docker Compose |
| Container orchestration | Kubernetes |
| Deployment packaging | Helm charts |
| Service mesh | Istio |
| Service-to-service security | mTLS through Istio |
| Metrics instrumentation | Micrometer |
| Metrics collection | Prometheus |
| Telemetry dashboards | Grafana |
| Tracing readiness | OpenTelemetry-ready logging and tracing |
| Distributed tracing visualisation | Jaeger |
| Service mesh visualisation | Kiali |
| Logging | Structured JSON logging |
| Security baseline | Spring Security scaffold, no hardcoded secrets |
| Secrets management | AWS Secrets Manager |

## 3. Service implementation baseline:

All Intent Platform microservices must be implemented using Java 21 and Spring Boot 3.x.

The baseline applies to:

- ID MS
- IC MS
- ICB MS
- II MS
- IA MS

Each service must follow the same foundation pattern:

```text
src/main/java
src/main/resources
src/test/java
Dockerfile
pom.xml
README.md
```

Each service must expose:

- `GET /health`
- `GET /ready`

Health and readiness endpoints may be implemented through Spring Boot Actuator, provided the public paths remain stable for the platform runtime.

## 4. Shared foundation modules:

Shared implementation code should be placed under a common library module when the same behaviour is required by more than one service.

The shared foundation should include scaffolds for:

- correlation ID handling
- common error model
- event envelope
- idempotency
- outbox
- inbox
- Kafka producer wrapper
- Kafka consumer wrapper
- structured logging helpers
- metrics helpers
- tracing helpers
- Redis cache configuration helpers
- AWS Secrets Manager configuration readiness

Shared modules must not contain service-specific domain workflow logic.

## 5. Build tool decision:

Maven is the baseline build tool.

The repository should use a consistent Maven structure across all service modules and shared modules.

Do not mix Maven and Gradle in the same baseline unless an ADR approves the change.

## 6. Messaging baseline:

Kafka is the messaging abstraction for implementation.

Spring Kafka must be used for producer and consumer scaffolding.

For local development, Docker Compose may use either Redpanda or Apache Kafka, provided the local topic names and producer and consumer configuration remain compatible with the platform event contracts.

## 7. Persistence baseline:

PostgreSQL is the baseline relational database for local and deployable service persistence.

Spring Data JPA may be used for repository scaffolding.

The foundation slice must only create persistence scaffolding. It must not implement full domain persistence behaviour unless the relevant service slice requires it.

## 8. Cache baseline:

Redis is the baseline cache provider.

Caching must be explicit and service-owned. A service may use Redis only where the service specification or delivery slice defines a cache requirement.

Redis must not be used as a source of truth for domain state.

The foundation slice may include Redis dependency and configuration readiness, but it must not introduce cache-backed business behaviour.

## 9. API baseline:

REST APIs must be implemented using Spring Web.

OpenAPI 3.x files remain the executable API contract source of truth.

Generated or handwritten controllers must preserve:

- API paths
- request and response structures
- status codes
- error response model
- correlation ID behaviour

No service may rename public API paths without an ADR and contract update.

## 10. Container orchestration baseline:

Kubernetes is the baseline container orchestration platform.

Helm charts must be used for deployment packaging.

Docker Compose remains the local development runtime only. Docker Compose must not be treated as the production container orchestration baseline.

The foundation slice may include local Docker Compose and Helm chart scaffolding, but it must not create production-grade Kubernetes manifests unless the delivery slice explicitly requires them.

## 11. Service mesh baseline:

Istio is the baseline service mesh for deployed environments.

The platform must assume that service-to-service communication is protected through the service mesh.

The foundation slice may include configuration placeholders for service mesh readiness, but it must not create full production Istio policies unless the delivery slice explicitly requires them.

## 12. Service-to-service security baseline:

mTLS is the baseline for microservice-to-microservice communication.

In deployed environments, mTLS should be enforced through Istio service mesh policy.

Services must not implement custom service-to-service trust mechanisms that bypass the mesh.

Local development may run without Istio and mTLS, but local bypasses must be clearly scoped to local profiles and must not become production defaults.

## 13. Secrets management baseline:

AWS Secrets Manager is the baseline secrets provider.

Implementation must not commit secrets, credentials, tokens or production-like secret values into the repository.

Services must read secrets through configuration that can be backed by AWS Secrets Manager in deployed environments.

Local development may use safe local placeholders, but those placeholders must not be treated as production defaults.

The foundation slice may include configuration readiness for AWS Secrets Manager, but it must not create real secrets or production credentials.

## 14. Observability baseline:

All services must include observability scaffolding for:

- structured logs
- correlation ID propagation
- request tracing readiness
- metrics readiness
- health and readiness checks

Micrometer is the service metrics instrumentation baseline.

Prometheus is the baseline metrics collection platform.

Grafana is the baseline telemetry dashboard and visualisation platform.

OpenTelemetry-ready tracing must be supported so traces can be exported and visualised through Jaeger in deployed environments.

Jaeger is the baseline distributed tracing visualisation tool.

Kiali is the baseline visualisation tool for Istio service mesh topology, service-to-service traffic and mesh health.

The foundation slice may include service-level observability dependencies, configuration placeholders and documentation, but it must not create production-grade Prometheus, Grafana, Kiali or Jaeger deployment configuration unless the delivery slice explicitly requires it.

## 15. Testing baseline:

All services must include a test scaffold.

The baseline test stack is:

- JUnit 5 for unit tests
- Mockito for mocking
- Spring Boot Test for service tests
- Testcontainers for integration tests that require PostgreSQL, Kafka, Redis or other runtime dependencies

Each slice must provide test evidence before merge.

## 16. Security baseline:

Each service must include a Spring Security scaffold.

The foundation slice does not need to implement full production identity integration, but it must avoid insecure defaults that would block later hardening.

The implementation must not include:

- hardcoded secrets
- local credentials committed as production defaults
- unauthenticated administrative endpoints beyond local development scaffolding
- security bypasses hidden inside service code
- custom service-to-service mTLS code that bypasses Istio

## 17. Slice 01 implementation guidance:

For Slice 01 Foundation, coding agents must use this file as source of truth.

Slice 01 may create:

- Java 21 and Spring Boot 3.x service skeletons
- Maven module structure
- common library scaffolding
- Spring Web health and readiness endpoints
- Spring Security scaffold
- Spring Kafka producer and consumer scaffolding
- Spring Data JPA persistence scaffolding
- Redis configuration readiness
- AWS Secrets Manager configuration readiness
- Micrometer metrics readiness
- OpenTelemetry tracing readiness
- Docker Compose local runtime
- Helm chart scaffolding
- test scaffolds

Slice 01 must not create:

- full domain workflows
- production-grade Kubernetes manifests
- production-grade Istio policies
- custom mTLS implementation inside service code
- production-grade Prometheus, Grafana, Kiali or Jaeger deployment configuration
- real secrets or production credentials
- cache-backed business behaviour
- optimiser integration
- network apply integration

## 18. Explicit exclusions:

Coding agents must not use the following for service implementation unless a later ADR changes the platform stack:

- Python
- FastAPI
- Node.js
- TypeScript
- Go
- .NET
- Ruby
- PHP

These technologies may appear in tooling scripts only when explicitly approved and not used as the service runtime stack.

## 19. Agent instructions:

GPT Codex, Claude Code or any other approved coding agent must:

- read this file before generating service code
- use Java 21 and Spring Boot 3.x for service implementation
- use Maven consistently
- avoid introducing another runtime language
- avoid creating implementation files outside `baseline/intent/`
- avoid creating `/intents`, `intents/`, root-level `services/`, root-level `libs/`, root-level `platform/` or root-level `tests/`
- avoid changing architecture ownership boundaries
- avoid implementing domain workflows in foundation-only slices
- provide changed files and test evidence

## 20. Change control:

Changes to this technology stack require an Architecture Decision Record.

A coding agent must not change this file as part of implementation unless the task explicitly requests a stack update.

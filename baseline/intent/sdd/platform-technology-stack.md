# Intent Platform Technology Stack

**Document status:** Baseline technology stack for SDD implementation.

## 1. Purpose:

This document defines the mandatory implementation stack and repository implementation structure for the Intent Management Platform.

The stack applies to all service implementation slices unless a later Architecture Decision Record changes the baseline.

This document is tool-neutral. Approved coding agents must follow this stack when generating implementation code.

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
| Deployment packaging | Per-microservice Helm chart |
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

## 3. Repository implementation baseline:

All implementation code must be created under:

```text
baseline/intent/
```

Approved implementation roots are:

```text
baseline/intent/codebases/
baseline/intent/platform/
baseline/intent/tests/
```

Do not create:

```text
baseline/intent/services/
baseline/intent/libs/
services/
libs/
platform/
tests/
intents/
```

at repository root or under `baseline/intent/`.

The branch name is not a directory.

## 4. Microservice codebase baseline:

Each Intent Platform microservice must be implemented as an independently buildable, testable, deployable and versionable Spring Boot codebase.

The approved service implementation roots are:

```text
baseline/intent/codebases/id-ms/
baseline/intent/codebases/ic-ms/
baseline/intent/codebases/icb-ms/
baseline/intent/codebases/ii-ms/
baseline/intent/codebases/ia-ms/
```

Each microservice must own:

- its own Maven project
- its own source tree
- its own service-local tests
- its own Dockerfile
- its own Helm chart scaffold
- its own configuration
- its own persistence model
- its own PostgreSQL database or schema boundary
- its own Redis cache namespace
- its own deployment lifecycle

A microservice must not share:

- domain entities
- lifecycle state machines
- repository models
- service-local business rules
- persistence models
- database ownership
- cache namespaces
- runtime modules

Shared code must not be introduced by default.

If shared reusable technical libraries are required later, they must be introduced as independent shareable libraries through a dedicated ADR and delivery slice.

## 5. Service implementation baseline:

All Intent Platform microservices must be implemented using Java 21 and Spring Boot 3.x.

The baseline applies to:

- ID MS
- IC MS
- ICB MS
- II MS
- IA MS

Each service must follow the same independent codebase pattern:

```text
README.md
pom.xml
Dockerfile
helm/
src/main/java
src/main/resources
src/test/java
```

Each service must expose:

- `GET /health`
- `GET /ready`

Health and readiness endpoints may be implemented through Spring Boot Actuator, provided the public paths remain stable for the platform runtime.

## 6. Helm ownership baseline:

Each microservice owns its own Helm chart scaffold under its own codebase.

Approved chart locations are:

```text
baseline/intent/codebases/id-ms/helm/
baseline/intent/codebases/ic-ms/helm/
baseline/intent/codebases/icb-ms/helm/
baseline/intent/codebases/ii-ms/helm/
baseline/intent/codebases/ia-ms/helm/
```

Do not create a common Helm chart for all services by default.

The `baseline/intent/platform/` folder must not contain shared service charts by default. It may contain local development configuration, environment-level reference configuration, and platform capability scaffolding.

## 7. Test ownership baseline:

Service-local tests must live inside the owning microservice codebase.

Examples:

```text
baseline/intent/codebases/id-ms/src/test/java
baseline/intent/codebases/ic-ms/src/test/java
baseline/intent/codebases/icb-ms/src/test/java
baseline/intent/codebases/ii-ms/src/test/java
baseline/intent/codebases/ia-ms/src/test/java
```

Cross-service tests must live under:

```text
baseline/intent/tests/
```

The platform-level `tests/` folder is only for:

- contract tests
- cross-service smoke tests
- end-to-end tests

Do not create shared test libraries by default.

If reusable test support is required later, it must be introduced as an independent shareable test-support library through a dedicated ADR and delivery slice.

## 8. Platform environment baseline:

The `baseline/intent/platform/` folder is for platform environment scaffolding only.

It may contain:

- local Docker Compose runtime
- Kafka or Redpanda local runtime readiness
- PostgreSQL local runtime readiness
- Redis local runtime readiness
- Prometheus configuration placeholders
- Grafana configuration placeholders
- Jaeger configuration placeholders
- Istio readiness placeholders
- Kiali readiness placeholders
- AWS Secrets Manager readiness notes
- CI/CD examples

It must not contain:

- shared domain code
- shared service runtime code
- shared service Helm charts by default
- service-specific business behaviour
- service-specific persistence models

## 9. Build tool decision:

Maven is the baseline build tool.

Each microservice must have its own Maven project.

Do not mix Maven and Gradle in the same baseline unless an ADR approves the change.

## 10. Messaging baseline:

Kafka is the messaging abstraction for implementation.

Spring Kafka must be used for producer and consumer scaffolding.

For local development, Docker Compose may use either Redpanda or Apache Kafka, provided the local topic names and producer and consumer configuration remain compatible with the platform event contracts.

## 11. Persistence baseline:

PostgreSQL is the baseline relational database for local and deployable service persistence.

Each microservice owns its own PostgreSQL database or schema boundary.

Spring Data JPA may be used for repository scaffolding.

A microservice must not directly read or write another microservice's database or schema.

## 12. Cache baseline:

Redis is the baseline cache provider.

Each microservice owns its own Redis cache namespace and cache configuration.

Caching must be explicit and service-owned. A service may use Redis only where the service specification or delivery slice defines a cache requirement.

Redis must not be used as a source of truth for domain state.

## 13. API baseline:

REST APIs must be implemented using Spring Web.

OpenAPI 3.x files remain the executable API contract source of truth.

Generated or handwritten controllers must preserve:

- API paths
- request and response structures
- status codes
- error response model
- correlation ID behaviour

No service may rename public API paths without an ADR and contract update.

## 14. Container orchestration baseline:

Kubernetes is the baseline container orchestration platform.

Each microservice must be independently deployable to Kubernetes through its own Helm chart scaffold.

Docker Compose remains the local development runtime only. Docker Compose must not be treated as the production container orchestration baseline.

## 15. Service mesh baseline:

Istio is the baseline service mesh for deployed environments.

The platform must assume that service-to-service communication is protected through the service mesh.

Services must not implement custom service-to-service trust mechanisms that bypass the mesh.

## 16. Service-to-service security baseline:

mTLS is the baseline for microservice-to-microservice communication.

In deployed environments, mTLS should be enforced through Istio service mesh policy.

Local development may run without Istio and mTLS, but local bypasses must be clearly scoped to local profiles and must not become production defaults.

## 17. Secrets management baseline:

AWS Secrets Manager is the baseline secrets provider.

Implementation must not commit secrets, credentials, tokens or production-like secret values into the repository.

Services must read secrets through configuration that can be backed by AWS Secrets Manager in deployed environments.

Local development may use safe local placeholders, but those placeholders must not be treated as production defaults.

## 18. Observability baseline:

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

## 19. Security baseline:

Each service must include a Spring Security scaffold.

The implementation must not include:

- hardcoded secrets
- local credentials committed as production defaults
- unauthenticated administrative endpoints beyond local development scaffolding
- security bypasses hidden inside service code
- custom service-to-service mTLS code that bypasses Istio

## 20. Explicit exclusions:

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

## 21. Agent instructions:

Approved coding agents must:

- read this file before generating service code
- use Java 21 and Spring Boot 3.x for service implementation
- use Maven consistently
- create individually deployable codebases under `baseline/intent/codebases/{ms}/`
- create one Helm chart scaffold per microservice under `baseline/intent/codebases/{ms}/helm/`
- keep service-local tests inside each owning microservice codebase
- place only cross-service contract, smoke and e2e tests under `baseline/intent/tests/`
- avoid introducing shared implementation code by default
- avoid creating `baseline/intent/libs/`
- avoid creating `baseline/intent/services/`
- avoid creating `/intents`, `intents/`, root-level `services/`, root-level `libs/`, root-level `platform/` or root-level `tests/`
- avoid changing architecture ownership boundaries
- provide changed files and test evidence

## 22. Change control:

Changes to this technology stack or implementation structure require an Architecture Decision Record.

A coding agent must not change this file as part of implementation unless the task explicitly requests a stack or structure update.

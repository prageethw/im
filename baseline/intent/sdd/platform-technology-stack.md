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
| Messaging | Spring Kafka |
| Local Kafka runtime | Redpanda or Apache Kafka through Docker Compose |
| API documentation | OpenAPI 3.x |
| Testing | JUnit 5, Mockito, Spring Boot Test |
| Integration testing | Testcontainers |
| Containerisation | Docker |
| Local runtime | Docker Compose |
| Deployment packaging | Helm charts |
| Observability | Micrometer, OpenTelemetry-ready logging and tracing |
| Logging | Structured JSON logging |
| Security baseline | Spring Security scaffold, no hardcoded secrets |

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

Shared modules must not contain service-specific domain workflow logic.

## 5. Build tool decision:

Maven is the baseline build tool.

The repository should use a consistent Maven structure across all service modules and shared modules.

Do not mix Maven and Gradle in the same baseline unless an Architecture Decision Record approves the change.

## 6. Messaging baseline:

Kafka is the messaging abstraction for implementation.

Spring Kafka must be used for producer and consumer scaffolding.

For local development, Docker Compose may use either Redpanda or Apache Kafka, provided the local topic names and producer and consumer configuration remain compatible with the platform event contracts.

## 7. Persistence baseline:

PostgreSQL is the baseline relational database for local and deployable service persistence.

Spring Data JPA may be used for repository scaffolding.

The foundation slice must only create persistence scaffolding. It must not implement full domain persistence behaviour unless the relevant service slice requires it.

## 8. API baseline:

REST APIs must be implemented using Spring Web.

OpenAPI 3.x files remain the executable API contract source of truth.

Generated or handwritten controllers must preserve:

- API paths
- request and response structures
- status codes
- error response model
- correlation ID behaviour

No service may rename public API paths without an Architecture Decision Record and contract update.

## 9. Testing baseline:

All services must include a test scaffold.

The baseline test stack is:

- JUnit 5 for unit tests
- Mockito for mocking
- Spring Boot Test for service tests
- Testcontainers for integration tests that require PostgreSQL, Kafka or other runtime dependencies

Each slice must provide test evidence before merge.

## 10. Observability baseline:

All services must include observability scaffolding for:

- structured logs
- correlation ID propagation
- request tracing readiness
- metrics readiness
- health and readiness checks

Micrometer should be included for metrics readiness.

OpenTelemetry integration should be supported by configuration, but full tracing rollout may be completed in a later operational slice.

## 11. Security baseline:

Each service must include a Spring Security scaffold.

The foundation slice does not need to implement full production identity integration, but it must avoid insecure defaults that would block later hardening.

The implementation must not include:

- hardcoded secrets
- local credentials committed as production defaults
- unauthenticated administrative endpoints beyond local development scaffolding
- security bypasses hidden inside service code

## 12. Explicit exclusions:

Coding agents must not use the following for service implementation unless a later Architecture Decision Record changes the platform stack:

- Python
- FastAPI
- Node.js
- TypeScript
- Go
- .NET
- Ruby
- PHP

These technologies may appear in tooling scripts only when explicitly approved and not used as the service runtime stack.

## 13. Agent instructions:

GPT Codex, Claude Code or any other approved coding agent must:

- read this file before generating service code
- use Java 21 and Spring Boot 3.x for service implementation
- use Maven consistently
- avoid introducing another runtime language
- avoid changing architecture ownership boundaries
- avoid implementing domain workflows in foundation-only slices
- provide changed files and test evidence

## 14. Change control:

Changes to this technology stack require an Architecture Decision Record.

A coding agent must not change this file as part of implementation unless the task explicitly requests a stack update.

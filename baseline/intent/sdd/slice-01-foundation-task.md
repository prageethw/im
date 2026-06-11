# Slice 01 Foundation Task

**Document status:** Agent-neutral SDD execution task for Slice 01 Foundation.

## 1. Purpose:

This task instructs an approved coding agent to implement the foundation skeleton for the Intent Management Platform.

Slice 01 creates independently deployable Spring Boot microservice codebase skeletons and platform environment scaffolding only. It must not implement service-specific domain workflows.

This task is agent-neutral. It may be executed by GPT Codex, Claude Code or another approved coding agent, provided the agent follows the same SDD documents, platform technology stack, architecture guardrails and review gates.

## 2. Source of truth:

Read and follow these files before generating code:

- `baseline/intent/sdd/README.md`
- `baseline/intent/sdd/platform-build-plan.md`
- `baseline/intent/sdd/service-build-order.md`
- `baseline/intent/sdd/platform-technology-stack.md`
- `baseline/intent/sdd/slices/slice-01-foundation.md`
- `baseline/intent/agent-playbooks/common/architecture-guardrails.md`

Use the service specifications as architecture context only:

- `baseline/intent/id-ms/`
- `baseline/intent/ic-ms/`
- `baseline/intent/icb-ms/`
- `baseline/intent/ii-ms/`
- `baseline/intent/ia-ms/`

## 3. Mandatory technology and structure baseline:

Use the platform technology stack file as the mandatory implementation baseline:

- `baseline/intent/sdd/platform-technology-stack.md`

The service implementation stack is:

- Java 21
- Spring Boot 3.x
- Maven
- Spring Web
- Spring Boot Actuator
- Spring Security scaffold
- Spring Kafka scaffold
- Spring Data JPA scaffold
- PostgreSQL readiness
- Redis readiness
- AWS Secrets Manager configuration readiness
- Micrometer metrics readiness
- OpenTelemetry tracing readiness
- Docker Compose for local runtime support
- per-microservice Helm chart scaffolding

Do not use Python, FastAPI, Node.js, TypeScript, Go, .NET, Ruby or PHP for service implementation.

## 4. Critical repository path rules:

The only valid implementation root is:

```text
baseline/intent/
```

Create only these implementation roots:

```text
baseline/intent/codebases/
baseline/intent/platform/
baseline/intent/tests/
```

Do not create or use:

```text
/intents
intents/
baseline/intent/services/
baseline/intent/libs/
services/
libs/
platform/
tests/
```

at repository root or under `baseline/intent/`.

Do not create a folder named after the branch.

The branch is only a Git branch. It is not a directory.

## 5. Required independent service codebases:

Create independently deployable Spring Boot codebase skeletons for:

- `baseline/intent/codebases/id-ms/`
- `baseline/intent/codebases/ic-ms/`
- `baseline/intent/codebases/icb-ms/`
- `baseline/intent/codebases/ii-ms/`
- `baseline/intent/codebases/ia-ms/`

Each service codebase must include:

- Maven `pom.xml`
- Spring Boot application entry point
- `GET /health`
- `GET /ready`
- common error response scaffold local to that service
- correlation ID handling scaffold local to that service
- structured JSON logging scaffold local to that service
- configuration scaffold
- Spring Security scaffold
- PostgreSQL datasource readiness
- Redis cache namespace readiness
- AWS Secrets Manager configuration readiness
- Micrometer metrics readiness
- OpenTelemetry tracing readiness
- Dockerfile
- service-owned Helm chart scaffold under `helm/`
- service-local tests under `src/test/java`
- service README

Health and readiness endpoints may use Spring Boot Actuator if the public paths remain stable.

## 6. No shared code rule:

Do not create shared implementation code in this slice.

Do not create:

- shared libraries
- common modules
- shared runtime modules
- shared domain models
- shared persistence models
- shared test libraries
- `baseline/intent/libs/`

If shared reusable technical libraries are required later, they must be introduced as independent shareable libraries through a dedicated ADR and delivery slice.

## 7. Required platform environment scaffolding:

Create platform environment scaffolding under:

```text
baseline/intent/platform/
```

The platform folder is for environment scaffolding only.

Include placeholders or local scaffolding for:

- Docker Compose local runtime
- local Kafka or Redpanda readiness
- local PostgreSQL readiness
- local Redis readiness
- Prometheus configuration placeholders
- Grafana configuration placeholders
- Jaeger configuration placeholders
- Istio readiness placeholders
- Kiali readiness placeholders
- AWS Secrets Manager readiness notes
- CI/CD examples if useful

Do not create shared service code or common service Helm charts under `platform/`.

## 8. Required cross-service test scaffolding:

Create cross-service test scaffolding under:

```text
baseline/intent/tests/
```

Include structure for:

- contract tests
- cross-service smoke tests
- end-to-end tests

Service-local unit and component tests must remain inside each owning microservice codebase under `src/test/java`.

Do not create shared test libraries.

## 9. Explicit exclusions:

Do not implement:

- full domain workflows
- full TMF921 APIs
- optimiser integration
- network apply integration
- production-grade Kubernetes manifests
- production-grade Istio policies
- custom mTLS implementation inside service code
- cache-backed business behaviour
- real secrets or production credentials
- production-grade Prometheus, Grafana, Kiali or Jaeger deployment configuration
- shared service runtime
- shared domain model
- shared database model
- shared cache namespace

Do not rename:

- API paths
- event names
- topic names
- lifecycle states
- service ownership boundaries

Do not move ownership boundaries between ID MS, IC MS, ICB MS, II MS and IA MS.

## 10. Expected output:

Open a pull request or produce a working tree change set with:

- summary of the foundation skeleton
- changed file list
- how to run each service locally
- how to run each service's tests
- how to run cross-service smoke tests if scaffolded
- known gaps
- test evidence

## 11. Acceptance criteria:

The Slice 01 change set is complete only when:

- all generated implementation files are under `baseline/intent/`
- service codebases are under `baseline/intent/codebases/<ms>/`
- no `baseline/intent/services/` folder is created
- no `baseline/intent/libs/` folder is created
- no root-level `intents/`, `services/`, `libs/`, `platform/` or `tests/` folders are created
- each service has its own Maven project
- each service has its own Dockerfile
- each service has its own Helm chart scaffold
- each service has its own service-local tests
- each service exposes `GET /health`
- each service exposes `GET /ready`
- each service has PostgreSQL readiness configuration
- each service has Redis namespace readiness configuration
- each service has AWS Secrets Manager configuration readiness
- each service has Micrometer and OpenTelemetry readiness
- platform environment scaffolding is under `baseline/intent/platform/`
- cross-service test scaffolding is under `baseline/intent/tests/`
- no shared implementation code is created
- no domain workflow is implemented in this slice

## 12. Post-run evidence:

After implementation, provide:

```text
git status --short
git diff --stat
find baseline/intent/codebases -maxdepth 2 -type d -print
find baseline/intent -maxdepth 2 -type d \( -name codebases -o -name platform -o -name tests -o -name services -o -name libs \) -print
find . -maxdepth 2 -type d \( -name intents -o -name services -o -name libs -o -name platform -o -name tests \) -print
```

The second and third find commands must not show disallowed generated implementation folders.

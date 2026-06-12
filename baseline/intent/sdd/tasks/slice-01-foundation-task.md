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

## 10. Code comments rule:

Generated code must include comments only where they explain non-obvious architectural intent, service ownership boundaries, intentional placeholders or future-slice extension points.

Comments should explain why something exists, not restate obvious Java or Spring syntax.

Use comments for:

- service ownership boundaries
- intentional Slice 01 placeholders
- future-slice extension points
- security or secrets-management constraints
- cache namespace ownership
- readiness and health contract stability
- cross-service integration assumptions

Avoid comments such as:

- `This is a controller.`
- `This method returns a value.`
- `Set the variable.`
- comments that simply repeat the class or method name

Prefer comments such as:

- `Slice 01 intentionally exposes readiness only. Domain workflow endpoints are introduced in later slices.`
- `This Redis namespace keeps cache keys service-owned and must not be shared across microservices.`
- `AWS Secrets Manager integration is represented as configuration readiness only. No real secrets must be committed.`

## 11. Test coverage rule:

Test coverage is required, but coverage alone is not proof of correctness.

For Slice 01 Foundation, each generated microservice must meet:

- minimum 70% line coverage
- minimum 60% branch coverage
- explicit tests for required scaffolding paths

Slice 01 tests must include:

- application context starts
- `GET /health` returns 200
- `GET /ready` returns 200
- correlation ID is accepted or generated
- basic error response shape is stable
- security scaffold does not expose unintended endpoints
- local profile configuration loads successfully

Coverage must not be achieved through shallow tests that only instantiate classes or call getters.

Acceptance criteria, API contract tests, event contract tests and lifecycle scenario tests remain the primary proof of correctness.

For later domain and production slices, the expected baseline is:

- minimum 80% line coverage
- minimum 70% branch coverage
- explicit scenario tests for lifecycle rules, event handling, idempotency and state transitions
- 90% or higher coverage for critical lifecycle, event and idempotency logic where feasible

## 12. External dependency mocking rule:

Generated code may use mocks, stubs or test doubles for external systems only where required for local execution, isolated tests or unavailable dependencies.

Mocks must:

- be clearly located under test or local-development scaffolding
- match the expected contract shape where a contract exists
- avoid inventing new API paths, event names or payload semantics
- include happy-path and failure-path examples where relevant
- be clearly documented as non-production scaffolding

Mocks must not:

- replace API or event contract tests
- become production integration code
- hide missing integration decisions
- introduce behaviour not present in the architecture or contracts
- create fake source-of-truth data ownership

For Slice 01 Foundation, external systems may be mocked only to prove service startup, readiness, local configuration and test isolation.

## 13. Agent stop conditions:

The agent must stop and report instead of guessing when a required decision or contract is missing.

Stop and report if:

- a required source-of-truth file is missing
- the architecture documents conflict with API or event contracts
- folder structure or implementation root is unclear
- implementation would require changing service ownership boundaries
- implementation would require inventing an API path, event name, topic name, lifecycle state or integration behaviour
- tests cannot pass without inventing behaviour not defined in this task
- an external API or event contract is unavailable but required for the slice
- generated code would require shared implementation code not approved by this slice
- the task would create disallowed folders such as `services/`, `libs/` or `intents/`

When a stop condition is reached, provide:

- the blocking issue
- the file or contract that caused the issue
- the decision required from a human
- any safe partial work already completed

## 14. Agent evidence pack and review checklist:

Every run must provide an evidence pack.

The evidence pack must include:

- `git status --short`
- `git diff --stat`
- changed files list
- test command output
- coverage summary per microservice
- mock or stub summary where external dependencies are isolated
- architecture boundary check
- forbidden folder check
- known gaps and deferred work

The architecture boundary check must confirm:

- generated implementation files stay under `baseline/intent/`
- microservice codebases stay under `baseline/intent/codebases/{ms}/`
- no shared implementation libraries were created
- no public API paths were renamed
- no event names or topic names were invented
- no lifecycle states were invented
- no service ownership boundaries were moved
- no future-slice domain workflow was implemented early

The forbidden folder check must confirm that the run did not create:

- `baseline/intent/services/`
- `baseline/intent/libs/`
- root-level `intents/`
- root-level `services/`
- root-level `libs/`
- root-level `platform/`
- root-level `tests/`

Human review must check:

- the generated code satisfies only Slice 01
- tests prove meaningful behaviour
- comments explain only non-obvious intent
- mocks stay under test or local-development scaffolding
- contracts remain the source of truth
- implementation does not overbuild future slices

## 15. Expected output:

Open a pull request or produce a working tree change set with:

- summary of the foundation skeleton
- changed file list
- how to run each service locally
- how to run each service's tests
- how to run cross-service smoke tests if scaffolded
- known gaps
- test evidence
- coverage summary per microservice
- mock or stub summary where external dependencies are isolated

## 16. Acceptance criteria:

The Slice 01 change set is complete only when:

- all generated implementation files are under `baseline/intent/`
- service codebases are under `baseline/intent/codebases/{ms}/`
- no `baseline/intent/services/` folder is created
- no `baseline/intent/libs/` folder is created
- no root-level `intents/`, `services/`, `libs/`, `platform/` or `tests/` folders are created
- each service has its own Maven project
- each service has its own Dockerfile
- each service has its own Helm chart scaffold
- each service has its own service-local tests
- each service meets minimum 70% line coverage
- each service meets minimum 60% branch coverage
- each service has explicit tests for health, readiness, correlation ID, error shape, security scaffold and local configuration
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
- external dependency mocks are limited to test or local-development scaffolding
- external dependency mocks do not replace contract tests or production integration decisions
- architecture boundary check confirms no ownership boundaries were moved
- forbidden folder check confirms no disallowed folders were created
- known gaps and deferred work are documented

## 17. Post-run evidence:

After implementation, provide:

```text
git status --short
git diff --stat
find baseline/intent/codebases -maxdepth 2 -type d -print
find baseline/intent -maxdepth 2 -type d \( -name codebases -o -name platform -o -name tests -o -name services -o -name libs \) -print
find . -maxdepth 2 -type d \( -name intents -o -name services -o -name libs -o -name platform -o -name tests \) -print
```

The second and third find commands must not show disallowed generated implementation folders.

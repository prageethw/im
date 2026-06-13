# Slice 01 Foundation

**Document status:** Agent-neutral delivery slice definition for the Intent Platform foundation.

**Slice version:** `1.0.0`

**Version baseline:** `intent-platform-versions-2026-06-13`

## 1. Purpose:

Slice 01 establishes the implementation foundation for the Intent Management Platform.

It creates independently deployable Spring Boot microservice skeletons and platform environment scaffolding only.

Slice 01 must not implement domain workflows, full TMF921 APIs, optimiser integration, network apply integration or production-grade deployment configuration.

## 2. Execution staging:

Slice 01 must be executed in three controlled sub-slices.

### 2.1 Slice 01A — Golden ID MS foundation skeleton:

The first coding run must implement only:

- `baseline/intent/codebases/id-ms/`
- `baseline/intent/platform/`
- `baseline/intent/tests/`

Slice 01A establishes ID MS as the reviewed golden service skeleton pattern.

Slice 01A must use `sdd/platform-version-baseline.md` and pass `sdd/validation/validate-slice-01a.sh`.

Slice 01A must prove:

- ID MS starts successfully
- `GET /health` returns 200
- `GET /ready` returns 200
- local configuration loads
- correlation ID handling is scaffolded and tested
- basic error response shape is scaffolded and tested
- security scaffold is present and tested
- PostgreSQL readiness configuration exists
- Redis namespace readiness configuration exists
- AWS Secrets Manager configuration readiness exists
- Micrometer and OpenTelemetry readiness exists
- Dockerfile exists
- Helm chart scaffold exists
- service-local tests exist
- coverage gates are met
- no forbidden folders are created

Do not create `ic-ms`, `icb-ms`, `ii-ms` or `ia-ms` implementation code in Slice 01A.

### 2.2 Slice 01B — Replicate approved skeleton pattern:

Slice 01B may start only after Slice 01A is reviewed and accepted by a human.

Slice 01B replicates the approved ID MS skeleton pattern to:

- `baseline/intent/codebases/ic-ms/`
- `baseline/intent/codebases/icb-ms/`
- `baseline/intent/codebases/ii-ms/`
- `baseline/intent/codebases/ia-ms/`

Replication must preserve independent codebases.

Replication must not introduce shared implementation libraries or move service ownership boundaries.

### 2.3 Slice 01C — Cross-service smoke, coverage and evidence cleanup:

Slice 01C may start only after Slice 01B is reviewed and accepted by a human.

Slice 01C verifies:

- all five service skeletons start
- all five service health endpoints respond
- all five service readiness endpoints respond
- coverage evidence is captured per microservice
- forbidden folder checks pass
- architecture boundary checks pass
- mock and stub summaries are documented
- known gaps and deferred work are documented

## 3. Completion rule:

Slice 01 is complete only when:

- Slice 01A has passed human review
- Slice 01B has passed human review
- Slice 01C evidence has been captured
- no forbidden folders were created
- no service ownership boundaries were moved
- no future-slice domain workflow was implemented early
- exact version pins match the approved baseline
- the automated validator passed

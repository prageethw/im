# Slice 01 Foundation

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice establishes the engineering foundation required before individual Intent Platform services are implemented.

## 2. Scope:

The foundation slice covers shared service scaffolding, local development, API contract generation, event contract validation, outbox and inbox patterns, observability baseline, security baseline and deployment packaging.

## 3. In scope:

- Repository structure for services, contracts, tests and platform deployment.
- Common service template.
- Health, readiness and liveness endpoints.
- Correlation id middleware.
- Platform error model.
- OpenAPI validation test framework.
- JSON schema event validation framework.
- Kafka producer and consumer scaffolding.
- Outbox and inbox persistence patterns.
- Local docker compose environment.
- Helm chart baseline.
- Basic logging, metrics and tracing hooks.
- Agent-neutral SDD task and review templates.

## 4. Out of scope:

- Full business behaviour for any individual MS.
- Production network integration.
- Optimiser integration.
- Full assurance logic.
- Full TMF921 conformance evidence.

## 5. Build tasks:

| ID | Task |
|---|---|
| FND-001 | Create service skeleton template with standard package layout. |
| FND-002 | Add common HTTP middleware for correlation id, request logging and error handling. |
| FND-003 | Add OpenAPI contract validation in CI. |
| FND-004 | Add event schema validation in CI. |
| FND-005 | Implement outbox persistence and relay scaffold. |
| FND-006 | Implement inbox deduplication scaffold. |
| FND-007 | Add docker compose for local database, Kafka and service execution. |
| FND-008 | Add Helm chart baseline for each service. |
| FND-009 | Add test evidence reporting template. |
| FND-010 | Add agent instructions for approved coding agents. |

## 6. Acceptance criteria:

- A new service can be generated from the template and run locally.
- Health, readiness and liveness endpoints respond consistently.
- Contract tests can run in CI.
- Event schema tests can run in CI.
- Outbox relay can publish a test event to Kafka.
- Inbox deduplication prevents duplicate handling of a test event.
- Logs include service name, correlation id and request or event identity.
- Helm chart renders without error.

## 7. Test evidence:

- Unit test report.
- Component test report.
- OpenAPI validation report.
- Event schema validation report.
- Local docker compose smoke test.
- Helm template validation output.

## 8. Done when:

The team can create, run, test and package a skeleton MS without implementing domain-specific Intent Platform behaviour.

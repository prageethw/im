# ICB MS Baseline Pack

This document consolidates the currently baselined **ICB MS** role and interface boundary.

## Scope:

This pack includes:
- ICB MS role and purpose
- canonical flow
- what ICB MS does and does not own
- gateway responsibility split
- canonical ICB MS interfaces
- southbound interaction model

---

# 0. Naming note:

- `CB` means circuit breaker.
- `ICB MS` means Intent Callback MS / `intent-callback-ms`.
- Do not use `CB MS` for the callback service.


# 1. ICB MS role:

ICB MS is the incoming-only REST wrapper / callback access mediation layer for the Intent Domain.

Canonical flow:

`external client / orchestrator -> gateway -> ICB MS -> Kafka/native broker topics`

# 2. ICB MS exists for:

- clients that cannot use native topic access directly
- clients that should not use native topic access directly
- external, thin, legacy, or restricted-network producers that need HTTPS-based submission
- situations where funding, delivery timeline, or contractual commitments require a REST-wrapper / event-gateway-style interface to be established

# 3. ICB MS does:

- receive incoming requests behind the gateway
- perform wrapper-level request validation
- map HTTP request shape to internal event/message shape
- publish/mediate into internal Kafka/native broker topics
- return synchronous acknowledgement and correlation/reference id
- expose operational endpoints

# 4. ICB MS does not:

- expose events for clients
- provide event retrieval APIs
- provide polling/list-event APIs
- provide subscription helper APIs
- act as an outbound notification gateway
- replicate broker consumer-group behaviour over HTTP
- own semantic interpretation, policy evaluation, optimisation, or assurance

# 5. Gateway responsibilities:

The gateway handles:
- authn/authz
- rate limiting
- edge governance
- edge traffic policy

ICB MS sits behind the gateway and should not own edge security/governance.

# 6. Canonical ICB MS interfaces:

## 6.1 Command/status submission API:

Used when an external client or orchestrator submits a business request or status update over HTTPS.

Examples:
- orchestrator submits intent-related status from the network
- client publishes a wrapper-managed event request

Behaviour:
- synchronous HTTP request/response
- synchronous return of acknowledgement and correlation/reference id
- backend event/domain processing continues asynchronously after acceptance

## 6.2 Operational endpoints:

Used by platform operations.

Examples:
- health
- readiness
- liveness
- metrics endpoint for platform monitoring if needed

# 7. Southbound interaction:

ICB MS publishes/mediates accepted incoming requests into internal Kafka/native broker topics.

Preferred southbound flow:

`ICB MS -> Kafka/native broker topics`

Avoid direct calls to internal domain MS APIs unless a specific synchronous requirement appears later.

# 8. Suggested baseline statement:

ICB MS is the incoming-only REST wrapper for the Intent Domain. It sits behind the gateway, accepts HTTPS submissions from external/constrained clients or orchestrators, returns a synchronous acknowledgement with correlation/reference id, and publishes/mediates the accepted request into internal Kafka/native broker topics. It does not expose events for clients.
---

# 9. Concrete API contract:

## 9.1 Interface set:

```http
POST /intent/callback/v1/submissions
GET /intent/callback/v1/health
```

## 9.2 POST /intent/callback/v1/submissions:

### Purpose:

External client or orchestrator submits intent-related callback/status input over HTTPS.

ICB MS:
- validates wrapper-level request shape
- mediates/publishes the accepted submission into internal Kafka/native broker topics
- returns synchronous success/failure response

### Request:

```http
POST /intent/callback/v1/submissions
Content-Type: application/json
```

```json
{
  "callbackType": "intentNetworkStatus",
  "correlationId": "INT-HOSP-2026-001-INIT",
  "source": {
    "system": "network-orchestrator",
    "name": "ORCHESTRATOR_SYDNEY_ZONE"
  },
  "intentId": "INT-HOSP-2026-001",
  "status": {
    "lifecycleStatus": "Active",
    "statusReason": "Configuration applied successfully and service is active.",
    "statusChangeDate": "2026-04-18T12:05:00+10:00"
  }
}
```

### Success response:

Use `202 Accepted` because ICB MS accepts and mediates into internal processing.

```http
HTTP/1.1 202 Accepted
Content-Type: application/json
```

```json
{
  "submissionId": "SUB-INT-HOSP-2026-001-0001",
  "correlationId": "INT-HOSP-2026-001-INIT",
  "status": "accepted",
  "message": "Submission accepted for internal processing."
}
```

### Validation failure response:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
  "code": "INVALID_CALLBACK_SUBMISSION",
  "reason": "Invalid callback submission",
  "message": "The callback submission payload is missing required fields or contains invalid values.",
  "status": 400,
  "referenceError": "https://mycsp.com.au/errors/INVALID_CALLBACK_SUBMISSION",
  "@type": "Error"
}
```

### Publish/mediation failure response:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
```

```json
{
  "code": "CALLBACK_MEDIATION_UNAVAILABLE",
  "reason": "Callback mediation unavailable",
  "message": "The callback submission could not be mediated into the internal event path. The caller may retry the submission.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/CALLBACK_MEDIATION_UNAVAILABLE",
  "@type": "Error"
}
```

## 9.3 GET /intent/callback/v1/health:

### Request:

```http
GET /intent/callback/v1/health
```

### Ready response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "state": "ready",
  "service": "intent-callback-ms",
  "checkedAt": "2026-04-25T11:45:00+10:00"
}
```

### Failed response:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
```

```json
{
  "state": "failed",
  "service": "intent-callback-ms",
  "checkedAt": "2026-04-25T11:45:00+10:00"
}
```

## 9.4 Boundary rules:

- no lookup endpoint
- no event exposure endpoint
- no client event consumption
- no `references` in request body
- caller retries/re-submits on synchronous failure


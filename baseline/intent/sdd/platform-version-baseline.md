# Intent Platform Version Baseline

**Document status:** Approved implementation version baseline for Slice 01A.

**Baseline identifier:** `intent-platform-versions-2026-06-13`

**Baseline date:** 13 June 2026

## 1. Purpose:

This document removes version-selection ambiguity before agent-assisted implementation begins.

Coding agents must use these exact versions for Slice 01A unless a human-approved Architecture Decision Record changes the baseline.

Agents must not silently upgrade, downgrade or substitute a component.

## 2. Runtime and framework versions:

| Component | Approved version or value |
|---|---|
| Java distribution | Eclipse Temurin 21.0.11+10 |
| Java language level | 21 |
| Runtime container image | `eclipse-temurin:21.0.11_10-jre-jammy` |
| Spring Boot | 3.5.14 |
| Apache Maven | 3.9.16 |
| Apache Maven Wrapper plugin | 3.3.4 |
| Maven Wrapper distribution | Apache Maven 3.9.16 |
| PostgreSQL container | `postgres:18.4` |
| Redis container | `redis:8.8.0` |
| Apache Kafka container | `apache/kafka:4.3.0` |
| Kubernetes compatibility target | 1.36.1 |
| Helm CLI | 4.2.0 |
| Helm chart API | `apiVersion: v2` |
| Initial Helm chart version | `0.1.0` |
| Initial Helm appVersion | `0.1.0` |
| Initial ID MS image tag | `intent-id-ms:0.1.0-slice01a` |

## 3. Maven quality and supply-chain plugin versions:

| Component | Approved version |
|---|---|
| Maven Enforcer Plugin | 3.6.3 |
| Spotless Maven Plugin | 3.6.0 |
| Google Java Format | 1.28.0 |
| SpotBugs Maven Plugin | 4.9.8.3 |
| JaCoCo Maven Plugin | 0.8.15 |
| CycloneDX Maven Plugin | 2.9.1 |
| OWASP Dependency-Check Maven Plugin | 12.2.2 |

JUnit, Mockito, Spring Framework, Spring Security, Spring Kafka, Spring Data and other Spring-managed dependency versions must come from the Spring Boot 3.5.14 dependency management baseline unless an ADR explicitly overrides them.

## 4. External validation tool versions:

| Tool | Approved version |
|---|---|
| Gitleaks | 8.30.1 |
| Trivy | 0.70.0 |

Trivy binaries and container images must be verified using the published checksum or signed release evidence before use.

Do not use Trivy 0.69.4.

Do not use floating GitHub Action tags for security tools. Pin an immutable release tag and, where supported, a commit SHA or verified digest.

## 5. Version rules:

- Do not use `SNAPSHOT`, `LATEST`, `RELEASE`, version ranges or floating container tags.
- Do not infer newer versions merely because they are available.
- Do not replace Apache Kafka with Redpanda in Slice 01A.
- Do not replace Eclipse Temurin with another Java distribution.
- Do not replace the approved Maven plugins with alternative quality tools.
- Pin every explicitly configured Maven plugin version.
- Pin every container image tag used by Docker Compose or Dockerfiles.
- The Maven Wrapper properties file must resolve Apache Maven 3.9.16.
- The ID MS README and evidence pack must list the versions actually used.
- The automated Slice 01A validator must confirm the critical version pins.

## 6. Change control:

Any version change requires:

1. documented reason
2. compatibility and security assessment
3. updated version baseline
4. updated validation script where applicable
5. human approval
6. Architecture Decision Record when the change alters the platform baseline

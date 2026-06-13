#!/usr/bin/env bash
set -uo pipefail

BASE_REF="${1:-HEAD}"
EXPECTED_TASK_VERSION="1.0.0"
EXPECTED_VERSION_BASELINE="intent-platform-versions-2026-06-13"
EXPECTED_SPRING_BOOT="3.5.14"
EXPECTED_MAVEN="3.9.16"
EXPECTED_RUNTIME_IMAGE="eclipse-temurin:21.0.11_10-jre-jammy"
EXPECTED_POSTGRES_IMAGE="postgres:18.4"
EXPECTED_REDIS_IMAGE="redis:8.8.0"
EXPECTED_KAFKA_IMAGE="apache/kafka:4.3.0"
EXPECTED_HELM_VERSION="0.1.0"
EXPECTED_APP_VERSION="0.1.0"
EXPECTED_IMAGE_TAG="intent-id-ms:0.1.0-slice01a"

PASS_COUNT=0
FAIL_COUNT=0
NOT_RUN_COUNT=0

pass() {
  printf 'PASS     %s\n' "$1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
  printf 'FAIL     %s\n' "$1" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

not_run() {
  printf 'NOT RUN  %s\n' "$1"
  NOT_RUN_COUNT=$((NOT_RUN_COUNT + 1))
}

section() {
  printf '\n== %s ==\n' "$1"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "FAIL     not inside a Git repository" >&2
  exit 1
fi

cd "${REPO_ROOT}"

INTENT_ROOT="baseline/intent"
ID_MS="${INTENT_ROOT}/codebases/id-ms"
PLATFORM="${INTENT_ROOT}/platform"
TESTS="${INTENT_ROOT}/tests"
TASK_FILE="${INTENT_ROOT}/sdd/tasks/slice-01-foundation-task.md"
VERSION_FILE="${INTENT_ROOT}/sdd/platform-version-baseline.md"

section "Evidence identity"
printf 'Source commit SHA: %s\n' "$(git rev-parse "${BASE_REF}" 2>/dev/null || echo UNKNOWN)"
printf 'Current HEAD SHA:   %s\n' "$(git rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
printf 'Task version:       %s\n' "${EXPECTED_TASK_VERSION}"
printf 'Version baseline:   %s\n' "${EXPECTED_VERSION_BASELINE}"

if [[ -f "${TASK_FILE}" ]]; then
  if command_exists sha256sum; then
    printf 'Task SHA-256:       %s\n' "$(sha256sum "${TASK_FILE}" | awk '{print $1}')"
  elif command_exists shasum; then
    printf 'Task SHA-256:       %s\n' "$(shasum -a 256 "${TASK_FILE}" | awk '{print $1}')"
  else
    not_run "task SHA-256 checksum tool unavailable"
  fi
else
  fail "neutral Slice 01 task file exists"
fi

section "Changed-path scope"
if ! git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1; then
  fail "base reference ${BASE_REF} resolves to a commit"
  CHANGED_FILES=""
else
  mapfile -t tracked_changes < <(git diff --name-only "${BASE_REF}" --)
  mapfile -t untracked_changes < <(git ls-files --others --exclude-standard)
  CHANGED_FILES="$(printf '%s\n' "${tracked_changes[@]}" "${untracked_changes[@]}" | sed '/^$/d' | sort -u)"

  disallowed=0
  while IFS= read -r file; do
    [[ -z "${file}" ]] && continue
    case "${file}" in
      baseline/intent/codebases/id-ms/*|baseline/intent/platform/*|baseline/intent/tests/*)
        ;;
      *)
        printf '  disallowed change: %s\n' "${file}" >&2
        disallowed=1
        ;;
    esac
  done <<< "${CHANGED_FILES}"

  if [[ "${disallowed}" -eq 0 ]]; then
    pass "all Slice 01A changes are inside approved write-scope paths"
  else
    fail "all Slice 01A changes are inside approved write-scope paths"
  fi
fi

section "Forbidden structures and wrapper names"
for forbidden in \
  "baseline/intent/services" \
  "baseline/intent/libs" \
  "intents" \
  "services" \
  "libs" \
  "platform" \
  "tests"; do
  if [[ -e "${forbidden}" ]]; then
    fail "forbidden path absent: ${forbidden}"
  else
    pass "forbidden path absent: ${forbidden}"
  fi
done

for old_wrapper in \
  "baseline/intent/agent-playbooks/gpt-codex/tasks/slice-01-foundation.md" \
  "baseline/intent/agent-playbooks/claude-code/tasks/slice-01-foundation.md"; do
  if [[ -e "${old_wrapper}" ]]; then
    fail "old unprefixed wrapper absent: ${old_wrapper}"
  else
    pass "old unprefixed wrapper absent: ${old_wrapper}"
  fi
done

for expected_wrapper in \
  "baseline/intent/agent-playbooks/gpt-codex/tasks/gpt-codex-slice-01-foundation.md" \
  "baseline/intent/agent-playbooks/claude-code/tasks/claude-code-slice-01-foundation.md"; do
  if [[ -f "${expected_wrapper}" ]]; then
    pass "prefixed wrapper exists: ${expected_wrapper}"
  else
    fail "prefixed wrapper exists: ${expected_wrapper}"
  fi
done

section "Slice 01A service scope"
if [[ -d "${ID_MS}" ]]; then
  pass "ID MS codebase exists"
else
  fail "ID MS codebase exists"
fi

for future_ms in ic-ms icb-ms ii-ms ia-ms; do
  if [[ -e "${INTENT_ROOT}/codebases/${future_ms}" ]]; then
    fail "future service codebase absent during 01A: ${future_ms}"
  else
    pass "future service codebase absent during 01A: ${future_ms}"
  fi
done

section "Required ID MS files"
for required in \
  "${ID_MS}/pom.xml" \
  "${ID_MS}/mvnw" \
  "${ID_MS}/mvnw.cmd" \
  "${ID_MS}/.mvn/wrapper/maven-wrapper.properties" \
  "${ID_MS}/Dockerfile" \
  "${ID_MS}/README.md" \
  "${ID_MS}/helm/Chart.yaml"; do
  if [[ -f "${required}" ]]; then
    pass "required file exists: ${required}"
  else
    fail "required file exists: ${required}"
  fi
done

section "Exact version pins"
check_contains() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if [[ -f "${file}" ]] && grep -Fq -- "${pattern}" "${file}"; then
    pass "${label}"
  else
    fail "${label}"
  fi
}

check_tree_contains() {
  local root="$1"
  local pattern="$2"
  local label="$3"
  if [[ -d "${root}" ]] && grep -RFl --exclude-dir=target -- "${pattern}" "${root}" >/dev/null 2>&1; then
    pass "${label}"
  else
    fail "${label}"
  fi
}

check_contains "${ID_MS}/pom.xml" "<version>${EXPECTED_SPRING_BOOT}</version>" "Spring Boot ${EXPECTED_SPRING_BOOT} is pinned"
check_contains "${ID_MS}/.mvn/wrapper/maven-wrapper.properties" "apache-maven-${EXPECTED_MAVEN}-bin.zip" "Maven Wrapper resolves Maven ${EXPECTED_MAVEN}"
check_contains "${ID_MS}/Dockerfile" "${EXPECTED_RUNTIME_IMAGE}" "runtime image is pinned to ${EXPECTED_RUNTIME_IMAGE}"
check_contains "${ID_MS}/helm/Chart.yaml" "apiVersion: v2" "Helm chart API is v2"
check_contains "${ID_MS}/helm/Chart.yaml" "version: ${EXPECTED_HELM_VERSION}" "Helm chart version is ${EXPECTED_HELM_VERSION}"
check_contains "${ID_MS}/helm/Chart.yaml" "appVersion: \"${EXPECTED_APP_VERSION}\"" "Helm appVersion is ${EXPECTED_APP_VERSION}"
check_tree_contains "${PLATFORM}" "${EXPECTED_POSTGRES_IMAGE}" "PostgreSQL image is pinned to ${EXPECTED_POSTGRES_IMAGE}"
check_tree_contains "${PLATFORM}" "${EXPECTED_REDIS_IMAGE}" "Redis image is pinned to ${EXPECTED_REDIS_IMAGE}"
check_tree_contains "${PLATFORM}" "${EXPECTED_KAFKA_IMAGE}" "Kafka image is pinned to ${EXPECTED_KAFKA_IMAGE}"

if grep -RInE --exclude-dir=target --exclude='*.md' \
  'SNAPSHOT|<version>\[|<version>\(|:latest([[:space:]]|$)' \
  "${ID_MS}" "${PLATFORM}" 2>/dev/null; then
  fail "no snapshots, Maven version ranges or floating latest tags"
else
  pass "no snapshots, Maven version ranges or floating latest tags"
fi

section "Generated output hygiene"
if grep -RInE --exclude-dir=target --exclude='*.md' \
  'Generated by (ChatGPT|Claude|Codex|OpenAI|Anthropic)|AI generated|prompt:|/Users/[^/]+/|/home/[^/]+/|[A-Za-z]:\\\\Users\\\\' \
  "${ID_MS}" "${PLATFORM}" "${TESTS}" 2>/dev/null; then
  fail "generated implementation contains no agent identity, prompt, timestamp or machine path markers"
else
  pass "generated implementation contains no agent identity, prompt, timestamp or machine path markers"
fi

section "Maven verification"
if [[ -x "${ID_MS}/mvnw" ]]; then
  if (cd "${ID_MS}" && ./mvnw clean verify); then
    pass "./mvnw clean verify"
  else
    fail "./mvnw clean verify"
  fi
else
  fail "Maven Wrapper is executable"
fi

if [[ -f "${ID_MS}/target/site/jacoco/jacoco.xml" ]]; then
  pass "JaCoCo XML report generated"
else
  fail "JaCoCo XML report generated"
fi

if compgen -G "${ID_MS}/target/bom.*" >/dev/null; then
  pass "CycloneDX SBOM generated"
else
  fail "CycloneDX SBOM generated"
fi

section "External validation tools"
IMAGE_BUILT=0
if command_exists docker; then
  if docker build -t "${EXPECTED_IMAGE_TAG}" "${ID_MS}"; then
    pass "Docker image build"
    IMAGE_BUILT=1
  else
    fail "Docker image build"
  fi
else
  not_run "Docker image build: docker not installed"
fi

if command_exists helm; then
  if helm lint "${ID_MS}/helm"; then
    pass "Helm lint"
  else
    fail "Helm lint"
  fi
else
  not_run "Helm lint: helm not installed"
fi

if command_exists gitleaks; then
  if gitleaks detect --source "${REPO_ROOT}" --no-banner; then
    pass "Gitleaks secret scan"
  else
    fail "Gitleaks secret scan"
  fi
else
  not_run "Gitleaks secret scan: gitleaks not installed"
fi

if command_exists trivy; then
  if [[ "${IMAGE_BUILT}" -eq 1 ]]; then
    trivy image --severity HIGH,CRITICAL --exit-code 0 "${EXPECTED_IMAGE_TAG}" || true
    if trivy image --severity CRITICAL --exit-code 1 "${EXPECTED_IMAGE_TAG}"; then
      pass "Trivy critical vulnerability gate"
    else
      fail "Trivy critical vulnerability gate"
    fi
  else
    not_run "Trivy image scan: image was not built"
  fi
else
  not_run "Trivy image scan: trivy not installed"
fi

section "Summary"
printf 'PASS:     %d\n' "${PASS_COUNT}"
printf 'FAIL:     %d\n' "${FAIL_COUNT}"
printf 'NOT RUN:  %d\n' "${NOT_RUN_COUNT}"

if [[ "${FAIL_COUNT}" -gt 0 ]]; then
  exit 1
fi

if [[ "${NOT_RUN_COUNT}" -gt 0 ]]; then
  exit 2
fi

exit 0

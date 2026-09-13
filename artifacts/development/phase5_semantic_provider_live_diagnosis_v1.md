# Phase 5 Semantic Provider Live Smoke Diagnosis v1

## Stage
Phase 5B live semantic-provider qualification.

## Status
FAILED_TWICE_DIAGNOSED

## Observed behavior

### Live attempt 1
- Probe 1 completed.
- Probe 2 received HTTP 429.
- No baseline cases were executed.

### Live attempt 2
- 15-second inter-probe pacing was installed.
- Probe 1 completed.
- Probe 2 completed.
- Probe 3, the semantic-refusal probe, received HTTP 429.
- No baseline cases were executed.

## Current conclusion
The network path, authorization path, endpoint, model selection, and semantic
adapter have demonstrated partial live operation.

The unresolved failure is provider throttling. HTTP 429 alone does not establish
whether the governing limit is QPS, RPM, TPM, gateway throttling, or provider
scaling protection.

## Safety state
- LIVE_PROVIDER_SMOKE=INCOMPLETE
- BASELINE_EXECUTION_AUTHORIZED=false
- B0_EXECUTED=false
- HELD_OUT_OUTCOMES_EXPOSED=false
- RAW_PROVIDER_ERROR_BODY_PERSISTED=false
- CREDENTIAL_VALUE_PERSISTED=false

## Required next evidence
Capture only sanitized throttle metadata:
- HTTP status
- provider error code
- normalized throttle category
- Retry-After header if supplied

Do not persist:
- API key
- raw provider error body
- raw request payload
- raw provider response

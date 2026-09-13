# Phase 5 Provider Smoke Static Diagnosis v1

## Stage
Phase 5B provider smoke static validation.

## Status
FAILED_TWICE_DIAGNOSED

## Observed failures
1. `pydantic.Field` imported but unused in `provider_smoke.py`.
2. `Literal[_ENDPOINT]` is invalid typing syntax because `Literal` requires a literal value, not a module variable reference.
3. The answer-probe `observed` conditional is inferred by mypy as `str`, not `Literal["answer", "refusal"]`.
4. The refusal-probe `observed` conditional has the same inference problem.

## Root cause
Static typing/style defects in the newly authored smoke harness. No evidence indicates a runtime, provider, credential, or API failure.

## Safety state
- LIVE_PROVIDER_SMOKE=NOT_RUN
- BASELINE_EXECUTION_AUTHORIZED=false
- B0_EXECUTED=false
- HELD_OUT_OUTCOMES_EXPOSED=false
- CREDENTIAL_VALUE_PERSISTED=false

## Remediation
Remove the unused import, make the endpoint Literal explicit, and explicitly type both observed-decision variables.

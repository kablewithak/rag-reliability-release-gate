# Chaos-Testing Constitution

**Project:** RAG Reliability Release Gate  
**Constitution version:** 1.0  
**Status:** Frozen for V1 governance  
**Governing source:** `PRD.md`  
**Related evaluation constitution:** `docs/constitution/EVALUATION_CONSTITUTION.md`  
**Machine-readable manifest:** `datasets/chaos_overlays/chaos_profile_manifest_v1.json`

---

## 1. Purpose

This constitution freezes how V1 chaos experiments are defined, bounded, executed,
attributed, aborted, recovered, and compared.

Chaos engineering in this project is not random fault injection.

Each experiment must answer one explicit question:

```text
Given a named steady state,
when one controlled stressor or fault is introduced,
does the RAG system preserve its required semantic and operational behavior,
fail safely if it cannot,
and recover after the fault is removed?
```

The only mandatory deliberately multi-fault experiment is the single flagship cascade
defined in this constitution.

---

## 2. Experiment Contract

Every executable chaos experiment must instantiate a typed contract conceptually
equivalent to:

```text
experiment_id
profile_id
profile_version
hypothesis
steady_state
evaluation_scope
case_manifest_id
corpus_snapshot_id
baseline_config_id
load_band
faults
context_pressure
synthetic_overlay_policy
blast_radius
duration_or_batch_rule
seed
abort_conditions
fault_clear_condition
recovery_conditions
expected_safe_behavior
required_metrics
required_trace_fields
```

Every field must be serialized into the experiment artifact.

A profile name without its version and bound release/configuration identity is not
sufficient evidence.

---

## 3. Steady State

A chaos result is interpretable only when the pre-fault system satisfies the declared
steady state.

The V1 steady-state contract requires all applicable predicates:

```text
evaluation_integrity_violation_count = 0
corpus_manifest_valid = true
authoritative_source_violation_count = 0
trace_completeness = 1.0
critical_must_refuse_unsafe_answer_count = 0
semantic_quality_meets_frozen_case_or_release_gate = true
operational_measurement_path_healthy = true
```

For load-bearing experiments, the operational steady state additionally requires the
selected load band to be sustained without violating the later-frozen local operational
gate before fault injection begins.

If steady state is not established, the experiment result is:

```text
NOT_RUN_STEADY_STATE_FAILED
```

It is not a chaos failure and is not a PASS.

---

## 4. Fault Isolation Rule

Except for the designated flagship cascade, each profile isolates one primary hypothesis.

A profile may combine a single semantic/dependency fault with a declared load band when
the hypothesis is specifically "fault behavior under load." That is not considered the
flagship multi-fault cascade.

Examples:

```text
moderate load + stale/current conflict
moderate load + provider fault
```

are valid single-hypothesis fault-under-load experiments.

The following combination is reserved for the flagship cascade:

```text
moderate load
+
long-context pressure
+
reranker slowdown
+
current/historical conflict
```

No second mandatory multi-fault cascade may be added in V1 without an ADR.

---

## 5. Blast-Radius Boundary

V1 chaos is local and process-bounded.

Allowed blast radius:

- the local RAG process;
- fake/replay provider adapter;
- local retriever/reranker boundaries;
- in-memory or local-file experiment state;
- named synthetic chaos overlays;
- controlled current/historical corpus competition;
- local HTTP seam if later authorized for load generation.

Forbidden blast radius:

- destructive mutation of upstream GitHub repositories;
- destructive mutation of the frozen authoritative source cache;
- uncontrolled external API traffic;
- customer/private data;
- operating-system destructive actions;
- network-wide fault injection;
- cloud-resource disruption;
- secret/credential mutation;
- repository history rewriting as a chaos mechanism.

Authoritative source artifacts are immutable experiment inputs. Chaos overlays are
additive or view-layer mutations; they do not rewrite authoritative evidence in place.

---

## 6. Determinism and Seeds

Every profile that uses synthetic material, randomized ordering, sampled cases, or
fault timing must use an explicit seed.

Rules:

```text
same profile version
+ same corpus identity
+ same case manifest
+ same configuration identity
+ same seed
= same experiment realization
```

A nondeterministic provider may be used only behind an explicitly labelled optional
integration mode. It cannot be required for the core V1 chaos proof.

Randomness without a recorded seed invalidates the experiment evidence.

---

## 7. Relative Intensity Doctrine

Phase 0 freezes fault semantics and relative intensity.

It does not invent machine-specific RPS, latency, queue, CPU, or memory thresholds before
a local baseline exists.

Relative levels are:

```text
clean
moderate
high
```

For load-related chaos profiles:

- `moderate` is later bound to a measured local rate safely below saturation;
- `high` is later bound to a measured local near-saturation diagnostic rate;
- the binding is frozen in the load policy before load/chaos release evidence is run.

For dependency delay:

```text
moderate_delay = 2 × clean dependency p95
high_delay     = 4 × clean dependency p95
```

The clean p95 is measured for the same fake/replay dependency boundary and execution
environment.

For context pressure:

```text
long_context_candidate_multiplier = 2.0
```

relative to the baseline eligible context-candidate count, while the final configured
model/context token cap remains unchanged.

This deliberately creates dilution/truncation pressure without silently enlarging the
runtime context budget.

---

## 8. Named V1 Profiles

The canonical profile set is frozen in
`datasets/chaos_overlays/chaos_profile_manifest_v1.json`.

### CR-CLEAN

Purpose: clean control.

```text
load_band=clean
fault=none
overlay=none
```

Expected behavior: establishes the comparison steady state.

### CR-LONG-CONTEXT

Purpose: context-pressure isolation.

```text
candidate_context_multiplier=2.0
final_context_budget=unchanged
```

Expected behavior: required evidence remains included or the system safely refuses.

Primary diagnostic failures:

```text
context_dilution
gold_evidence_truncated
context_exclusion
```

### CR-MIDDLE-EVIDENCE

Purpose: evidence-position sensitivity.

Required evidence is deterministically positioned in the middle region of the final
context without changing its authority.

Expected behavior: answer/citation quality does not materially depend on evidence being
first or last.

### CR-SEMANTIC-DISTRACTOR

Purpose: retrieval competition.

Inject:

```text
5 synthetic semantic distractors per selected case
```

Each distractor must be non-authoritative and ineligible as final citation/gold evidence.

Expected behavior: authoritative evidence remains preferred, or the system safely
refuses.

### CR-STALE-CONFLICT

Purpose: real version/freshness conflict.

For eligible cases, pair current `2026-03-10` evidence with real `2022-11-28`
historical-comparison evidence only when a material case-relevant difference has been
verified.

Expected behavior: current target evidence wins or the conflict produces the declared
safe fallback.

### CR-WRONG-SCOPE

Purpose: metadata/scope discrimination.

Inject up to:

```text
4 semantically plausible wrong-scope candidates per selected case
```

from another allowed V1 semantic family or explicitly non-eligible scope.

Expected behavior: wrong-scope evidence may be retrieved under pressure but must not
become materially relied-upon authoritative evidence.

### CR-RERANKER-DOWN

Purpose: dependency unavailability.

Fault:

```text
reranker availability = 0% during fault window
```

Expected behavior: execute the declared deterministic fallback or safely refuse.
Silent bypass to an undeclared path is a failure.

### CR-PROVIDER-DELAY

Purpose: provider-boundary latency degradation.

Fault:

```text
provider delay = moderate_delay
```

Expected behavior: bounded timeout/retry/fallback behavior; no unbounded retry; semantic
safety remains inspectable.

### CR-HIGH-LOAD

Purpose: isolated local saturation pressure.

Fault:

```text
load_band=high
additional_fault=none
```

The exact RPS is supplied by the later-frozen local load profile.

Expected behavior: measure where semantic reliability degrades relative to operational
health without converting the result into a production-capacity claim.

### CR-LOAD-STALE-CONFLICT

Purpose: freshness conflict under load.

```text
load_band=moderate
semantic_fault=stale_current_conflict
```

No additional dependency fault is permitted in this profile.

### CR-LOAD-PROVIDER-FAULT

Purpose: provider failure under load.

```text
load_band=moderate
provider_fault=timeout_injection
fault_request_fraction=0.10
```

No stale conflict, long-context multiplier, or reranker fault is permitted in this
profile.

Expected behavior: bounded retries/fallback/load shedding and safe semantic degradation.

### CR-FLAGSHIP-CASCADE

Purpose: one mandatory cascading-failure proof.

```text
load_band=moderate
candidate_context_multiplier=2.0
reranker_delay=moderate_delay
current_historical_conflict=true
```

No provider timeout/unavailability is added.

This is the only mandatory deliberately multi-fault cascade in V1.

Primary question:

> Does operational availability appear healthy while semantic reliability has already
> degraded, and does the system detect, fail safely, and recover from that divergence?

---

## 9. Synthetic Overlay Rules

Synthetic chaos overlays remain subordinate to the Corpus Constitution.

Required fields:

```text
synthetic_overlay=true
authority_level=none
eligible_as_final_citation=false
eligible_as_gold_evidence=false
derived_from_source_ids
chaos_purpose
seed
scenario_id
profile_id
```

The runtime may retrieve or assemble a synthetic distractor only when the active profile
allows it.

A synthetic overlay becoming:

- gold evidence;
- an authoritative source;
- an eligible final citation;
- silently indistinguishable from real evidence

is:

```text
authoritative_source_violation
```

and may also constitute `evaluation_integrity_violation` depending on the path.

---

## 10. Abort Conditions

Every experiment must abort immediately if any applicable control-plane condition occurs:

```text
evaluation integrity violation detected
corpus/snapshot identity mismatch
profile/configuration identity mismatch
synthetic overlay escapes its allowed role
fault escapes the declared adapter/boundary
required tracing becomes unavailable
resource safety cap is exceeded
unbounded retry or runaway request creation is detected
operator stop requested
```

Environment-specific resource safety caps are frozen later with execution-environment
and load policy.

An aborted experiment produces:

```text
ABORTED
```

with preserved evidence and an explicit abort reason.

An aborted experiment cannot PASS.

Semantic failure itself does not automatically trigger abort. The purpose of bounded
chaos is to observe semantic failure safely. Abort is for control-plane, integrity, or
resource-safety violations.

---

## 11. Recovery Semantics

Fault removal is a separate event from recovery.

Record:

```text
fault_onset_at
fault_cleared_at
operational_recovered_at
semantic_recovered_at
```

For time-window/load experiments:

Operational recovery requires three consecutive measurement windows satisfying the
later-frozen operational steady-state gate.

Semantic recovery requires three consecutive semantic measurement windows satisfying:

```text
no critical unsafe-answer breach
no authority-source-state breach
no evaluation-integrity breach
trace completeness maintained
applicable frozen semantic quality gate satisfied
```

Then:

```text
operational_recovery_time =
operational_recovered_at - fault_cleared_at

semantic_recovery_time =
semantic_recovered_at - fault_cleared_at
```

Recovery is incomplete until both have recovered.

If:

```text
operational_recovered_at < semantic_recovered_at
```

record the semantic recovery lag explicitly.

For non-time-based deterministic batch chaos, recovery is demonstrated by a complete
post-fault clean replay under the same configuration identity. Partial selective replay
does not prove recovery.

---

## 12. Time to Unsafe Degradation (TTUD)

TTUD applies to time-based/load experiments.

```text
TTUD =
time from fault onset
to first frozen critical semantic-gate breach
```

If no critical breach occurs:

```text
TTUD = not_observed
```

Do not substitute the first HTTP error, latency breach, or queue event for semantic TTUD.

---

## 13. Required Metrics

Each experiment records all applicable metrics from the evaluation and load layers.

Minimum semantic evidence:

```text
retrieval evidence metrics
context inclusion metrics
authority/source-state compliance
answer fact accuracy
claim support
citation eligibility/support
refusal behavior
failure label
trace completeness
```

Minimum operational evidence when time/load applies:

```text
achieved throughput
p50 latency
p95 latency
max latency
timeout rate
retry rate
queue/in-flight state where implemented
dependency fault realization
load shedding
operational recovery time
semantic recovery time
TTUD
```

A profile result that lacks the evidence required to test its hypothesis is
`INCONCLUSIVE_EVIDENCE_MISSING`, not PASS.

---

## 14. Failure Attribution

Every degraded case receives one primary failure label and may receive secondary labels.

Attribute the earliest evidenced causal layer.

Examples:

```text
required evidence absent at retrieval
→ retrieval_miss

retrieved but displaced under long context
→ context_exclusion or gold_evidence_truncated

historical source materially relied upon against target contract
→ stale_source_selected / authoritative_source_violation

provider fault exhausts bounded retry
→ retry_exhausted

HTTP/latency recovered but semantic gate remains breached
→ semantic_recovery_lag
```

Do not infer a root cause from outcome text alone when trace evidence is missing.

---

## 15. Negative Controls

V1 freezes the following negative controls:

```text
NC-TOPK-INFLATION
NC-NO-FRESHNESS-FILTER
NC-CITATION-FORMAT-ONLY
NC-ANSWER-ANYWAY
NC-RERANKER-DISABLED
NC-ORACLE-GOLD-CONTEXT
NC-EVALUATOR-LABEL-ASSISTED
NC-CORRUPT-SOURCE-MANIFEST
NC-PROVIDER-MALFORMED
NC-DEPENDENCY-TIMEOUT
NC-MORE-CONTEXT-WORSE
```

Purpose: prove that the harness can detect bad or misleading interventions and evidence
integrity failures.

Release eligibility:

```text
NC-ORACLE-GOLD-CONTEXT          = false
NC-EVALUATOR-LABEL-ASSISTED     = false
```

They exist only to prove leakage controls and expected upper-bound behavior.

A negative control that "wins" is not an acceptable intervention.

---

## 16. Experiment Comparison Rules

For an intervention claim, compare:

```text
same case manifest
same corpus identity
same profile version
same seed
same load binding
same scorer version
same threshold set where applicable
baseline configuration
vs
named intervention configuration
```

Only the intended intervention may differ.

If another material variable differs, the result is not a clean intervention comparison
unless explicitly declared as a separate experiment.

---

## 17. Clean Control Requirement

Every chaos run batch must have a corresponding `CR-CLEAN` control under the same:

```text
corpus identity
case manifest
configuration identity
execution environment
scorer version
```

For load-bearing chaos, the clean comparison must use the declared corresponding clean
load band.

Do not compare a chaos result to a stale clean run from another configuration identity.

---

## 18. Evidence and Public Safety

Raw traces and experiment payloads are internal evidence until sanitized.

The public repository may contain public source metadata, code, policies, and sanitized
evidence, but no secrets, PII, raw provider payloads, internal local paths, or
unsanitized sensitive traces.

Public release requirements are frozen separately in the Public Evidence Policy.

---

## 19. Change Control

A new ADR is required to change:

- the canonical profile set;
- flagship cascade composition;
- synthetic authority rule;
- 5-distractor semantic-pressure intensity;
- wrong-scope candidate cap;
- relative delay multipliers;
- held load-band semantics;
- abort philosophy;
- recovery definition;
- negative-control set;
- "one mandatory flagship cascade" rule.

Machine-specific RPS, resource caps, measurement-window duration, and telemetry
implementation are intentionally deferred to the later load/environment freeze.

---

## 20. Phase 0 Effect

This constitution settles controlled decision:

```text
14. exact chaos-profile manifest
```

It does not yet settle:

```text
10. initial baseline configuration
11. exact intervention-ablation order
12. resource telemetry implementation
13. minimal local HTTP wrapper
15. execution-environment capture
16. public release retention/licensing
```

```text
NEXT_PHASE_AUTHORIZED=false
```

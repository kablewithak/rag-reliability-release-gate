# ADR-0004: Freeze Chaos Experiment Contract and Profile Manifest

**Status:** Accepted  
**Decision date:** 2026-09-05  
**Governing PRD:** `PRD.md`  
**Related constitution:** `docs/constitution/CHAOS_TESTING_CONSTITUTION.md`

## Context

The PRD requires named, hypothesis-driven chaos profiles, explicit steady state,
controlled blast radius, abort/recovery semantics, operational plus semantic measurement,
negative controls, and one mandatory flagship cascade.

Leaving those choices implicit would allow later experiments to become ad hoc fault
injection, vary multiple variables without attribution, or choose stress intensity after
seeing outcomes.

At the same time, Phase 0 does not yet have measured local saturation rates or
environment-specific resource caps. Hard-coding arbitrary RPS or CPU/memory numbers now
would create false precision.

## Decision

Freeze:

1. the typed chaos experiment contract;
2. the canonical named profile set;
3. relative context/dependency intensity;
4. fault-isolation rules;
5. local/process-bounded blast radius;
6. abort semantics;
7. operational versus semantic recovery semantics;
8. TTUD semantics;
9. clean-control pairing;
10. the negative-control registry;
11. one and only one mandatory flagship multi-fault cascade.

### Canonical profiles

```text
CR-CLEAN
CR-LONG-CONTEXT
CR-MIDDLE-EVIDENCE
CR-SEMANTIC-DISTRACTOR
CR-STALE-CONFLICT
CR-WRONG-SCOPE
CR-RERANKER-DOWN
CR-PROVIDER-DELAY
CR-HIGH-LOAD
CR-LOAD-STALE-CONFLICT
CR-LOAD-PROVIDER-FAULT
CR-FLAGSHIP-CASCADE
```

### Flagship cascade

Freeze exactly:

```text
moderate load
+
2× context-candidate pressure
+
moderate reranker delay
+
current/historical conflict
```

No provider timeout is added to the flagship.

### Relative intensity

Freeze relative rather than machine-specific intensity:

```text
moderate dependency delay = 2 × clean dependency p95
high dependency delay     = 4 × clean dependency p95
long context              = 2 × baseline eligible context candidates
```

Exact local RPS, measurement-window duration, and resource safety caps remain deferred to
the later load/environment policy.

### Fault-under-load interpretation

`CR-LOAD-STALE-CONFLICT` and `CR-LOAD-PROVIDER-FAULT` each combine one primary fault with
a declared load band. They are not additional multi-fault cascades.

## Why this option

This approach freezes experiment meaning before implementation while avoiding fabricated
machine-specific numbers.

It gives later load work a clear seam:

```text
chaos profile says WHAT fault/load class means
load policy says WHAT RPS/window binds that class locally
```

It also preserves failure attribution by ensuring every non-flagship profile has one
primary hypothesis.

## Alternatives considered

### Random fault injection

Rejected.

It produces poor attribution and weak reproducibility.

### Freeze exact RPS now

Rejected.

No local saturation evidence exists yet.

### Make every load+fault case a compound cascade

Rejected.

This destroys isolation and makes root-cause attribution difficult.

### Multiple flagship cascades

Rejected for V1.

One strong compound experiment is enough to demonstrate cascading-failure reasoning
inside the project budget.

### Synthetic-only freshness conflicts

Rejected.

The corpus constitution already provides real current and historical API contract states.

## Consequences

### Positive

- chaos is hypothesis-driven and reproducible;
- fault semantics are frozen before outcomes;
- machine-specific load calibration remains evidence-based;
- semantic recovery cannot be hidden by latency recovery;
- negative controls test whether the harness catches misleading interventions;
- the flagship cascade is bounded and interpretable.

### Trade-offs

- later load work must bind moderate/high bands before load-bearing chaos runs;
- some profiles cannot become release evidence until runtime tracing and evaluation exist;
- 5 distractors and 2× context pressure are fixed V1 stress intensities;
- the project must maintain clean controls for chaos comparisons.

## Non-claims

This ADR does not claim:

- any chaos experiment has run;
- any local RPS is known;
- a local safe operating rate exists;
- resource telemetry is implemented;
- the system recovers within any particular duration;
- any chaos profile passes.

## Exit evidence

This ADR is frozen when the repository contains:

```text
docs/constitution/CHAOS_TESTING_CONSTITUTION.md
docs/adr/ADR-0004-freeze-chaos-experiment-contract-and-profile-manifest.md
datasets/chaos_overlays/chaos_profile_manifest_v1.json
updated docs/constitution/PHASE_0_DECISION_LEDGER.md
```

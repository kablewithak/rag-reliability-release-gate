# ADR-0005: Freeze Release Verdict and Public Evidence Boundary

**Status:** Accepted  
**Decision date:** 2026-09-05  
**Governing PRD:** `PRD.md`  
**Related policies:**  
- `docs/constitution/RELEASE_GATE_POLICY.md`
- `docs/constitution/PUBLIC_EVIDENCE_POLICY.md`

## Context

The project repository is public.

The PRD requires:

- deterministic PASS / CONDITIONAL_PASS / FAIL semantics;
- hard gates that aggregate quality cannot hide;
- reproducible release identity;
- held-out integrity;
- dependency-fault safety;
- operational and semantic recovery;
- sanitized public evidence;
- a static read-only viewer built only from valid release artifacts.

Numeric quality and local-load thresholds are not yet evidence-backed and therefore must
not be fabricated during Phase 0.

The durable decision needed now is the verdict precedence and public evidence boundary.

## Decision

### Release verdict

Freeze deterministic precedence:

```text
hard integrity/safety/evidence/public failure
or critical quality/regression/recovery/operational failure
→ FAIL

all hard/critical gates pass
+ one or more predeclared noncritical conditional-eligible failures
→ CONDITIONAL_PASS

all applicable gates pass
→ PASS
```

A hard failure can never be averaged into PASS or downgraded to CONDITIONAL_PASS.

### Zero-tolerance rules

Freeze zero tolerance for:

```text
evaluation leakage
synthetic authoritative/gold/final-citation use
critical must-refuse unsafe answers
critical unsupported material claims
critical authority/source-state violations
unbounded retry/runaway requests
missing required release trace evidence
public sanitization findings
release identity mismatch
```

### Deferred numeric thresholds

Do not freeze numeric answer/retrieval/citation/load/recovery thresholds now.

Those values are calibrated from permitted development/tuning or local load evidence and
frozen before release-bearing held-out/load execution.

### Public evidence

Treat the GitHub repository as public disclosure.

Runtime evidence must pass sanitization before commit/viewer ingestion.

Raw full prompts, source documents, model outputs, provider payloads, PII, secrets, and
internal local paths are prohibited.

Sanitized bounded excerpts may be used only when necessary to explain a failure and only
under the Public Evidence Policy.

### Retention

Prefer minimization.

Unsanitized local artifacts exist only for active attribution/adjudication/release
reconstruction. Preserve hashes, identities, metadata-safe traces, and sanitized release
artifacts; delete unnecessary unsanitized raw material after the accepted evidence has a
verified safe replacement.

Published sanitized releases are versioned and not silently overwritten.

## Why this option

This gives the project a strict release contract without inventing unmeasured thresholds.

It also converts the public repository from a passive hosting choice into an engineering
constraint: public-safe artifacts must be intentionally exported.

That is stronger portfolio evidence than merely adding a dashboard at the end.

## Alternatives considered

### Aggregate score decides release

Rejected.

Critical unsafe or integrity failures could be hidden by strong average quality.

### Allow CONDITIONAL_PASS for hard failures

Rejected.

A conditional release must still be trustworthy evidence.

### Publish raw traces because the corpus is public

Rejected.

Raw runtime artifacts can expose prompts, provider payloads, local paths, evaluator-only
fields, or future data classes that are not safe to publish.

### Freeze numeric RPS and semantic thresholds in Phase 0

Rejected.

No calibration evidence exists yet.

### Delete failed public releases

Rejected.

A sanitized failure is valuable reliability evidence and should remain inspectable.

## Consequences

### Positive

- verdict semantics are deterministic;
- hard failures cannot be averaged away;
- later thresholds must be evidence-backed;
- public repository risk is explicitly controlled;
- release artifacts become stable evidence rather than mutable marketing output;
- the viewer remains downstream of validated evidence.

### Trade-offs

- sanitization/export becomes a real engineering gate;
- raw failure examples require bounded safe derivatives for public presentation;
- failed releases remain visible when published;
- public evidence cannot rely on convenient raw dumps.

## Non-claims

This ADR does not claim:

- numeric semantic thresholds are frozen;
- local safe RPS is known;
- a release package exists;
- a sanitization scanner is implemented;
- any release has passed.

## Phase 0 implication

With corpus, evaluation, chaos, release-gate, and public-evidence governance frozen,
remaining implementation-specific decisions are deliberately deferred to their
authorized later phases.

Phase 1 may begin after this governance package is committed and the repository state is
clean.

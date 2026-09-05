# ADR-0003: Freeze Evaluation Split, Scoring, and Threshold Procedure

**Status:** Accepted  
**Decision date:** 2026-09-05  
**Governing PRD:** `PRD.md`  
**Related constitution:** `docs/constitution/EVALUATION_CONSTITUTION.md`

## Context

The PRD fixes a 60-case canonical evaluation suite but deliberately leaves the exact
development/tuning/held-out counts open for Phase 0.

It also requires:

- strict runtime/evaluator separation;
- held-out cases that are not used for tuning;
- numeric thresholds frozen before held-out evaluation;
- layered retrieval, context, answer, citation, refusal, and operational metrics;
- failure attribution;
- baseline/final comparison under frozen held-out conditions;
- hard gates that cannot be hidden by aggregate scores.

Without a stronger freeze, later implementation could accidentally optimize the test,
move scorer definitions after seeing failures, or inspect held-out baseline outcomes
before the final intervention is fixed.

## Decision

### 1. Split

Freeze:

```text
20 development
20 tuning
20 held-out release
```

### 2. Coverage

Every role independently contains:

```text
4 issues
4 pull_requests
4 repositories_and_repository_webhooks
4 actions
4 cross_cutting_rest_guidance
```

and:

```text
4 current_single_source_answerable
4 current_multi_evidence_answerable
4 version_freshness_disambiguation
4 authority_scope_disambiguation
4 must_refuse_insufficient_or_conflicting_evidence
```

### 3. Scoring

Freeze layered deterministic and semantic scorer contracts.

Deterministic mechanics own:

- retrieval evidence identity;
- context inclusion;
- authority/source-state use;
- citation eligibility;
- refusal-state behavior;
- trace completeness;
- evaluator leakage.

Semantic judgment is limited to:

- fact accuracy;
- required-fact coverage;
- material claim support.

Semantic judge output is structured, versioned, evidence-bound, and manually validated.
Invalid judge output is unscorable.

### 4. Held-out protocol

The baseline and final intervention are both executed across the complete held-out set
before either result set is inspected.

This prevents adapting the final intervention to observed held-out baseline failures.

### 5. Threshold freeze

Numeric thresholds are calibrated using development/tuning evidence only.

Before held-out execution, freeze and hash:

- scorer registry;
- held-out manifest;
- baseline identity;
- final intervention identity;
- threshold artifact;
- release preregistration.

Any threshold or intervention change made after held-out outcomes are observed invalidates
the held-out claim for that suite identity.

## Why this option

A 20/20/20 split is intentionally simple and auditable.

It gives enough development room for the mandatory thin slice, preserves a separate
tuning surface, and keeps one third of the canonical suite untouched for release
confirmation.

The paired held-out execution protocol materially strengthens the project because it
prevents a subtle but common form of leakage: inspecting baseline held-out failures
before executing or finalizing the intervention.

The scorer design also keeps deterministic evidence deterministic instead of delegating
everything to an LLM judge.

## Alternatives considered

### 30 / 15 / 15

Rejected.

It makes development comfortable but weakens the final confirmation surface.

### 24 / 18 / 18

Reasonable, but rejected.

It adds arithmetic complexity without a clear V1 evidence advantage.

### 20 / 20 / 20

Accepted.

Simple, balanced, and sufficient for a 60-case portfolio reliability suite.

### Fully LLM-judged evaluation

Rejected.

Retrieval identity, source-state compliance, citation eligibility, refusal state, trace
completeness, and leakage are deterministic system facts and should be scored as such.

### Inspect baseline held-out, then run final held-out

Rejected.

This creates an opportunity for unintentional adaptation to held-out evidence.

## Consequences

### Positive

- case roles are unambiguous;
- scorer ownership is explicit;
- held-out leakage risk is reduced;
- intervention comparisons use a stable scoring surface;
- semantic judging has an auditable human check;
- later release thresholds have a predeclared freeze procedure.

### Trade-offs

- 20 held-out cases cannot support broad statistical claims;
- human review of 20 held-out cases adds work;
- case authoring must satisfy two independent quota systems;
- scorer versioning becomes part of release identity;
- invalid held-out cases cannot be casually replaced.

## Non-claims

This ADR does not claim:

- the 60 cases already exist;
- the case IDs are frozen;
- numeric thresholds are already chosen;
- the baseline configuration is chosen;
- the intervention ladder is finalized;
- the semantic judge model is already selected;
- any system has passed evaluation.

## Exit evidence

This ADR is frozen when the repository contains:

```text
docs/constitution/EVALUATION_CONSTITUTION.md
docs/adr/ADR-0003-freeze-evaluation-split-scoring-and-threshold-procedure.md
datasets/controlled_cases/evaluation_policy_v1.json
updated docs/constitution/PHASE_0_DECISION_LEDGER.md
```

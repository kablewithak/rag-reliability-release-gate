# RAG Reliability Release Gate — Session Brief

**Document role:** Stable start-of-session operating brief  
**Use with:** `PRD.md` and the latest approved formal handover  
**Project type:** Standalone AI reliability, load-testing, and chaos-engineering proof project  
**Status:** Phase 0 — governance and experiment constitution  
**Current baseline:** PRD v0.2

---

## 1. Source-of-Truth Order

When sources conflict, use:

```text
1. PRD.md
2. Accepted ADRs
3. Constitutions, committed contracts, tests, reports, and release artifacts
4. Current terminal output and GitHub state
5. Latest approved formal handover
6. SESSION_BRIEF.md
7. Earlier chat
```

Do not invent repository state, branch state, test outcomes, corpus hashes, model/provider
configuration, load capacity, release verdicts, or publication state.

---

## 2. Project Identity

**Project:** RAG Reliability Release Gate  
**Public evidence viewer:** Context Rot RAG Chaos Lab  
**V1 ceiling:** 150 hours  
**Committed target:** 132 hours  
**Reliability reserve:** 18 hours  
**Operating posture:** Local-first, provider-neutral, zero-cash-required, public-evidence-safe

### North Star

Build a locally validated, public, evidence-backed RAG reliability release gate that
deliberately stresses a RAG system under context pressure, corpus drift, dependency
faults, and controlled traffic load; identifies what fails first; proves whether a
bounded intervention improves the failure; measures operational and semantic recovery;
and produces a defensible release verdict with a remediation backlog.

### Core thesis

```text
operational health
+
semantic reliability
```

A RAG system can remain operationally available while becoming semantically unsafe.

### Core release output

```text
PASS
CONDITIONAL_PASS
FAIL
```

for a named release identity covering code, corpus, retrieval configuration,
model/provider mode, evaluation suite, chaos profiles, workload, environment, and result
package.

---

## 3. Non-Negotiable Invariants

1. This is a load-testing and chaos-engineering release gate for RAG, not a generic RAG app.
2. The public viewer is read-only evidence inspection, not a live testing product.
3. Real public documents are authoritative; synthetic material is a labelled chaos overlay only.
4. The goal is a defensible release decision and failure attribution, not decorative charts or maximum RPS.
5. No paid service may be required for correctness, testing, the core demo, or public evidence viewing.
6. Every meaningful claim requires a named baseline, intervention, fixed evaluation conditions, score, failure labels, trace evidence, and limitation.
7. Runtime RAG code must never receive evaluator-only gold labels, gold source IDs, hidden expected outcomes, or post-run annotations.
8. Held-out release cases may not be used to tune prompts, retrieval, reranking, thresholds, fallback policy, or case selection after outcomes are observed.
9. No raw prompts, raw documents, raw model outputs, PII, secrets, provider payloads, or internal local paths may enter public artifacts.
10. Local load results are environment-bounded evidence, not production-capacity claims.
11. The public viewer must not be built before valid sanitized release artifacts exist.
12. Scope expansion may not consume the protected reliability reserve without empirical justification.

---

## 4. V1 Corpus Boundary

V1 uses a frozen, version-aware **GitHub REST API technical-documentation stress corpus**,
subject to the corpus constitution and snapshot ADR.

Planned corpus layers:

```text
curated current evaluation core
selected real historical corpus
real background load corpus
unit fixtures
synthetic chaos overlay
```

Synthetic overlays are never authoritative and may never become eligible final citations
or gold evidence.

Exact source families, snapshot/version, historical comparison, extraction method,
licensing manifest, and provenance details remain Phase 0 decisions until frozen.

---

## 5. Evaluation-Integrity Boundary

Runtime may use only:

```text
user query
authorized source content
allowed source metadata
declared retrieval/reranking/context configuration
permitted model/provider output
declared fault state
declared fallback policy
```

Runtime must not receive:

```text
gold answers
required source IDs
allowed citation IDs
forbidden source IDs
hidden expected refusal labels
post-run failure labels
held-out scoring outcomes
```

Gold labels belong only in the evaluator.

```text
better metric + evaluation leakage = rejected result
```

Held-out release cases must remain untouched during intervention tuning. Numeric release
thresholds must be frozen before held-out release evaluation.

---

## 6. V1 Architecture

Prefer one installable Python package with strong module boundaries:

```text
src/rag_reliability/
  contracts/
  config/
  corpus/
  inference/
  retrieval/
  grounding/
  evaluation/
  chaos/
  load/
  tracing/
  release/
  reporting/
  privacy/
```

Do not split modules into separate packages without a concrete independence requirement.

Runtime path:

```text
query
→ retrieval
→ metadata / authority / source-state filtering
→ optional reranking
→ context assembly
→ answer generation
→ citation-support validation
→ safe refusal or final answer
```

Use Python 3.11+, type hints, Pydantic v2, explicit errors/refusal states, deterministic
seeds where applicable, and provider-neutral adapters. Provider SDK objects must not
escape the provider boundary.

---

## 7. Mandatory Thin Slice

Before the full corpus, chaos suite, load suite, or public viewer:

```text
10–20 public source documents
6–10 development-only cases
1 fake/replay provider
1 retriever
1 context builder
1 citation-support validator
1 refusal path
1 trace contract
1 evaluation report
```

Required end-to-end path:

```text
query
→ retrieve
→ select evidence
→ assemble context
→ answer/refuse
→ validate citations
→ score
→ assign failure label
→ emit trace
→ emit result artifact
```

The thin slice is development proof, not release evidence.

---

## 8. Chaos and Load Doctrine

Every chaos experiment must define:

```text
experiment_id
hypothesis
steady_state
load_profile
fault_profile
blast_radius
duration
seed
abort_conditions
recovery_conditions
expected_safe_behavior
evaluation_scope
```

Use bounded named profiles rather than a Cartesian-product explosion.

Load testing has two lanes:

- **Lane A:** deterministic fake/replay provider for application and reliability load;
- **Lane B:** optional live-provider integration that must not become a paid correctness dependency.

Every load stage must report operational and semantic health together.

Recovery is not complete until both are satisfied:

```text
operational_recovery_time
semantic_recovery_time
```

Measure TTUD where meaningful.

---

## 9. Phase Order and Stop Rule

```text
Phase 0  — Governance and experiment constitution
Phase 1  — Contracts and repository foundation
Phase 2  — Thin deterministic vertical slice
Phase 3  — Frozen corpus and provenance
Phase 4  — Frozen evaluation suite and case-role manifests
Phase 5  — Baseline characterization
Phase 6  — Chaos profiles and negative controls
Phase 7  — Intervention development and regression
Phase 8  — Held-out confirmation
Phase 9  — Load, saturation, fault-under-load, and recovery
Phase 10 — Release gate and sanitized export
Phase 11 — Static public evidence viewer
Phase 12 — Final proof package and handover
```

> Do not start the next phase until the current phase's committed exit evidence exists and is accepted.

---

## 10. Current Session Mission Order

At the beginning of a working session:

1. Read `PRD.md`.
2. Read relevant accepted ADRs and constitutions.
3. Read the latest formal handover when one exists.
4. Run `git status`.
5. Run `git --no-pager log -1 --oneline` when commits exist.
6. Confirm current phase and authorization gate.
7. Inspect the relevant source/tests before changing behavior.
8. Preserve evidence for every meaningful AI-system change.

For behavior-changing work, validate before staging and inspect the diff/repository state
before Git commands are finalized.

For docs-only changes, do not claim behavioral validation.

---

## 11. Current Phase

```text
phase=0
phase_name=Governance and experiment constitution
status=repository scaffold created locally; governance baseline being frozen
highest_supported_maturity=repository_scaffolded
```

The next safe work is to resolve the remaining Phase 0 controlled decisions and commit
the governance baseline before implementing RAG runtime behavior.

# ADR-0001: Freeze V1 Project Boundary, Repository Shape, and Phase Governance

**Status:** Accepted  
**Decision scope:** Durable V1 architecture and scope controls  
**Superseded by:** None

## Context

The RAG Reliability Release Gate is a bounded 150-hour proof project whose primary
engineering focus is load testing and chaos engineering applied to RAG reliability.
The project needs an initial durable boundary before runtime implementation begins.

Without an explicit freeze, the repository could drift into a generic chatbot, a
dashboard-first demo, a cloud platform, a multi-package architecture, or a broad RAG
benchmark. Those directions would consume the V1 budget without improving the core
reliability proof.

## Decision

Version 1 is frozen around the following durable choices.

### Product boundary

The project is a local-first RAG reliability release gate that measures both:

```text
operational health
+
semantic reliability
```

under controlled context pressure, corpus drift, dependency faults, and traffic load.

The release output is:

```text
PASS
CONDITIONAL_PASS
FAIL
```

for a named release identity.

The static public viewer, Context Rot RAG Chaos Lab, is an evidence-inspection surface.
It is not the system under test and is not a live inference product.

### Repository boundary

Use one installable Python package:

```text
src/rag_reliability/
```

with strong internal module boundaries for contracts, configuration, corpus,
inference, retrieval, grounding, evaluation, chaos, load, tracing, release, reporting,
and privacy.

A module may become a separate package only when a concrete independence requirement is
demonstrated.

### Environment boundary

Core correctness, testing, and evidence generation must remain:

```text
local-first
provider-neutral
zero-cash-required
```

No paid API, managed vector database, hosted database, Kubernetes deployment, queue,
GPU-hosted service, or cloud-first architecture is required for V1 correctness.

### Data boundary

V1 uses one domain: a frozen, version-aware GitHub REST API technical-documentation
stress corpus.

Real public documents are authoritative according to their declared source metadata.
Synthetic chaos overlays are never authoritative and are never eligible as final
citations or gold evidence.

The exact source families, snapshot/version, historical comparison, extraction method,
and licensing manifest are intentionally not frozen by this ADR; they remain Phase 0
decisions.

### Evaluation-integrity boundary

Evaluator-only gold labels, source IDs, hidden expected outcomes, and post-run labels
must never cross into the runtime RAG path.

Held-out release cases may not be used to tune prompts, retrieval, reranking,
thresholds, fallback policy, or case selection after outcomes are observed.

### Delivery boundary

```text
V1 maximum: 150 hours
committed target: 132 hours
protected reliability reserve: 18 hours
```

The reserve is for empirically necessary reliability work, not feature expansion.

### Sequencing boundary

The project follows the PRD's Phase 0–12 order. A phase may not begin until the
current phase's committed exit evidence exists and is accepted.

In particular:

- no full chaos engine before the thin deterministic vertical slice works;
- no full load suite before the relevant runtime/evaluation contracts exist;
- no public viewer before valid sanitized release artifacts exist.

## Consequences

### Positive

- Prevents scope drift into generic RAG/product work.
- Keeps implementation inspectable and maintainable.
- Preserves the budget for evaluation, chaos, load, recovery, and release evidence.
- Makes provider and infrastructure choices replaceable.
- Keeps the public demo subordinate to actual evidence.

### Trade-offs

- V1 intentionally avoids broader infrastructure and multi-domain coverage.
- Local load results remain environment-bounded.
- Some architecture that could help a future SaaS product is deliberately deferred.
- Exact corpus snapshot and evaluation thresholds still require separate Phase 0 freezes.

## Change Rule

Changing any of the following requires a new ADR and PRD reconciliation:

- project north star;
- one-domain V1 boundary;
- authoritative-source definition;
- synthetic-overlay authority rules;
- provider-neutral requirement;
- zero-cash-required correctness boundary;
- 150-hour ceiling or protected reserve model;
- release-gate philosophy;
- public sanitization boundary;
- repository single-package architecture;
- viewer-as-static-evidence-only boundary.

# Product Requirements Document
# RAG Reliability Release Gate
## Public Evidence Viewer: Context Rot RAG Chaos Lab

**Status:** Draft v0.2 — revised implementation baseline  
**Project type:** Standalone AI reliability, load-testing, and chaos-engineering proof project  
**Delivery constraint:** 150 hours maximum for Version 1  
**Committed work target:** 132 hours  
**Reliability reserve:** 18 hours  
**Operating posture:** Local-first, provider-neutral, zero-cash-required, public-evidence-safe  
**Primary maturity target:** Locally validated → controlled-chaos evaluated → local-load evaluated → public evidence release  
**Not claimed:** Production-ready, customer-data tested, universally model-valid, globally load-valid, or security-complete

---

## 1. Executive Summary

The **RAG Reliability Release Gate** is a local-first reliability harness for determining whether a named retrieval-augmented generation (RAG) configuration remains grounded, citation-safe, appropriately cautious, and operationally stable when exposed to controlled semantic pressure, corpus drift, dependency faults, and traffic load.

Its primary engineering focus is **load testing plus chaos engineering applied to an AI system**.

The project does not ask only:

> Does the RAG system return HTTP 200?

It asks:

> Under named load and fault conditions, does the RAG system remain semantically reliable, fail safely, recover correctly, and produce enough evidence to justify release?

The harness must distinguish:

1. retrieval failure;
2. context-assembly failure;
3. generation failure;
4. citation-support failure;
5. unsafe answer or unsafe refusal;
6. freshness and source-version failure;
7. dependency and provider-boundary failure;
8. load, saturation, and recovery failure;
9. evaluation-integrity or evidence-integrity failure.

The principal output is a reproducible:

```text
PASS
CONDITIONAL_PASS
FAIL
```

for a named release identity consisting of code, corpus, retrieval configuration, model/provider mode, evaluation suite, chaos profile set, workload, execution environment, and result package.

The public presentation layer, **Context Rot RAG Chaos Lab**, is a read-only static evidence viewer. It exists to make the release evidence inspectable. It is not the system under test and is not a live inference product.

---

## 2. North Star

> Build a locally validated, public, evidence-backed RAG reliability release gate that deliberately stresses a RAG system under context pressure, corpus drift, dependency faults, and controlled traffic load; identifies what fails first; proves whether a bounded intervention improves the failure; measures operational and semantic recovery; and produces a defensible release verdict with a remediation backlog.

### 2.1 Core thesis

A RAG system can remain operationally available while becoming semantically unsafe.

Version 1 must therefore measure both:

```text
operational health
+
semantic reliability
```

during load and chaos experiments.

### 2.2 Non-negotiable invariants

1. **This is a load-testing and chaos-engineering release gate for RAG, not a generic RAG app.**
2. **The public viewer is read-only evidence inspection, not a live testing product.**
3. **Real public documents are authoritative; synthetic material is a labelled chaos overlay only.**
4. **The goal is a defensible release decision and failure attribution, not decorative charts or maximum RPS.**
5. **No paid service may be required for correctness, testing, the core demo, or public evidence viewing.**
6. **Every meaningful claim requires a named baseline, intervention, fixed evaluation conditions, score, failure labels, trace evidence, and limitation.**
7. **Runtime RAG code must never receive evaluator-only gold labels, gold source IDs, hidden expected outcomes, or post-run annotations.**
8. **Held-out release cases may not be used to tune prompts, retrieval, reranking, thresholds, fallback policy, or case selection after outcomes are observed.**
9. **No raw prompts, raw documents, raw model outputs, PII, secrets, provider payloads, or internal local paths may enter public artifacts.**
10. **Local load results are environment-bounded evidence, not production-capacity claims.**
11. **The Hugging Face viewer must not be built before valid sanitized release artifacts exist.**
12. **The project must remain inside the 150-hour V1 ceiling; scope expands only if the reliability reserve remains protected.**

---

## 3. Problem Statement

RAG systems often appear reliable in clean demonstrations but fail under realistic stress:

- semantically similar documents crowd out required evidence;
- stale or historical documents compete with current sources;
- increasing context dilutes or displaces important evidence;
- the correct source is retrieved but excluded during context assembly;
- citations are formatted correctly but do not support the claim;
- missing or conflicting evidence produces a confident answer instead of a safe fallback;
- a reranker, embedding service, provider, or other dependency slows or fails;
- queueing, contention, or timeouts change which fallback paths execute;
- latency recovers while answer quality remains degraded;
- traditional load tests report success while semantic reliability has already breached a release gate.

The project converts these risks into controlled, reproducible experiments.

---

## 4. Product Positioning and Buyer Value

### 4.1 Buyer promise

> I help technical teams stress-test RAG systems under document complexity, dependency faults, and traffic load; identify where semantic reliability degrades; prove which interventions reduce the failure; and establish a release gate that catches regressions before deployment.

### 4.2 Commercial translation

| Offer | Buyer pain | Evidence produced |
|---|---|---|
| AI System Reliability Audit | “We do not know where our RAG system fails.” | System map, baseline, failure taxonomy, top risks |
| RAG Chaos & Load Sprint | “Our assistant behaves unpredictably under larger corpora, long context, faults, or traffic.” | Chaos experiments, load evidence, failure autopsies, remediation |
| AI Reliability Pilot | “We need confidence before exposing a narrow workflow.” | Controlled scope, release gate, regression suite, final verdict |
| AI Reliability Retainer | “Models, prompts, documents, providers, and traffic patterns drift.” | Recurring release gate, regression runs, evidence review, remediation backlog |

### 4.3 Primary portfolio signal

The project must demonstrate:

```text
build the AI path
→ define steady state
→ inject controlled faults
→ apply controlled load
→ measure operational + semantic degradation
→ attribute the failure
→ test a bounded intervention
→ verify recovery and regression
→ issue a release decision
```

---

## 5. Intended Users

| User | Primary question | Required evidence |
|---|---|---|
| CTO / technical founder | Can this named RAG configuration ship under the tested conditions? | Verdict, residual risk, remediation |
| AI / LLM engineer | Which layer fails first and why? | Layered metrics, traces, failure labels |
| Platform / reliability engineer | What happens under load, dependency faults, and recovery? | Saturation, latency, queue, fault, recovery evidence |
| Tech lead | Can this be reproduced and regression-tested? | Versioned inputs, fixed evals, deterministic experiments |
| Hiring manager | Does the author understand AI reliability beyond prompting? | Typed boundaries, chaos method, load method, eval integrity |
| Consultancy prospect | What would an audit or sprint actually deliver? | Buyer-readable report, evidence viewer, remediation backlog |

---

## 6. Goals

### 6.1 Product goals

1. Build a provider-neutral RAG path with source provenance, citation validation, safe fallback, and metadata-safe traces.
2. Define a steady-state reliability hypothesis for every chaos experiment.
3. Inject deterministic semantic, source-state, dependency, and context faults.
4. Apply deterministic load profiles and measure both operational and semantic health.
5. Distinguish operational recovery from semantic recovery.
6. Compare a weak baseline with bounded interventions on fixed development and held-out cases.
7. Generate a release verdict with hard integrity/safety gates plus diagnostic metrics.
8. Export sanitized, reproducible evidence artifacts.
9. Publish a static evidence viewer driven entirely by release artifacts.
10. Preserve enough governance and handover evidence that another engineer or LLM can resume without inventing state.

### 6.2 Explicitly secondary goals

The following are useful only if they support the primary release-gate evidence:

- model/provider comparison;
- cost analysis;
- UI polish;
- broad corpus coverage;
- high request-rate bragging rights.

They are not independent goals.

---

## 7. Non-Goals and Explicit Exclusions

Version 1 excludes:

- customer, employee, medical, financial, or private client data;
- live production traffic;
- production serving;
- customer accounts or multi-tenancy;
- live chaos execution from the public viewer;
- autonomous remediation;
- agents or multi-agent workflows;
- cloud-first infrastructure;
- Kubernetes deployment;
- managed vector databases;
- hosted databases;
- message queues unless direct evidence proves they are necessary;
- a paid LLM API as a correctness dependency;
- GPU hosting as a requirement;
- production throughput claims;
- universal model benchmarking;
- multi-domain benchmarking;
- a complete prompt-injection security product;
- a generic chatbot;
- dashboard-first implementation;
- adding a second corpus in V1.

---

## 8. V1 Data and Corpus Strategy

### 8.1 Primary domain

Version 1 uses a **frozen, version-aware GitHub REST API technical-documentation stress corpus**, subject to the corpus constitution and snapshot ADR.

The corpus consists of:

1. current authoritative GitHub REST documentation;
2. associated GitHub OpenAPI records;
3. selected real historical source states for version/freshness conflict;
4. a larger real background corpus for retrieval and load pressure;
5. explicitly non-authoritative synthetic chaos overlays.

The exact current snapshot date, API version, historical comparison version, source families, extraction method, and licensing manifest must be frozen before ingestion is accepted.

### 8.2 Why this domain

GitHub REST documentation is suitable because it provides:

- semantically overlapping endpoint families;
- permissions, pagination, rate-limit, webhook, error, and version concepts;
- current and historical source states;
- structured OpenAPI evidence;
- machine-readable and human-readable representations;
- realistic metadata-scope and authority questions;
- public provenance suitable for a public evidence project;
- enough corpus scale for load and retrieval-pressure experiments without making corpus curation the whole project.

### 8.3 Corpus layers

| Layer | V1 purpose | Authority |
|---|---|---|
| Curated current evaluation core | Authoritative evidence for canonical questions | Authoritative |
| Selected real historical corpus | Freshness, deprecation, version-conflict chaos | Historical |
| Real background load corpus | Retrieval competition, index-size pressure, latency/memory stress | Authoritative only according to its metadata |
| Unit fixtures | Contract and deterministic mechanic tests | Test-only authoritative |
| Synthetic chaos overlay | Exact distractors, metadata mutation, duplication, filler, bounded conflicts | Never authoritative |

### 8.4 Initial scale targets

These are **targets, not vanity minimums**.

| Layer | Approximate target |
|---|---:|
| Curated current evaluation core | 300–500 chunks |
| Selected historical material | 100–200 chunks |
| Real background load corpus | 500–1,500 chunks |
| Persistent real corpus total | ~900–2,200 chunks |
| Synthetic overlay | Generated per named scenario |
| Canonical evaluation cases | 60 |

The project may stop below the upper range if diagnostic difficulty and load behaviour are already sufficient.

### 8.5 Data-role ledger

Every source, chunk, case, trace, report, and overlay must have exactly one primary role:

```text
unit_fixture
corpus_source
historical_source
background_load_source
chaos_overlay
evaluation_development_case
intervention_tuning_case
held_out_release_case
load_test_replay_case
public_demonstration_artifact
```

### 8.6 Source manifest requirements

Every real source record must include at least:

```text
source_id
source_family
source_url
source_license
retrieved_at
source_commit_sha_or_version
document_version
effective_from
effective_to
authority_level
source_state
product_scope
api_version_or_snapshot
content_sha256
title
topic_tags
data_role
```

### 8.7 Synthetic overlay requirements

Every synthetic overlay must include:

```text
synthetic_overlay: true
authority_level: none
eligible_as_final_citation: false
eligible_as_gold_evidence: false
derived_from_source_ids
chaos_purpose
seed
scenario_id
```

Allowed purposes:

- semantic distractor;
- neutral filler;
- duplicate evidence;
- metadata mutation;
- controlled conflict;
- context-order mutation;
- malformed record fixture;
- dependency-fault fixture.

---

## 9. Evaluation Integrity and Split Constitution

### 9.1 Runtime evidence boundary

Runtime RAG code may use only:

- user query;
- authorized source content;
- allowed source metadata;
- declared retrieval/reranking/context configuration;
- permitted model/provider output;
- declared fault state;
- declared fallback policy.

Runtime code must not receive:

- gold answers;
- required source IDs;
- allowed citation IDs;
- forbidden source IDs;
- hidden expected refusal labels;
- post-run failure labels;
- held-out scoring outcomes.

### 9.2 Case-role split

The 60 canonical cases must be assigned an immutable role before intervention tuning begins:

```text
evaluation_development_case
intervention_tuning_case
held_out_release_case
```

The exact split count must be frozen in the evaluation constitution.

Rules:

- development cases may be used to build scorers and debug mechanics;
- tuning cases may be used to compare candidate interventions;
- held-out release cases may not be used to tune retrieval, prompts, thresholds, reranking, fallback, or case selection after outcomes are observed;
- the held-out manifest must be versioned and hashed before final intervention selection.

### 9.3 Threshold-freeze rule

Numeric release thresholds may be calibrated on permitted development/tuning evidence.

They must be frozen **before held-out release evaluation**.

A held-out result must never be used to retroactively choose a favourable threshold.

### 9.4 Evaluation-integrity failure

Canonical failure label:

```text
evaluation_integrity_violation
```

Any measured improvement associated with evaluation leakage is rejected.

---

## 10. RAG Runtime Requirements

The baseline path is:

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

Requirements:

- Python 3.11+;
- typed interfaces;
- Pydantic v2 contracts;
- explicit errors and refusal states;
- provider-neutral adapter;
- fake/replay provider;
- deterministic seeds where applicable;
- no provider SDK objects beyond the adapter;
- no blanket exception handling;
- provenance preserved through the pipeline;
- source authority preserved through context assembly;
- citations or explicit refusal;
- no evaluator-only fields crossing into runtime.

---

## 11. Thin Vertical Slice Requirement

Before the full corpus or full chaos suite is built, Version 1 must prove one small end-to-end path using:

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

The slice must execute:

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

The thin slice is disposable development proof. It is not release evidence.

No chaos engine, load suite, or public viewer may be built before this path works deterministically.

---

## 12. Evaluation Layers and Metrics

Evaluation must keep layers separate.

### 12.1 Retrieval quality

- Gold Evidence Recall@k
- required-source retrieval rate
- stale/historical selection rate
- wrong-scope selection rate

### 12.2 Context-assembly quality

- Gold Evidence Inclusion Rate
- required-evidence position
- evidence truncation
- context dilution
- authority-priority violations

### 12.3 Answer quality

- Answer Fact Accuracy
- required-fact coverage
- unsupported material claim rate

### 12.4 Citation quality

- Claim Support Rate
- Citation Precision
- Citation Recall
- citation-missing rate

### 12.5 Refusal quality

- Unsafe Answer Rate
- Safe Refusal Precision
- false-refusal rate
- source-conflict fallback correctness

### 12.6 Operational quality

- throughput / achieved RPS
- p50 latency
- p95 latency
- max latency
- timeout rate
- retry rate
- queue depth
- requests in flight
- CPU utilization
- memory utilization
- dependency fault rate
- load shedding
- operational recovery time
- semantic recovery time
- Time To Unsafe Degradation (TTUD)

p99 may be reported only when sample volume makes it meaningful. It is not a mandatory V1 headline metric.

### 12.7 Flagship combined view

Every load stage must report both:

| Operational health | Semantic reliability |
|---|---|
| achieved RPS | claim support |
| p95 latency | unsupported-answer rate |
| timeout rate | safe-refusal behavior |
| queue depth | citation precision |
| CPU / memory | retrieval/context inclusion |

The flagship question is:

> At what point does semantic reliability degrade relative to operational saturation?

---

## 13. Failure Taxonomy

Every degraded result carries one primary label; secondary labels are permitted.

### 13.1 RAG failures

```text
retrieval_miss
context_exclusion
context_dilution
gold_evidence_truncated
stale_source_selected
source_conflict_unresolved
metadata_scope_failure
citation_not_supported
citation_missing
unsupported_answer
unsafe_refusal
```

### 13.2 Dependency / operational failures

```text
provider_timeout
provider_malformed_response
reranker_unavailable
retry_exhausted
load_shedding
queue_saturation
trace_incomplete
recovery_incomplete
semantic_recovery_lag
```

### 13.3 Reliability-system / release failures

```text
evaluation_integrity_violation
corpus_manifest_invalid
authoritative_source_violation
configuration_identity_mismatch
release_evidence_incomplete
public_sanitization_failure
```

---

## 14. Chaos Engineering Method

### 14.1 Chaos is hypothesis-driven

Every chaos experiment must define a steady-state hypothesis before fault injection.

Required experiment fields:

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

### 14.2 Required ChaosExperiment contract

A typed contract must exist conceptually equivalent to:

```text
ChaosExperiment
  experiment_id
  hypothesis
  steady_state
  load_profile
  fault_profile
  blast_radius
  duration
  abort_conditions
  recovery_conditions
  expected_safe_behavior
  seed
  scenario_ids
```

### 14.3 Steady-state example

```text
Before fault:
- critical unsafe-answer rate = 0
- claim-support rate meets the frozen threshold
- trace completeness = 100%
- queue depth remains bounded
- p95 latency remains inside the experiment band
```

### 14.4 Chaos families

#### Corpus pressure
Increase real index size or retrieval candidate competition.

#### Semantic distractor pressure
Increase semantically plausible but incorrect or irrelevant candidates.

#### Freshness/version pressure
Mix current and historical material and test source-state priority.

#### Context pressure
Hold retrieval evidence constant while increasing context budget.

#### Evidence-position pressure
Move required evidence between beginning, middle, and end.

#### Metadata pressure
Corrupt, omit, or mis-scope critical metadata.

#### Dependency faults
Inject delay, unavailability, malformed response, or bounded failure into provider/reranker boundaries.

#### Operational load
Apply smoke, staircase, spike, soak, and named fault-under-load profiles.

### 14.5 Named chaos profiles

Do not execute the full Cartesian product.

Version 1 should use a bounded named profile set, for example:

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
```

Each profile must isolate one hypothesis unless it is the designated compound-failure experiment.

### 14.6 Single flagship cascading-failure experiment

Version 1 must include **one**, and only one mandatory, deliberately compound failure such as:

```text
moderate load
+
large context
+
reranker slowdown
+
current/historical source conflict
```

The purpose is to capture and explain a failure cascade, not to create combinatorial test explosion.

---

## 15. Load Testing Method

### 15.1 Lane A — deterministic application/reliability load

Uses fake/replay provider behavior.

Purpose:

- retrieval capacity;
- context assembly pressure;
- queueing and saturation;
- timeouts and retries;
- fallback behavior;
- trace emission;
- schema validity;
- semantic reliability under controlled load;
- recovery.

Initial profiles:

| Test | Target |
|---|---|
| Smoke | 1 RPS for 3 minutes |
| Staircase | 2, 5, 10, 15 RPS; 3 minutes each |
| Spike | 2 RPS baseline → 15 RPS spike → 2 RPS recovery |
| Soak | 70% of measured local safe operating rate for 45 minutes |
| Fault under load | 70% local safe rate + one named dependency fault |

These rates may be revised by ADR if the local environment makes them non-diagnostic.

### 15.2 Lane B — optional live-provider integration

A real model/provider may be used only as an optional integration lane if available without becoming a paid correctness dependency.

Purpose:

- adapter behavior;
- real provider latency/error classification;
- modest-concurrency groundedness;
- real answer and citation behavior.

This lane must not become a general provider-capacity benchmark.

### 15.3 Traffic mix

Initial deterministic load mix:

| Traffic group | Share |
|---|---:|
| Normal grounded requests | 50% |
| Moderate semantic overlap | 20% |
| Long-context pressure | 15% |
| Freshness conflict | 10% |
| Must-refuse cases | 5% |

Cold-path and warm-path tests must be reported separately when both exist.

---

## 16. Recovery Semantics

Recovery is not complete when latency alone returns to normal.

Version 1 must measure:

```text
operational_recovery_time
semantic_recovery_time
```

### 16.1 Operational recovery

Time until operational metrics return to the declared steady-state band.

### 16.2 Semantic recovery

Time until semantic metrics return to the declared steady-state band.

### 16.3 Time To Unsafe Degradation

```text
TTUD
```

is the time between fault onset and the first breach of a frozen critical semantic release criterion.

Where meaningful, experiment timelines should record:

```text
fault_started
operational_breach
semantic_breach
fault_removed
operational_recovered
semantic_recovered
```

---

## 17. Negative Controls and Intervention Design

### 17.1 Mandatory negative controls

Keep and report:

- naive top-k context inflation;
- no source-state/freshness filter;
- citation formatting without support validation;
- answer-anyway fallback;
- reranker-disabled fallback;
- oracle gold-evidence context builder;
- evaluator-label-assisted selection;
- corrupted source manifest;
- malformed provider response;
- dependency timeout;
- losing intervention cases;
- cases where more context makes results worse.

Oracle and evaluator-assisted paths are never release-eligible.

### 17.2 Intervention ladder

Do not treat the intervention as one unexplained bundle.

Development/tuning should use a bounded ablation ladder such as:

```text
B0  baseline
I1  + authority / current-source filtering
I2  + bounded evidence / context policy
I3  + citation-support validation and refusal policy
I4  + reranker, only if justified
IF  final frozen intervention
```

The exact ladder may change through ADR, but the principle is mandatory:

> We must be able to explain which bounded intervention addressed which failure class.

### 17.3 Final held-out comparison

Only the frozen baseline and frozen final intervention are required for the final held-out release comparison.

---

## 18. Release Gate Policy

### 18.1 Gate philosophy

A single aggregate score may not hide a critical failure.

Metrics are classified as:

```text
hard integrity gate
hard safety gate
hard evidence gate
hard public-release gate
quality threshold
regression gate
diagnostic metric
environment-bounded operational metric
```

### 18.2 Hard-gate examples

A release cannot PASS if any applicable critical rule fails:

- evaluator leakage;
- invalid corpus provenance;
- unsafe answers on critical must-refuse cases beyond the frozen rule;
- critical citation-support failure beyond the frozen rule;
- required trace evidence missing;
- unbounded retry or unsafe dependency degradation;
- release evidence identity mismatch;
- public sanitization failure.

### 18.3 PASS

PASS requires:

1. all critical integrity gates pass;
2. critical semantic thresholds pass;
3. no disallowed regression against the baseline;
4. dependency faults degrade safely;
5. local workload remains inside the declared operational gate;
6. operational and semantic recovery conditions are satisfied;
7. evidence package is reproducible and sanitized.

### 18.4 CONDITIONAL_PASS

Allowed when:

- all hard safety/integrity gates pass;
- named non-critical stress conditions fail;
- residual risk is explicit;
- remediation is bounded;
- the report does not overstate readiness.

### 18.5 FAIL

Required when:

- a hard integrity or safety gate fails;
- evidence cannot be reproduced;
- public evidence cannot be sanitized;
- critical dependency behavior is unsafe or unbounded;
- the system breaches frozen critical release criteria.

---

## 19. Release Evidence Identity

Every meaningful run must record:

```text
release_id
run_id
git_commit_sha
corpus_manifest_hash
chunking_configuration_hash
retrieval_configuration_hash
reranker_configuration_hash
model_or_provider_identifier
provider_mode
eval_suite_version
case_role_manifest_hash
chaos_profile_version
scorer_version
threshold_policy_version
baseline_or_intervention
execution_environment
load_profile_id
fault_profile_id
result_hash
sanitization_passed
verdict
```

The system must make it possible to state:

> This verdict came from this exact code, corpus, configuration, evaluation scope, chaos profile, workload, environment, and result package.

---

## 20. Architecture

### 20.1 High-level architecture

```text
Local reliability harness
  ├── corpus ingestion + manifests
  ├── retrieval
  ├── provider-neutral inference boundary
  ├── context assembly
  ├── citation + refusal validation
  ├── evaluation
  ├── chaos experiment runner
  ├── load runner
  ├── resource + trace instrumentation
  ├── release gate
  └── sanitized evidence exporter
           ↓
Static release artifacts
           ↓
Context Rot RAG Chaos Lab
```

### 20.2 Preferred V1 repository shape

Prefer one installable Python package with strong module boundaries rather than unnecessary multi-package overhead.

```text
rag-reliability-release-gate/
├── README.md
├── NORTH_STAR.md
├── PRD.md
├── SESSION_BRIEF.md
├── pyproject.toml
├── src/
│   └── rag_reliability/
│       ├── contracts/
│       ├── config/
│       ├── corpus/
│       ├── inference/
│       ├── retrieval/
│       ├── grounding/
│       ├── evaluation/
│       ├── chaos/
│       ├── load/
│       ├── tracing/
│       ├── release/
│       ├── reporting/
│       └── privacy/
├── datasets/
│   ├── source_documents/
│   ├── source_manifests/
│   ├── historical_snapshots/
│   ├── chaos_overlays/
│   ├── controlled_cases/
│   └── rejected_cases/
├── apps/
│   └── evidence-viewer/
├── docs/
│   ├── constitution/
│   ├── adr/
│   ├── methodology/
│   ├── runbooks/
│   ├── handovers/
│   └── commercial/
├── evidence_vault/
│   ├── releases/
│   ├── eval_reports/
│   ├── load_reports/
│   ├── chaos_reports/
│   ├── trace_samples/
│   └── before_after_tables/
├── scripts/
└── tests/
```

A module may become a separate package later only when a concrete independence requirement justifies it.

---

## 21. Public Evidence Viewer

The public viewer is built only after a valid sanitized release package exists.

It must:

- be static and read-only;
- contain no API keys or live provider calls;
- execute no live chaos or load tests;
- display release identity and sanitization status;
- show methodology and non-claims;
- load only sanitized versioned JSON artifacts;
- reproduce charts from release artifacts.

### 21.1 Flagship views

V1 should prioritize five high-value views:

1. **Quality Under Load** — operational vs semantic degradation;
2. **Context Rot Curve** — context size vs grounded/citation-safe behavior;
3. **Failure Funnel** — retrieval → context → answer → citation → refusal;
4. **Spike / Fault Recovery Timeline** — operational vs semantic recovery;
5. **Failure Taxonomy / Autopsy** — dominant failure modes and one flagship cascading failure.

Additional charts are optional only if time remains.

### 21.2 Required case-explorer fields

```text
case_id
case_role
question_class
context_budget
evidence_position
distractor_profile
source_state
load_profile
fault_profile
baseline_outcome
intervention_outcome
citation_support
primary_failure_label
latency_summary
resource_summary
trace_completeness
sanitized_trace_timeline
why_case_matters
```

---

## 22. Privacy, Security, and Public-Evidence Controls

Required engineering controls:

- data minimization;
- public documentation only in V1;
- source licensing and attribution manifest;
- no customer data;
- no PII or secrets in logs;
- no raw prompt/document/model output in public artifacts;
- metadata-safe traces;
- least-privilege settings;
- sanitization test before public export;
- release artifact integrity hashes;
- retention/deletion notes for local artifacts;
- provider boundaries documented;
- no public artifact is assumed safe until the sanitization gate passes.

This is engineering guidance, not legal advice.

---

## 23. V1 Phase Sequence

The project uses the following chronological sequence:

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

### Stop rule

> Do not start the next phase until the current phase’s committed exit evidence exists and is accepted.

### Important sequencing rule

The public viewer may not begin before:

- release schema exists;
- sanitized evidence export exists;
- release verdict policy exists;
- at least one valid baseline/intervention evidence package exists.

---

## 24. Hour Budget

Version 1 commits approximately 132 hours and preserves 18 hours as reliability reserve.

| Stage | Hours |
|---|---:|
| Governance + ADR freeze | 12 |
| Contracts and scaffold | 10 |
| Thin vertical slice | 10 |
| Corpus constitution + frozen corpus | 16 |
| Full evaluation suite | 12 |
| Baseline characterization | 14 |
| Chaos + negative controls | 16 |
| Intervention + regression | 12 |
| Load / fault / recovery evidence | 10 |
| Release gate + export | 8 |
| Static viewer | 6 |
| Final proof package | 6 |
| **Committed** | **132** |
| **Reliability reserve** | **18** |
| **Maximum** | **150** |

Reserve is used only for empirically necessary work such as:

- corpus ambiguity;
- scorer defects;
- trace-contract defects;
- unexpected load bottlenecks;
- evaluation-label correction;
- release-export/sanitization defects.

It is not feature-expansion budget.

---

## 25. Acceptance Criteria for V1

### 25.1 Core system

- [ ] deterministic local RAG path runs from documented commands;
- [ ] typed contracts surround model/provider boundaries;
- [ ] fake/replay provider supports deterministic tests;
- [ ] evaluator-only fields are blocked from runtime;
- [ ] metadata-safe traces exist;
- [ ] explicit refusal and error states exist.

### 25.2 Corpus and evaluation

- [ ] corpus snapshot/version and licensing are frozen;
- [ ] current, historical, and background-load roles are explicit;
- [ ] synthetic overlays cannot become authoritative citations;
- [ ] 60 canonical cases exist;
- [ ] case roles are frozen and hashed;
- [ ] held-out cases remain untouched during tuning;
- [ ] release thresholds are frozen before held-out evaluation;
- [ ] failure taxonomy is applied to actual results.

### 25.3 Chaos

- [ ] every experiment declares steady state, hypothesis, blast radius, abort, and recovery conditions;
- [ ] context size is tested;
- [ ] evidence position is tested;
- [ ] semantic distractors are tested;
- [ ] freshness/version conflict is tested;
- [ ] metadata-scope failure is tested;
- [ ] at least one dependency fault is tested;
- [ ] mandatory negative controls exist;
- [ ] one flagship cascading-failure experiment exists.

### 25.4 Load and recovery

- [ ] smoke test executed;
- [ ] staircase executed;
- [ ] spike/recovery executed;
- [ ] soak executed;
- [ ] one fault-under-load profile executed;
- [ ] CPU, memory, queue depth, and in-flight requests are captured where applicable;
- [ ] operational and semantic reliability are reported together;
- [ ] TTUD is measured where meaningful;
- [ ] operational recovery and semantic recovery are distinguished;
- [ ] local safe operating rate is reported only as environment-bounded evidence.

### 25.5 Release evidence

- [ ] baseline and final intervention are compared on frozen held-out conditions;
- [ ] clean-case regressions are checked;
- [ ] hard gates cannot be hidden by aggregate scores;
- [ ] PASS / CONDITIONAL_PASS / FAIL policy is implemented;
- [ ] release identity is complete;
- [ ] evidence package is reproducible;
- [ ] public sanitization gate passes.

### 25.6 Public evidence

- [ ] static viewer uses only sanitized release artifacts;
- [ ] viewer contains no secrets or live inference;
- [ ] flagship charts are reproducible from versioned JSON;
- [ ] methodology and non-claims are visible;
- [ ] a skeptical CTO can identify verdict, dominant risks, and remediation in under 15 minutes.

---

## 26. Documentation and Handover Doctrine

Source-of-truth hierarchy:

```text
1. PRD.md
2. Accepted ADRs
3. Constitutions, committed contracts, tests, reports, release artifacts
4. Current terminal output and GitHub state
5. Latest approved handover
6. SESSION_BRIEF.md
7. Earlier chat
```

Handover documents must record current facts and next safe action. They must not duplicate the full PRD.

Stable doctrine belongs here or in constitutions/ADRs.

Current state belongs in the handover.

Session objective belongs in the Session Brief.

---

## 27. Risks and Controls

| Risk | Control |
|---|---|
| Project becomes generic RAG | Load/chaos/release-gate north star |
| Project becomes dashboard theatre | Viewer only after release evidence |
| Chaos becomes random fault injection | Steady-state hypothesis + blast radius + abort/recovery contract |
| Load testing becomes HTTP benchmarking | Operational + semantic metrics reported together |
| Corpus becomes the project | Bounded GitHub REST domain and scale tiers |
| Evaluation gets tuned to implementation | Eval constitution before baseline; held-out role freeze |
| Thresholds chosen after results | Threshold freeze before held-out run |
| Intervention becomes an unexplained bundle | Bounded ablation ladder |
| Synthetic evidence becomes authoritative | Typed overlay role and citation prohibition |
| Local RPS is overclaimed | Environment-bounded language only |
| Latency recovers before quality | Separate operational and semantic recovery |
| Cartesian explosion | Named chaos profiles only |
| Scope consumes 150 hours | 132-hour committed scope + 18-hour reserve |
| Public traces leak data | Sanitization gate and public-evidence policy |

---

## 28. Controlled Decisions Remaining Before Implementation

Phase 0 must resolve:

1. final repository name and path;
2. exact GitHub source families;
3. exact current source snapshot / API version;
4. exact historical comparison snapshot / version;
5. extraction and normalization method;
6. source licensing and attribution manifest format;
7. exact 60-case split among development, tuning, and held-out release roles;
8. scorer definitions and evidence requirements;
9. threshold-freeze procedure;
10. initial baseline configuration;
11. intervention-ablation order;
12. exact resource telemetry implementation;
13. whether a minimal local HTTP wrapper is needed for load tests;
14. exact chaos-profile manifest;
15. execution-environment capture format;
16. public release licensing and evidence retention policy.

Decisions that alter the north star, public-data policy, authoritative-source definition, synthetic-overlay rules, release-gate policy, scoring definitions, public sanitization boundary, paid-dependency prohibition, or provider-neutral rule require an ADR.

---

## 29. Success Definition

The project succeeds when a skeptical CTO, hiring manager, or senior AI/reliability engineer can inspect the repository and evidence and conclude:

> This author understands that AI reliability under load is not equivalent to HTTP availability. They can define steady state, inject controlled faults, measure semantic degradation, identify the failing layer, distinguish operational from semantic recovery, test bounded interventions without evaluation leakage, and issue a reproducible release decision.

Commercially, the project succeeds when it can support the offer:

> “I can stress-test your RAG workflow under document pressure, dependency faults, and load; show where semantic reliability breaks; prove which remediation changes the result; and leave you with a repeatable release gate.”

---

## 30. Final Product Statement

**RAG Reliability Release Gate** is a local-first AI reliability harness for chaos engineering and load testing of RAG systems.

**Context Rot RAG Chaos Lab** is the static public evidence surface.

The achievement is not the chatbot, the load generator, or the dashboard.

> The achievement is a reproducible explanation of how a RAG system degrades under controlled stress, whether it recovers safely, whether a bounded intervention materially improves it, and whether the named configuration should ship.

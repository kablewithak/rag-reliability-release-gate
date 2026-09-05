# Evaluation Constitution

**Project:** RAG Reliability Release Gate  
**Constitution version:** 1.0  
**Status:** Frozen for V1 governance  
**Governing source:** `PRD.md`  
**Related corpus constitution:** `docs/constitution/CORPUS_CONSTITUTION.md`  
**Machine-readable policy:** `datasets/controlled_cases/evaluation_policy_v1.json`

---

## 1. Purpose

This constitution freezes the V1 evaluation split, scorer contracts, evidence boundary,
leakage controls, adjudication rules, and threshold-freeze procedure.

It does not create the 60 cases. Case authoring and case-manifest hashing occur later,
under the frozen rules below.

The evaluation exists to answer:

```text
Under fixed evidence and fixed conditions:
where did the RAG path fail,
did a bounded intervention improve that failure,
did it introduce a regression,
and is the resulting release claim defensible?
```

A higher aggregate score is not sufficient evidence if a hard safety, integrity,
authority, or evidence rule fails.

---

## 2. Canonical 60-Case Split

The V1 canonical evaluation suite contains exactly:

```text
evaluation_development_case = 20
intervention_tuning_case     = 20
held_out_release_case        = 20
total                        = 60
```

The split is intentionally balanced.

Rationale:

- 20 development cases are enough to build evaluator mechanics and contain the mandatory
  6–10-case thin slice without touching tuning or held-out cases;
- 20 tuning cases provide a separate surface for intervention comparison and threshold
  calibration;
- 20 held-out cases preserve one third of the suite for final release confirmation;
- equal role sizes make before/after comparisons easier to inspect and harder to
  selectively report.

The 60-case count is a project proof-suite size, not a claim of statistical
representativeness for GitHub REST as a whole.

---

## 3. Coverage Quotas

Each 20-case role must independently satisfy both quota systems below.

### 3.1 Source-family quota per role

```text
issues                                     = 4
pull_requests                              = 4
repositories_and_repository_webhooks       = 4
actions                                    = 4
cross_cutting_rest_guidance                = 4
total                                     = 20
```

### 3.2 Scenario-class quota per role

```text
current_single_source_answerable                    = 4
current_multi_evidence_answerable                    = 4
version_freshness_disambiguation                     = 4
authority_scope_disambiguation                       = 4
must_refuse_insufficient_or_conflicting_evidence     = 4
total                                               = 20
```

The quota systems are crossed during case authoring. They do not require every possible
source-family/scenario-class cell to be populated.

No exact query, gold-fact set, or source requirement may be duplicated across roles.

---

## 4. Case Roles

### 4.1 Development cases

Development cases may be used to:

- build and debug scorer mechanics;
- verify case schemas;
- debug retrieval/context/citation instrumentation;
- exercise the thin deterministic vertical slice;
- identify ambiguous or invalid case designs;
- improve evaluator prompts or deterministic evaluators.

Development results are not release evidence.

A development case may be repaired while the evaluator is being built, but every
material case change increments its case version.

### 4.2 Tuning cases

Before intervention comparison begins, the tuning-case manifest is frozen and hashed.

Tuning cases may be used to:

- compare bounded candidate interventions;
- select the final intervention;
- calibrate numeric quality/regression thresholds;
- identify clean-case regressions.

Once intervention tuning begins:

- tuning queries may not be rewritten to favor a candidate;
- required facts/source requirements may not be changed because a candidate failed;
- case removal requires an explicit invalid-case record;
- the scorer version used for intervention comparison must be frozen.

### 4.3 Held-out release cases

Held-out cases are release-confirmation evidence.

The held-out case manifest must be versioned and hashed before final intervention
selection.

After held-out case authoring is frozen:

- no held-out case outcome may be used to change retrieval;
- no held-out case outcome may be used to change reranking;
- no held-out case outcome may be used to change context assembly;
- no held-out case outcome may be used to change prompts;
- no held-out case outcome may be used to change fallback/refusal policy;
- no held-out case outcome may be used to change model/provider selection;
- no held-out case outcome may be used to change scorer definitions;
- no held-out case outcome may be used to change numeric thresholds;
- no held-out case outcome may be used to remove an inconvenient case.

A changed held-out case creates a new evaluation-suite identity.

---

## 5. Held-Out Execution Protocol

The final held-out comparison is paired.

Required sequence:

```text
1. freeze held-out manifest + hash
2. freeze scorer registry/version
3. freeze baseline identity
4. select and freeze final intervention identity
5. freeze numeric release thresholds
6. freeze release-candidate preregistration record
7. execute baseline on all held-out cases
8. execute final intervention on all held-out cases
9. hash both raw result sets
10. only then inspect case-level held-out outcomes
11. score, adjudicate, compare, and issue verdict
```

Do not inspect held-out baseline failures before the final intervention's held-out run
has completed.

If a run is interrupted by an infrastructure/evidence-integrity failure, preserve the
failed attempt and rerun the complete affected held-out batch under the same frozen
identity. Do not selectively rerun only failed semantic cases.

Held-out release cases do not become `load_test_replay_case` merely because they are
useful examples. The PRD's one-primary-role rule remains in force.

---

## 6. Case Contract

Each canonical case must contain or resolve to the following fields.

### 6.1 Orchestration-visible fields

```text
case_id
case_version
data_role
source_family
scenario_class
criticality
query
```

`case_id` may be used for orchestration and tracing, but it is not semantic evidence.

### 6.2 Evaluator-only fields

```text
expected_response_mode
required_fact_ids
required_source_ids
allowed_source_states
forbidden_source_ids
required_api_version
required_authority_level
must_refuse_reason
gold_fact_rubric
scoring_notes
authoring_evidence
```

Allowed response modes:

```text
answer
qualified_answer
refuse
```

The exact evaluator-only representation may evolve before implementation only if these
semantics are preserved.

---

## 7. Runtime/Evaluator Boundary

Runtime RAG code may use only the evidence permitted by the PRD and runtime contracts.

Runtime code must not receive:

```text
gold_fact_rubric
required_fact_ids
required_source_ids
forbidden_source_ids
expected_response_mode
must_refuse_reason
held_out scoring outcomes
post-run failure labels
scoring_notes
```

Gold information may exist in the evaluation harness, but it must not cross into:

- retriever queries;
- reranker inputs;
- context-builder inputs;
- model/provider prompts;
- fallback decisions;
- answer-generation state.

A result produced with evaluator leakage is invalid regardless of metric improvement.

Canonical failure label:

```text
evaluation_integrity_violation
```

---

## 8. Scoring Doctrine

Scorers are layered. Do not compress retrieval, context, answer, citation, refusal,
authority, and operational evidence into one opaque score.

Scorers must declare:

```text
scorer_id
scorer_version
layer
method
required_evidence
output_contract
unscorable_behavior
```

Every metric report must include numerator/denominator or case count where applicable.
Percentages without counts are insufficient evidence for this 60-case suite.

---

## 9. Deterministic Scorers

### 9.1 Gold Evidence Recall@k

**ID:** `retrieval_gold_recall_at_k_v1`

For each answerable case:

```text
number of required source IDs present in top-k retrieval
/
number of required source IDs
```

Required evidence:

- evaluator-only `required_source_ids`;
- retrieval trace with ordered source IDs;
- frozen `k`.

If a case has no required source because it is a must-refuse case, this scorer is
`not_applicable`, not zero.

### 9.2 Required-source retrieval rate

**ID:** `required_source_retrieval_v1`

Case passes when all sources designated as required for the case are present inside the
declared retrieval boundary.

This is separate from Recall@k so a partial retrieval cannot be hidden by averaging.

### 9.3 Gold Evidence Inclusion Rate

**ID:** `context_gold_inclusion_v1`

For each answerable case:

```text
number of required source IDs included in final model context
/
number of required source IDs
```

Required evidence:

- evaluator-only required source IDs;
- context-assembly trace containing source IDs.

### 9.4 Authority/source-state compliance

**ID:** `authority_source_state_compliance_v1`

Fail when the runtime uses a source outside the case's allowed authority/source-state
boundary in a way that affects context, answer, or final citation.

The scorer must distinguish:

```text
retrieved_but_not_used
included_in_context
cited
materially_relied_upon
```

Mere retrieval of a historical or distractor record is not automatically a failure if
the experiment permits retrieval pressure and the record is correctly filtered before
material use.

### 9.5 Citation reference validity

**ID:** `citation_reference_validity_v1`

Every final citation must:

- resolve to a source record in the frozen corpus identity;
- have been available to the runtime;
- be eligible as a final citation;
- not be a synthetic overlay;
- preserve source provenance.

A syntactically well-formed but ineligible citation fails.

### 9.6 Refusal behavior

**ID:** `refusal_behavior_v1`

Uses the structured runtime response state and evaluator-only expected response mode.

Derived metrics:

```text
unsafe_answer_rate
safe_refusal_precision
false_refusal_rate
```

A must-refuse case answered materially is an unsafe-answer event even if the answer
contains uncertainty language.

### 9.7 Trace completeness

**ID:** `trace_completeness_v1`

Checks presence and schema validity of the trace evidence required to attribute:

```text
retrieval
filtering
context assembly
provider/generation
citation validation
refusal/fallback
timing/error state where applicable
```

Missing required evidence is not silently scored as a semantic failure.

### 9.8 Runtime gold-leakage check

**ID:** `runtime_gold_leakage_v1`

Checks that evaluator-only field names and evaluator-only identifiers/values do not cross
the runtime/model boundary.

A positive leakage finding invalidates the measured result.

---

## 10. Semantic Scorers

Semantic scoring is permitted only where deterministic evidence is insufficient.

The semantic judge must be:

- local or otherwise non-paid for correctness;
- identified by model/version/configuration;
- schema-constrained;
- given an explicit rubric;
- given only the evidence required for the scoring task;
- prevented from altering runtime behavior;
- reproducible enough to rerun on the same frozen artifacts;
- validated by manual adjudication before it becomes release evidence.

Invalid judge output is `unscorable`; it is not coerced into a pass.

### 10.1 Answer Fact Accuracy

**ID:** `answer_fact_accuracy_v1`

Unit: evaluator-defined required atomic facts and material answer claims.

The scorer determines whether a material answer claim is:

```text
supported_correct
unsupported
contradicted
not_applicable
```

### 10.2 Required-fact coverage

**ID:** `required_fact_coverage_v1`

For answer/qualified-answer cases:

```text
required gold facts correctly expressed
/
required gold facts
```

A fact need not match gold wording verbatim.

### 10.3 Claim Support Rate

**ID:** `claim_support_v1`

A material claim is supported only when the cited authoritative evidence actually
supports that claim under the case's required API version/source-state rules.

Derived citation metrics:

```text
claim_support_rate
citation_precision
citation_recall
citation_missing_rate
unsupported_material_claim_rate
```

Citation formatting alone never counts as support.

---

## 11. Semantic-Judge Adjudication

Before threshold freeze:

- all semantic-judge failures on development/tuning evidence are manually inspected;
- a deterministic sample of passing development/tuning judgments is manually inspected;
- material disagreement must be logged and either corrected through scorer revision or
  documented as a known scorer limitation.

For the final 20 held-out cases:

- every held-out output receives automated scoring;
- all 20 held-out outputs receive human evidence review after both baseline and final
  held-out runs are complete;
- human review may correct scorer error only through an adjudication record;
- human review may not change the query, gold evidence, threshold, intervention, or case
  membership;
- both raw automated score and adjudicated score remain preserved.

This project therefore does not claim that an LLM judge is ground truth.

---

## 12. Failure Attribution

Every degraded result has one primary failure label; secondary labels are permitted.

Primary attribution should identify the earliest evidenced causal layer where possible.

Examples:

```text
required source absent from retrieval
→ primary: retrieval_miss

required source retrieved but omitted from final context
→ primary: context_exclusion

required evidence present in context but material claim unsupported
→ primary: unsupported_answer or citation-support failure, as evidence supports

must-refuse case materially answered
→ primary: unsafe_answer

historical/synthetic source materially relied upon against policy
→ primary: authoritative_source_violation

gold/evaluator data crosses runtime boundary
→ primary: evaluation_integrity_violation
```

Do not infer a lower-layer cause without trace evidence.

---

## 13. Metric Use Classes

Evaluation outputs must distinguish:

```text
hard_integrity_gate
hard_safety_gate
hard_evidence_gate
quality_threshold
regression_gate
diagnostic_metric
```

Exact PASS/CONDITIONAL_PASS/FAIL hard-gate semantics belong to the release-gate policy.

This constitution freezes scorer meaning, not all numeric release values.

---

## 14. Threshold-Freeze Procedure

Numeric release thresholds are not chosen in this Phase 0 document.

They must be calibrated only from permitted development/tuning evidence and frozen before
held-out evaluation.

The threshold artifact must contain at least:

```text
threshold_set_id
threshold_version
created_at
project_commit_sha
corpus_snapshot_id
evaluation_suite_id
scorer_registry_hash
baseline_config_id
final_intervention_config_id
metric_id
scope
comparator
value
calibration_evidence_ids
rationale
known_limitations
```

Required freeze sequence:

```text
development mechanics complete
→ scorer registry frozen
→ tuning manifest frozen
→ bounded interventions compared on tuning only
→ final intervention selected
→ held-out manifest already frozen and hashed
→ numeric thresholds calibrated from development/tuning only
→ threshold artifact committed and hashed
→ release preregistration committed
→ held-out execution authorized
```

Forbidden:

- choosing a threshold after seeing held-out outcomes;
- changing metric definitions after seeing held-out outcomes;
- excluding a held-out failure to make a threshold pass;
- changing the final intervention after inspecting held-out outcomes and continuing to
  call the same suite held out.

Any such event is:

```text
evaluation_integrity_violation
```

---

## 15. Regression Rule

Intervention success is always checked against:

```text
targeted failure reduction
+
clean-case non-regression
```

A targeted gain does not count as an improvement if it creates an unacceptable
regression elsewhere.

The exact numeric regression tolerance is frozen with the release thresholds, not here.

Before/after reports must preserve per-case results so aggregate improvement cannot hide
a concentrated regression.

---

## 16. Case Invalidity

A case is invalid only for an evidence-backed reason such as:

- gold source identity is wrong;
- expected behavior is internally inconsistent;
- source evidence cannot support the gold rubric;
- case schema is invalid;
- frozen corpus identity makes the case impossible for reasons unrelated to system
  quality.

A model failure does not make a case invalid.

Development cases may be repaired with versioning.

After tuning/held-out freeze, invalidation requires an explicit record preserving:

```text
case_id
old_case_hash
reason
evidence
decision_time
affected_suite_identity
replacement_policy
```

No ad hoc held-out replacement is permitted after outcomes are inspected. A material
held-out case change creates a new suite version and invalidates comparisons claiming
the old suite identity.

---

## 17. Required Evidence Artifacts

When implemented, the evaluation system must be able to preserve:

```text
evaluation suite manifest + hash
role-specific case manifests + hashes
scorer registry + hash
threshold set + hash
baseline configuration identity
final intervention identity
per-case runtime traces
per-case scorer outputs
failure labels
automated semantic judgments
human adjudication log
before/after table
limitations
```

Public artifacts are separately subject to the public-evidence sanitization policy.

---

## 18. Change Control

A new ADR is required to change:

- 20/20/20 canonical split;
- source-family quota;
- scenario-class quota;
- held-out paired execution protocol;
- evaluator/runtime leakage boundary;
- scorer semantic meaning;
- manual held-out adjudication rule;
- threshold-freeze sequence.

Case wording, actual case IDs, and numeric thresholds are intentionally deferred to
their later authorized phases, but must comply with this constitution.

---

## 19. Phase 0 Effect

This constitution settles Phase 0 controlled decisions:

```text
7. exact 60-case split
8. scorer definitions and evidence requirements
9. threshold-freeze procedure
```

It does not authorize the next project phase by itself.

```text
NEXT_PHASE_AUTHORIZED=false
```

# RAG Reliability Release Gate — Project Handover Template

Use this template only at a real transition boundary. It records current, confirmed
state; it is not a second PRD.

The governing product contract is `PRD.md`. Stable operating doctrine is in
`SESSION_BRIEF.md`.

---

# RAG Reliability Release Gate — Formal Handover

## 1. Mandatory Header

```text
1. The project is a load-testing and chaos-engineering release gate for RAG, not a generic RAG app.
2. The public viewer is read-only evidence inspection, not a live testing product.
3. Real public documents are authoritative; synthetic material is a labelled chaos overlay only.
4. The goal is a defensible release verdict and failure attribution, not maximum RPS or decorative charts.
5. No paid service is required for correctness, testing, the core demo, or public evidence viewing.
6. Local load results are environment-bounded evidence, not production-capacity claims.
7. Runtime RAG code must not receive evaluator-only labels or held-out outcomes.
```

## 2. Project Identity

```text
project_name=RAG Reliability Release Gate
public_viewer=Context Rot RAG Chaos Lab
v1_max_hours=150
committed_target_hours=132
reliability_reserve_hours=18
operating_posture=local-first, provider-neutral, zero-cash-required, public-evidence-safe
local_repo_path=C:\Users\kabom\Documents\Machine Learning\Machine Learning Workspace\rag-reliability-release-gate
repository_url=<confirmed value or uncertain — verify first>
primary_branch=<confirmed value or uncertain — verify first>
```

## 3. Source-of-Truth Hierarchy

```text
1. PRD.md
2. Accepted ADRs
3. Constitutions, committed contracts, tests, reports, and release artifacts
4. Current terminal output and GitHub state
5. Latest approved formal handover
6. SESSION_BRIEF.md
7. Earlier chat
```

Where evidence conflicts, state the conflict explicitly and use the higher-ranked source.

## 4. Git and Repository State

Record only current evidence:

```text
current_branch=
working_tree=
latest_commit=
remote=
latest_pr=
branch_cleanup=
python_version=
venv_status=
```

Include the exact terminal evidence used.

## 5. Current Phase and Authorization Gate

```text
phase=
phase_status=
objective=
completed_exit_evidence=
next_authorized_slice=
what_must_not_start_yet=
```

Phase sequence:

```text
0  Governance and experiment constitution
1  Contracts and repository foundation
2  Thin deterministic vertical slice
3  Frozen corpus and provenance
4  Frozen evaluation suite and case-role manifests
5  Baseline characterization
6  Chaos profiles and negative controls
7  Intervention development and regression
8  Held-out confirmation
9  Load, saturation, fault-under-load, and recovery
10 Release gate and sanitized export
11 Static public evidence viewer
12 Final proof package and handover
```

Do not promote a later phase without committed exit evidence for the current phase.

## 6. Evidence-Maturity Ledger

Use the highest supported level only:

```text
repository_scaffolded
contracts_enforced
thin_slice_validated
public_corpus_validated
controlled_chaos_evaluated
local_load_evaluated
public_evidence_release
production_serving_validated
```

Record:

```text
highest_confirmed_evidence_level=
what_it_proves=
what_it_does_not_prove=
```

## 7. Runtime and Evaluation Integrity

Record:

```text
runtime_evidence_boundary_status=
evaluator_only_fields=
integrity_guard_status=
case_role_manifest_status=
held_out_status=
threshold_freeze_status=
known_negative_controls=
integrity_tests=
```

Hard rule:

```text
better metric + evaluation leakage = rejected result
```

Runtime must not receive gold answers, required source IDs, allowed/forbidden citation IDs,
hidden refusal labels, post-run failure labels, or held-out outcomes.

## 8. Corpus and Provenance State

Record:

```text
corpus_domain=GitHub REST API technical documentation
current_snapshot=
api_version_or_snapshot=
historical_comparison=
source_families=
extraction_method=
licensing_manifest=
corpus_manifest_hash=
persistent_real_chunk_count=
synthetic_overlay_status=
```

Synthetic overlays must remain:

```text
synthetic_overlay=true
authority_level=none
eligible_as_final_citation=false
eligible_as_gold_evidence=false
```

## 9. Evaluation State

Record:

```text
canonical_case_count=
development_case_count=
tuning_case_count=
held_out_release_case_count=
case_role_manifest_hash=
scorer_version=
threshold_policy_version=
baseline_configuration=
final_intervention_configuration=
```

List actual failure labels observed. Do not copy planned labels as observed outcomes.

## 10. Chaos State

For each executed experiment record:

```text
experiment_id=
hypothesis=
steady_state=
load_profile=
fault_profile=
blast_radius=
abort_conditions=
recovery_conditions=
expected_safe_behavior=
actual_outcome=
primary_failure_label=
```

Do not describe planned chaos profiles as executed.

## 11. Load and Recovery State

Record only environment-bounded evidence:

```text
execution_environment=
smoke=
staircase=
spike=
soak=
fault_under_load=
local_safe_operating_rate=
ttud=
operational_recovery_time=
semantic_recovery_time=
```

Never translate local RPS into production-capacity claims.

## 12. Release State

Record:

```text
release_id=
run_id=
git_commit_sha=
corpus_manifest_hash=
retrieval_configuration_hash=
model_or_provider_identifier=
provider_mode=
eval_suite_version=
case_role_manifest_hash=
chaos_profile_version=
scorer_version=
threshold_policy_version=
load_profile_id=
fault_profile_id=
result_hash=
sanitization_passed=
verdict=
```

State failed hard gates and residual risks separately from aggregate metrics.

## 13. Public Evidence Boundary

Record:

```text
sanitization_gate=
public_release_status=
viewer_status=
```

Public artifacts must not contain raw prompts, raw documents, raw model outputs, PII,
secrets, provider payloads, or internal local paths.

The viewer is static and read-only. It executes no live inference, chaos, or load tests.

## 14. Files Changed and Validation Evidence

List:

- exact files changed;
- exact tests/validation run;
- exact relevant results;
- before/after evidence where behavior changed;
- known failures or skipped evidence;
- docs-only changes explicitly marked as docs-only.

## 15. ADR and Constitution State

List accepted/current versions of:

```text
corpus constitution
evaluation constitution
chaos-testing constitution
failure taxonomy
release-gate policy
public-evidence policy
snapshot/version ADRs
architecture/scope ADRs
```

Record unresolved decisions without inventing values.

## 16. Risks, Blockers, and Non-Claims

Separate:

```text
confirmed risks
active blockers
open uncertainties
non-claims
```

If a fact cannot be confirmed, write:

```text
uncertain — verify first
```

## 17. Next Safe Action

Provide exactly one immediate next slice:

```text
NEXT_GATE=
objective=
required_inputs=
expected_files=
validation_gate=
stop_condition=
```

## 18. GitOps Handover

When implementation changes are pending, include:

```text
git status before staging
exact git add paths
git status after staging
semantic commit
push
PR title/description
after-merge sync/delete commands
```

Never invent branch names, commit hashes, PR numbers, remotes, or successful merge state.

## 19. Quick Resume Checklist

```text
- Read PRD.md.
- Read accepted ADRs and relevant constitutions.
- Read this handover.
- Run git status.
- Run git --no-pager log -1 --oneline when commits exist.
- Confirm current branch, remote, and phase.
- Confirm the runtime/evaluator boundary.
- Confirm corpus/source-state and synthetic-overlay roles.
- Confirm case-role and held-out integrity.
- Confirm latest validation evidence.
- Do not build the viewer before sanitized release evidence exists.
- Do not overclaim local load evidence.
- Continue only from the recorded NEXT_GATE.
```

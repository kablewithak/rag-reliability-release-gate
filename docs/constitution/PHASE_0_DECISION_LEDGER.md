# Phase 0 Controlled Decision Ledger

**Phase:** 0 — Governance and experiment constitution  
**Purpose:** Track the decisions that must be frozen before implementation proceeds.  
**Rule:** `SETTLED_BY_PRD` means the governing PRD fixes the decision. `SETTLED` means an
accepted constitution/ADR freezes it. `DEFERRED_TO_PHASE_X` means Phase 0 deliberately
defers the implementation-specific value to the named evidence-producing phase.

| # | Decision | Status | Current evidence / required output |
|---:|---|---|---|
| 1 | Final repository name and path | SETTLED_BY_PRD | `rag-reliability-release-gate`; local path under the user's Machine Learning Workspace |
| 2 | Exact GitHub source families | SETTLED | Corpus Constitution v1 + ADR-0002 |
| 3 | Exact current source snapshot / API version | SETTLED | Target `2026-03-10`; pinned upstream identities in `source_snapshot_v1.json` |
| 4 | Exact historical comparison snapshot / version | SETTLED | Comparison `2022-11-28`; pinned upstream identity |
| 5 | Extraction and normalization method | SETTLED | Corpus Constitution v1 |
| 6 | Source licensing and attribution manifest format | SETTLED | Corpus Constitution v1 |
| 7 | Exact 60-case split: development / tuning / held-out | SETTLED | Evaluation Constitution v1: 20 / 20 / 20 |
| 8 | Scorer definitions and evidence requirements | SETTLED | Evaluation Constitution v1 + `evaluation_policy_v1.json` |
| 9 | Threshold-freeze procedure | SETTLED | Development/tuning calibration only; freeze before held-out |
| 10 | Initial baseline configuration | DEFERRED_TO_PHASE_5 | Must be frozen before baseline characterization; no Phase 0 evidence justifies exact runtime values |
| 11 | Intervention-ablation order | DEFERRED_TO_PHASE_7 | PRD constrains bounded B0/I1/I2/I3/I4/IF ladder; exact evidence-backed ladder frozen before intervention comparison |
| 12 | Resource telemetry implementation | DEFERRED_TO_PHASE_9 | Freeze with measured load/environment implementation |
| 13 | Minimal local HTTP wrapper for load tests | DEFERRED_TO_PHASE_9 | Decide from diagnostic load need; not assumed in Phase 0 |
| 14 | Exact chaos-profile manifest | SETTLED | Chaos-Testing Constitution v1 + ADR-0004 + `chaos_profile_manifest_v1.json` |
| 15 | Execution-environment capture format | DEFERRED_TO_PHASE_9 | Freeze before release-bearing load runs |
| 16 | Public release licensing and evidence retention policy | SETTLED | Public Evidence Policy v1 + ADR-0005 |

## Phase 0 Exit Evidence

Committed Phase 0 governance requires:

- governing PRD and project-scope ADR;
- corpus constitution and snapshot ADR;
- evaluation constitution and split/scoring policy;
- chaos-testing constitution and profile manifest;
- release-gate policy;
- public-evidence policy;
- deliberate deferral records for implementation-specific decisions whose values require later evidence.

With ADR-0005 and the two policies committed, Phase 0 governance is complete.

```text
PHASE_0_STATUS=COMPLETE
NEXT_PHASE_AUTHORIZED=true
NEXT_PHASE=1
NEXT_GATE=IMPLEMENT_TYPED_CONTRACTS_AND_REPOSITORY_FOUNDATION
```

No runtime RAG behavior, corpus ingestion, chaos execution, load execution, or viewer work
is implied by Phase 0 completion.

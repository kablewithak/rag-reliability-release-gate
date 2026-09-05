# Phase 0 Controlled Decision Ledger

**Phase:** 0 — Governance and experiment constitution  
**Purpose:** Track the decisions that must be frozen before implementation proceeds.  
**Rule:** A status of `SETTLED_BY_PRD` means the governing PRD already fixes the decision.
`OPEN` means implementation must not invent a value.

| # | Decision | Status | Current evidence / required output |
|---:|---|---|---|
| 1 | Final repository name and path | SETTLED_BY_PRD | `rag-reliability-release-gate`; local path under the user's Machine Learning Workspace |
| 2 | Exact GitHub source families | OPEN | Freeze in corpus constitution / snapshot ADR |
| 3 | Exact current source snapshot / API version | OPEN | Freeze in snapshot ADR |
| 4 | Exact historical comparison snapshot / version | OPEN | Freeze in snapshot ADR |
| 5 | Extraction and normalization method | OPEN | Freeze in corpus constitution / methodology |
| 6 | Source licensing and attribution manifest format | OPEN | Freeze in corpus constitution |
| 7 | Exact 60-case split: development / tuning / held-out | OPEN | Freeze in evaluation constitution |
| 8 | Scorer definitions and evidence requirements | OPEN | Freeze in evaluation constitution |
| 9 | Threshold-freeze procedure | OPEN | Freeze in evaluation constitution / release policy |
| 10 | Initial baseline configuration | OPEN | Freeze before baseline characterization |
| 11 | Intervention-ablation order | PARTIALLY_SETTLED | PRD requires bounded B0/I1/I2/I3/I4/IF-style ladder; exact final ladder remains open |
| 12 | Resource telemetry implementation | OPEN | Freeze before load implementation |
| 13 | Minimal local HTTP wrapper for load tests | OPEN | Decide only if required for diagnostic load evidence |
| 14 | Exact chaos-profile manifest | PARTIALLY_SETTLED | PRD names required profile families; exact frozen manifest remains open |
| 15 | Execution-environment capture format | OPEN | Freeze before meaningful load/release runs |
| 16 | Public release licensing and evidence retention policy | OPEN | Freeze in public-evidence policy |

## Phase 0 Exit Condition

Phase 0 is complete only when:

- the governing PRD and accepted scope ADR are committed;
- the corpus constitution freezes source policy, provenance, snapshot/version, extraction,
  and licensing rules;
- the evaluation constitution freezes case roles, scorer evidence, leakage controls, and
  threshold-freeze procedure;
- the chaos-testing constitution freezes experiment contracts and named profiles;
- the release-gate policy freezes hard-gate semantics;
- the public-evidence policy freezes sanitization, licensing, retention, and public-release
  boundaries;
- unresolved implementation choices are either explicitly deferred to their correct later
  phase or frozen with evidence.

Until then:

```text
NEXT_PHASE_AUTHORIZED=false
```

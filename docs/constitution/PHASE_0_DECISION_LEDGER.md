# Phase 0 Controlled Decision Ledger

**Phase:** 0 — Governance and experiment constitution  
**Purpose:** Track the decisions that must be frozen before implementation proceeds.  
**Rule:** A status of `SETTLED_BY_PRD` means the governing PRD already fixes the decision.
`SETTLED` means an accepted constitution/ADR freezes the decision. `OPEN` means
implementation must not invent a value.

| # | Decision | Status | Current evidence / required output |
|---:|---|---|---|
| 1 | Final repository name and path | SETTLED_BY_PRD | `rag-reliability-release-gate`; local path under the user's Machine Learning Workspace |
| 2 | Exact GitHub source families | SETTLED | Corpus Constitution v1 + ADR-0002: authored cross-cutting REST guidance plus `issues`, `pull_requests`, `repositories_and_repository_webhooks`, `actions` OpenAPI families |
| 3 | Exact current source snapshot / API version | SETTLED | `github/docs@ec3629a...`; `github/rest-api-description@3cef12e...`; target API `2026-03-10` |
| 4 | Exact historical comparison snapshot / version | SETTLED | Same frozen OpenAPI repository snapshot; comparison API `2022-11-28` |
| 5 | Extraction and normalization method | SETTLED | Commit/version-pinned acquisition; fail-closed authored-Markdown normalization; deterministic per-operation OpenAPI normalization |
| 6 | Source licensing and attribution manifest format | SETTLED | GitHub Docs content `CC-BY-4.0`; REST API description `MIT`; source ledger JSONL + frozen snapshot JSON |
| 7 | Exact 60-case split: development / tuning / held-out | SETTLED | Evaluation Constitution v1 + ADR-0003: 20 development / 20 tuning / 20 held-out |
| 8 | Scorer definitions and evidence requirements | SETTLED | Layered deterministic + semantic scorer registry frozen in Evaluation Constitution v1 and `evaluation_policy_v1.json` |
| 9 | Threshold-freeze procedure | SETTLED | Calibrate on development/tuning only; freeze scorer/suite/config/threshold identities before paired held-out execution |
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

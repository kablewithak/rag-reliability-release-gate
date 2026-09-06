# Phase 2B Thin-Slice Development Fixtures

These fixtures exist only to prove the deterministic end-to-end evaluation path required
by Phase 2 of `PRD.md`.

They are **development-only** and **not release evidence**. They do not replace the Phase 3
corpus ingestion pipeline or the frozen 60-case evaluation suite.

## Source boundary

- Source repository: `github/docs`
- Frozen commit: `ec3629a841129ae28189d7bb2274a7b3d40c5095`
- Eligible source area: the Phase 0 GitHub REST authored-guidance prefixes
- License: CC-BY-4.0
- Target API version/snapshot metadata: `2026-03-10`
- Data role: `unit_fixture`

Each source fixture contains a short excerpt from one pinned public document plus a
`RealSourceRecord` manifest. The excerpt SHA-256 is validated before execution.

## Evaluation boundary

The suite contains ten development-only cases:

- eight answerable single-source cases;
- two must-refuse cases with no supporting evidence in this mini-corpus.

Replay-provider fixtures are stored separately from evaluator-owned case definitions.
The runtime receives only `RuntimeCaseInput(case_id, query)`.

## Non-claims

This fixture set does not establish retrieval quality, corpus coverage, held-out quality,
production readiness, load capacity, chaos resilience, or a release verdict.

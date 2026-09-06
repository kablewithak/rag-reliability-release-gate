# Phase 3A — Frozen Source Acquisition and Operation Catalog

Phase 3A does **not** ingest or chunk the production corpus.

It performs three custody tasks first:

1. acquire exactly pinned GitHub Docs and bundled OpenAPI files;
2. verify each file against its expected Git blob SHA-1 before caching it;
3. generate a candidate operation catalog for the four frozen semantic endpoint families.

The operation catalog is explicitly `candidate_only`, `ingestion_authorized=false`, and
`release_eligible=false`. A later review must freeze an explicit operation allowlist before
corpus ingestion is accepted.

Raw upstream bytes are written only below `datasets/source_documents/_upstream_cache/`, which
is gitignored. The committed acquisition receipt and operation catalog contain hashes and
metadata only, not raw upstream content.

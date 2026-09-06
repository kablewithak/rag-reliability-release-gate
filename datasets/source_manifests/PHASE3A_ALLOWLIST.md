# Phase 3A Explicit Operation Allowlist

This file records the human-reviewed freeze of the Phase 3A GitHub REST OpenAPI operation core.

## Evidence chain

The allowlist is bound to:

- snapshot `github_rest_v1_2026_09_05`;
- the pinned current and historical OpenAPI files in `source_snapshot_v1.json`;
- the deterministic operation shortlist whose SHA-256 is
  `26ca1daa07f469260c0912017c415f4df71b2518f9223ee396ad52144877b335`.

The shortlist was produced only after acquisition custody, operation identity comparison,
contract-delta comparison, contract-change review, and substantive-change tiering.

## Selection decision

The frozen allowlist contains 20 operations: five from each semantic family.
All eight direct contract changes from the shortlist remain included. Tier B operations fill
family gaps so that every frozen evaluation family has a version-aware OpenAPI core.

The Actions family intentionally includes org/repository registration-token and removal-token
pairs. This is accepted scope-pair redundancy: it supports later authority/scope and stale-contract
experiments. It must not be presented as broad Actions semantic coverage.

## Authorization boundary

`ingestion_authorized=true` means only that Phase 3 corpus ingestion may consume these exact
allowlisted operations from the exact pinned snapshot. It does not authorize mutable refs,
additional operations, arbitrary GitHub REST content, baseline execution, held-out evaluation,
chaos/load execution, release eligibility, or public release.

Any change to the snapshot identity, source shortlist hash, operation membership, or family
assignment requires a new allowlist version and a new authorization receipt.

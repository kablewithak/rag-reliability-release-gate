# Phase 3A corpus snapshot erratum — 2026-09-06

## Status

Accepted correction to frozen metadata. This does not change the selected repository,
commit, API versions, source path, authority, source state, or corpus role.

## Finding

The historical GitHub REST OpenAPI blob SHA-1 recorded for
`descriptions/api.github.com/api.github.com.2022-11-28.yaml` at
`github/rest-api-description@3cef12e8a02d612ad032473d4fb87266f2befeae`
was transcribed incorrectly.

Recorded value:

`88a3cc7326d6fd3968042dde112d1c4c838af5bc`

Verified GitHub blob value:

`88a3cc3fe7e4ddbfd1d2fdbd4e6dc9bbd8e3c9b8`

## Evidence and correction

GitHub's repository contents identity for that exact path and pinned commit reports
`88a3cc3fe7e4ddbfd1d2fdbd4e6dc9bbd8e3c9b8`.

The correction is applied to:

- `datasets/source_manifests/source_snapshot_v1.json`
- `datasets/source_manifests/phase3a_source_selection_v1.json`

A regression test now requires the Phase 3A OpenAPI selection identities to match the
frozen snapshot descriptor.

## Non-changes

No source bytes are accepted because of this document alone. Acquisition still computes
the Git blob identity from fetched bytes and fails closed on mismatch. SHA-256 content
digests remain required in acquisition receipts.

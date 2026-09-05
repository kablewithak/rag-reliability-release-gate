# Public Evidence Policy

**Project:** RAG Reliability Release Gate  
**Policy version:** 1.0  
**Status:** Frozen for V1 governance  
**Repository posture:** Public  
**Governing source:** `PRD.md`  
**Machine-readable policy:** `docs/constitution/public_evidence_policy_v1.json`

---

## 1. Purpose

This policy defines what may leave the internal experiment/evidence boundary and enter:

- the public GitHub repository;
- a public release package;
- the future Context Rot RAG Chaos Lab viewer.

The repository is public, therefore any committed runtime evidence is treated as
publicly disclosed at commit time.

Public evidence must be useful enough to support engineering claims while remaining
sanitized, attributable, minimal, and reproducible.

---

## 2. Public-by-Default Repository Rule

Code, governance documents, manifests, schemas, tests, sanitized reports, and public
source provenance may be committed.

Runtime artifacts are **not** public-by-default.

Before runtime evidence is committed or viewer-consumed, it must pass the sanitization
gate defined here.

The current local `evidence_vault/` remains an internal evidence workspace unless a
specific artifact has been sanitized and exported through the public release process.

Do not remove ignore protections merely to make evidence visible.

---

## 3. Publicly Allowed Artifact Classes

Allowed when sanitized:

```text
release identity and hashes
configuration identifiers
corpus/source manifest metadata
public upstream source URLs and repository identities
license/attribution records
aggregate evaluation metrics with counts
per-case IDs, roles, scenario classes, and failure labels
sanitized before/after tables
sanitized metadata-safe trace samples
chaos/load profile identities
achieved local load measurements with environment limitation
recovery measurements
TTUD
remediation backlog
limitations and non-claims
bounded sanitized excerpts when needed to explain a failure
```

A sanitized excerpt is a minimal evidence fragment, not a full raw prompt/document/output.

---

## 4. Publicly Prohibited Content

Never publish:

```text
secrets
API keys
access tokens
cookies
credential material
private repository credentials
PII
customer/private data
raw full prompts
raw full source documents
raw full model outputs
provider request/response envelopes
provider debug payloads
internal absolute local paths
environment variables containing secrets
hidden evaluator-only gold fields
private adjudicator notes containing prohibited content
```

Public-source provenance is not considered sensitive, but copying a complete raw source
document into the public evidence package is still prohibited by project policy.

---

## 5. Bounded Sanitized Excerpts

A public report may include a bounded excerpt from an otherwise prohibited raw runtime
artifact only when all conditions hold:

1. the excerpt is necessary to understand a named failure;
2. it contains no secret, PII, credential, private path, provider envelope, or evaluator-only field;
3. it is minimal rather than the full artifact;
4. it is explicitly labelled `sanitized_excerpt`;
5. the originating artifact is referenced by internal hash, not published raw;
6. source-derived text retains appropriate attribution;
7. the excerpt passes the same sanitization checks as the release package.

This exception does not permit publishing raw full prompts, documents, or model outputs.

---

## 6. Public Case Representation

Public case evidence may contain:

```text
case_id
case_role
source_family
scenario_class
criticality
result status
metric values
failure labels
sanitized explanation
source IDs / public source URLs
```

Do not publish evaluator-only:

```text
gold_fact_rubric
hidden expected response
hidden refusal reason
scoring notes
forbidden-source hints
held-out optimization information
```

A release may publish post-evaluation ground-truth summaries only when doing so cannot
affect an active held-out suite. Once published, those exact cases are no longer suitable
as secret held-out evidence for a future suite unless a new independent hidden set is
created.

---

## 7. Trace Publication

Internal traces may contain richer evidence than public traces.

Public trace samples are metadata-safe projections.

Allowed trace fields include, where sanitized:

```text
trace_id
release_id
case_id
profile_id
stage names
timings
source IDs
authority/source-state labels
retrieval ranks
context inclusion flags
citation validation status
refusal/error enums
failure labels
resource measurements
```

Do not publish raw prompt/context/model/provider bodies.

---

## 8. Source Licensing and Attribution

For source-derived evidence, preserve the corpus constitution's licensing metadata.

Current V1 source families include:

```text
github/docs documentation content -> CC-BY-4.0
github/rest-api-description        -> MIT
```

Public evidence must retain sufficient upstream provenance to identify the source
repository, frozen version/commit, and applicable license.

The project does not relicense upstream material merely by including metadata or a
sanitized excerpt.

---

## 9. Sanitization Gate

Every candidate public release artifact set must be scanned and reviewed before commit
or viewer ingestion.

The sanitization result must record:

```text
sanitization_run_id
policy_version
input_artifact_hashes
scanner_version
prohibited_field_scan
secret_pattern_scan
absolute_path_scan
PII_review_status
raw_payload_policy_check
license_attribution_check
manual_review_status
output_artifact_hashes
finding_count
passed
```

Release requirement:

```text
finding_count == 0
passed == true
```

A false positive may be resolved only with a documented review record. Do not silently
suppress it.

---

## 10. Internal Evidence Retention

Data minimization is the default.

### Never persist by default

```text
secrets
credentials
cookies
unnecessary raw provider payloads
unnecessary PII
```

### Active-run retention

Unsanitized experiment traces and raw local artifacts may be retained only while needed
for:

```text
failure attribution
scorer/adjudication review
release reconstruction
sanitization verification
```

### After a release package is frozen

Keep:

```text
hashes
configuration identity
manifest identity
metric outputs
failure labels
metadata-safe traces
adjudication records that contain no prohibited content
sanitized public release artifacts
```

Delete unsanitized raw artifacts when they are no longer necessary to reproduce or
audit the accepted evidence.

If deletion would destroy the only evidence needed to reproduce a claim, create and
verify the sanitized/metadata-safe replacement first.

No fixed statutory retention period is claimed by this engineering policy.

---

## 11. Public Artifact Retention

Sanitized published release artifacts are versioned evidence.

They should not be silently overwritten.

When superseded:

```text
retain prior release identity
mark status=superseded
link successor release_id
preserve verdict and limitations as originally issued
```

A failed historical release may remain public if sanitized. This is useful engineering
evidence and must not be rewritten to appear successful.

---

## 12. Public Viewer Boundary

The Context Rot RAG Chaos Lab may be built only after a valid sanitized release artifact
exists.

The viewer is:

```text
static
read-only
artifact-driven
```

It may not:

- execute inference;
- inject faults;
- run load tests;
- access internal raw traces;
- hold provider credentials;
- require a private database;
- mutate release evidence.

If a viewer needs data not present in the sanitized release package, the release export
must be improved first. The viewer may not reach back into internal evidence as a
shortcut.

---

## 13. Public Claims

Allowed claim shape:

```text
Under release <id>,
using corpus <hash>,
configuration <hash>,
evaluation suite <version>,
chaos/load profile <version>,
and environment <id>,
the system received <verdict>.
```

Required limitations accompany environment-bounded load evidence.

Forbidden claim inflation includes:

```text
production ready
production capacity = local measured RPS
universally reliable
secure against all prompt injection
customer-data validated
globally load tested
```

unless later independent evidence actually establishes such a claim.

---

## 14. Public Repository Incident Rule

Because the repository is public, a secret committed to Git history must be treated as
disclosed.

If prohibited sensitive material is committed:

1. stop publication work;
2. revoke/rotate affected credentials when applicable;
3. preserve an incident record without repeating the secret;
4. remove the material from active public surfaces;
5. assess whether history rewriting is required;
6. rerun sanitization before publication resumes.

Deleting the visible file alone is not considered credential remediation.

---

## 15. Change Control

A new ADR is required to change:

- prohibited public content classes;
- raw-evidence publication boundary;
- public trace policy;
- public viewer isolation rule;
- sanitization as a hard gate;
- public artifact versioning/overwrite rule;
- source-attribution requirement.

Implementation of scanners may evolve as long as the policy semantics remain unchanged.

---

## 16. Phase 0 Effect

This policy settles controlled decision:

```text
16. public release licensing and evidence retention policy
```

It also establishes the public-repository operating boundary for all later phases.

"""Phase 4C HELD_OUT canonical-case candidate authoring."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    RefusalReason,
    ResponseMode,
    ScenarioClass,
    SourceState,
)
from rag_reliability.contracts.evaluation import (
    EvaluationCase,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.authoring_dossier import (
    Phase4AuthoringClusterReview,
    Phase4AuthoringDossier,
    Phase4AuthoringEvidence,
)
from rag_reliability.evaluation.refusal_corpus_review import (
    Phase4RefusalSemanticReview,
)

_DOSSIER_PATH = Path("artifacts") / "development" / "phase4c_authoring_dossier_v1.json"

_REFUSAL_REVIEW_PATH = (
    Path("artifacts") / "development" / "phase4c_refusal_full_corpus_review_v1.json"
)

_SUITE_JSON_PATH = Path("artifacts") / "development" / "phase4c_held_out_cases_v1.json"

_SUITE_MARKDOWN_PATH = Path("artifacts") / "development" / "phase4c_held_out_cases_v1.md"


class HeldOutCaseSpec(ContractModel):
    """Human-authored semantic intent before evidence resolution."""

    case_id: NonEmptyStr
    cluster_id: NonEmptyStr
    scenario_class: ScenarioClass
    query: NonEmptyStr

    gold_fact_rubric: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    evidence_terms: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    forbid_historical: bool = False

    refusal_review_intent_id: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_spec(
        self,
    ) -> Self:
        is_refusal = (
            self.scenario_class is ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        )

        if is_refusal:
            if self.gold_fact_rubric:
                raise ValueError("refusal spec cannot carry gold facts")

            if self.refusal_review_intent_id is None:
                raise ValueError("refusal spec requires semantic-review intent")

        if not is_refusal:
            if not self.gold_fact_rubric:
                raise ValueError("answerable spec requires gold facts")

            if self.refusal_review_intent_id is not None:
                raise ValueError("answerable spec cannot carry refusal-review intent")

        if (
            self.scenario_class is ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
            and len(self.evidence_terms) < 2
        ):
            raise ValueError("multi-evidence spec requires at least two evidence selectors")

        if len(self.evidence_terms) != len(set(self.evidence_terms)):
            raise ValueError("evidence selector terms must be unique")

        return self


class HeldOutCaseRecord(ContractModel):
    """One canonical case plus its frozen cluster identity."""

    cluster_id: NonEmptyStr
    case: EvaluationCase


class Phase4HeldOutCaseSuite(ContractModel):
    """HeldOut-only candidate suite before Phase 4 case freeze."""

    suite_version: Literal["phase4c-held-out-cases-v1"] = "phase4c-held-out-cases-v1"

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256
    review_markdown_sha256: Sha256

    case_count: Literal[18] = 18
    cluster_count: Literal[9] = 9

    current_single_source_count: Literal[5] = 5

    current_multi_evidence_count: Literal[4] = 4

    version_freshness_count: Literal[4] = 4

    authority_scope_count: Literal[2] = 2

    must_refuse_count: Literal[3] = 3

    held_out_case_authoring_complete: Literal[True] = True

    held_out_suite_frozen: Literal[False] = False

    held_out_outcomes_exposed: Literal[False] = False

    baseline_authorized: Literal[False] = False

    release_eligible: Literal[False] = False

    records: tuple[
        HeldOutCaseRecord,
        ...,
    ] = Field(
        min_length=18,
        max_length=18,
    )

    @model_validator(mode="after")
    def validate_suite(
        self,
    ) -> Self:
        case_ids = tuple(record.case.case_id for record in self.records)

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("held_out case IDs must be unique")

        queries = tuple(record.case.query for record in self.records)

        if len(queries) != len(set(queries)):
            raise ValueError("held_out queries must be unique")

        if any(record.case.data_role is not EvaluationRole.HELD_OUT for record in self.records):
            raise ValueError("suite may only contain HELD_OUT cases")

        scenario_counts = Counter(record.case.scenario_class for record in self.records)

        expected_scenarios = Counter(
            {
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 5,
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 4,
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 4,
                ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 2,
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 3,
            }
        )

        if scenario_counts != expected_scenarios:
            raise ValueError("HELD_OUT scenario quotas drifted")

        family_counts = Counter(record.case.source_family for record in self.records)

        expected_families = Counter(
            {
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 6,
                EvaluationSourceFamily.ACTIONS: 2,
                EvaluationSourceFamily.ISSUES: 4,
                EvaluationSourceFamily.PULL_REQUESTS: 2,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 4,
            }
        )

        if family_counts != expected_families:
            raise ValueError("HELD_OUT family quotas drifted")

        cluster_counts = Counter(record.cluster_id for record in self.records)

        if len(cluster_counts) != 9:
            raise ValueError("HELD_OUT suite must use 9 clusters")

        if any(count != 2 for count in cluster_counts.values()):
            raise ValueError("each HELD_OUT cluster requires exactly two cases")

        for record in self.records:
            runtime = record.case.to_runtime_input().model_dump()

            if set(runtime) != {
                "case_id",
                "query",
            }:
                raise ValueError("gold fields leaked through runtime case projection")

        return self


class Phase4HeldOutCaseError(ValueError):
    """HELD_OUT case candidate cannot be safely materialized."""


CASE_SPECS: tuple[
    HeldOutCaseSpec,
    ...,
] = (
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-best-practices-"
            "poll-cache"
        ),
        cluster_id=(
            "guidance:docs-best-practices"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "An integration cannot use webhooks and must poll the "
            "GitHub REST API. Under the frozen current best-practices "
            "guidance, how should it control polling frequency and "
            "x-poll-interval, use conditional authenticated requests, "
            "and keep requests stable so unchanged resources are more "
            "likely to return HTTP 304 without consuming primary "
            "rate-limit budget?"
        ),
        gold_fact_rubric=(
            (
                "When polling is unavoidable, poll only as often as "
                "needed on a fixed schedule."
            ),
            (
                "If x-poll-interval is returned, wait at least that "
                "many seconds before polling the same endpoint again."
            ),
            (
                "Correctly authorized conditional requests that return "
                "HTTP 304 do not count against the primary rate limit."
            ),
            (
                "Request only the data needed and keep the request "
                "stable and specific so unchanged data is more likely "
                "to return HTTP 304."
            ),
            (
                "Repeated polls of the same data should use the same "
                "parameters, because changing page size, page number, "
                "or filters produces a different response and etag."
            ),
        ),
        evidence_terms=(
            "## Avoid polling",
            "## Make requests that can be cached",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-best-practices-"
            "repeated-errors"
        ),
        cluster_id=(
            "guidance:docs-best-practices"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "A polling integration repeatedly receives HTTP 404 from "
            "a resource that the operator believes exists. What does "
            "the frozen current best-practices guidance say about the "
            "possible authorization meaning of 404 and how the "
            "integration should behave instead of continually retrying?"
        ),
        gold_fact_rubric=(
            (
                "A 404 does not always mean the resource is absent, "
                "because GitHub may return 404 instead of 403 for some "
                "private resources when credentials lack access."
            ),
            (
                "The integration should first verify that the 404 is "
                "not caused by authentication or authorization."
            ),
            (
                "After credentials are confirmed, the integration "
                "should wait much longer before checking again or retry "
                "only when there is reason to believe the resource exists."
            ),
            (
                "Repeatedly requesting a missing resource wastes rate "
                "limit and can trigger a secondary rate limit."
            ),
        ),
        evidence_terms=(
            "## Do not ignore errors",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-getting-started-"
            "request-contract"
        ),
        cluster_id=(
            "guidance:docs-getting-started"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "A developer is constructing a REST request from the "
            "current GitHub guidance. Which request elements are always "
            "present, how do path, body, and query parameters differ, "
            "and which version and media-type headers does the guidance "
            "describe?"
        ),
        gold_fact_rubric=(
            (
                "Every REST API request includes an HTTP method "
                "and a path."
            ),
            (
                "Path parameters modify the endpoint path and are "
                "required where the endpoint defines them."
            ),
            (
                "Body parameters send additional data and may be "
                "optional or required depending on the endpoint."
            ),
            (
                "Query parameters control what data is returned and "
                "are usually optional."
            ),
            (
                "The X-GitHub-Api-Version header specifies the REST "
                "API version for the request."
            ),
            (
                "Most REST endpoints recommend Accept: "
                "application/vnd.github+json."
            ),
        ),
        evidence_terms=(
            "### Parameters",
            "## About requests to the REST API",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-getting-started-"
            "request-inspection"
        ),
        cluster_id=(
            "guidance:docs-getting-started"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "Using the frozen getting-started guidance, explain the "
            "key method/header controls for making requests with GitHub "
            "CLI or curl and how a caller can inspect the returned HTTP "
            "status code and headers."
        ),
        gold_fact_rubric=(
            (
                "GitHub CLI uses the api subcommand and allows the "
                "HTTP method to be supplied with --method."
            ),
            (
                "The examples send Accept and X-GitHub-Api-Version "
                "headers."
            ),
            (
                "For curl, the request method can be supplied with "
                "--request or -X and the full API URL with --url."
            ),
            (
                "An authenticated curl request sends the access token "
                "in the Authorization header."
            ),
            (
                "The --include or --i option can be used to display "
                "the response status code and headers."
            ),
        ),
        evidence_terms=(
            "### 4. Make a request with GitHub CLI",
            "### About the response code and headers",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-timezones-"
            "current-precedence"
        ),
        cluster_id=(
            "guidance:docs-timezones"
        ),
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy runbook says GitHub always generates request "
            "timestamps in UTC unless the timestamp itself contains an "
            "offset. Under the frozen current timezone guidance, what "
            "precedence is actually used for applicable API calls when "
            "determining timezone information?"
        ),
        gold_fact_rubric=(
            (
                "An explicitly supplied ISO 8601 timestamp with "
                "timezone information has highest priority."
            ),
            (
                "If an explicit timestamp does not determine it, a "
                "Time-Zone header can provide the timezone."
            ),
            (
                "Without a Time-Zone header, an authenticated request "
                "uses the authenticated user's last known timezone."
            ),
            (
                "UTC is the fallback when no other timezone information "
                "is available."
            ),
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-timezones-"
            "last-known-refusal"
        ),
        cluster_id=(
            "guidance:docs-timezones"
        ),
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "No Time-Zone header or explicit timezone was provided, "
            "and I have no observed user state. What exact last-known "
            "timezone will GitHub use for this authenticated user?"
        ),
        refusal_review_intent_id=(
            "heldout-last-known-timezone"
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-actions-remove-token-"
            "authority"
        ),
        cluster_id=(
            "openapi-pair:actions/"
            "create-remove-token-for-org"
        ),
        scenario_class=(
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION
        ),
        query=(
            "Under the current organization self-hosted-runner "
            "remove-token operation, what organization authority must "
            "the authenticated user have and what organization scope is "
            "required for OAuth tokens or classic personal access tokens?"
        ),
        gold_fact_rubric=(
            (
                "The authenticated user must have admin access to "
                "the organization."
            ),
            (
                "OAuth tokens and classic personal access tokens need "
                "the admin:org scope."
            ),
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-actions-remove-token-"
            "contract"
        ),
        cluster_id=(
            "openapi-pair:actions/"
            "create-remove-token-for-org"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current GitHub REST operation that creates a "
            "self-hosted-runner remove token for an organization, what "
            "HTTP method and endpoint are used, how long is the token "
            "valid, and what successful status is documented?"
        ),
        gold_fact_rubric=(
            (
                "The operation uses POST "
                "/orgs/{org}/actions/runners/remove-token."
            ),
            "The token expires after one hour.",
            "The successful response status is HTTP 201.",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-blocked-by-404-refusal"
        ),
        cluster_id=(
            "openapi-pair:issues/"
            "add-blocked-by-dependency"
        ),
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "An Add blocked-by dependency request returns HTTP 404, "
            "but I have no further request, resource, credential, or "
            "response details. Which exact resource or access condition "
            "caused this particular failure?"
        ),
        refusal_review_intent_id=(
            "heldout-blocked-by-failure-cause"
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-blocked-by-contract"
        ),
        cluster_id=(
            "openapi-pair:issues/"
            "add-blocked-by-dependency"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current Add blocked-by dependency operation, "
            "what method and endpoint are used, which request-body "
            "field is required, what does that field identify, and "
            "what successful response status is documented?"
        ),
        gold_fact_rubric=(
            (
                "The operation uses POST "
                "/repos/{owner}/{repo}/issues/{issue_number}/"
                "dependencies/blocked_by."
            ),
            "The request body requires issue_id.",
            (
                "issue_id identifies the issue that blocks the "
                "current issue."
            ),
            "The successful response status is HTTP 201.",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-issues-update-"
            "assignee-freshness"
        ),
        cluster_id=(
            "openapi-pair:issues/update"
        ),
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy Update issue request schema contains a singular "
            "assignee field marked as closing down. Under the frozen "
            "current 2026-03-10 request contract, is that singular "
            "assignee field still present, and what plural field is "
            "available for replacing or clearing assignees?"
        ),
        gold_fact_rubric=(
            (
                "The current request schema does not contain the "
                "legacy singular assignee field."
            ),
            (
                "The current request schema contains the plural "
                "assignees field."
            ),
            (
                "Passing one or more logins to assignees replaces the "
                "set of assignees."
            ),
            (
                "Passing an empty assignees array clears all assignees."
            ),
        ),
        evidence_terms=(
            (
                "Issue owners and users with push access or "
                "Triage role can edit an issue."
            ),
        ),
        forbid_historical=True,
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-issues-update-"
            "suggestions"
        ),
        cluster_id=(
            "openapi-pair:issues/update"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "For the current Update issue contract, who may edit an "
            "issue, and how do request-side suggestion metadata and "
            "the response-side suggestions object represent proposed "
            "or ignored changes?"
        ),
        gold_fact_rubric=(
            (
                "Issue owners and users with push access or the "
                "Triage role can edit an issue."
            ),
            (
                "Suggestible request fields can carry metadata such "
                "as confidence, rationale, and suggest."
            ),
            (
                "When suggest is true, the requested change is stored "
                "as a pending suggestion for human review rather than "
                "being applied directly."
            ),
            (
                "The response suggestions object reports pending "
                "suggestions for suggestible fields touched by the "
                "request."
            ),
            (
                "Items marked ignored echo request inputs that were "
                "not persisted as pending suggestions."
            ),
        ),
        evidence_terms=(
            (
                "Issue owners and users with push access or "
                "Triage role can edit an issue."
            ),
            "Pending suggestions for each suggestible field",
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-pulls-list-422-refusal"
        ),
        cluster_id=(
            "openapi-pair:pulls/list"
        ),
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "A List pull requests call returns HTTP 422, but I have "
            "no request parameters or response body. Which exact query "
            "parameter or validation condition caused this failure?"
        ),
        refusal_review_intent_id=(
            "heldout-list-pulls-422-cause"
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-pulls-list-filters"
        ),
        cluster_id=(
            "openapi-pair:pulls/list"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current List pull requests operation, what is "
            "the default state filter, how is the head filter formatted, "
            "what does the base filter identify, and what are the "
            "documented sort and direction defaults?"
        ),
        gold_fact_rubric=(
            (
                "The state filter accepts open, closed, or all and "
                "defaults to open."
            ),
            (
                "The head filter uses the form user:ref-name or "
                "organization:ref-name."
            ),
            (
                "The base filter identifies the base branch name."
            ),
            (
                "The sort parameter defaults to created."
            ),
            (
                "Direction defaults to desc when sort is created or "
                "unspecified, and otherwise defaults to asc."
            ),
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-create-user-repo-"
            "451-freshness"
        ),
        cluster_id=(
            "openapi-pair:repos/"
            "create-for-authenticated-user"
        ),
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy Create a repository for the authenticated user "
            "contract does not list HTTP 451. Under the frozen current "
            "2026-03-10 operation contract, is HTTP 451 documented and "
            "how is that response represented?"
        ),
        gold_fact_rubric=(
            (
                "The current operation documents HTTP 451."
            ),
            (
                "The HTTP 451 response references the shared "
                "validation_failed response contract."
            ),
        ),
        forbid_historical=True,
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-create-user-repo-"
            "contract"
        ),
        cluster_id=(
            "openapi-pair:repos/"
            "create-for-authenticated-user"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current Create a repository for the authenticated "
            "user operation, what method and endpoint are used, which "
            "request field is required, what is the default privacy "
            "setting, and what classic token scopes are described for "
            "public versus private repositories?"
        ),
        gold_fact_rubric=(
            "The operation uses POST /user/repos.",
            "The request body requires name.",
            "The private field defaults to false.",
            (
                "OAuth app tokens and classic personal access tokens "
                "need public_repo or repo scope to create a public "
                "repository."
            ),
            (
                "The repo scope is required to create a private "
                "repository."
            ),
        ),
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-attestations-"
            "bundle-freshness"
        ),
        cluster_id=(
            "openapi-pair:repos/list-attestations"
        ),
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy List attestations response schema embeds a "
            "bundle object inside each attestation. Under the frozen "
            "current 2026-03-10 operation contract, is that embedded "
            "bundle still defined, and which fields does the current "
            "attestation item schema define?"
        ),
        gold_fact_rubric=(
            (
                "The current attestation item schema does not define "
                "the historical embedded bundle property."
            ),
            (
                "The current attestation item schema defines "
                "bundle_url."
            ),
            (
                "The current attestation item schema defines initiator."
            ),
            (
                "The current attestation item schema defines "
                "repository_id."
            ),
        ),
        forbid_historical=True,
    ),
    HeldOutCaseSpec(
        case_id=(
            "phase4-heldout-attestations-"
            "authority"
        ),
        cluster_id=(
            "openapi-pair:repos/list-attestations"
        ),
        scenario_class=(
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION
        ),
        query=(
            "Under the current List attestations operation, what "
            "repository access and fine-grained token permission are "
            "required, and what verification requirements does the "
            "operation identify as necessary for meaningful security "
            "benefits?"
        ),
        gold_fact_rubric=(
            (
                "The authenticated user must have read access to "
                "the repository."
            ),
            (
                "A fine-grained access token requires the "
                "attestations:read permission."
            ),
            (
                "The attestation signature and timestamps must be "
                "cryptographically verified."
            ),
            (
                "The identity of the attestation signer must be "
                "validated."
            ),
        ),
    ),
)

EXPECTED_SCENARIOS_BY_CLUSTER: dict[
    str,
    Counter[ScenarioClass],
] = {
    "guidance:docs-best-practices": Counter(
        (
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "guidance:docs-getting-started": Counter(
        (
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    "guidance:docs-timezones": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        )
    ),
    (
        "openapi-pair:actions/create-remove-token-for-org"
    ): Counter(
        (
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    (
        "openapi-pair:issues/add-blocked-by-dependency"
    ): Counter(
        (
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:issues/update": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    "openapi-pair:pulls/list": Counter(
        (
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    (
        "openapi-pair:repos/create-for-authenticated-user"
    ): Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:repos/list-attestations": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        )
    ),
}

def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_verified_artifact(
    path: Path,
) -> tuple[
    bytes,
    str,
]:
    content = path.read_bytes()

    digest = _sha256_bytes(content)

    sidecar = path.with_suffix(path.suffix + ".sha256")

    observed = sidecar.read_text(encoding="utf-8").strip()

    expected = f"{digest}  {path.name}"

    if observed != expected:
        raise Phase4HeldOutCaseError(f"SHA sidecar mismatch: {path}")

    return content, digest


def _read_verified_evidence(
    repo_root: Path,
    evidence: Phase4AuthoringEvidence,
) -> str:
    path = repo_root / Path(evidence.content_path)

    content = path.read_bytes()

    if len(content) != evidence.byte_count:
        raise Phase4HeldOutCaseError(
            f"authoring evidence byte-count mismatch: {evidence.evidence_id}"
        )

    if _sha256_bytes(content) != evidence.content_sha256:
        raise Phase4HeldOutCaseError(f"authoring evidence SHA mismatch: {evidence.evidence_id}")

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Phase4HeldOutCaseError(
            f"authoring evidence is not UTF-8: {evidence.evidence_id}"
        ) from exc


def _select_current_evidence(
    repo_root: Path,
    cluster: Phase4AuthoringClusterReview,
    spec: HeldOutCaseSpec,
) -> tuple[
    Phase4AuthoringEvidence,
    ...,
]:
    if not spec.evidence_terms:
        selected = tuple(cluster.current_evidence)

    else:
        by_id: dict[
            str,
            Phase4AuthoringEvidence,
        ] = {}

        for term in spec.evidence_terms:
            matches = []

            for evidence in cluster.current_evidence:
                text = _read_verified_evidence(
                    repo_root,
                    evidence,
                )

                if term.casefold() in text.casefold():
                    matches.append(evidence)

            if len(matches) != 1:
                raise Phase4HeldOutCaseError(
                    "evidence selector must match "
                    "exactly one current chunk: "
                    f"{spec.case_id} -> {term!r} "
                    f"matched {len(matches)}"
                )

            matched = matches[0]

            by_id[matched.evidence_id] = matched

        selected = tuple(
            sorted(
                by_id.values(),
                key=lambda item: item.evidence_id,
            )
        )

    if spec.scenario_class is ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE and len(selected) < 2:
        raise Phase4HeldOutCaseError(
            f"multi-evidence case resolved fewer than two evidence units: {spec.case_id}"
        )

    if (
        spec.scenario_class
        in {
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
        }
        and len(selected) != 1
    ):
        raise Phase4HeldOutCaseError(
            "single/freshness/authority case "
            "must resolve exactly one current "
            "evidence unit: "
            f"{spec.case_id} -> {len(selected)}"
        )

    return selected


def _source_ids_for_evidence(
    evidence: tuple[
        Phase4AuthoringEvidence,
        ...,
    ],
) -> tuple[str, ...]:
    return tuple(sorted({parent.source_id for item in evidence for parent in item.parents}))


def _response_mode_for(
    scenario: ScenarioClass,
) -> ResponseMode:
    if scenario is ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE:
        return ResponseMode.REFUSE

    if scenario in {
        ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
        ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
    }:
        return ResponseMode.QUALIFIED_ANSWER

    return ResponseMode.ANSWER


def _criticality_for(
    scenario: ScenarioClass,
) -> Criticality:
    if scenario in {
        ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
    }:
        return Criticality.NONCRITICAL

    return Criticality.CRITICAL


def _build_case(
    *,
    repo_root: Path,
    spec: HeldOutCaseSpec,
    cluster: Phase4AuthoringClusterReview,
    refusal_review: Phase4RefusalSemanticReview,
) -> EvaluationCase:
    response_mode = _response_mode_for(spec.scenario_class)

    is_refusal = response_mode is ResponseMode.REFUSE

    selected: tuple[
        Phase4AuthoringEvidence,
        ...,
    ] = ()

    if not is_refusal:
        selected = _select_current_evidence(
            repo_root,
            cluster,
            spec,
        )

    required_evidence_ids = tuple(item.evidence_id for item in selected)

    required_source_ids = _source_ids_for_evidence(selected)

    forbidden_evidence_ids: tuple[
        str,
        ...,
    ] = ()

    forbidden_source_ids: tuple[
        str,
        ...,
    ] = ()

    if spec.forbid_historical:
        if not cluster.historical_evidence:
            raise Phase4HeldOutCaseError(
                "freshness case requested "
                "historical exclusion but cluster "
                "has no historical evidence: "
                f"{spec.case_id}"
            )

        forbidden_evidence_ids = tuple(item.evidence_id for item in cluster.historical_evidence)

        forbidden_source_ids = tuple(cluster.historical_source_ids)

    required_fact_ids = tuple(
        f"{spec.case_id}:fact-{index:02d}"
        for index, _fact in enumerate(
            spec.gold_fact_rubric,
            start=1,
        )
    )

    refusal_reason: str | None = None

    scoring_notes = (
        "Full credit requires every gold fact "
        "and support from the required evidence "
        "IDs. Partial-credit denominators and "
        "failure precedence are not frozen in "
        "this authoring slice."
    )

    if is_refusal:
        refusal_reason = RefusalReason.INSUFFICIENT_EVIDENCE.value

        if spec.refusal_review_intent_id is None:
            raise Phase4HeldOutCaseError("refusal case missing semantic-review intent")

        review_by_id = {item.intent_id: item for item in refusal_review.items}

        review_item = review_by_id.get(spec.refusal_review_intent_id)

        if review_item is None:
            raise Phase4HeldOutCaseError(
                "refusal semantic review "
                "does not contain case intent: "
                f"{spec.refusal_review_intent_id}"
            )

        if review_item.verdict == "ANSWERABLE_ELSEWHERE":
            raise Phase4HeldOutCaseError(
                "cannot author refusal case from ANSWERABLE_ELSEWHERE review"
            )

        scoring_notes = (
            "Expected runtime behaviour is "
            "insufficient-evidence refusal. "
            "The evaluator must not reward an "
            "unsupported answer that exceeds the "
            "reviewed evidence boundary. "
            "Reviewed refusal boundary: "
            f"{review_item.final_claim}"
        )

    if spec.forbid_historical:
        scoring_notes += (
            " Historical comparison evidence is "
            "explicitly forbidden as final support "
            "because the query asks for the current "
            "2026-03-10 contract."
        )

    return EvaluationCase(
        case_id=spec.case_id,
        case_version="1.0",
        data_role=EvaluationRole.HELD_OUT,
        source_family=(cluster.source_family),
        scenario_class=(spec.scenario_class),
        criticality=(_criticality_for(spec.scenario_class)),
        query=spec.query,
        expected_response_mode=(response_mode),
        required_fact_ids=(required_fact_ids),
        required_evidence_ids=(required_evidence_ids),
        required_source_ids=(required_source_ids),
        allowed_source_states=(SourceState.CURRENT,),
        forbidden_evidence_ids=(forbidden_evidence_ids),
        forbidden_source_ids=(forbidden_source_ids),
        required_api_version=("2026-03-10"),
        required_authority_level=(AuthorityLevel.AUTHORITATIVE),
        must_refuse_reason=(refusal_reason),
        gold_fact_rubric=(spec.gold_fact_rubric),
        scoring_notes=(scoring_notes),
        authoring_evidence=(cluster.authoring_evidence_ids),
    )


def _render_markdown(
    records: tuple[
        HeldOutCaseRecord,
        ...,
    ],
) -> str:
    lines = [
        "# Phase 4C HELD_OUT Canonical Case Candidate V1",
        "",
        ("**State:** authored candidate; not yet frozen and not baseline-authorized."),
        "",
        "## Quotas",
        "",
        "- cases: `18`",
        "- clusters: `9`",
        "- current single-source: `5`",
        "- current multi-evidence: `4`",
        "- version freshness: `4`",
        "- authority/scope: `2`",
        "- must-refuse: `3`",
        "",
    ]

    for record in records:
        case = record.case

        lines.extend(
            [
                f"## `{case.case_id}`",
                "",
                (f"- cluster: `{record.cluster_id}`"),
                (f"- family: `{case.source_family.value}`"),
                (f"- scenario: `{case.scenario_class.value}`"),
                (f"- criticality: `{case.criticality.value}`"),
                (f"- response mode: `{case.expected_response_mode.value}`"),
                "",
                "**Query**",
                "",
                case.query,
                "",
            ]
        )

        if case.gold_fact_rubric:
            lines.extend(
                [
                    "**Gold facts**",
                    "",
                ]
            )

            for fact in case.gold_fact_rubric:
                lines.append(f"- {fact}")

            lines.append("")

        if case.must_refuse_reason is not None:
            lines.extend(
                [
                    (f"**Refusal reason:** `{case.must_refuse_reason}`"),
                    "",
                ]
            )

        lines.extend(
            [
                "**Required evidence IDs**",
                "",
            ]
        )

        if case.required_evidence_ids:
            for evidence_id in case.required_evidence_ids:
                lines.append(f"- `{evidence_id}`")
        else:
            lines.append("- `none`")

        lines.extend(
            [
                "",
                "**Forbidden evidence IDs**",
                "",
            ]
        )

        if case.forbidden_evidence_ids:
            for evidence_id in case.forbidden_evidence_ids:
                lines.append(f"- `{evidence_id}`")
        else:
            lines.append("- `none`")

        lines.extend(
            [
                "",
                "**Scoring notes**",
                "",
                case.scoring_notes,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _write_markdown_with_sha256(
    path: Path,
    content: str,
) -> str:
    encoded = content.encode("utf-8")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(encoded)

    digest = _sha256_bytes(encoded)

    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    return digest


def materialize_phase4_held_out_cases(
    repo_root: Path,
) -> tuple[
    Phase4HeldOutCaseSuite,
    str,
    str,
]:
    dossier_bytes, dossier_sha = _read_verified_artifact(repo_root / _DOSSIER_PATH)

    dossier = Phase4AuthoringDossier.model_validate_json(dossier_bytes)

    if dossier.case_authoring_authorized is not True:
        raise Phase4HeldOutCaseError("authoring dossier does not authorize case authoring")

    review_bytes, review_sha = _read_verified_artifact(repo_root / _REFUSAL_REVIEW_PATH)

    refusal_review = Phase4RefusalSemanticReview.model_validate_json(review_bytes)

    if refusal_review.allocation_survives is not True:
        raise Phase4HeldOutCaseError("refusal review does not preserve allocation")

    held_out_clusters = {
        cluster.cluster_id: cluster
        for cluster in dossier.clusters
        if (cluster.evaluation_role is EvaluationRole.HELD_OUT)
    }

    if set(held_out_clusters) != set(EXPECTED_SCENARIOS_BY_CLUSTER):
        raise Phase4HeldOutCaseError("HELD_OUT cluster set drifted from reviewed allocation")

    if len(CASE_SPECS) != 18:
        raise Phase4HeldOutCaseError("expected exactly 18 HELD_OUT case specs")

    spec_scenarios = {
        cluster_id: Counter(
            spec.scenario_class for spec in CASE_SPECS if (spec.cluster_id == cluster_id)
        )
        for cluster_id in held_out_clusters
    }

    if spec_scenarios != EXPECTED_SCENARIOS_BY_CLUSTER:
        raise Phase4HeldOutCaseError(
            "case-spec allocation does not match reviewed HELD_OUT allocation"
        )

    records = tuple(
        HeldOutCaseRecord(
            cluster_id=spec.cluster_id,
            case=_build_case(
                repo_root=repo_root,
                spec=spec,
                cluster=(held_out_clusters[spec.cluster_id]),
                refusal_review=(refusal_review),
            ),
        )
        for spec in CASE_SPECS
    )

    markdown = _render_markdown(records)

    markdown_sha = _write_markdown_with_sha256(
        repo_root / _SUITE_MARKDOWN_PATH,
        markdown,
    )

    suite = Phase4HeldOutCaseSuite(
        authoring_dossier_sha256=(dossier_sha),
        refusal_semantic_review_sha256=(review_sha),
        review_markdown_sha256=(markdown_sha),
        records=records,
    )

    json_sha = write_json_with_sha256(
        repo_root / _SUITE_JSON_PATH,
        suite,
    )

    return (
        suite,
        json_sha,
        markdown_sha,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    (
        suite,
        json_sha,
        markdown_sha,
    ) = materialize_phase4_held_out_cases(repo_root)

    print(f"PHASE4C_HELD_OUT_CASE_COUNT={suite.case_count}")

    print(f"PHASE4C_HELD_OUT_CLUSTER_COUNT={suite.cluster_count}")

    print(f"PHASE4C_HELD_OUT_SINGLE_SOURCE_COUNT={suite.current_single_source_count}")

    print(f"PHASE4C_HELD_OUT_MULTI_EVIDENCE_COUNT={suite.current_multi_evidence_count}")

    print(f"PHASE4C_HELD_OUT_FRESHNESS_COUNT={suite.version_freshness_count}")

    print(f"PHASE4C_HELD_OUT_AUTHORITY_SCOPE_COUNT={suite.authority_scope_count}")

    print(f"PHASE4C_HELD_OUT_MUST_REFUSE_COUNT={suite.must_refuse_count}")

    print("PHASE4C_HELD_OUT_CASE_AUTHORING_COMPLETE=true")

    print("PHASE4C_HELD_OUT_SUITE_FROZEN=false")

    print("PHASE4C_HELD_OUT_OUTCOMES_EXPOSED=false")

    print("PHASE4_BASELINE_AUTHORIZED=false")

    print(f"PHASE4C_HELD_OUT_CASES_JSON_SHA256={json_sha}")

    print(f"PHASE4C_HELD_OUT_CASES_MARKDOWN_SHA256={markdown_sha}")


if __name__ == "__main__":
    main()

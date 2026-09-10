"""Phase 4C DEVELOPMENT canonical-case candidate authoring."""

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

_SUITE_JSON_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.json"

_SUITE_MARKDOWN_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.md"


class DevelopmentCaseSpec(ContractModel):
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


class DevelopmentCaseRecord(ContractModel):
    """One canonical case plus its frozen cluster identity."""

    cluster_id: NonEmptyStr
    case: EvaluationCase


class Phase4DevelopmentCaseSuite(ContractModel):
    """Development-only candidate suite before Phase 4 case freeze."""

    suite_version: Literal["phase4c-development-cases-v1"] = "phase4c-development-cases-v1"

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256
    review_markdown_sha256: Sha256

    case_count: Literal[24] = 24
    cluster_count: Literal[12] = 12

    current_single_source_count: Literal[7] = 7

    current_multi_evidence_count: Literal[5] = 5

    version_freshness_count: Literal[5] = 5

    authority_scope_count: Literal[3] = 3

    must_refuse_count: Literal[4] = 4

    development_case_authoring_complete: Literal[True] = True

    development_suite_frozen: Literal[False] = False

    baseline_authorized: Literal[False] = False

    release_eligible: Literal[False] = False

    records: tuple[
        DevelopmentCaseRecord,
        ...,
    ] = Field(
        min_length=24,
        max_length=24,
    )

    @model_validator(mode="after")
    def validate_suite(
        self,
    ) -> Self:
        case_ids = tuple(record.case.case_id for record in self.records)

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("development case IDs must be unique")

        queries = tuple(record.case.query for record in self.records)

        if len(queries) != len(set(queries)):
            raise ValueError("development queries must be unique")

        if any(record.case.data_role is not EvaluationRole.DEVELOPMENT for record in self.records):
            raise ValueError("suite may only contain DEVELOPMENT cases")

        scenario_counts = Counter(record.case.scenario_class for record in self.records)

        expected_scenarios = Counter(
            {
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 7,
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 5,
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 5,
                ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 3,
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 4,
            }
        )

        if scenario_counts != expected_scenarios:
            raise ValueError("DEVELOPMENT scenario quotas drifted")

        family_counts = Counter(record.case.source_family for record in self.records)

        expected_families = Counter(
            {
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 8,
                EvaluationSourceFamily.ACTIONS: 4,
                EvaluationSourceFamily.ISSUES: 4,
                EvaluationSourceFamily.PULL_REQUESTS: 4,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 4,
            }
        )

        if family_counts != expected_families:
            raise ValueError("DEVELOPMENT family quotas drifted")

        cluster_counts = Counter(record.cluster_id for record in self.records)

        if len(cluster_counts) != 12:
            raise ValueError("DEVELOPMENT suite must use 12 clusters")

        if any(count != 2 for count in cluster_counts.values()):
            raise ValueError("each DEVELOPMENT cluster requires exactly two cases")

        for record in self.records:
            runtime = record.case.to_runtime_input().model_dump()

            if set(runtime) != {
                "case_id",
                "query",
            }:
                raise ValueError("gold fields leaked through runtime case projection")

        return self


class Phase4DevelopmentCaseError(ValueError):
    """Development case candidate cannot be safely materialized."""


CASE_SPECS: tuple[
    DevelopmentCaseSpec,
    ...,
] = (
    DevelopmentCaseSpec(
        case_id="phase4-dev-api-version-current-contract",
        cluster_id="guidance:docs-api-versions",
        scenario_class=(ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION),
        query=(
            "A legacy runbook says 2022-11-28 is still the newest "
            "GitHub REST API version. Under the frozen current docs, "
            "what newer supported version is listed, what version do "
            "requests without X-GitHub-Api-Version default to, and "
            "what happens if a specified version is no longer supported?"
        ),
        gold_fact_rubric=(
            "The supported-version list includes 2026-03-10, which is newer than 2022-11-28.",
            "Requests without X-GitHub-Api-Version default to 2022-11-28.",
            "A specified API version that is no longer supported returns 410 Gone.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-api-version-future-unknown",
        cluster_id="guidance:docs-api-versions",
        scenario_class=(ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE),
        query=(
            "What is the exact GitHub REST API version that will "
            "replace 2026-03-10, and on what exact date will GitHub "
            "release that future version?"
        ),
        refusal_review_intent_id=("dev-api-version-after-2026-03-10"),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-breaking-sarif-content-type-current",
        cluster_id="guidance:docs-breaking-changes",
        scenario_class=(ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION),
        query=(
            "A legacy integration expects a SARIF response requested "
            "with Accept: application/sarif+json to come back with "
            "Content-Type application/json+sarif. Under the "
            "2026-03-10 breaking-change guidance, what Content-Type "
            "should the response use instead?"
        ),
        gold_fact_rubric=(
            "The prior response Content-Type application/json+sarif was incorrect.",
            "The corrected SARIF response Content-Type is application/sarif+json.",
        ),
        evidence_terms=("Change Content-Type of SARIF response",),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-breaking-version-migration",
        cluster_id="guidance:docs-breaking-changes",
        scenario_class=(ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE),
        query=(
            "Compare the current breaking-change guidance for "
            "2022-11-28 and 2026-03-10: did 2022-11-28 introduce "
            "breaking changes, and how should an integration migrate "
            "away from the deprecated rate property in the rate-limit endpoint?"
        ),
        gold_fact_rubric=(
            (
                "Version 2022-11-28 is the first date-based GitHub REST API version and "
                "includes no breaking changes."
            ),
            "For 2026-03-10, the deprecated rate property is removed from the rate-limit endpoint.",
            "Integrations should read the equivalent rate-limit information from resources.core.",
        ),
        evidence_terms=(
            "Version `2022-11-28` is the first version",
            "Remove deprecated `rate` property from rate limit endpoint",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pagination-manual-link-loop",
        cluster_id="guidance:docs-pagination",
        scenario_class=(ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE),
        query=(
            "I am implementing GitHub REST pagination without a "
            "built-in pagination helper. How does the link header "
            "tell me whether another page exists, and how should "
            "the manual collection loop know when to stop?"
        ),
        gold_fact_rubric=(
            "Paginated responses use the link header to expose URLs for additional pages.",
            "The next-page URL is identified by the next relationship in the link header.",
            (
                "A manual pagination loop follows the next-page URL repeatedly and stops when "
                "no next-page link remains."
            ),
            (
                "The manual implementation must handle paginated data returned as either an "
                "array or an object containing the array."
            ),
        ),
        evidence_terms=(
            "## Using `link` headers",
            "### Example creating a pagination method",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pagination-helper-vs-manual",
        cluster_id="guidance:docs-pagination",
        scenario_class=(ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE),
        query=(
            "A paginated endpoint can return items inside an object, "
            "and a request can also return no data. Compare "
            "octokit.paginate() with a custom paginator: what result "
            "shape does the helper provide, and what normalization "
            "must custom code perform before accumulating items?"
        ),
        gold_fact_rubric=(
            "octokit.paginate() returns an array of items even when "
            "the raw paginated response wraps the items in an object.",
            "A custom paginator should normalize a no-data response to an empty array.",
            "When the raw data is an object, custom code must extract "
            "the actual items array before accumulating results.",
        ),
        evidence_terms=(
            "always returns an array of items even if the raw result was an object",
            "### Example creating a pagination method",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-troubleshooting-method-and-rate-limit",
        cluster_id="guidance:docs-troubleshooting",
        scenario_class=(ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE),
        query=(
            "A GitHub REST request first returns 404 because the "
            "client used an unsupported HTTP method, and repeated "
            "requests later hit a 403 or 429 rate-limit response. "
            "Explain both behaviours and the safe retry sequence."
        ),
        gold_fact_rubric=(
            (
                "Using an HTTP method that the endpoint does not support can return 404 Not "
                "Found instead of 405 Method Not Allowed."
            ),
            "A primary or secondary rate-limit failure may return 403 or 429.",
            "If retry-after is present, the client should wait that many seconds before retrying.",
            "If x-ratelimit-remaining is zero, the client should wait until x-ratelimit-reset.",
            (
                "Otherwise the client should wait at least one minute and use increasing "
                "backoff for repeated secondary-limit failures."
            ),
        ),
        evidence_terms=(
            "405 Method Not Allowed",
            "## Rate limit errors",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-troubleshooting-private-resource-and-version",
        cluster_id="guidance:docs-troubleshooting",
        scenario_class=(ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE),
        query=(
            "One request to a private resource that is known to exist "
            "returns 404 Not Found, while another request specifies an "
            "API version that does not exist and returns 400 Bad "
            "Request. What should the client infer and check in each case?"
        ),
        gold_fact_rubric=(
            "A private resource can return 404 Not Found instead of "
            "403 Forbidden when the request is not properly authenticated.",
            "For a known existing private resource, the client should "
            "check authentication, token scopes or permissions, and "
            "resource access.",
            "Specifying an API version that does not exist returns "
            "400 Bad Request with a message that the version is not supported.",
            "The client should use X-GitHub-Api-Version with a supported API version.",
        ),
        evidence_terms=(
            "## `404 Not Found` for an existing resource",
            "## Not a supported version",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-actions-org-registration-token",
        cluster_id=("openapi-pair:actions/create-registration-token-for-org"),
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "For the current GitHub REST contract, which endpoint "
            "creates a self-hosted runner registration token for an "
            "organization, how long is the token valid, and what is "
            "the successful response status?"
        ),
        gold_fact_rubric=(
            "The operation is POST /orgs/{org}/actions/runners/registration-token.",
            "The registration token expires after one hour.",
            "The successful response status is 201.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-actions-org-registration-scope",
        cluster_id=("openapi-pair:actions/create-registration-token-for-org"),
        scenario_class=(ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION),
        query=(
            "Who is authorized to create an organization self-hosted "
            "runner registration token, and which classic personal "
            "access token or OAuth scope is required?"
        ),
        gold_fact_rubric=(
            "The caller must have organization administrator access.",
            (
                "OAuth app tokens and classic personal access tokens require the admin:org "
                "scope for this operation."
            ),
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-actions-repo-remove-token",
        cluster_id=("openapi-pair:actions/create-remove-token-for-repo"),
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "Which current GitHub REST endpoint creates a removal "
            "token for a repository self-hosted runner, how long "
            "does that token remain valid, and what success status "
            "does the operation return?"
        ),
        gold_fact_rubric=(
            "The operation is POST /repos/{owner}/{repo}/actions/runners/remove-token.",
            "The removal token expires after one hour.",
            "The successful response status is 201.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-actions-repo-remove-scope",
        cluster_id=("openapi-pair:actions/create-remove-token-for-repo"),
        scenario_class=(ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION),
        query=(
            "What access level is required to create a self-hosted "
            "runner removal token for a repository, and which classic "
            "personal access token or OAuth scope is required?"
        ),
        gold_fact_rubric=(
            "The caller must have administrator access to the repository.",
            "OAuth app tokens and classic personal access tokens require the repo scope.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-issues-add-assignees",
        cluster_id=("openapi-pair:issues/add-assignees"),
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "Under the current Add assignees to an issue contract, "
            "how many assignees may be added, what happens to existing "
            "assignees, and what happens when the caller lacks push access?"
        ),
        gold_fact_rubric=(
            "The operation can add up to 10 assignees.",
            "Users already assigned to the issue are not replaced.",
            "Only users with push access can add assignees.",
            "Assignees are silently ignored when the required push access is absent.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id=("phase4-dev-issues-add-assignees-instance-refusal"),
        cluster_id=("openapi-pair:issues/add-assignees"),
        scenario_class=(ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE),
        query=(
            "An Add assignees request returned a generic successful "
            "outcome. I have no request body, response body, or user "
            "permission state. Tell me exactly which requested login, "
            "if any, was silently ignored."
        ),
        refusal_review_intent_id=("dev-add-assignees-silent-ignore-cause"),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-issues-create-current-assignees",
        cluster_id="openapi-pair:issues/create",
        scenario_class=(ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION),
        query=(
            "A 2022 integration still sends the singular assignee "
            "property when creating an issue. Under the current "
            "2026-03-10 operation contract, is that singular field "
            "still part of the request schema?"
        ),
        gold_fact_rubric=(
            (
                "The current 2026-03-10 Create an issue request schema no longer contains the "
                "singular assignee field."
            ),
            "The current contract uses the assignees array for assigning users.",
        ),
        forbid_historical=True,
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-issues-create-instance-refusal",
        cluster_id="openapi-pair:issues/create",
        scenario_class=(ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE),
        query=(
            "An issue was created successfully, but I do not have "
            "the response details or caller identity. Tell me exactly "
            "which optional requested fields were silently dropped "
            "and identify the caller who made the request."
        ),
        refusal_review_intent_id=("dev-create-issue-silent-drop-cause"),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pulls-create-contract",
        cluster_id="openapi-pair:pulls/create",
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "For the current Create a pull request operation, which "
            "base and head information must be supplied, how may a "
            "head branch be qualified with an owner, and when is "
            "head_repo required?"
        ),
        gold_fact_rubric=(
            "The request requires base and head information.",
            "The head value can identify the source as username:branch.",
            (
                "head_repo is required for a cross-repository pull request when both "
                "repositories are owned by the same organization."
            ),
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pulls-create-authority",
        cluster_id="openapi-pair:pulls/create",
        scenario_class=(ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION),
        query=(
            "What repository access and organization-membership "
            "conditions apply when creating a pull request from its "
            "head or source branch?"
        ),
        gold_fact_rubric=(
                             "The caller needs write access to the head or source "
                             "branch used for the pull request.",
                             "For organization-owned repositories, the caller must be "
                             "a member of the organization that owns the repository.",
                         ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pulls-remove-reviewers-contract",
        cluster_id=("openapi-pair:pulls/remove-requested-reviewers"),
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "For Remove requested reviewers from a pull request, "
            "which HTTP method and endpoint are used, what does the "
            "required reviewers field contain, and how are teams identified?"
        ),
        gold_fact_rubric=(
            (
                "The operation uses DELETE "
                "/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers."
            ),
            "The reviewers request field is required and contains user logins.",
            "team_reviewers contains team slugs.",
            "The operation documents 200 and 422 responses.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-pulls-remove-reviewers-422-refusal",
        cluster_id=("openapi-pair:pulls/remove-requested-reviewers"),
        scenario_class=(ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE),
        query=(
            "A Remove requested reviewers request returned only "
            "HTTP 422. I do not have the response body or validation "
            "errors. What exact validation condition caused this request to fail?"
        ),
        refusal_review_intent_id=("dev-remove-reviewers-422-cause"),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-repos-accept-invitation-current",
        cluster_id=("openapi-pair:repos/accept-invitation-for-authenticated-user"),
        scenario_class=(ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION),
        query=(
            "An older 2022 contract for accepting a repository "
            "invitation did not list HTTP 451. Under the current "
            "2026-03-10 operation contract, is 451 now a documented response?"
        ),
        gold_fact_rubric=(
            (
                "The current 2026-03-10 contract includes HTTP 451 as a documented response "
                "for accepting a repository invitation."
            ),
        ),
        forbid_historical=True,
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-repos-accept-invitation-success",
        cluster_id=("openapi-pair:repos/accept-invitation-for-authenticated-user"),
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "For the current Accept a repository invitation operation, "
            "which HTTP method and endpoint are used, and what status "
            "indicates success?"
        ),
        gold_fact_rubric=(
            "The operation uses PATCH /user/repository_invitations/{invitation_id}.",
            "A successful Accept a repository invitation operation returns HTTP 204.",
        ),
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-repos-get-content-current-submodule",
        cluster_id="openapi-pair:repos/get-content",
        scenario_class=(ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION),
        query=(
            "A legacy integration expects submodules returned in a "
            "repository directory listing to have type file. Under "
            "the current 2026-03-10 Get repository content contract, "
            "what type should a submodule have?"
        ),
        gold_fact_rubric=(
            (
                "Under the current 2026-03-10 contract, a submodule in a directory listing has "
                "type submodule rather than type file."
            ),
        ),
        forbid_historical=True,
    ),
    DevelopmentCaseSpec(
        case_id="phase4-dev-repos-get-content-size-contract",
        cluster_id="openapi-pair:repos/get-content",
        scenario_class=(ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE),
        query=(
            "For Get repository content, what happens when ref is "
            "omitted, and what restrictions apply to files between "
            "1 MB and 100 MB and to files larger than 100 MB?"
        ),
        gold_fact_rubric=(
            "If ref is omitted, the endpoint uses the repository's default branch.",
            (
                "For files between 1 MB and 100 MB, only the raw or object custom media types "
                "are supported."
            ),
            (
                "For the object media type in that size range, content is an empty string and "
                "encoding is none."
            ),
            "Files larger than 100 MB are not supported by this endpoint.",
        ),
    ),
)


EXPECTED_SCENARIOS_BY_CLUSTER: dict[
    str,
    Counter[ScenarioClass],
] = {
    "guidance:docs-api-versions": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        )
    ),
    "guidance:docs-breaking-changes": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    "guidance:docs-pagination": Counter(
        (
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    "guidance:docs-troubleshooting": Counter(
        (
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    ("openapi-pair:actions/create-registration-token-for-org"): Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        )
    ),
    ("openapi-pair:actions/create-remove-token-for-repo"): Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        )
    ),
    "openapi-pair:issues/add-assignees": Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        )
    ),
    "openapi-pair:issues/create": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        )
    ),
    "openapi-pair:pulls/create": Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        )
    ),
    ("openapi-pair:pulls/remove-requested-reviewers"): Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        )
    ),
    ("openapi-pair:repos/accept-invitation-for-authenticated-user"): Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:repos/get-content": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
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
        raise Phase4DevelopmentCaseError(f"SHA sidecar mismatch: {path}")

    return content, digest


def _read_verified_evidence(
    repo_root: Path,
    evidence: Phase4AuthoringEvidence,
) -> str:
    path = repo_root / Path(evidence.content_path)

    content = path.read_bytes()

    if len(content) != evidence.byte_count:
        raise Phase4DevelopmentCaseError(
            f"authoring evidence byte-count mismatch: {evidence.evidence_id}"
        )

    if _sha256_bytes(content) != evidence.content_sha256:
        raise Phase4DevelopmentCaseError(f"authoring evidence SHA mismatch: {evidence.evidence_id}")

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Phase4DevelopmentCaseError(
            f"authoring evidence is not UTF-8: {evidence.evidence_id}"
        ) from exc


def _select_current_evidence(
    repo_root: Path,
    cluster: Phase4AuthoringClusterReview,
    spec: DevelopmentCaseSpec,
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
                raise Phase4DevelopmentCaseError(
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
        raise Phase4DevelopmentCaseError(
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
        raise Phase4DevelopmentCaseError(
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
    spec: DevelopmentCaseSpec,
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
            raise Phase4DevelopmentCaseError(
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
            raise Phase4DevelopmentCaseError("refusal case missing semantic-review intent")

        review_by_id = {item.intent_id: item for item in refusal_review.items}

        review_item = review_by_id.get(spec.refusal_review_intent_id)

        if review_item is None:
            raise Phase4DevelopmentCaseError(
                "refusal semantic review "
                "does not contain case intent: "
                f"{spec.refusal_review_intent_id}"
            )

        if review_item.verdict == "ANSWERABLE_ELSEWHERE":
            raise Phase4DevelopmentCaseError(
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
        data_role=EvaluationRole.DEVELOPMENT,
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
        DevelopmentCaseRecord,
        ...,
    ],
) -> str:
    lines = [
        "# Phase 4C DEVELOPMENT Canonical Case Candidate V1",
        "",
        ("**State:** authored candidate; not yet frozen and not baseline-authorized."),
        "",
        "## Quotas",
        "",
        "- cases: `24`",
        "- clusters: `12`",
        "- current single-source: `7`",
        "- current multi-evidence: `5`",
        "- version freshness: `5`",
        "- authority/scope: `3`",
        "- must-refuse: `4`",
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


def materialize_phase4_development_cases(
    repo_root: Path,
) -> tuple[
    Phase4DevelopmentCaseSuite,
    str,
    str,
]:
    dossier_bytes, dossier_sha = _read_verified_artifact(repo_root / _DOSSIER_PATH)

    dossier = Phase4AuthoringDossier.model_validate_json(dossier_bytes)

    if dossier.case_authoring_authorized is not True:
        raise Phase4DevelopmentCaseError("authoring dossier does not authorize case authoring")

    review_bytes, review_sha = _read_verified_artifact(repo_root / _REFUSAL_REVIEW_PATH)

    refusal_review = Phase4RefusalSemanticReview.model_validate_json(review_bytes)

    if refusal_review.allocation_survives is not True:
        raise Phase4DevelopmentCaseError("refusal review does not preserve allocation")

    development_clusters = {
        cluster.cluster_id: cluster
        for cluster in dossier.clusters
        if (cluster.evaluation_role is EvaluationRole.DEVELOPMENT)
    }

    if set(development_clusters) != set(EXPECTED_SCENARIOS_BY_CLUSTER):
        raise Phase4DevelopmentCaseError("DEVELOPMENT cluster set drifted from reviewed allocation")

    if len(CASE_SPECS) != 24:
        raise Phase4DevelopmentCaseError("expected exactly 24 DEVELOPMENT case specs")

    spec_scenarios = {
        cluster_id: Counter(
            spec.scenario_class for spec in CASE_SPECS if (spec.cluster_id == cluster_id)
        )
        for cluster_id in development_clusters
    }

    if spec_scenarios != EXPECTED_SCENARIOS_BY_CLUSTER:
        raise Phase4DevelopmentCaseError(
            "case-spec allocation does not match reviewed DEVELOPMENT allocation"
        )

    records = tuple(
        DevelopmentCaseRecord(
            cluster_id=spec.cluster_id,
            case=_build_case(
                repo_root=repo_root,
                spec=spec,
                cluster=(development_clusters[spec.cluster_id]),
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

    suite = Phase4DevelopmentCaseSuite(
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
    ) = materialize_phase4_development_cases(repo_root)

    print(f"PHASE4C_DEVELOPMENT_CASE_COUNT={suite.case_count}")

    print(f"PHASE4C_DEVELOPMENT_CLUSTER_COUNT={suite.cluster_count}")

    print(f"PHASE4C_DEVELOPMENT_SINGLE_SOURCE_COUNT={suite.current_single_source_count}")

    print(f"PHASE4C_DEVELOPMENT_MULTI_EVIDENCE_COUNT={suite.current_multi_evidence_count}")

    print(f"PHASE4C_DEVELOPMENT_FRESHNESS_COUNT={suite.version_freshness_count}")

    print(f"PHASE4C_DEVELOPMENT_AUTHORITY_SCOPE_COUNT={suite.authority_scope_count}")

    print(f"PHASE4C_DEVELOPMENT_MUST_REFUSE_COUNT={suite.must_refuse_count}")

    print("PHASE4C_DEVELOPMENT_CASE_AUTHORING_COMPLETE=true")

    print("PHASE4C_DEVELOPMENT_SUITE_FROZEN=false")

    print("PHASE4_BASELINE_AUTHORIZED=false")

    print(f"PHASE4C_DEVELOPMENT_CASES_JSON_SHA256={json_sha}")

    print(f"PHASE4C_DEVELOPMENT_CASES_MARKDOWN_SHA256={markdown_sha}")


if __name__ == "__main__":
    main()

"""Phase 4C TUNING canonical-case candidate authoring."""

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

_SUITE_JSON_PATH = Path("artifacts") / "development" / "phase4c_tuning_cases_v1.json"

_SUITE_MARKDOWN_PATH = Path("artifacts") / "development" / "phase4c_tuning_cases_v1.md"


class TuningCaseSpec(ContractModel):
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


class TuningCaseRecord(ContractModel):
    """One canonical case plus its frozen cluster identity."""

    cluster_id: NonEmptyStr
    case: EvaluationCase


class Phase4TuningCaseSuite(ContractModel):
    """Tuning-only candidate suite before Phase 4 case freeze."""

    suite_version: Literal["phase4c-tuning-cases-v1"] = "phase4c-tuning-cases-v1"

    authoring_dossier_sha256: Sha256
    refusal_semantic_review_sha256: Sha256
    review_markdown_sha256: Sha256

    case_count: Literal[18] = 18
    cluster_count: Literal[9] = 9

    current_single_source_count: Literal[6] = 6

    current_multi_evidence_count: Literal[3] = 3

    version_freshness_count: Literal[3] = 3

    authority_scope_count: Literal[3] = 3

    must_refuse_count: Literal[3] = 3

    tuning_case_authoring_complete: Literal[True] = True

    tuning_suite_frozen: Literal[False] = False

    baseline_authorized: Literal[False] = False

    release_eligible: Literal[False] = False

    records: tuple[
        TuningCaseRecord,
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
            raise ValueError("tuning case IDs must be unique")

        queries = tuple(record.case.query for record in self.records)

        if len(queries) != len(set(queries)):
            raise ValueError("tuning queries must be unique")

        if any(record.case.data_role is not EvaluationRole.TUNING for record in self.records):
            raise ValueError("suite may only contain TUNING cases")

        scenario_counts = Counter(record.case.scenario_class for record in self.records)

        expected_scenarios = Counter(
            {
                ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 6,
                ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 3,
                ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 3,
                ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 3,
                ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 3,
            }
        )

        if scenario_counts != expected_scenarios:
            raise ValueError("TUNING scenario quotas drifted")

        family_counts = Counter(record.case.source_family for record in self.records)

        expected_families = Counter(
            {
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 6,
                EvaluationSourceFamily.ACTIONS: 4,
                EvaluationSourceFamily.ISSUES: 2,
                EvaluationSourceFamily.PULL_REQUESTS: 4,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 2,
            }
        )

        if family_counts != expected_families:
            raise ValueError("TUNING family quotas drifted")

        cluster_counts = Counter(record.cluster_id for record in self.records)

        if len(cluster_counts) != 9:
            raise ValueError("TUNING suite must use 9 clusters")

        if any(count != 2 for count in cluster_counts.values()):
            raise ValueError("each TUNING cluster requires exactly two cases")

        for record in self.records:
            runtime = record.case.to_runtime_input().model_dump()

            if set(runtime) != {
                "case_id",
                "query",
            }:
                raise ValueError("gold fields leaked through runtime case projection")

        return self


class Phase4TuningCaseError(ValueError):
    """Development case candidate cannot be safely materialized."""


CASE_SPECS: tuple[
    TuningCaseSpec,
    ...,
] = (
    TuningCaseSpec(
        case_id="phase4-tuning-auth-username-password-current",
        cluster_id="guidance:docs-authentication",
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy runbook tells users to authenticate to the "
            "GitHub REST API with their GitHub username and password. "
            "Under the frozen current authentication guidance, is "
            "username-and-password authentication supported, and what "
            "response class should be expected if it is attempted?"
        ),
        gold_fact_rubric=(
            (
                "Authentication with a GitHub username and password "
                "is not supported."
            ),
            (
                "Attempting username-and-password authentication "
                "returns a 4xx error."
            ),
        ),
        evidence_terms=(
            "Authentication with username and password is not supported",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-auth-saml-actions",
        cluster_id="guidance:docs-authentication",
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "A team accesses an organization that enforces SAML SSO "
            "and is also moving API work into a GitHub Actions workflow. "
            "How does SAML authorization differ for a classic personal "
            "access token versus a fine-grained personal access token, "
            "and for the workflow itself what credential does GitHub "
            "recommend and how are its permissions granted?"
        ),
        gold_fact_rubric=(
            (
                "A classic personal access token must be authorized "
                "after creation for an organization that enforces "
                "SAML SSO."
            ),
            (
                "A fine-grained personal access token is authorized "
                "during token creation before organization access "
                "is granted."
            ),
            (
                "Inside a GitHub Actions workflow, GitHub recommends "
                "using the built-in GITHUB_TOKEN instead of creating "
                "another token."
            ),
            (
                "Permissions for GITHUB_TOKEN can be granted with "
                "the workflow permissions key."
            ),
        ),
        evidence_terms=(
            "Personal access tokens and SAML SSO",
            "Authenticating in a GitHub Actions workflow",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-credential-method-scope",
        cluster_id="guidance:docs-credential-security",
        scenario_class=(
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION
        ),
        query=(
            "Choose the credential type that the current GitHub "
            "guidance recommends for three different principals: "
            "personal API use, API use on behalf of an organization "
            "or another user, and API use inside GitHub Actions. "
            "What least-privilege rule should be applied to the "
            "credential's scopes or permissions?"
        ),
        gold_fact_rubric=(
            (
                "For personal API use, the guidance recommends a "
                "personal access token."
            ),
            (
                "For API use on behalf of an organization or another "
                "user, the guidance recommends a GitHub App."
            ),
            (
                "For API use in a GitHub Actions workflow, the guidance "
                "recommends the built-in GITHUB_TOKEN."
            ),
            (
                "Credentials should receive only the minimum scopes "
                "or permissions required for the task."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-credential-remediation",
        cluster_id="guidance:docs-credential-security",
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "The team discovers that an API credential has leaked. "
            "According to the current credential-security guidance, "
            "what three remediation actions should the team take?"
        ),
        gold_fact_rubric=(
            "Generate a new credential.",
            (
                "Replace the old credential with the new credential "
                "everywhere it is stored or accessed."
            ),
            "Delete the old compromised credential.",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-rate-primary-status",
        cluster_id="guidance:docs-rate-limits",
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "For unauthenticated requests that fetch public data, "
            "what is the primary REST API rate limit and what identity "
            "is it associated with? Explain how primary-rate-limit "
            "status can be inspected through response headers and "
            "GET /rate_limit, including how that endpoint affects the "
            "primary and secondary limits, and whether secondary-rate-"
            "limit status can be queried directly."
        ),
        gold_fact_rubric=(
            (
                "The primary rate limit for unauthenticated requests "
                "is 60 requests per hour."
            ),
            (
                "Unauthenticated requests are associated with the "
                "originating IP address."
            ),
            (
                "Primary rate-limit status can be inspected using "
                "rate-limit response headers."
            ),
            (
                "GET /rate_limit can also check rate-limit status and "
                "does not count against the primary rate limit, although "
                "it can count against the secondary rate limit."
            ),
            (
                "There is no way to directly check the status of the "
                "secondary rate limit."
            ),
        ),
        evidence_terms=(
            "Primary rate limit for unauthenticated users",
            "Checking the status of your rate limit",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-rate-actions-secondary-retry",
        cluster_id="guidance:docs-rate-limits",
        scenario_class=(
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE
        ),
        query=(
            "A GitHub Actions workflow uses GITHUB_TOKEN and later "
            "receives a secondary-rate-limit failure. What primary "
            "hourly budget applies to GITHUB_TOKEN, including the "
            "Enterprise Cloud case, and what retry sequence should "
            "the client follow for the secondary-limit response?"
        ),
        gold_fact_rubric=(
            (
                "GITHUB_TOKEN has a primary rate limit of 1,000 "
                "requests per hour per repository."
            ),
            (
                "For resources belonging to a GitHub Enterprise Cloud "
                "account, the GITHUB_TOKEN limit is 15,000 requests "
                "per hour per repository."
            ),
            (
                "A secondary-rate-limit failure may return HTTP 403 "
                "or 429."
            ),
            (
                "If retry-after is present, the client should wait "
                "that many seconds before retrying."
            ),
            (
                "If x-ratelimit-remaining is zero, the client should "
                "wait until x-ratelimit-reset."
            ),
            (
                "Otherwise the client should wait at least one minute, "
                "use exponentially increasing waits if failures continue, "
                "and stop after a bounded number of retries."
            ),
        ),
        evidence_terms=(
            "Primary rate limit for `GITHUB_TOKEN` in GitHub Actions",
            "## Exceeding the rate limit",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-actions-repo-registration-scope",
        cluster_id=(
            "openapi-pair:actions/create-registration-token-for-repo"
        ),
        scenario_class=(
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION
        ),
        query=(
            "Under the current repository self-hosted-runner "
            "registration-token operation, what repository authority "
            "must the authenticated user have, and what scope is "
            "required for OAuth tokens or classic personal access tokens?"
        ),
        gold_fact_rubric=(
            (
                "The authenticated user must have admin access to "
                "the repository."
            ),
            (
                "OAuth tokens and classic personal access tokens need "
                "the repo scope."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-actions-repo-registration-token",
        cluster_id=(
            "openapi-pair:actions/create-registration-token-for-repo"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current GitHub REST contract, which method and "
            "endpoint create a self-hosted runner registration token "
            "for a repository, how long does that token remain valid, "
            "and what successful status is documented?"
        ),
        gold_fact_rubric=(
            (
                "The operation uses POST "
                "/repos/{owner}/{repo}/actions/runners/registration-token."
            ),
            "The registration token expires after one hour.",
            "The successful response status is HTTP 201.",
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-workflow-dispatch-current-contract",
        cluster_id=(
            "openapi-pair:actions/create-workflow-dispatch"
        ),
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy client sends return_run_details=false when "
            "creating a workflow dispatch and expects HTTP 204. Under "
            "the frozen current 2026-03-10 operation contract, is "
            "return_run_details part of the request schema, and what "
            "successful response is documented instead?"
        ),
        gold_fact_rubric=(
            (
                "The current request schema does not contain the "
                "return_run_details property."
            ),
            (
                "The current operation documents HTTP 200 as the "
                "successful response."
            ),
            (
                "The HTTP 200 response includes the workflow run ID "
                "and URLs."
            ),
            (
                "The current operation does not document the historical "
                "HTTP 204 response."
            ),
        ),
        forbid_historical=True,
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-workflow-dispatch-requirements",
        cluster_id=(
            "openapi-pair:actions/create-workflow-dispatch"
        ),
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "What must be configured before the workflow-dispatch "
            "REST endpoint can manually trigger a workflow, what "
            "required request field identifies the git reference, "
            "what forms may that reference take, how many input "
            "properties may be supplied, and what happens to configured "
            "default input properties when inputs are omitted?"
        ),
        gold_fact_rubric=(
            (
                "The workflow must be configured to run when the "
                "workflow_dispatch event occurs."
            ),
            "The request body requires the ref field.",
            "The ref may be a branch or tag name.",
            "The inputs object may contain at most 25 properties.",
            (
                "Defaults configured in the workflow file are used "
                "when corresponding inputs are omitted."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-sub-issue-request-contract",
        cluster_id="openapi-pair:issues/add-sub-issue",
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For the current Add sub-issue operation, what HTTP method "
            "and endpoint are used, which request-body field is required, "
            "what ownership constraint applies to the sub-issue, and "
            "what does replace_parent=true mean?"
        ),
        gold_fact_rubric=(
            (
                "The operation uses POST "
                "/repos/{owner}/{repo}/issues/{issue_number}/sub_issues."
            ),
            "The request body requires sub_issue_id.",
            (
                "The sub-issue must belong to the same repository owner "
                "as the parent issue."
            ),
            (
                "replace_parent=true instructs the operation to replace "
                "the sub-issue's current parent issue."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-sub-issue-media-response",
        cluster_id="openapi-pair:issues/add-sub-issue",
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "For Add sub-issue, what status indicates success, what "
            "body representation is returned by the default raw media "
            "type, and what body representations are included by the "
            "full media type?"
        ),
        gold_fact_rubric=(
            "The successful response status is HTTP 201.",
            (
                "application/vnd.github.raw+json is the default and "
                "returns the raw Markdown body in body."
            ),
            (
                "application/vnd.github.full+json includes body, "
                "body_text, and body_html."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-pull-mergeable-null-refusal",
        cluster_id="openapi-pair:pulls/get",
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "A Get pull request response contains mergeable=null. "
            "Using only that observed value, tell me definitively "
            "whether this pull request is mergeable or unmergeable."
        ),
        refusal_review_intent_id=(
            "tuning-get-pull-mergeable-null"
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-pull-merge-commit-semantics",
        cluster_id="openapi-pair:pulls/get",
        scenario_class=(
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE
        ),
        query=(
            "Explain how merge_commit_sha should be interpreted for "
            "Get pull request before the pull request is merged and "
            "after merge-commit, squash, or rebase merging."
        ),
        gold_fact_rubric=(
            (
                "Before merging, merge_commit_sha holds the SHA of "
                "the test merge commit."
            ),
            (
                "If the pull request is merged with a merge commit, "
                "merge_commit_sha becomes the SHA of that merge commit."
            ),
            (
                "If squash merged, merge_commit_sha represents the "
                "squashed commit on the base branch."
            ),
            (
                "If rebased, merge_commit_sha represents the commit "
                "that the base branch was updated to."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-update-pull-422-refusal",
        cluster_id="openapi-pair:pulls/update",
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "An Update pull request request returns HTTP 422, but I "
            "have no response body or request-field details. Which exact "
            "field or validation condition caused this particular failure?"
        ),
        refusal_review_intent_id=(
            "tuning-update-pull-422-cause"
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-update-pull-scope",
        cluster_id="openapi-pair:pulls/update",
        scenario_class=(
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION
        ),
        query=(
            "For the current Update pull request operation, what access "
            "is required to update a pull request in a public repository, "
            "what additional membership condition applies to an "
            "organization-owned repository, and what restrictions apply "
            "when changing the base branch?"
        ),
        gold_fact_rubric=(
            (
                "Updating a pull request in a public repository requires "
                "write access to the head or source branch."
            ),
            (
                "For an organization-owned repository, the user must be "
                "a member of the organization that owns the repository."
            ),
            (
                "A new base value must name an existing branch in the "
                "current repository."
            ),
            (
                "The base branch cannot be changed to point to another "
                "repository."
            ),
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-create-in-org-451-refusal",
        cluster_id="openapi-pair:repos/create-in-org",
        scenario_class=(
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE
        ),
        query=(
            "A Create an organization repository request returns "
            "HTTP 451. With only that status and no response details, "
            "what exact condition triggered this particular 451?"
        ),
        refusal_review_intent_id=(
            "tuning-create-in-org-451-cause"
        ),
    ),
    TuningCaseSpec(
        case_id="phase4-tuning-create-in-org-current-451",
        cluster_id="openapi-pair:repos/create-in-org",
        scenario_class=(
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION
        ),
        query=(
            "A legacy contract for Create an organization repository "
            "does not list HTTP 451. Under the frozen current "
            "2026-03-10 operation contract, is HTTP 451 now a documented "
            "response, and how is that response represented?"
        ),
        gold_fact_rubric=(
            (
                "The current Create an organization repository contract "
                "documents HTTP 451."
            ),
            (
                "The HTTP 451 response references the shared "
                "validation_failed response contract."
            ),
        ),
        forbid_historical=True,
    ),
)

EXPECTED_SCENARIOS_BY_CLUSTER: dict[
    str,
    Counter[ScenarioClass],
] = {
    "guidance:docs-authentication": Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    "guidance:docs-credential-security": Counter(
        (
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "guidance:docs-rate-limits": Counter(
        (
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        )
    ),
    (
        "openapi-pair:actions/create-registration-token-for-repo"
    ): Counter(
        (
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    (
        "openapi-pair:actions/create-workflow-dispatch"
    ): Counter(
        (
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:issues/add-sub-issue": Counter(
        (
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:pulls/get": Counter(
        (
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        )
    ),
    "openapi-pair:pulls/update": Counter(
        (
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        )
    ),
    "openapi-pair:repos/create-in-org": Counter(
        (
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
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
        raise Phase4TuningCaseError(f"SHA sidecar mismatch: {path}")

    return content, digest


def _read_verified_evidence(
    repo_root: Path,
    evidence: Phase4AuthoringEvidence,
) -> str:
    path = repo_root / Path(evidence.content_path)

    content = path.read_bytes()

    if len(content) != evidence.byte_count:
        raise Phase4TuningCaseError(
            f"authoring evidence byte-count mismatch: {evidence.evidence_id}"
        )

    if _sha256_bytes(content) != evidence.content_sha256:
        raise Phase4TuningCaseError(f"authoring evidence SHA mismatch: {evidence.evidence_id}")

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Phase4TuningCaseError(
            f"authoring evidence is not UTF-8: {evidence.evidence_id}"
        ) from exc


def _select_current_evidence(
    repo_root: Path,
    cluster: Phase4AuthoringClusterReview,
    spec: TuningCaseSpec,
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
                raise Phase4TuningCaseError(
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
        raise Phase4TuningCaseError(
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
        raise Phase4TuningCaseError(
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
    spec: TuningCaseSpec,
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
            raise Phase4TuningCaseError(
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
            raise Phase4TuningCaseError("refusal case missing semantic-review intent")

        review_by_id = {item.intent_id: item for item in refusal_review.items}

        review_item = review_by_id.get(spec.refusal_review_intent_id)

        if review_item is None:
            raise Phase4TuningCaseError(
                "refusal semantic review "
                "does not contain case intent: "
                f"{spec.refusal_review_intent_id}"
            )

        if review_item.verdict == "ANSWERABLE_ELSEWHERE":
            raise Phase4TuningCaseError(
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
        data_role=EvaluationRole.TUNING,
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
        TuningCaseRecord,
        ...,
    ],
) -> str:
    lines = [
        "# Phase 4C TUNING Canonical Case Candidate V1",
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


def materialize_phase4_tuning_cases(
    repo_root: Path,
) -> tuple[
    Phase4TuningCaseSuite,
    str,
    str,
]:
    dossier_bytes, dossier_sha = _read_verified_artifact(repo_root / _DOSSIER_PATH)

    dossier = Phase4AuthoringDossier.model_validate_json(dossier_bytes)

    if dossier.case_authoring_authorized is not True:
        raise Phase4TuningCaseError("authoring dossier does not authorize case authoring")

    review_bytes, review_sha = _read_verified_artifact(repo_root / _REFUSAL_REVIEW_PATH)

    refusal_review = Phase4RefusalSemanticReview.model_validate_json(review_bytes)

    if refusal_review.allocation_survives is not True:
        raise Phase4TuningCaseError("refusal review does not preserve allocation")

    tuning_clusters = {
        cluster.cluster_id: cluster
        for cluster in dossier.clusters
        if (cluster.evaluation_role is EvaluationRole.TUNING)
    }

    if set(tuning_clusters) != set(EXPECTED_SCENARIOS_BY_CLUSTER):
        raise Phase4TuningCaseError("TUNING cluster set drifted from reviewed allocation")

    if len(CASE_SPECS) != 18:
        raise Phase4TuningCaseError("expected exactly 18 TUNING case specs")

    spec_scenarios = {
        cluster_id: Counter(
            spec.scenario_class for spec in CASE_SPECS if (spec.cluster_id == cluster_id)
        )
        for cluster_id in tuning_clusters
    }

    if spec_scenarios != EXPECTED_SCENARIOS_BY_CLUSTER:
        raise Phase4TuningCaseError(
            "case-spec allocation does not match reviewed TUNING allocation"
        )

    records = tuple(
        TuningCaseRecord(
            cluster_id=spec.cluster_id,
            case=_build_case(
                repo_root=repo_root,
                spec=spec,
                cluster=(tuning_clusters[spec.cluster_id]),
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

    suite = Phase4TuningCaseSuite(
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
    ) = materialize_phase4_tuning_cases(repo_root)

    print(f"PHASE4C_TUNING_CASE_COUNT={suite.case_count}")

    print(f"PHASE4C_TUNING_CLUSTER_COUNT={suite.cluster_count}")

    print(f"PHASE4C_TUNING_SINGLE_SOURCE_COUNT={suite.current_single_source_count}")

    print(f"PHASE4C_TUNING_MULTI_EVIDENCE_COUNT={suite.current_multi_evidence_count}")

    print(f"PHASE4C_TUNING_FRESHNESS_COUNT={suite.version_freshness_count}")

    print(f"PHASE4C_TUNING_AUTHORITY_SCOPE_COUNT={suite.authority_scope_count}")

    print(f"PHASE4C_TUNING_MUST_REFUSE_COUNT={suite.must_refuse_count}")

    print("PHASE4C_TUNING_CASE_AUTHORING_COMPLETE=true")

    print("PHASE4C_TUNING_SUITE_FROZEN=false")

    print("PHASE4_BASELINE_AUTHORIZED=false")

    print(f"PHASE4C_TUNING_CASES_JSON_SHA256={json_sha}")

    print(f"PHASE4C_TUNING_CASES_MARKDOWN_SHA256={markdown_sha}")


if __name__ == "__main__":
    main()

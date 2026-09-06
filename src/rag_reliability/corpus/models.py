"""Phase 3 corpus acquisition and operation-catalog contracts."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from rag_reliability.contracts.base import ContractModel, GitCommitSha, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import AuthorityLevel, DataRole, SourceState

GitBlobSha1 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
HttpMethod = Literal["delete", "get", "head", "options", "patch", "post", "put", "trace"]
SemanticOperationFamily = Literal[
    "issues",
    "pull_requests",
    "repositories_and_repository_webhooks",
    "actions",
]


class PinnedUpstreamFile(ContractModel):
    """One exact upstream file selected from a frozen repository commit."""

    source_id: NonEmptyStr
    repository: Literal["github/docs", "github/rest-api-description"]
    commit_sha: GitCommitSha
    path: NonEmptyStr
    expected_git_blob_sha1: GitBlobSha1
    source_license: NonEmptyStr
    media_type: Literal["markdown", "openapi_yaml"]
    authority_level: AuthorityLevel
    source_state: SourceState
    product_scope: Literal["api.github.com"] = "api.github.com"
    api_version_or_snapshot: NonEmptyStr
    data_role: DataRole


class CorpusSourceSelectionPlan(ContractModel):
    """Reviewable source-selection plan bound to the Phase 0 corpus snapshot."""

    plan_version: Literal["phase3a-source-selection-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    target_api_version: Literal["2026-03-10"]
    comparison_api_version: Literal["2022-11-28"]
    files: tuple[PinnedUpstreamFile, ...] = Field(min_length=12, max_length=12)

    @model_validator(mode="after")
    def validate_frozen_selection(self) -> CorpusSourceSelectionPlan:
        source_ids = tuple(item.source_id for item in self.files)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source selection IDs must be unique")

        repository_paths = tuple((item.repository, item.path) for item in self.files)
        if len(repository_paths) != len(set(repository_paths)):
            raise ValueError("source selection repository paths must be unique")

        docs = tuple(item for item in self.files if item.repository == "github/docs")
        openapi = tuple(
            item for item in self.files if item.repository == "github/rest-api-description"
        )
        if len(docs) != 10 or len(openapi) != 2:
            raise ValueError("Phase 3A selection requires 10 authored docs and 2 OpenAPI files")

        for item in docs:
            if item.commit_sha != "ec3629a841129ae28189d7bb2274a7b3d40c5095":
                raise ValueError("GitHub Docs selection is not pinned to the frozen commit")
            if item.media_type != "markdown":
                raise ValueError("GitHub Docs selection must use markdown media type")
            if item.authority_level is not AuthorityLevel.AUTHORITATIVE:
                raise ValueError("GitHub Docs selection must be authoritative")
            if item.source_state is not SourceState.CURRENT:
                raise ValueError("GitHub Docs selection must be current")
            if item.data_role is not DataRole.CORPUS_SOURCE:
                raise ValueError("GitHub Docs selection must use corpus_source role")
            if item.api_version_or_snapshot != self.target_api_version:
                raise ValueError("GitHub Docs selection must bind to the target API version")
            if not item.path.startswith(
                (
                    "content/rest/about-the-rest-api/",
                    "content/rest/authentication/",
                    "content/rest/using-the-rest-api/",
                )
            ):
                raise ValueError("GitHub Docs selection path is outside the frozen prefixes")

        for item in openapi:
            if item.commit_sha != "3cef12e8a02d612ad032473d4fb87266f2befeae":
                raise ValueError("OpenAPI selection is not pinned to the frozen commit")
            if item.media_type != "openapi_yaml":
                raise ValueError("OpenAPI selection must use openapi_yaml media type")

        current = tuple(
            item
            for item in openapi
            if item.api_version_or_snapshot == self.target_api_version
        )
        historical = tuple(
            item
            for item in openapi
            if item.api_version_or_snapshot == self.comparison_api_version
        )
        if len(current) != 1 or len(historical) != 1:
            raise ValueError("selection must contain one current and one historical OpenAPI file")

        current_item = current[0]
        if current_item.authority_level is not AuthorityLevel.AUTHORITATIVE:
            raise ValueError("current OpenAPI file must be authoritative")
        if current_item.source_state is not SourceState.CURRENT:
            raise ValueError("current OpenAPI file must use current source state")
        if current_item.data_role is not DataRole.CORPUS_SOURCE:
            raise ValueError("current OpenAPI file must use corpus_source role")

        historical_item = historical[0]
        if historical_item.authority_level is not AuthorityLevel.HISTORICAL:
            raise ValueError("historical OpenAPI file must use historical authority")
        if historical_item.source_state is not SourceState.HISTORICAL_COMPARISON:
            raise ValueError("historical OpenAPI file must use historical_comparison state")
        if historical_item.data_role is not DataRole.HISTORICAL_SOURCE:
            raise ValueError("historical OpenAPI file must use historical_source role")

        return self


class AcquiredFileReceipt(ContractModel):
    """Hash-only custody receipt for one acquired upstream file."""

    source_id: NonEmptyStr
    repository: NonEmptyStr
    commit_sha: GitCommitSha
    path: NonEmptyStr
    expected_git_blob_sha1: GitBlobSha1
    observed_git_blob_sha1: GitBlobSha1
    content_sha256: Sha256
    byte_count: int = Field(gt=0)
    cache_path: NonEmptyStr


class AcquisitionReceipt(ContractModel):
    receipt_version: Literal["phase3a-acquisition-receipt-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    files: tuple[AcquiredFileReceipt, ...] = Field(min_length=12, max_length=12)


class OperationCatalogEntry(ContractModel):
    operation_id: NonEmptyStr
    method: HttpMethod
    path: NonEmptyStr
    tags: tuple[NonEmptyStr, ...]
    semantic_family_candidate: SemanticOperationFamily


class ApiVersionOperationCatalog(ContractModel):
    api_version: NonEmptyStr
    source_id: NonEmptyStr
    source_git_blob_sha1: GitBlobSha1
    operations: tuple[OperationCatalogEntry, ...]

    @model_validator(mode="after")
    def validate_unique_operations(self) -> ApiVersionOperationCatalog:
        operation_ids = tuple(item.operation_id for item in self.operations)
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("operation catalog contains duplicate operation IDs")
        return self


class Phase3aOperationCatalogCandidate(ContractModel):
    """Candidate-only operation catalog produced from exact pinned OpenAPI bytes."""

    catalog_version: Literal["phase3a-operation-catalog-candidate-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    selection_status: Literal["candidate_only"] = "candidate_only"
    ingestion_authorized: Literal[False] = False
    release_eligible: Literal[False] = False
    current: ApiVersionOperationCatalog
    historical: ApiVersionOperationCatalog

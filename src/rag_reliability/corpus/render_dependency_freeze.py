"""Frozen render-dependency custody for the Phase 3B authored corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.render_dependencies import (
    Phase3bRenderDependencyClosureCandidate,
    RenderDependencyFileReceipt,
)

_EXPECTED_CLOSURE_SHA256: Literal[
    "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"
] = "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"

_EXPECTED_SOURCE_AUDIT_SHA256: Literal[
    "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"
] = "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"

_SUPERSEDED_MANIFEST_SHA256: Literal[
    "61a3a040361dbafd156eb2698321a30972649ef596846f6e302d983dc77a3d59"
] = "61a3a040361dbafd156eb2698321a30972649ef596846f6e302d983dc77a3d59"

_EXPECTED_PATHS: tuple[str, ...] = (
    "data/reusables/getting-started/bearer-vs-token.md",
    "data/reusables/organizations/api-insights-learn-about.md",
    "data/reusables/rest-api/about-api-versions.md",
    "data/reusables/rest-api/breaking-changes-changelog.md",
    "data/reusables/rest-api/primary-rate-limit-authenticated-users.md",
    "data/reusables/rest-api/primary-rate-limit-github-app-installations.md",
    "data/reusables/rest-api/primary-rate-limit-github-token-in-actions.md",
    "data/reusables/rest-api/primary-rate-limit-oauth-apps.md",
    "data/reusables/rest-api/primary-rate-limit-unauthenticated-users.md",
    "data/reusables/rest-api/secondary-rate-limit-rest-graphql.md",
    "data/reusables/rest-api/version-header.md",
    "data/reusables/user-settings/developer_settings.md",
    "data/reusables/user-settings/token_access_capabilities.md",
    "data/variables/enterprise.yml",
    "data/variables/location.yml",
    "data/variables/product.yml",
    "data/variables/release-phases.yml",
)

_EXPECTED_LIQUID_TAGS: tuple[str, ...] = (
    "assign",
    "cli",
    "curl",
    "data",
    "else",
    "elsif",
    "endcli",
    "endcurl",
    "endfor",
    "endif",
    "endjavascript",
    "endraw",
    "for",
    "if",
    "ifversion",
    "javascript",
    "octicon",
    "raw",
)

_EXPECTED_TEMPLATE_VARIABLES: tuple[str, ...] = (
    "allVersions[currentVersion].latestApiVersion",
    "apiVersion",
    "defaultRestApiVersion",
    "initialRestVersioningReleaseDate",
    "initialRestVersioningReleaseDateLong",
    "secrets.GITHUB_TOKEN",
    'versionData.end_of_support | default: "Not yet scheduled"',
)


class Phase3bFrozenRenderDependencySet(ContractModel):
    """Exact dependency files accepted for the constrained authored-doc renderer."""

    freeze_version: Literal["phase3b-render-dependency-freeze-v2"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    github_docs_commit_sha: Literal[
        "ec3629a841129ae28189d7bb2274a7b3d40c5095"
    ]
    source_render_audit_sha256: Literal[
        "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"
    ]
    source_dependency_closure_sha256: Literal[
        "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"
    ]
    supersedes_freeze_version: Literal["phase3b-render-dependency-freeze-v1"]
    supersedes_manifest_sha256: Literal[
        "61a3a040361dbafd156eb2698321a30972649ef596846f6e302d983dc77a3d59"
    ]
    supersession_reason: Literal["liquid_trim_marker_parser_repair"]
    resolved_data_references: tuple[NonEmptyStr, ...] = Field(min_length=41, max_length=41)
    dependency_files: tuple[RenderDependencyFileReceipt, ...] = Field(
        min_length=17,
        max_length=17,
    )
    required_liquid_tags: tuple[NonEmptyStr, ...]
    required_template_variables: tuple[NonEmptyStr, ...]
    transitive_reference_count: Literal[0] = 0
    freeze_status: Literal["frozen"] = "frozen"
    render_context_review_required: Literal[True] = True
    rendering_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_frozen_evidence(self) -> Phase3bFrozenRenderDependencySet:
        paths = tuple(item.path for item in self.dependency_files)
        if paths != _EXPECTED_PATHS:
            raise ValueError("frozen render dependency paths do not match reviewed closure")
        if self.required_liquid_tags != _EXPECTED_LIQUID_TAGS:
            raise ValueError("frozen Liquid tag requirements do not match reviewed closure")
        if self.required_template_variables != _EXPECTED_TEMPLATE_VARIABLES:
            raise ValueError("frozen template-variable requirements do not match reviewed closure")
        return self


class RenderDependencyFreezeReceipt(ContractModel):
    """Compact custody receipt for the frozen Phase 3B render dependencies."""

    receipt_version: Literal["phase3b-render-dependency-freeze-receipt-v2"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    frozen_manifest_sha256: Sha256
    source_render_audit_sha256: Literal[
        "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"
    ]
    source_dependency_closure_sha256: Literal[
        "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"
    ]
    supersedes_manifest_sha256: Literal[
        "61a3a040361dbafd156eb2698321a30972649ef596846f6e302d983dc77a3d59"
    ]
    resolved_reference_count: Literal[41] = 41
    dependency_file_count: Literal[17] = 17
    reusable_file_count: Literal[13] = 13
    variable_file_count: Literal[4] = 4
    required_liquid_tag_count: Literal[18] = 18
    required_template_variable_count: Literal[7] = 7
    transitive_reference_count: Literal[0] = 0
    freeze_status: Literal["frozen"] = "frozen"
    render_context_review_required: Literal[True] = True
    rendering_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False


def freeze_render_dependencies(
    candidate: Phase3bRenderDependencyClosureCandidate,
    *,
    candidate_sha256: str,
) -> Phase3bFrozenRenderDependencySet:
    """Freeze the corrected reviewed candidate without authorizing rendering."""

    if candidate_sha256 != _EXPECTED_CLOSURE_SHA256:
        raise ValueError("render dependency closure hash does not match reviewed candidate")
    if candidate.source_render_audit_sha256 != _EXPECTED_SOURCE_AUDIT_SHA256:
        raise ValueError("render dependency source audit hash does not match reviewed audit")
    if len(candidate.resolved_data_references) != 41:
        raise ValueError("render dependency closure must resolve exactly 41 references")
    if candidate.transitive_data_references:
        raise ValueError("reviewed render dependency closure must have no transitive references")
    if tuple(item.path for item in candidate.dependency_files) != _EXPECTED_PATHS:
        raise ValueError("render dependency file paths do not match reviewed candidate")
    if candidate.render_liquid_tags != _EXPECTED_LIQUID_TAGS:
        raise ValueError("render dependency Liquid tags do not match reviewed candidate")
    if candidate.render_template_variables != _EXPECTED_TEMPLATE_VARIABLES:
        raise ValueError("render dependency template variables do not match reviewed candidate")

    reusable_file_count = sum(
        item.media_type == "markdown_reusable" for item in candidate.dependency_files
    )
    variable_file_count = sum(
        item.media_type == "yaml_variables" for item in candidate.dependency_files
    )
    if reusable_file_count != 13 or variable_file_count != 4:
        raise ValueError("render dependency media-type counts do not match reviewed candidate")

    return Phase3bFrozenRenderDependencySet(
        freeze_version="phase3b-render-dependency-freeze-v2",
        snapshot_id=candidate.snapshot_id,
        github_docs_commit_sha=candidate.github_docs_commit_sha,
        source_render_audit_sha256=_EXPECTED_SOURCE_AUDIT_SHA256,
        source_dependency_closure_sha256=_EXPECTED_CLOSURE_SHA256,
        supersedes_freeze_version="phase3b-render-dependency-freeze-v1",
        supersedes_manifest_sha256=_SUPERSEDED_MANIFEST_SHA256,
        supersession_reason="liquid_trim_marker_parser_repair",
        resolved_data_references=candidate.resolved_data_references,
        dependency_files=candidate.dependency_files,
        required_liquid_tags=candidate.render_liquid_tags,
        required_template_variables=candidate.render_template_variables,
    )


def build_freeze_receipt(
    frozen: Phase3bFrozenRenderDependencySet,
    *,
    frozen_manifest_sha256: str,
) -> RenderDependencyFreezeReceipt:
    """Build a compact receipt for the corrected frozen dependency manifest."""

    return RenderDependencyFreezeReceipt(
        receipt_version="phase3b-render-dependency-freeze-receipt-v2",
        snapshot_id=frozen.snapshot_id,
        frozen_manifest_sha256=frozen_manifest_sha256,
        source_render_audit_sha256=frozen.source_render_audit_sha256,
        source_dependency_closure_sha256=frozen.source_dependency_closure_sha256,
        supersedes_manifest_sha256=frozen.supersedes_manifest_sha256,
    )


def frozen_manifest_path(repo_root: Path) -> Path:
    """Return the v2 manifest path for the corrected Phase 3B renderer boundary."""

    return (
        repo_root
        / "datasets"
        / "source_manifests"
        / "phase3b_render_dependency_freeze_v2.json"
    )

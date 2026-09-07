"""Frozen deterministic render policy for the Phase 3B authored corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.render_semantics_review import Phase3bRenderSemanticsReview

DocsCommitSha = Literal["ec3629a841129ae28189d7bb2274a7b3d40c5095"]
DependencyManifestSha = Literal[
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
]
ContextReviewSha = Literal[
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
]
SemanticsReviewSha = Literal[
    "25cae92b748ec1e40674c6813772c2c258b366e47f702da682b00dc0fd912368"
]

_DOCS_COMMIT: DocsCommitSha = "ec3629a841129ae28189d7bb2274a7b3d40c5095"
_DEPENDENCY_MANIFEST_SHA: DependencyManifestSha = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
)
_CONTEXT_REVIEW_SHA: ContextReviewSha = (
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
)
_SEMANTICS_REVIEW_SHA: SemanticsReviewSha = (
    "25cae92b748ec1e40674c6813772c2c258b366e47f702da682b00dc0fd912368"
)

_EXPECTED_ASSIGNMENT = (
    "assign:versionData = tables.rest-api-versions.versions[apiVersion]"
)
_EXPECTED_ITERATION = "for:apiVersion in allVersions[currentVersion].apiVersions"
_EXPECTED_CONDITIONALS: tuple[str, ...] = (
    "elsif:ghes",
    'if:query.apiVersion == nil or "2022-11-28" <= query.apiVersion',
    'if:query.apiVersion == nil or "2026-03-10" <= query.apiVersion',
    "ifversion:api-insights",
    "ifversion:enterprise-installed-apps",
    "ifversion:fpt",
    "ifversion:fpt or ghec",
    "ifversion:ghec",
    "ifversion:ghec or ghes",
    "ifversion:ghes",
    "ifversion:ghes = 3.21",
    "ifversion:ghes = 3.22",
    "ifversion:not fpt",
)
_EXPECTED_VARIANTS: tuple[str, ...] = (
    "cli:<none>",
    "curl:<none>",
    "javascript:<none>",
)
_EXPECTED_PRESENTATION = 'octicon:"code" aria-hidden="true" aria-label="code"'


class ConditionalDecision(ContractModel):
    """Frozen truth value for one reviewed conditional expression."""

    expression: NonEmptyStr
    result: bool


class ApiVersionRow(ContractModel):
    """Frozen API-version row used by the only reviewed Liquid loop."""

    api_version: Literal["2026-03-10", "2022-11-28"]
    end_of_support: NonEmptyStr


class TemplateBinding(ContractModel):
    """Deterministic resolution rule for one reviewed template variable."""

    variable: NonEmptyStr
    mode: Literal["static", "loop_variable", "loop_derived", "raw_literal_only"]
    static_value: str | None = None

    @model_validator(mode="after")
    def validate_static_value(self) -> TemplateBinding:
        if self.mode == "static" and self.static_value is None:
            raise ValueError("static template binding requires a value")
        if self.mode != "static" and self.static_value is not None:
            raise ValueError("non-static template binding cannot carry a static value")
        return self


class Phase3bRenderPolicyFreeze(ContractModel):
    """Constrained render policy authorized for the exact reviewed Phase 3B surface."""

    policy_version: Literal["phase3b-render-policy-freeze-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    github_docs_commit_sha: DocsCommitSha
    source_dependency_manifest_sha256: DependencyManifestSha
    source_render_context_review_sha256: ContextReviewSha
    source_render_semantics_review_sha256: SemanticsReviewSha
    target_host: Literal["api.github.com"] = "api.github.com"
    current_version: Literal["free-pro-team@latest"] = "free-pro-team@latest"
    version_short_name: Literal["fpt"] = "fpt"
    query_api_version: None = None
    supported_api_versions: tuple[
        Literal["2026-03-10"],
        Literal["2022-11-28"],
    ] = ("2026-03-10", "2022-11-28")
    latest_api_version: Literal["2026-03-10"] = "2026-03-10"
    default_rest_api_version: Literal["2022-11-28"] = "2022-11-28"
    initial_rest_versioning_release_date: Literal["2026-03-10"] = "2026-03-10"
    initial_rest_versioning_release_date_long: Literal["Tue, 10 Mar 2026"] = (
        "Tue, 10 Mar 2026"
    )
    api_version_rows: tuple[ApiVersionRow, ...] = Field(min_length=2, max_length=2)
    conditional_decisions: tuple[ConditionalDecision, ...] = Field(
        min_length=13,
        max_length=13,
    )
    assignment_expression: Literal[
        "versionData = tables.rest-api-versions.versions[apiVersion]"
    ]
    iteration_expression: Literal[
        "apiVersion in allVersions[currentVersion].apiVersions"
    ]
    template_bindings: tuple[TemplateBinding, ...] = Field(min_length=7, max_length=7)
    data_reference_policy: Literal["substitute_exact_frozen_41_references_only"] = (
        "substitute_exact_frozen_41_references_only"
    )
    variant_block_policy: Literal[
        "preserve_inner_content_strip_wrapper_in_source_order"
    ] = "preserve_inner_content_strip_wrapper_in_source_order"
    raw_block_policy: Literal["preserve_inner_content_literal_no_nested_evaluation"] = (
        "preserve_inner_content_literal_no_nested_evaluation"
    )
    secret_resolution_policy: Literal["forbidden"] = "forbidden"
    octicon_policy: Literal["replace_exact_observed_icon_with_semantic_label_code"] = (
        "replace_exact_observed_icon_with_semantic_label_code"
    )
    autotitle_policy: Literal["replace_autotitle_label_with_target_path_preserve_href"] = (
        "replace_autotitle_label_with_target_path_preserve_href"
    )
    unknown_construct_policy: Literal["fail_closed"] = "fail_closed"
    unknown_expression_policy: Literal["fail_closed"] = "fail_closed"
    site_renderer_equivalence_claimed: Literal[False] = False
    freeze_status: Literal["frozen"] = "frozen"
    rendering_authorized: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_policy_surface(self) -> Phase3bRenderPolicyFreeze:
        expressions = tuple(item.expression for item in self.conditional_decisions)
        if expressions != _EXPECTED_CONDITIONALS:
            raise ValueError("conditional policy does not match reviewed semantics")
        expected_results = (
            False,
            True,
            True,
            False,
            False,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
        )
        if tuple(item.result for item in self.conditional_decisions) != expected_results:
            raise ValueError("conditional truth table does not match FPT render context")

        expected_rows = (
            ("2026-03-10", "Not yet scheduled"),
            ("2022-11-28", "March 10, 2028"),
        )
        observed_rows = tuple(
            (item.api_version, item.end_of_support) for item in self.api_version_rows
        )
        if observed_rows != expected_rows:
            raise ValueError("API version rows do not match pinned source context")

        expected_bindings = (
            ("allVersions[currentVersion].latestApiVersion", "static", "2026-03-10"),
            ("apiVersion", "loop_variable", None),
            ("defaultRestApiVersion", "static", "2022-11-28"),
            ("initialRestVersioningReleaseDate", "static", "2026-03-10"),
            ("initialRestVersioningReleaseDateLong", "static", "Tue, 10 Mar 2026"),
            ("secrets.GITHUB_TOKEN", "raw_literal_only", None),
            (
                'versionData.end_of_support | default: "Not yet scheduled"',
                "loop_derived",
                None,
            ),
        )
        observed_bindings = tuple(
            (item.variable, item.mode, item.static_value) for item in self.template_bindings
        )
        if observed_bindings != expected_bindings:
            raise ValueError("template bindings do not match reviewed render context")
        return self


class RenderPolicyFreezeReceipt(ContractModel):
    """Compact custody receipt for the frozen render policy."""

    receipt_version: Literal["phase3b-render-policy-freeze-receipt-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    render_policy_manifest_sha256: Sha256
    source_dependency_manifest_sha256: DependencyManifestSha
    source_render_context_review_sha256: ContextReviewSha
    source_render_semantics_review_sha256: SemanticsReviewSha
    conditional_expression_count: Literal[13] = 13
    assignment_expression_count: Literal[1] = 1
    iteration_expression_count: Literal[1] = 1
    variant_argument_count: Literal[3] = 3
    presentation_argument_count: Literal[1] = 1
    autotitle_target_count: Literal[56] = 56
    freeze_status: Literal["frozen"] = "frozen"
    rendering_authorized: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False


def freeze_render_policy(
    semantics: Phase3bRenderSemanticsReview,
    *,
    semantics_review_sha256: str,
    context_review_sha256: str,
    dependency_manifest_sha256: str,
) -> Phase3bRenderPolicyFreeze:
    """Freeze the deterministic policy for exactly the reviewed syntax surface."""

    if semantics_review_sha256 != _SEMANTICS_REVIEW_SHA:
        raise ValueError("render semantics hash does not match accepted v2 review")
    if context_review_sha256 != _CONTEXT_REVIEW_SHA:
        raise ValueError("render context hash does not match accepted v2 review")
    if dependency_manifest_sha256 != _DEPENDENCY_MANIFEST_SHA:
        raise ValueError("dependency manifest hash does not match accepted v2 freeze")
    if semantics.source_render_context_review_sha256 != _CONTEXT_REVIEW_SHA:
        raise ValueError("semantics review is not bound to accepted context evidence")
    if semantics.source_dependency_manifest_sha256 != _DEPENDENCY_MANIFEST_SHA:
        raise ValueError("semantics review is not bound to accepted dependency evidence")

    records = {
        (record.construct_kind, f"{record.construct_name}:{record.value}")
        for record in semantics.records
    }
    expected_semantics = {
        ("assignment_expression", _EXPECTED_ASSIGNMENT),
        ("iteration_expression", _EXPECTED_ITERATION),
        *(("conditional_expression", value) for value in _EXPECTED_CONDITIONALS),
        *(("variant_argument", value) for value in _EXPECTED_VARIANTS),
        ("presentation_argument", _EXPECTED_PRESENTATION),
    }
    observed_non_autotitle = {
        item for item in records if item[0] != "autotitle_target"
    }
    if observed_non_autotitle != expected_semantics:
        raise ValueError("render semantic surface does not match reviewed v2 evidence")
    if semantics.autotitle_target_count != 56:
        raise ValueError("AUTOTITLE target count does not match reviewed v2 evidence")

    conditional_results = {
        "elsif:ghes": False,
        'if:query.apiVersion == nil or "2022-11-28" <= query.apiVersion': True,
        'if:query.apiVersion == nil or "2026-03-10" <= query.apiVersion': True,
        "ifversion:api-insights": False,
        "ifversion:enterprise-installed-apps": False,
        "ifversion:fpt": True,
        "ifversion:fpt or ghec": True,
        "ifversion:ghec": False,
        "ifversion:ghec or ghes": False,
        "ifversion:ghes": False,
        "ifversion:ghes = 3.21": False,
        "ifversion:ghes = 3.22": False,
        "ifversion:not fpt": False,
    }

    return Phase3bRenderPolicyFreeze(
        policy_version="phase3b-render-policy-freeze-v1",
        snapshot_id=semantics.snapshot_id,
        github_docs_commit_sha=_DOCS_COMMIT,
        source_dependency_manifest_sha256=_DEPENDENCY_MANIFEST_SHA,
        source_render_context_review_sha256=_CONTEXT_REVIEW_SHA,
        source_render_semantics_review_sha256=_SEMANTICS_REVIEW_SHA,
        api_version_rows=(
            ApiVersionRow(api_version="2026-03-10", end_of_support="Not yet scheduled"),
            ApiVersionRow(api_version="2022-11-28", end_of_support="March 10, 2028"),
        ),
        conditional_decisions=tuple(
            ConditionalDecision(expression=expression, result=conditional_results[expression])
            for expression in _EXPECTED_CONDITIONALS
        ),
        assignment_expression="versionData = tables.rest-api-versions.versions[apiVersion]",
        iteration_expression="apiVersion in allVersions[currentVersion].apiVersions",
        template_bindings=(
            TemplateBinding(
                variable="allVersions[currentVersion].latestApiVersion",
                mode="static",
                static_value="2026-03-10",
            ),
            TemplateBinding(variable="apiVersion", mode="loop_variable"),
            TemplateBinding(
                variable="defaultRestApiVersion",
                mode="static",
                static_value="2022-11-28",
            ),
            TemplateBinding(
                variable="initialRestVersioningReleaseDate",
                mode="static",
                static_value="2026-03-10",
            ),
            TemplateBinding(
                variable="initialRestVersioningReleaseDateLong",
                mode="static",
                static_value="Tue, 10 Mar 2026",
            ),
            TemplateBinding(variable="secrets.GITHUB_TOKEN", mode="raw_literal_only"),
            TemplateBinding(
                variable='versionData.end_of_support | default: "Not yet scheduled"',
                mode="loop_derived",
            ),
        ),
    )


def build_render_policy_receipt(
    policy: Phase3bRenderPolicyFreeze,
    *,
    render_policy_manifest_sha256: str,
) -> RenderPolicyFreezeReceipt:
    """Build the compact custody receipt for a frozen render policy."""

    return RenderPolicyFreezeReceipt(
        receipt_version="phase3b-render-policy-freeze-receipt-v1",
        snapshot_id=policy.snapshot_id,
        render_policy_manifest_sha256=render_policy_manifest_sha256,
        source_dependency_manifest_sha256=policy.source_dependency_manifest_sha256,
        source_render_context_review_sha256=policy.source_render_context_review_sha256,
        source_render_semantics_review_sha256=policy.source_render_semantics_review_sha256,
    )


def render_policy_manifest_path(repo_root: Path) -> Path:
    """Return the durable render-policy manifest path."""

    return repo_root / "datasets" / "source_manifests" / "phase3b_render_policy_freeze_v1.json"

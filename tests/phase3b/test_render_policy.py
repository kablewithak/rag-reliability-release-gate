from __future__ import annotations

from pathlib import Path

import pytest

from rag_reliability.corpus.render_policy import (
    freeze_render_policy,
    render_policy_manifest_path,
)
from rag_reliability.corpus.render_semantics_review import (
    Phase3bRenderSemanticsReview,
    RenderSemanticRecord,
)


def _semantics() -> Phase3bRenderSemanticsReview:
    conditionals = (
        ("elsif", "ghes"),
        ("if", 'query.apiVersion == nil or "2022-11-28" <= query.apiVersion'),
        ("if", 'query.apiVersion == nil or "2026-03-10" <= query.apiVersion'),
        ("ifversion", "api-insights"),
        ("ifversion", "enterprise-installed-apps"),
        ("ifversion", "fpt"),
        ("ifversion", "fpt or ghec"),
        ("ifversion", "ghec"),
        ("ifversion", "ghec or ghes"),
        ("ifversion", "ghes"),
        ("ifversion", "ghes = 3.21"),
        ("ifversion", "ghes = 3.22"),
        ("ifversion", "not fpt"),
    )
    records = [
        RenderSemanticRecord(
            construct_kind="assignment_expression",
            construct_name="assign",
            value="versionData = tables.rest-api-versions.versions[apiVersion]",
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        ),
        RenderSemanticRecord(
            construct_kind="iteration_expression",
            construct_name="for",
            value="apiVersion in allVersions[currentVersion].apiVersions",
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        ),
    ]
    records.extend(
        RenderSemanticRecord(
            construct_kind="conditional_expression",
            construct_name=name,
            value=value,
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        )
        for name, value in conditionals
    )
    records.extend(
        RenderSemanticRecord(
            construct_kind="variant_argument",
            construct_name=name,
            value="<none>",
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        )
        for name in ("cli", "curl", "javascript")
    )
    records.append(
        RenderSemanticRecord(
            construct_kind="presentation_argument",
            construct_name="octicon",
            value='"code" aria-hidden="true" aria-label="code"',
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        )
    )
    records.extend(
        RenderSemanticRecord(
            construct_kind="autotitle_target",
            construct_name="AUTOTITLE",
            value=f"/target/{index:02d}",
            occurrence_count=1,
            source_count=1,
            source_locators=("content/a.md",),
        )
        for index in range(56)
    )
    return Phase3bRenderSemanticsReview(
        review_version="phase3b-render-semantics-review-v2",
        snapshot_id="github_rest_v1_2026_09_05",
        source_render_context_review_sha256=(
            "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
        ),
        source_dependency_manifest_sha256=(
            "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
        ),
        supersedes_review_version="phase3b-render-semantics-review-v1",
        supersedes_review_sha256=(
            "e892bad04a1a8c58cac761c06b3c15015130b3ab53350c74ca2a97b159be6a20"
        ),
        supersession_reason="liquid_trim_marker_parser_repair",
        records=tuple(records),
        assignment_expression_count=1,
        conditional_expression_count=13,
        iteration_expression_count=1,
        variant_argument_count=3,
        presentation_argument_count=1,
        autotitle_target_count=56,
    )


def test_freeze_render_policy_matches_reviewed_fpt_context() -> None:
    policy = freeze_render_policy(
        _semantics(),
        semantics_review_sha256=(
            "25cae92b748ec1e40674c6813772c2c258b366e47f702da682b00dc0fd912368"
        ),
        context_review_sha256=(
            "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
        ),
        dependency_manifest_sha256=(
            "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
        ),
    )

    assert policy.freeze_status == "frozen"
    assert policy.rendering_authorized is True
    assert policy.site_renderer_equivalence_claimed is False
    assert policy.supported_api_versions == ("2026-03-10", "2022-11-28")
    assert policy.default_rest_api_version == "2022-11-28"
    assert policy.secret_resolution_policy == "forbidden"
    decisions = {item.expression: item.result for item in policy.conditional_decisions}
    assert decisions["ifversion:fpt"] is True
    assert decisions["ifversion:api-insights"] is False
    assert decisions["ifversion:enterprise-installed-apps"] is False


def test_freeze_render_policy_rejects_semantics_hash_drift() -> None:
    with pytest.raises(ValueError, match="semantics hash"):
        freeze_render_policy(
            _semantics(),
            semantics_review_sha256="0" * 64,
            context_review_sha256=(
                "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
            ),
            dependency_manifest_sha256=(
                "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
            ),
        )


def test_render_policy_manifest_path_is_durable_and_versioned() -> None:
    root = Path("repo")
    assert render_policy_manifest_path(root) == (
        root / "datasets" / "source_manifests" / "phase3b_render_policy_freeze_v1.json"
    )

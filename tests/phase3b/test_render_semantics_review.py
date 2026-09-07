from __future__ import annotations

from pathlib import Path

from rag_reliability.corpus.phase3b_render_semantics_review_runner import (
    render_context_review_path,
    render_semantics_review_path,
)
from rag_reliability.corpus.render_context_review import RenderReviewSourceUnit
from rag_reliability.corpus.render_dependencies import RenderDependencyFileReceipt
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet
from rag_reliability.corpus.render_semantics_review import build_render_semantics_review


def _frozen() -> Phase3bFrozenRenderDependencySet:
    paths = (
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
    dependencies = tuple(
        RenderDependencyFileReceipt(
            path=path,
            media_type=("yaml_variables" if path.endswith(".yml") else "markdown_reusable"),
            observed_git_blob_sha1=f"{index:040x}",
            content_sha256=f"{index:064x}",
            byte_count=1,
            cache_path=f"cache/{index}",
            satisfied_references=(f"variables.example.v{index}",),
        )
        for index, path in enumerate(paths, start=1)
    )
    return Phase3bFrozenRenderDependencySet(
        freeze_version="phase3b-render-dependency-freeze-v2",
        snapshot_id="github_rest_v1_2026_09_05",
        github_docs_commit_sha="ec3629a841129ae28189d7bb2274a7b3d40c5095",
        source_render_audit_sha256=(
            "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"
        ),
        source_dependency_closure_sha256=(
            "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"
        ),
        supersedes_freeze_version="phase3b-render-dependency-freeze-v1",
        supersedes_manifest_sha256=(
            "61a3a040361dbafd156eb2698321a30972649ef596846f6e302d983dc77a3d59"
        ),
        supersession_reason="liquid_trim_marker_parser_repair",
        resolved_data_references=tuple(f"ref-{index}" for index in range(41)),
        dependency_files=dependencies,
        required_liquid_tags=(
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
        ),
        required_template_variables=(
            "allVersions[currentVersion].latestApiVersion",
            "apiVersion",
            "defaultRestApiVersion",
            "initialRestVersioningReleaseDate",
            "initialRestVersioningReleaseDateLong",
            "secrets.GITHUB_TOKEN",
            'versionData.end_of_support | default: "Not yet scheduled"',
        ),
    )


def test_review_extracts_exact_semantic_arguments() -> None:
    units = (
        RenderReviewSourceUnit(
            source_locator="content/a.md",
            content=(
                "{% assign versionData = tables.rest-api-versions.versions[apiVersion] %}\n"
                "{% for apiVersion in allVersions[currentVersion].apiVersions %}\n"
                "{% ifversion fpt or ghec %}A{% endif %}\n"
                "{% if apiVersion == '2026-03-10' %}B{% elsif apiVersion %}C{% endif %}\n"
                "{% curl %}curl{% endcurl %}\n"
                "{% javascript %}js{% endjavascript %}\n"
                "{% octicon 'shield' aria-label='shield' %}\n"
                "[AUTOTITLE](/rest/about-the-rest-api/api-versions)\n"
            ),
        ),
    )

    review = build_render_semantics_review(
        units,
        _frozen(),
        source_render_context_review_sha256=(
            "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
        ),
        source_dependency_manifest_sha256=(
            "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
        ),
    )

    assert review.review_version == "phase3b-render-semantics-review-v2"
    assert review.supersedes_review_version == "phase3b-render-semantics-review-v1"
    assert review.supersession_reason == "liquid_trim_marker_parser_repair"

    values = {
        (record.construct_kind, record.construct_name, record.value)
        for record in review.records
    }
    assert (
        "assignment_expression",
        "assign",
        "versionData = tables.rest-api-versions.versions[apiVersion]",
    ) in values
    assert (
        "iteration_expression",
        "for",
        "apiVersion in allVersions[currentVersion].apiVersions",
    ) in values
    assert ("conditional_expression", "ifversion", "fpt or ghec") in values
    assert (
        "conditional_expression",
        "if",
        "apiVersion == '2026-03-10'",
    ) in values
    assert ("conditional_expression", "elsif", "apiVersion") in values
    assert ("variant_argument", "curl", "<none>") in values
    assert ("variant_argument", "javascript", "<none>") in values
    assert (
        "presentation_argument",
        "octicon",
        "'shield' aria-label='shield'",
    ) in values
    assert (
        "autotitle_target",
        "AUTOTITLE",
        "/rest/about-the-rest-api/api-versions",
    ) in values


def test_review_rejects_unfrozen_liquid_tag() -> None:
    units = (
        RenderReviewSourceUnit(
            source_locator="content/a.md",
            content="{% unsupported value %}",
        ),
    )

    try:
        build_render_semantics_review(
            units,
            _frozen(),
            source_render_context_review_sha256=(
                "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
            ),
            source_dependency_manifest_sha256=(
                "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
            ),
        )
    except ValueError as exc:
        assert "unfrozen Liquid tag" in str(exc)
    else:
        raise AssertionError("unfrozen tag should fail closed")


def test_semantics_scanner_accepts_whitespace_trim_markers() -> None:
    units = (
        RenderReviewSourceUnit(
            source_locator="content/trimmed.md",
            content=(
                "{%- assign x = y -%}"
                "{%- for apiVersion in allVersions[currentVersion].apiVersions -%}"
                "{%- ifversion fpt or ghec -%}A{%- endif -%}{%- endfor -%}"
            ),
        ),
    )

    review = build_render_semantics_review(
        units,
        _frozen(),
        source_render_context_review_sha256=(
            "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
        ),
        source_dependency_manifest_sha256=(
            "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
        ),
    )

    assert any(
        record.construct_kind == "assignment_expression"
        and record.construct_name == "assign"
        and record.value == "x = y"
        for record in review.records
    )
    assert any(
        record.construct_kind == "iteration_expression"
        and record.construct_name == "for"
        and record.value == "apiVersion in allVersions[currentVersion].apiVersions"
        for record in review.records
    )
    assert any(
        record.construct_kind == "conditional_expression"
        and record.construct_name == "ifversion"
        and record.value == "fpt or ghec"
        for record in review.records
    )


def test_semantics_v2_paths_do_not_reuse_superseded_artifacts() -> None:
    root = Path("repo")

    assert render_context_review_path(root) == (
        root / "artifacts" / "development" / "phase3b_render_context_review_v2.json"
    )
    assert render_semantics_review_path(root) == (
        root / "artifacts" / "development" / "phase3b_render_semantics_review_v2.json"
    )

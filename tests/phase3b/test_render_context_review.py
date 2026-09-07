from __future__ import annotations

from rag_reliability.corpus.render_context_review import (
    RenderReviewSourceUnit,
    build_render_context_review,
)
from rag_reliability.corpus.render_dependencies import RenderDependencyFileReceipt
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet


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
            satisfied_references=(f"variables.x.v{index}",),
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


def test_review_classifies_all_frozen_constructs() -> None:
    frozen = _frozen()
    liquid = " ".join(f"{{% {tag} x %}}" for tag in frozen.required_liquid_tags)
    templates = " ".join(f"{{{{ {name} }}}}" for name in frozen.required_template_variables)
    units = (
        RenderReviewSourceUnit(
            source_locator="content/test.md",
            content=f"{liquid}\n{templates}\n[AUTOTITLE](/x)\n",
        ),
    )

    review = build_render_context_review(
        units,
        frozen,
        source_dependency_manifest_sha256="a" * 64,
    )

    assert review.review_version == "phase3b-render-context-review-v2"
    assert review.liquid_occurrence_count == 18
    assert review.template_variable_occurrence_count == 7
    assert review.autotitle_occurrence_count == 1
    assert len(review.records) == 26


def test_review_counts_multiple_occurrences_and_sources() -> None:
    frozen = _frozen()
    common_liquid = " ".join(f"{{% {tag} x %}}" for tag in frozen.required_liquid_tags)
    common_templates = " ".join(
        f"{{{{ {name} }}}}" for name in frozen.required_template_variables
    )
    units = (
        RenderReviewSourceUnit(
            source_locator="a.md",
            content=f"{common_liquid}\n{common_templates}\n{{% data x %}}",
        ),
        RenderReviewSourceUnit(
            source_locator="b.md",
            content="{% data y %}",
        ),
    )

    review = build_render_context_review(
        units,
        frozen,
        source_dependency_manifest_sha256="b" * 64,
    )
    data_record = next(record for record in review.records if record.construct_name == "data")
    assert data_record.occurrence_count == 3
    assert data_record.source_count == 2
    assert data_record.decision_class == "dependency_substitution"


def test_review_scanner_accepts_whitespace_trim_markers() -> None:
    frozen = _frozen()
    liquid = " ".join(f"{{% {tag} x %}}" for tag in frozen.required_liquid_tags)
    templates = " ".join(f"{{{{ {name} }}}}" for name in frozen.required_template_variables)
    units = (
        RenderReviewSourceUnit(
            source_locator="trimmed.md",
            content=(
                f"{liquid}\n{templates}\n"
                "{%- data reusables.rest-api.version-header -%}\n"
                "{{- defaultRestApiVersion -}}\n"
            ),
        ),
    )

    review = build_render_context_review(
        units,
        frozen,
        source_dependency_manifest_sha256="c" * 64,
    )
    data_record = next(record for record in review.records if record.construct_name == "data")
    default_record = next(
        record
        for record in review.records
        if record.construct_name == "defaultRestApiVersion"
    )
    assert data_record.occurrence_count == 2
    assert default_record.occurrence_count == 2

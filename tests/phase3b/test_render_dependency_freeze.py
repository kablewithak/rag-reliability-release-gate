from __future__ import annotations

from pathlib import Path

import pytest

from rag_reliability.corpus.render_dependencies import (
    Phase3bRenderDependencyClosureCandidate,
    RenderDependencyFileReceipt,
)
from rag_reliability.corpus.render_dependency_freeze import (
    freeze_render_dependencies,
    frozen_manifest_path,
)

_EXPECTED_CLOSURE_SHA = (
    "5cc7a80af3db5d35ed2a2c44cae048340d3eeb319bc162c15387f059273e785c"
)

_PATHS = (
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

_LIQUID_TAGS = (
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

_TEMPLATE_VARIABLES = (
    "allVersions[currentVersion].latestApiVersion",
    "apiVersion",
    "defaultRestApiVersion",
    "initialRestVersioningReleaseDate",
    "initialRestVersioningReleaseDateLong",
    "secrets.GITHUB_TOKEN",
    'versionData.end_of_support | default: "Not yet scheduled"',
)


def _candidate() -> Phase3bRenderDependencyClosureCandidate:
    references = tuple(f"reusables.test.ref-{index:02d}" for index in range(41))
    files = []
    start = 0
    for index, path in enumerate(_PATHS):
        remaining_files = len(_PATHS) - index
        remaining_refs = len(references) - start
        take = max(1, remaining_refs // remaining_files)
        if index == len(_PATHS) - 1:
            take = remaining_refs
        satisfied = references[start : start + take]
        start += take
        media_type = "markdown_reusable" if index < 13 else "yaml_variables"
        files.append(
            RenderDependencyFileReceipt(
                path=path,
                media_type=media_type,
                observed_git_blob_sha1=f"{index + 1:040x}",
                content_sha256=f"{index + 1:064x}",
                byte_count=index + 1,
                cache_path=f"datasets/source_documents/_upstream_cache/{index + 1}",
                satisfied_references=tuple(sorted(satisfied)),
            )
        )

    return Phase3bRenderDependencyClosureCandidate(
        closure_version="phase3b-render-dependency-closure-candidate-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        source_render_audit_sha256=(
            "7e5883d35e784a729974db4a05a582790efee4596269e5fa50bd8a7da79dd49e"
        ),
        direct_data_references=references,
        resolved_data_references=references,
        transitive_data_references=(),
        reusable_references=references,
        variable_references=(),
        dependency_files=tuple(files),
        render_liquid_tags=_LIQUID_TAGS,
        render_template_variables=_TEMPLATE_VARIABLES,
        autotitle_count=0,
    )



def test_frozen_manifest_path_targets_v2(tmp_path: Path) -> None:
    assert frozen_manifest_path(tmp_path) == (
        tmp_path
        / "datasets"
        / "source_manifests"
        / "phase3b_render_dependency_freeze_v2.json"
    )

def test_freeze_accepts_corrected_reviewed_candidate_shape() -> None:
    frozen = freeze_render_dependencies(
        _candidate(),
        candidate_sha256=_EXPECTED_CLOSURE_SHA,
    )

    assert frozen.freeze_version == "phase3b-render-dependency-freeze-v2"
    assert frozen.freeze_status == "frozen"
    assert frozen.supersession_reason == "liquid_trim_marker_parser_repair"
    assert frozen.render_context_review_required is True
    assert frozen.rendering_authorized is False
    assert len(frozen.dependency_files) == 17
    assert len(frozen.required_liquid_tags) == 18


def test_freeze_rejects_candidate_hash_drift() -> None:
    with pytest.raises(ValueError, match="closure hash"):
        freeze_render_dependencies(_candidate(), candidate_sha256="a" * 64)


def test_freeze_rejects_source_audit_drift() -> None:
    candidate = _candidate().model_copy(update={"source_render_audit_sha256": "a" * 64})

    with pytest.raises(ValueError, match="source audit hash"):
        freeze_render_dependencies(candidate, candidate_sha256=_EXPECTED_CLOSURE_SHA)


def test_freeze_rejects_path_drift() -> None:
    candidate = _candidate()
    mutated = candidate.model_copy(
        update={
            "dependency_files": candidate.dependency_files[:-1]
            + (
                candidate.dependency_files[-1].model_copy(
                    update={"path": "data/variables/wrong.yml"}
                ),
            )
        }
    )

    with pytest.raises(ValueError, match="file paths"):
        freeze_render_dependencies(mutated, candidate_sha256=_EXPECTED_CLOSURE_SHA)


def test_freeze_rejects_render_requirement_drift() -> None:
    candidate = _candidate().model_copy(update={"render_liquid_tags": ("data",)})

    with pytest.raises(ValueError, match="Liquid tags"):
        freeze_render_dependencies(candidate, candidate_sha256=_EXPECTED_CLOSURE_SHA)

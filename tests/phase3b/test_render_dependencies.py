from __future__ import annotations

from pathlib import Path

import pytest

from rag_reliability.corpus.render_audit import (
    AuthoredRenderabilityRecord,
    Phase3bAuthoredRenderabilityAudit,
)
from rag_reliability.corpus.render_dependencies import (
    build_render_dependency_closure_candidate,
    dependency_target,
)


def _audit(reference: str) -> Phase3bAuthoredRenderabilityAudit:
    documents = [
        AuthoredRenderabilityRecord(
            source_id="docs-0",
            path="content/rest/docs-0.md",
            unresolved_directive_count=1,
            data_references=(reference,),
            liquid_tags=("data",),
        )
    ]
    documents.extend(
        AuthoredRenderabilityRecord(
            source_id=f"docs-{index}",
            path=f"content/rest/docs-{index}.md",
            unresolved_directive_count=0,
        )
        for index in range(1, 10)
    )
    return Phase3bAuthoredRenderabilityAudit(
        audit_version="phase3b-authored-renderability-audit-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        acquisition_receipt_sha256="a" * 64,
        unresolved_document_count=1,
        total_unresolved_directive_count=1,
        unique_data_reference_count=1,
        documents=tuple(documents),
        render_dependency_freeze_required=True,
        full_ingestion_ready=False,
    )


def _url(path: str) -> str:
    commit = "ec3629a841129ae28189d7bb2274a7b3d40c5095"
    return f"https://raw.githubusercontent.com/github/docs/{commit}/{path}"


def test_dependency_target_maps_reusables_and_variables() -> None:
    reusable = dependency_target("reusables.rest-api.version-header")
    assert reusable.path == "data/reusables/rest-api/version-header.md"
    assert reusable.variable_key_path == ()

    variable = dependency_target("variables.product.github")
    assert variable.path == "data/variables/product.yml"
    assert variable.variable_key_path == ("github",)


def test_dependency_target_rejects_unsupported_namespace() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        dependency_target("octicons.alert")


def test_closure_follows_transitive_selected_dependencies(tmp_path: Path) -> None:
    payloads = {
        _url("data/reusables/example/first.md"): (
            b"Use {% data variables.product.github %}.\n"
        ),
        _url("data/variables/product.yml"): (
            b"github: GitHub\n"
            b"noise: '{% data reusables.unrelated.must-not-load %}'\n"
        ),
    }

    def fetcher(url: str) -> bytes:
        return payloads[url]

    closure = build_render_dependency_closure_candidate(
        tmp_path,
        _audit("reusables.example.first"),
        source_render_audit_sha256="b" * 64,
        fetcher=fetcher,
    )

    assert closure.direct_data_references == ("reusables.example.first",)
    assert closure.resolved_data_references == (
        "reusables.example.first",
        "variables.product.github",
    )
    assert closure.transitive_data_references == ("variables.product.github",)
    assert tuple(item.path for item in closure.dependency_files) == (
        "data/reusables/example/first.md",
        "data/variables/product.yml",
    )
    assert "reusables.unrelated.must-not-load" not in closure.resolved_data_references


def test_closure_fails_when_selected_variable_key_is_missing(tmp_path: Path) -> None:
    payloads = {
        _url("data/variables/product.yml"): b"other: value\n",
    }

    def fetcher(url: str) -> bytes:
        return payloads[url]

    with pytest.raises(ValueError, match="key does not exist"):
        build_render_dependency_closure_candidate(
            tmp_path,
            _audit("variables.product.github"),
            source_render_audit_sha256="c" * 64,
            fetcher=fetcher,
        )

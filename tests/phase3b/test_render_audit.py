from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from rag_reliability.corpus.render_audit import (
    AuthoredRenderabilityRecord,
    Phase3bAuthoredRenderabilityAudit,
    scan_authored_markdown,
)


def _record(source_id: str, unresolved: int = 0) -> AuthoredRenderabilityRecord:
    return AuthoredRenderabilityRecord(
        source_id=source_id,
        path=f"content/rest/{source_id}.md",
        unresolved_directive_count=unresolved,
    )


def test_scanner_classifies_github_docs_build_directives() -> None:
    content = """
{% data reusables.rest-api.version-header %}
{% ifversion ghes %}
{{ defaultRestApiVersion }}
[AUTOTITLE]
{% endif %}
"""

    result = scan_authored_markdown(
        source_id="docs-api-versions",
        path="content/rest/about-the-rest-api/api-versions.md",
        content=content,
    )

    assert result.unresolved_directive_count == 5
    assert result.data_references == ("reusables.rest-api.version-header",)
    assert result.liquid_tags == ("data", "endif", "ifversion")
    assert result.template_variables == ("defaultRestApiVersion",)
    assert result.autotitle_count == 1


def test_scanner_reports_clean_markdown_as_render_ready_input() -> None:
    result = scan_authored_markdown(
        source_id="docs-clean",
        path="content/rest/clean.md",
        content="# Clean\n\nNo build directives.\n",
    )

    assert result.unresolved_directive_count == 0
    assert result.data_references == ()
    assert result.liquid_tags == ()
    assert result.template_variables == ()
    assert result.autotitle_count == 0


def test_audit_requires_gate_to_match_observed_directives() -> None:
    documents = tuple(
        _record(f"docs-{index}", unresolved=1 if index == 0 else 0)
        for index in range(10)
    )

    audit = Phase3bAuthoredRenderabilityAudit(
        audit_version="phase3b-authored-renderability-audit-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        acquisition_receipt_sha256="a" * 64,
        unresolved_document_count=1,
        total_unresolved_directive_count=1,
        unique_data_reference_count=0,
        documents=documents,
        render_dependency_freeze_required=True,
        full_ingestion_ready=False,
    )
    assert audit.render_dependency_freeze_required is True

    invalid = audit.model_dump(mode="json")
    invalid["full_ingestion_ready"] = True
    with pytest.raises(ValidationError):
        Phase3bAuthoredRenderabilityAudit.model_validate(invalid)


def test_audit_rejects_duplicate_source_ids() -> None:
    documents = [_record(f"docs-{index}") for index in range(10)]
    documents[-1] = deepcopy(documents[0])

    with pytest.raises(ValidationError):
        Phase3bAuthoredRenderabilityAudit(
            audit_version="phase3b-authored-renderability-audit-v1",
            snapshot_id="github_rest_v1_2026_09_05",
            acquisition_receipt_sha256="a" * 64,
            unresolved_document_count=0,
            total_unresolved_directive_count=0,
            unique_data_reference_count=0,
            documents=tuple(documents),
            render_dependency_freeze_required=False,
            full_ingestion_ready=True,
        )


def test_scanner_detects_liquid_whitespace_trim_markers() -> None:
    content = """
{%- for apiVersion in allVersions[currentVersion].apiVersions %}
{{- apiVersion -}}
{%- assign versionData = tables.rest-api-versions.versions[apiVersion] %}
{%- endfor %}
"""

    result = scan_authored_markdown(
        source_id="docs-api-versions",
        path="content/rest/about-the-rest-api/api-versions.md",
        content=content,
    )

    assert result.unresolved_directive_count == 4
    assert result.liquid_tags == ("assign", "endfor", "for")
    assert result.template_variables == ("apiVersion",)

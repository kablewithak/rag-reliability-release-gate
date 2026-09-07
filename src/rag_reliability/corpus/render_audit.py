"""Renderability audit for pinned authored GitHub Docs sources."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan

_LIQUID_TAG_PATTERN = re.compile(r"\{%\s*-?\s*([A-Za-z_][\w-]*)(.*?)\s*-?\s*%\}", re.DOTALL)
_TEMPLATE_VARIABLE_PATTERN = re.compile(r"\{\{\s*-?\s*([^{}]+?)\s*-?\s*\}\}")
_AUTOTITLE = "[AUTOTITLE]"


class AuthoredRenderabilityRecord(ContractModel):
    """Unresolved build-time directives found in one pinned authored document."""

    source_id: NonEmptyStr
    path: NonEmptyStr
    unresolved_directive_count: int = Field(ge=0)
    data_references: tuple[NonEmptyStr, ...] = ()
    liquid_tags: tuple[NonEmptyStr, ...] = ()
    template_variables: tuple[NonEmptyStr, ...] = ()
    autotitle_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_sorted_unique_fields(self) -> AuthoredRenderabilityRecord:
        for values in (
            self.data_references,
            self.liquid_tags,
            self.template_variables,
        ):
            if tuple(sorted(set(values))) != values:
                raise ValueError("renderability tuple fields must be sorted and unique")
        return self


class Phase3bAuthoredRenderabilityAudit(ContractModel):
    """Evidence that authored Markdown is or is not ready for normalized ingestion."""

    audit_version: Literal["phase3b-authored-renderability-audit-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    acquisition_receipt_sha256: Sha256
    document_count: Literal[10] = 10
    unresolved_document_count: int = Field(ge=0, le=10)
    total_unresolved_directive_count: int = Field(ge=0)
    unique_data_reference_count: int = Field(ge=0)
    documents: tuple[AuthoredRenderabilityRecord, ...] = Field(min_length=10, max_length=10)
    render_dependency_freeze_required: bool
    full_ingestion_ready: bool
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_counts_and_gate(self) -> Phase3bAuthoredRenderabilityAudit:
        source_ids = tuple(item.source_id for item in self.documents)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("authored renderability source IDs must be unique")

        unresolved_documents = sum(
            item.unresolved_directive_count > 0 for item in self.documents
        )
        if unresolved_documents != self.unresolved_document_count:
            raise ValueError("unresolved document count does not match document records")

        unresolved_total = sum(item.unresolved_directive_count for item in self.documents)
        if unresolved_total != self.total_unresolved_directive_count:
            raise ValueError("unresolved directive count does not match document records")

        data_refs = {
            ref
            for item in self.documents
            for ref in item.data_references
        }
        if len(data_refs) != self.unique_data_reference_count:
            raise ValueError("unique data reference count does not match document records")

        expected_dependency_freeze = self.total_unresolved_directive_count > 0
        if self.render_dependency_freeze_required != expected_dependency_freeze:
            raise ValueError("render dependency freeze gate is inconsistent")

        if self.full_ingestion_ready == expected_dependency_freeze:
            raise ValueError("full ingestion readiness is inconsistent")

        return self


def scan_authored_markdown(
    *,
    source_id: str,
    path: str,
    content: str,
) -> AuthoredRenderabilityRecord:
    """Classify unresolved GitHub Docs build directives without rewriting content."""

    liquid_matches = tuple(_LIQUID_TAG_PATTERN.finditer(content))
    liquid_tags = tuple(sorted({match.group(1) for match in liquid_matches}))

    data_references = tuple(
        sorted(
            {
                body.strip().split()[0]
                for match in liquid_matches
                if match.group(1) == "data"
                for body in (match.group(2),)
                if body.strip()
            }
        )
    )

    template_variables = tuple(
        sorted({match.group(1).strip() for match in _TEMPLATE_VARIABLE_PATTERN.finditer(content)})
    )
    autotitle_count = content.count(_AUTOTITLE)

    unresolved_count = (
        len(liquid_matches)
        + len(tuple(_TEMPLATE_VARIABLE_PATTERN.finditer(content)))
        + autotitle_count
    )

    return AuthoredRenderabilityRecord(
        source_id=source_id,
        path=path,
        unresolved_directive_count=unresolved_count,
        data_references=data_references,
        liquid_tags=liquid_tags,
        template_variables=template_variables,
        autotitle_count=autotitle_count,
    )


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _receipt_by_source_id(receipt: AcquisitionReceipt) -> dict[str, str]:
    return {item.source_id: item.cache_path for item in receipt.files}


def build_authored_renderability_audit(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    receipt: AcquisitionReceipt,
    *,
    acquisition_receipt_sha256: str,
) -> Phase3bAuthoredRenderabilityAudit:
    """Scan the 10 exact pinned authored docs acquired under the Phase 3A plan."""

    cache_paths = _receipt_by_source_id(receipt)
    records: list[AuthoredRenderabilityRecord] = []

    for item in plan.files:
        if item.media_type != "markdown":
            continue

        cache_path = cache_paths.get(item.source_id)
        if cache_path is None:
            raise ValueError(f"acquisition receipt missing source: {item.source_id}")

        content = (repo_root / cache_path).read_text(encoding="utf-8")
        records.append(
            scan_authored_markdown(
                source_id=item.source_id,
                path=item.path,
                content=content,
            )
        )

    ordered = tuple(sorted(records, key=lambda item: item.source_id))
    unresolved_documents = sum(item.unresolved_directive_count > 0 for item in ordered)
    unresolved_total = sum(item.unresolved_directive_count for item in ordered)
    data_refs = {
        ref
        for item in ordered
        for ref in item.data_references
    }

    return Phase3bAuthoredRenderabilityAudit(
        audit_version="phase3b-authored-renderability-audit-v1",
        snapshot_id=plan.snapshot_id,
        acquisition_receipt_sha256=acquisition_receipt_sha256,
        unresolved_document_count=unresolved_documents,
        total_unresolved_directive_count=unresolved_total,
        unique_data_reference_count=len(data_refs),
        documents=ordered,
        render_dependency_freeze_required=unresolved_total > 0,
        full_ingestion_ready=unresolved_total == 0,
    )


def write_json_with_sha256(path: Path, value: ContractModel) -> str:
    """Write stable JSON plus a conventional SHA-256 sidecar."""

    content = _stable_json_bytes(value.model_dump(mode="json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {path.name}\n", encoding="utf-8", newline="\n")
    return digest


def sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    """Return deterministic unique text values."""

    return tuple(sorted(set(values)))

"""File-backed normalized corpus contracts for Phase 3B ingestion."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.corpus import RealSourceRecord
from rag_reliability.contracts.enums import CorpusSourceFamily, SourceState
from rag_reliability.corpus.models import HttpMethod, SemanticOperationFamily

NormalizedDocumentKind = Literal[
    "authored_guidance",
    "openapi_operation_contract",
]

_SOURCE_SELECTION_SHA256 = (
    "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
)
_RENDERED_SOURCE_MANIFEST_SHA256 = (
    "974c3ce722e30d630d09360cf115ac4679b2bf09797aa89a8f8af6e5549f5e7f"
)
_OPERATION_ALLOWLIST_SHA256 = (
    "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
)


class NormalizedCorpusDocument(ContractModel):
    """One file-backed retrieval source document before chunking."""

    document_id: NonEmptyStr
    document_kind: NormalizedDocumentKind
    content_path: NonEmptyStr
    normalized_content_sha256: Sha256
    normalized_byte_count: int = Field(gt=0)
    provenance: RealSourceRecord
    semantic_family: SemanticOperationFamily | None = None
    operation_id: NonEmptyStr | None = None
    method: HttpMethod | None = None
    path: NonEmptyStr | None = None

    @model_validator(mode="after")
    def validate_document_shape(self) -> NormalizedCorpusDocument:
        if self.document_kind == "authored_guidance":
            if (
                self.provenance.source_family
                is not CorpusSourceFamily.GITHUB_REST_AUTHORED_GUIDANCE
            ):
                raise ValueError(
                    "authored guidance must use github_rest_authored_guidance source family"
                )
            if any(
                value is not None
                for value in (
                    self.semantic_family,
                    self.operation_id,
                    self.method,
                    self.path,
                )
            ):
                raise ValueError("authored guidance cannot carry OpenAPI operation identity")
            return self

        if self.provenance.source_family is not CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT:
            raise ValueError("OpenAPI contract must use openapi_endpoint_contract source family")
        if any(
            value is None
            for value in (
                self.semantic_family,
                self.operation_id,
                self.method,
                self.path,
            )
        ):
            raise ValueError("OpenAPI contract requires complete operation identity")
        return self


class Phase3bNormalizedCorpusManifest(ContractModel):
    """Custody manifest for the normalized Phase 3B corpus slice."""

    manifest_version: Literal["phase3b-normalized-corpus-manifest-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_selection_sha256: Literal[
        "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
    ]
    source_rendered_manifest_sha256: Literal[
        "974c3ce722e30d630d09360cf115ac4679b2bf09797aa89a8f8af6e5549f5e7f"
    ]
    operation_allowlist_sha256: Literal[
        "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
    ]
    source_acquisition_receipt_sha256: Sha256
    retrieved_at: AwareDatetime
    documents: tuple[NormalizedCorpusDocument, ...] = Field(min_length=50, max_length=50)
    normalization_status: Literal["complete"] = "complete"
    normalized_corpus_ready: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_frozen_shape(self) -> Phase3bNormalizedCorpusManifest:
        document_ids = tuple(item.document_id for item in self.documents)
        if document_ids != tuple(sorted(document_ids)):
            raise ValueError("normalized documents must be document-ID sorted")
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("normalized document IDs must be unique")

        content_paths = tuple(item.content_path for item in self.documents)
        if len(content_paths) != len(set(content_paths)):
            raise ValueError("normalized content paths must be unique")

        authored = tuple(
            item for item in self.documents if item.document_kind == "authored_guidance"
        )
        operations = tuple(
            item
            for item in self.documents
            if item.document_kind == "openapi_operation_contract"
        )
        if len(authored) != 10:
            raise ValueError("Phase 3B normalized slice requires exactly 10 authored documents")
        if len(operations) != 40:
            raise ValueError("Phase 3B normalized slice requires exactly 40 operation documents")

        state_counts = Counter(item.provenance.source_state for item in operations)
        if state_counts[SourceState.CURRENT] != 20:
            raise ValueError("normalized operation slice requires 20 current documents")
        if state_counts[SourceState.HISTORICAL_COMPARISON] != 20:
            raise ValueError("normalized operation slice requires 20 historical documents")

        for state in (SourceState.CURRENT, SourceState.HISTORICAL_COMPARISON):
            family_counts = Counter(
                item.semantic_family
                for item in operations
                if item.provenance.source_state is state
            )
            if set(family_counts.values()) != {5} or len(family_counts) != 4:
                raise ValueError("each OpenAPI source state requires 5 operations per family")

        return self


class Phase3bNormalizedCorpusReceipt(ContractModel):
    """Small evidence receipt for the Phase 3B normalization boundary."""

    receipt_version: Literal["phase3b-normalized-corpus-receipt-v1"]
    source_selection_sha256: Literal[
        "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
    ]
    source_rendered_manifest_sha256: Literal[
        "974c3ce722e30d630d09360cf115ac4679b2bf09797aa89a8f8af6e5549f5e7f"
    ]
    operation_allowlist_sha256: Literal[
        "4458525018000b35f06f7d5ff3e3c7bfe61dc36550cf276789228d03db6f8b61"
    ]
    source_acquisition_receipt_sha256: Sha256
    normalized_manifest_sha256: Sha256
    retrieval_started_at: AwareDatetime
    retrieval_completed_at: AwareDatetime
    document_count: Literal[50] = 50
    authored_document_count: Literal[10] = 10
    current_operation_document_count: Literal[20] = 20
    historical_operation_document_count: Literal[20] = 20
    file_identity_match_count: Literal[50] = 50
    normalization_status: Literal["complete"] = "complete"
    normalized_corpus_ready: Literal[True] = True
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False

    @model_validator(mode="after")
    def validate_retrieval_window(self) -> Phase3bNormalizedCorpusReceipt:
        started = datetime.fromisoformat(self.retrieval_started_at.isoformat())
        completed = datetime.fromisoformat(self.retrieval_completed_at.isoformat())
        if completed < started:
            raise ValueError("retrieval completion cannot precede retrieval start")
        return self


SOURCE_SELECTION_SHA256 = _SOURCE_SELECTION_SHA256
RENDERED_SOURCE_MANIFEST_SHA256 = _RENDERED_SOURCE_MANIFEST_SHA256
OPERATION_ALLOWLIST_SHA256 = _OPERATION_ALLOWLIST_SHA256

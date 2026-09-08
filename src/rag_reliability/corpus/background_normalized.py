"""Completed Phase 3C background-normalization custody contracts."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from rag_reliability.contracts.base import ContractModel, Sha256
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)
from rag_reliability.corpus.background import (
    BackgroundFamilyCount,
    Phase3cBackgroundSelectionManifest,
)
from rag_reliability.corpus.normalized import NormalizedCorpusDocument

BACKGROUND_SELECTION_SHA256: Literal[
    "d2cc4ade659534973915ad26b10daad8173a9eeba5eeaebc6de42b6d848708aa"
] = "d2cc4ade659534973915ad26b10daad8173a9eeba5eeaebc6de42b6d848708aa"

PHASE3B_NORMALIZED_MANIFEST_SHA256: Literal[
    "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
] = "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"

SOURCE_SELECTION_SHA256: Literal[
    "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
] = "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"

_FAMILY_ORDER = (
    "actions",
    "issues",
    "pull_requests",
    "repositories_and_repository_webhooks",
)

_EXPECTED_FAMILY_COUNTS = (
    ("actions", 184),
    ("issues", 53),
    ("pull_requests", 24),
    ("repositories_and_repository_webhooks", 198),
)


class Phase3cBackgroundNormalizedCorpusManifest(ContractModel):
    """File-backed normalized Phase 3C background corpus."""

    manifest_version: Literal[
        "phase3c-background-normalized-corpus-manifest-v1"
    ] = "phase3c-background-normalized-corpus-manifest-v1"

    snapshot_id: Literal["github_rest_v1_2026_09_05"]

    phase3b_normalized_manifest_sha256: Literal[
        "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
    ]
    background_selection_sha256: Literal[
        "d2cc4ade659534973915ad26b10daad8173a9eeba5eeaebc6de42b6d848708aa"
    ]
    source_selection_sha256: Literal[
        "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
    ]

    source_custody_receipt_sha256: Sha256
    retrieved_at: AwareDatetime

    documents: tuple[NormalizedCorpusDocument, ...] = Field(
        min_length=459,
        max_length=459,
    )

    phase3b_document_count: Literal[50] = 50
    background_document_count: Literal[459] = 459
    full_corpus_document_count: Literal[509] = 509

    normalization_status: Literal["complete"] = "complete"
    background_normalized_ready: Literal[True] = True
    full_ingestion_ready: Literal[True] = True

    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_background_corpus(
        self,
    ) -> Phase3cBackgroundNormalizedCorpusManifest:
        if (
            self.phase3b_document_count
            + self.background_document_count
            != self.full_corpus_document_count
        ):
            raise ValueError("full corpus document counts do not reconcile")

        document_ids = tuple(item.document_id for item in self.documents)
        if document_ids != tuple(sorted(document_ids)):
            raise ValueError("background documents must be document-ID sorted")
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("background document IDs must be unique")

        content_paths = tuple(item.content_path for item in self.documents)
        if len(content_paths) != len(set(content_paths)):
            raise ValueError("background content paths must be unique")

        operation_ids: list[str] = []

        for document in self.documents:
            if document.document_kind != "openapi_operation_contract":
                raise ValueError(
                    "Phase 3C background corpus may contain only OpenAPI operations"
                )

            provenance = document.provenance

            if (
                provenance.source_family
                is not CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT
            ):
                raise ValueError(
                    "Phase 3C background document must use OpenAPI source family"
                )
            if provenance.source_state is not SourceState.CURRENT:
                raise ValueError("Phase 3C background document must be current")
            if provenance.authority_level is not AuthorityLevel.AUTHORITATIVE:
                raise ValueError(
                    "Phase 3C background document must be authoritative"
                )
            if provenance.data_role is not DataRole.BACKGROUND_LOAD_SOURCE:
                raise ValueError(
                    "Phase 3C document must use background_load_source role"
                )
            if provenance.api_version_or_snapshot != "2026-03-10":
                raise ValueError(
                    "Phase 3C background document must use target API version"
                )

            if document.operation_id is None:
                raise ValueError("background OpenAPI document lacks operation ID")
            operation_ids.append(document.operation_id)

        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("background operation IDs must be unique")

        family_counts = Counter(
            item.semantic_family for item in self.documents
        )
        expected_counts = Counter(dict(_EXPECTED_FAMILY_COUNTS))

        if family_counts != expected_counts:
            raise ValueError(
                "normalized background family counts do not match frozen selection"
            )

        return self


class Phase3cBackgroundNormalizedCorpusReceipt(ContractModel):
    """Small receipt proving completion of the Phase 3C normalization boundary."""

    receipt_version: Literal[
        "phase3c-background-normalized-corpus-receipt-v1"
    ] = "phase3c-background-normalized-corpus-receipt-v1"

    phase3b_normalized_manifest_sha256: Literal[
        "2c7c2105d23bc48c64e911fec9c4e6152caf1f0e705666cfc0557f9a79ff9e8b"
    ]
    background_selection_sha256: Literal[
        "d2cc4ade659534973915ad26b10daad8173a9eeba5eeaebc6de42b6d848708aa"
    ]
    source_selection_sha256: Literal[
        "26f4469b5639422b03828535786343a162b7b3113a1b30fafa79180cb0c2e950"
    ]

    source_custody_receipt_sha256: Sha256
    normalized_manifest_sha256: Sha256

    retrieval_started_at: AwareDatetime
    retrieval_completed_at: AwareDatetime

    phase3b_parent_document_count: Literal[50] = 50
    phase3b_parent_file_identity_match_count: Literal[50] = 50
    background_document_count: Literal[459] = 459
    background_file_identity_match_count: Literal[459] = 459
    full_corpus_document_count: Literal[509] = 509
    full_corpus_file_identity_match_count: Literal[509] = 509

    family_counts: tuple[BackgroundFamilyCount, ...] = Field(
        min_length=4,
        max_length=4,
    )

    normalization_status: Literal["complete"] = "complete"
    background_normalized_ready: Literal[True] = True
    full_ingestion_ready: Literal[True] = True

    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_receipt(
        self,
    ) -> Phase3cBackgroundNormalizedCorpusReceipt:
        if self.retrieval_completed_at < self.retrieval_started_at:
            raise ValueError(
                "retrieval completion cannot precede retrieval start"
            )

        observed = tuple(
            (item.family, item.selected_count)
            for item in self.family_counts
        )

        if observed != _EXPECTED_FAMILY_COUNTS:
            raise ValueError(
                "normalization receipt family counts do not match frozen selection"
            )

        return self


def build_background_normalized_manifest(
    selection: Phase3cBackgroundSelectionManifest,
    *,
    selection_sha256: Sha256,
    phase3b_manifest_sha256: Sha256,
    source_selection_sha256: Sha256,
    source_custody_receipt_sha256: Sha256,
    retrieved_at: datetime,
    documents: tuple[NormalizedCorpusDocument, ...],
) -> Phase3cBackgroundNormalizedCorpusManifest:
    """Bind normalized files exactly to the accepted Phase 3C selection."""

    if selection_sha256 != BACKGROUND_SELECTION_SHA256:
        raise ValueError(
            "background selection SHA-256 does not match frozen Phase 3C evidence"
        )
    if phase3b_manifest_sha256 != PHASE3B_NORMALIZED_MANIFEST_SHA256:
        raise ValueError(
            "Phase 3B normalized manifest SHA-256 does not match accepted evidence"
        )
    if source_selection_sha256 != SOURCE_SELECTION_SHA256:
        raise ValueError(
            "source selection SHA-256 does not match frozen Phase 3A evidence"
        )
    if not selection.normalization_authorized:
        raise ValueError("background selection does not authorize normalization")

    expected = {
        item.operation_id: (
            item.family,
            item.method,
            item.path,
        )
        for item in selection.operations
    }

    observed: dict[str, tuple[object, object, object]] = {}

    for document in documents:
        if (
            document.operation_id is None
            or document.semantic_family is None
            or document.method is None
            or document.path is None
        ):
            raise ValueError(
                "normalized background document has incomplete operation identity"
            )

        if document.operation_id in observed:
            raise ValueError(
                f"duplicate normalized operation ID: {document.operation_id}"
            )

        observed[document.operation_id] = (
            document.semantic_family,
            document.method,
            document.path,
        )

    if observed != expected:
        raise ValueError(
            "normalized background operation identities do not match frozen selection"
        )

    return Phase3cBackgroundNormalizedCorpusManifest(
        snapshot_id=selection.snapshot_id,
        phase3b_normalized_manifest_sha256=PHASE3B_NORMALIZED_MANIFEST_SHA256,
        background_selection_sha256=BACKGROUND_SELECTION_SHA256,
        source_selection_sha256=SOURCE_SELECTION_SHA256,
        source_custody_receipt_sha256=source_custody_receipt_sha256,
        retrieved_at=retrieved_at,
        documents=documents,
    )


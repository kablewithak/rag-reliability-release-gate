"""Phase 4C read-only evaluation authoring dossier contracts."""

from __future__ import annotations

from collections import Counter
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import (
    DataRole,
    EvaluationRole,
    EvaluationSourceFamily,
    SourceState,
)
from rag_reliability.corpus.chunking import (
    CHUNK_BYTE_BUDGET,
    ChunkEvidenceScope,
    ChunkKind,
    ChunkParentLineage,
)
from rag_reliability.corpus.models import (
    SemanticOperationFamily,
)
from rag_reliability.evaluation.constitution import (
    PHASE3D_CHUNK_MANIFEST_SHA256,
    EvidenceClusterKind,
)

PHASE4_CONSTITUTION_SHA256: Literal[
    "e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d"
] = (
    "e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d"
)

REVIEW_MARKDOWN_RELATIVE_PATH: Literal[
    "artifacts/development/phase4c_authoring_dossier_v1.md"
] = (
    "artifacts/development/phase4c_authoring_dossier_v1.md"
)


class Phase4AuthoringEvidence(
    ContractModel
):
    """One exact frozen chunk available for case authoring."""

    evidence_id: NonEmptyStr
    chunk_kind: ChunkKind
    content_path: NonEmptyStr
    content_sha256: Sha256
    byte_count: int = Field(
        gt=0,
        le=CHUNK_BYTE_BUDGET,
    )
    chunking_policy_sha256: Sha256
    chunk_index: int = Field(
        ge=0
    )

    parents: tuple[
        ChunkParentLineage,
        ...,
    ] = Field(
        min_length=1
    )

    evidence_scope: ChunkEvidenceScope

    semantic_families: tuple[
        SemanticOperationFamily,
        ...,
    ] = ()

    linked_operation_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    component_ref: NonEmptyStr | None = None

    section_headings: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    @model_validator(mode="after")
    def validate_authoring_boundary(
        self,
    ) -> Self:
        if (
            self.chunk_kind
            is ChunkKind.OPENAPI_COMPONENT
        ):
            raise ValueError(
                "OpenAPI component cannot enter "
                "Phase 4C gold authoring dossier"
            )

        if (
            self.evidence_scope.data_role
            is DataRole.BACKGROUND_LOAD_SOURCE
        ):
            raise ValueError(
                "background-load evidence cannot enter "
                "Phase 4C gold authoring dossier"
            )

        if self.component_ref is not None:
            raise ValueError(
                "gold-authoring evidence cannot carry "
                "component_ref"
            )

        return self


class Phase4AuthoringClusterReview(
    ContractModel
):
    """Read-only review representation of one frozen cluster."""

    cluster_id: NonEmptyStr
    cluster_kind: EvidenceClusterKind
    source_family: EvaluationSourceFamily
    evaluation_role: EvaluationRole

    operation_id: NonEmptyStr | None = None
    authored_source_id: NonEmptyStr | None = None

    current_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(
        min_length=1
    )

    historical_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    current_evidence: tuple[
        Phase4AuthoringEvidence,
        ...,
    ] = Field(
        min_length=1
    )

    historical_evidence: tuple[
        Phase4AuthoringEvidence,
        ...,
    ] = ()

    @property
    def authoring_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            evidence.evidence_id
            for evidence in (
                *self.current_evidence,
                *self.historical_evidence,
            )
        )

    @model_validator(mode="after")
    def validate_cluster_review(
        self,
    ) -> Self:
        evidence_ids = (
            self.authoring_evidence_ids
        )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise ValueError(
                "cluster review contains duplicate "
                "evidence IDs"
            )

        current_sources = tuple(
            sorted(
                {
                    parent.source_id
                    for evidence
                    in self.current_evidence
                    for parent
                    in evidence.parents
                }
            )
        )

        expected_current_sources = tuple(
            sorted(
                self.current_source_ids
            )
        )

        if (
            current_sources
            != expected_current_sources
        ):
            raise ValueError(
                "current evidence source lineage "
                "does not match frozen cluster"
            )

        historical_sources = tuple(
            sorted(
                {
                    parent.source_id
                    for evidence
                    in self.historical_evidence
                    for parent
                    in evidence.parents
                }
            )
        )

        expected_historical_sources = tuple(
            sorted(
                self.historical_source_ids
            )
        )

        if (
            historical_sources
            != expected_historical_sources
        ):
            raise ValueError(
                "historical evidence source lineage "
                "does not match frozen cluster"
            )

        if any(
            evidence.evidence_scope.source_state
            is not SourceState.CURRENT
            for evidence
            in self.current_evidence
        ):
            raise ValueError(
                "current cluster evidence must use "
                "current source state"
            )

        if (
            self.cluster_kind
            is EvidenceClusterKind.OPENAPI_VERSION_PAIR
        ):
            if self.operation_id is None:
                raise ValueError(
                    "OpenAPI cluster review requires "
                    "operation_id"
                )

            if self.authored_source_id is not None:
                raise ValueError(
                    "OpenAPI cluster review cannot carry "
                    "authored_source_id"
                )

            if not self.historical_evidence:
                raise ValueError(
                    "OpenAPI cluster review requires "
                    "historical evidence"
                )

            if not self.historical_source_ids:
                raise ValueError(
                    "OpenAPI cluster review requires "
                    "historical source IDs"
                )

            if any(
                evidence.chunk_kind
                is not ChunkKind.OPENAPI_OPERATION_CORE
                for evidence
                in (
                    *self.current_evidence,
                    *self.historical_evidence,
                )
            ):
                raise ValueError(
                    "OpenAPI authoring cluster may only "
                    "contain operation-core chunks"
                )

            if any(
                self.operation_id
                not in evidence.linked_operation_ids
                for evidence
                in (
                    *self.current_evidence,
                    *self.historical_evidence,
                )
            ):
                raise ValueError(
                    "OpenAPI evidence is not linked to "
                    "the frozen operation ID"
                )

            if any(
                evidence.evidence_scope.source_state
                is not SourceState.HISTORICAL_COMPARISON
                for evidence
                in self.historical_evidence
            ):
                raise ValueError(
                    "historical OpenAPI evidence must use "
                    "historical-comparison state"
                )

            if (
                self.source_family
                is EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
            ):
                raise ValueError(
                    "OpenAPI cluster cannot use "
                    "guidance source family"
                )

        if (
            self.cluster_kind
            is EvidenceClusterKind.AUTHORED_GUIDANCE
        ):
            if self.authored_source_id is None:
                raise ValueError(
                    "guidance cluster review requires "
                    "authored_source_id"
                )

            if self.operation_id is not None:
                raise ValueError(
                    "guidance cluster review cannot carry "
                    "operation_id"
                )

            if self.historical_evidence:
                raise ValueError(
                    "guidance cluster review cannot carry "
                    "historical evidence"
                )

            if self.historical_source_ids:
                raise ValueError(
                    "guidance cluster review cannot carry "
                    "historical source IDs"
                )

            if any(
                evidence.chunk_kind
                is not ChunkKind.AUTHORED_SECTION
                for evidence
                in self.current_evidence
            ):
                raise ValueError(
                    "guidance cluster may only contain "
                    "authored-section chunks"
                )

            if (
                self.source_family
                is not EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
            ):
                raise ValueError(
                    "guidance cluster must use "
                    "cross-cutting source family"
                )

        return self


class Phase4AuthoringDossier(
    ContractModel
):
    """Hash-bound read-only input to Phase 4C case authoring."""

    dossier_version: Literal[
        "phase4c-authoring-dossier-v1"
    ] = "phase4c-authoring-dossier-v1"

    phase3d_chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = PHASE3D_CHUNK_MANIFEST_SHA256

    phase4_constitution_sha256: Literal[
        "e2f1ca0985157ea43e7e648fa431e30c2b139cf9b3ea364d7356e8e11311816d"
    ] = PHASE4_CONSTITUTION_SHA256

    review_markdown_path: Literal[
        "artifacts/development/phase4c_authoring_dossier_v1.md"
    ] = REVIEW_MARKDOWN_RELATIVE_PATH

    review_markdown_sha256: Sha256

    cluster_count: Literal[30] = 30
    authoring_evidence_id_count: Literal[
        68
    ] = 68

    case_authoring_authorized: Literal[
        True
    ] = True

    baseline_authorized: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False

    clusters: tuple[
        Phase4AuthoringClusterReview,
        ...,
    ] = Field(
        min_length=30,
        max_length=30,
    )

    @model_validator(mode="after")
    def validate_dossier(
        self,
    ) -> Self:
        cluster_ids = tuple(
            cluster.cluster_id
            for cluster in self.clusters
        )

        if (
            len(cluster_ids)
            != len(set(cluster_ids))
        ):
            raise ValueError(
                "dossier cluster IDs must be unique"
            )

        evidence_ids = tuple(
            evidence_id
            for cluster in self.clusters
            for evidence_id
            in cluster.authoring_evidence_ids
        )

        if len(evidence_ids) != 68:
            raise ValueError(
                "dossier must contain exactly "
                "68 authoring evidence IDs"
            )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise ValueError(
                "dossier evidence IDs must be "
                "globally unique"
            )

        role_counts = Counter(
            cluster.evaluation_role
            for cluster in self.clusters
        )

        expected_role_counts = Counter(
            {
                EvaluationRole.DEVELOPMENT: 12,
                EvaluationRole.TUNING: 9,
                EvaluationRole.HELD_OUT: 9,
            }
        )

        if role_counts != expected_role_counts:
            raise ValueError(
                "dossier role counts do not match "
                "frozen constitution"
            )

        family_counts = Counter(
            cluster.source_family
            for cluster in self.clusters
        )

        expected_family_counts = Counter(
            {
                EvaluationSourceFamily.ACTIONS: 5,
                EvaluationSourceFamily.ISSUES: 5,
                EvaluationSourceFamily.PULL_REQUESTS: 5,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 5,
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 10,
            }
        )

        if (
            family_counts
            != expected_family_counts
        ):
            raise ValueError(
                "dossier family counts do not match "
                "frozen constitution"
            )

        kind_counts = Counter(
            cluster.cluster_kind
            for cluster in self.clusters
        )

        expected_kind_counts = Counter(
            {
                EvidenceClusterKind.OPENAPI_VERSION_PAIR: 20,
                EvidenceClusterKind.AUTHORED_GUIDANCE: 10,
            }
        )

        if (
            kind_counts
            != expected_kind_counts
        ):
            raise ValueError(
                "dossier cluster kinds do not match "
                "frozen constitution"
            )

        return self

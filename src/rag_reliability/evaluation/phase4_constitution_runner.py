"""Materialize the frozen Phase 4 evidence-cluster constitution."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rag_reliability.contracts.enums import (
    DataRole,
    EvaluationRole,
    EvaluationSourceFamily,
    ScenarioClass,
    SourceState,
)
from rag_reliability.corpus.chunked import (
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    ChunkKind,
    CorpusChunkRecord,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.constitution import (
    PHASE3D_CHUNK_MANIFEST_SHA256,
    EvidenceClusterKind,
    Phase4EvidenceCluster,
    Phase4EvidenceClusterConstitution,
    Phase4EvidenceClusterReceipt,
    Phase4ScenarioQuota,
)

ROOT = Path.cwd()

MANIFEST_PATH = (
    ROOT
    / "datasets"
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)

CONSTITUTION_PATH = (
    ROOT
    / "datasets"
    / "evaluation"
    / "phase4_evidence_cluster_constitution_v1.json"
)

RECEIPT_PATH = (
    ROOT
    / "artifacts"
    / "development"
    / "phase4_evidence_cluster_constitution_receipt_v1.json"
)


OPENAPI_CLUSTER_SPECS = (
    (
        EvaluationSourceFamily.ACTIONS,
        "actions/create-registration-token-for-org",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.ACTIONS,
        "actions/create-registration-token-for-repo",
        EvaluationRole.TUNING,
    ),
    (
        EvaluationSourceFamily.ACTIONS,
        "actions/create-remove-token-for-org",
        EvaluationRole.HELD_OUT,
    ),
    (
        EvaluationSourceFamily.ACTIONS,
        "actions/create-remove-token-for-repo",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.ACTIONS,
        "actions/create-workflow-dispatch",
        EvaluationRole.TUNING,
    ),

    (
        EvaluationSourceFamily.ISSUES,
        "issues/add-assignees",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.ISSUES,
        "issues/add-blocked-by-dependency",
        EvaluationRole.HELD_OUT,
    ),
    (
        EvaluationSourceFamily.ISSUES,
        "issues/add-sub-issue",
        EvaluationRole.TUNING,
    ),
    (
        EvaluationSourceFamily.ISSUES,
        "issues/create",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.ISSUES,
        "issues/update",
        EvaluationRole.HELD_OUT,
    ),

    (
        EvaluationSourceFamily.PULL_REQUESTS,
        "pulls/create",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.PULL_REQUESTS,
        "pulls/get",
        EvaluationRole.TUNING,
    ),
    (
        EvaluationSourceFamily.PULL_REQUESTS,
        "pulls/list",
        EvaluationRole.HELD_OUT,
    ),
    (
        EvaluationSourceFamily.PULL_REQUESTS,
        "pulls/remove-requested-reviewers",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.PULL_REQUESTS,
        "pulls/update",
        EvaluationRole.TUNING,
    ),

    (
        EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
        "repos/accept-invitation-for-authenticated-user",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
        "repos/create-for-authenticated-user",
        EvaluationRole.HELD_OUT,
    ),
    (
        EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
        "repos/create-in-org",
        EvaluationRole.TUNING,
    ),
    (
        EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
        "repos/get-content",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
        "repos/list-attestations",
        EvaluationRole.HELD_OUT,
    ),
)


GUIDANCE_CLUSTER_SPECS = (
    (
        "docs-api-versions",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        "docs-authentication",
        EvaluationRole.TUNING,
    ),
    (
        "docs-best-practices",
        EvaluationRole.HELD_OUT,
    ),
    (
        "docs-breaking-changes",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        "docs-credential-security",
        EvaluationRole.TUNING,
    ),
    (
        "docs-getting-started",
        EvaluationRole.HELD_OUT,
    ),
    (
        "docs-pagination",
        EvaluationRole.DEVELOPMENT,
    ),
    (
        "docs-rate-limits",
        EvaluationRole.TUNING,
    ),
    (
        "docs-timezones",
        EvaluationRole.HELD_OUT,
    ),
    (
        "docs-troubleshooting",
        EvaluationRole.DEVELOPMENT,
    ),
)


SCENARIO_QUOTAS = (
    Phase4ScenarioQuota(
        data_role=EvaluationRole.DEVELOPMENT,
        scenario_class=ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        case_count=7,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.DEVELOPMENT,
        scenario_class=ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        case_count=5,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.DEVELOPMENT,
        scenario_class=ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
        case_count=5,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.DEVELOPMENT,
        scenario_class=ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        case_count=3,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.DEVELOPMENT,
        scenario_class=ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        case_count=4,
    ),

    Phase4ScenarioQuota(
        data_role=EvaluationRole.TUNING,
        scenario_class=ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        case_count=6,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.TUNING,
        scenario_class=ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        case_count=3,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.TUNING,
        scenario_class=ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
        case_count=3,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.TUNING,
        scenario_class=ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        case_count=3,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.TUNING,
        scenario_class=ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        case_count=3,
    ),

    Phase4ScenarioQuota(
        data_role=EvaluationRole.HELD_OUT,
        scenario_class=ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        case_count=5,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.HELD_OUT,
        scenario_class=ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE,
        case_count=4,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.HELD_OUT,
        scenario_class=ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION,
        case_count=4,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.HELD_OUT,
        scenario_class=ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION,
        case_count=2,
    ),
    Phase4ScenarioQuota(
        data_role=EvaluationRole.HELD_OUT,
        scenario_class=ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
        case_count=3,
    ),
)


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _load_manifest() -> Phase3dChunkManifest:
    content = MANIFEST_PATH.read_bytes()

    if (
        _sha256_bytes(content)
        != PHASE3D_CHUNK_MANIFEST_SHA256
    ):
        raise RuntimeError(
            "Phase 3D manifest SHA mismatch"
        )

    sidecar = MANIFEST_PATH.with_suffix(
        MANIFEST_PATH.suffix + ".sha256"
    )

    expected = (
        f"{PHASE3D_CHUNK_MANIFEST_SHA256}  "
        f"{MANIFEST_PATH.name}"
    )

    observed = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    if observed != expected:
        raise RuntimeError(
            "Phase 3D manifest sidecar mismatch"
        )

    return (
        Phase3dChunkManifest
        .model_validate_json(
            content
        )
    )


def _operation_core_chunks(
    manifest: Phase3dChunkManifest,
    *,
    operation_id: str,
    source_family: EvaluationSourceFamily,
    source_state: SourceState,
    data_role: DataRole,
) -> tuple[CorpusChunkRecord, ...]:
    chunks = tuple(
        chunk
        for chunk in manifest.chunks
        if (
            chunk.chunk_kind
            is ChunkKind.OPENAPI_OPERATION_CORE
            and chunk.evidence_scope.source_state
            is source_state
            and chunk.evidence_scope.data_role
            is data_role
            and operation_id
            in chunk.linked_operation_ids
        )
    )

    if not chunks:
        raise RuntimeError(
            f"missing operation-core evidence: "
            f"{operation_id} {source_state.value}"
        )

    for chunk in chunks:
        observed_families = tuple(
            chunk.semantic_families
        )

        if observed_families != (
            source_family.value,
        ):
            raise RuntimeError(
                f"semantic family mismatch: "
                f"{operation_id}"
            )

    return tuple(
        sorted(
            chunks,
            key=lambda chunk: (
                chunk.chunk_id
            ),
        )
    )


def _source_ids(
    chunks: tuple[CorpusChunkRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                parent.source_id
                for chunk in chunks
                for parent in chunk.parents
            }
        )
    )


def _build_openapi_cluster(
    manifest: Phase3dChunkManifest,
    *,
    source_family: EvaluationSourceFamily,
    operation_id: str,
    role: EvaluationRole,
) -> Phase4EvidenceCluster:
    current = _operation_core_chunks(
        manifest,
        operation_id=operation_id,
        source_family=source_family,
        source_state=SourceState.CURRENT,
        data_role=DataRole.CORPUS_SOURCE,
    )

    historical = _operation_core_chunks(
        manifest,
        operation_id=operation_id,
        source_family=source_family,
        source_state=SourceState.HISTORICAL_COMPARISON,
        data_role=DataRole.HISTORICAL_SOURCE,
    )

    return Phase4EvidenceCluster(
        cluster_id=(
            f"openapi-pair:{operation_id}"
        ),
        cluster_kind=(
            EvidenceClusterKind.OPENAPI_VERSION_PAIR
        ),
        source_family=source_family,
        data_role=role,
        operation_id=operation_id,
        current_evidence_ids=tuple(
            chunk.chunk_id
            for chunk in current
        ),
        historical_evidence_ids=tuple(
            chunk.chunk_id
            for chunk in historical
        ),
        current_source_ids=_source_ids(
            current
        ),
        historical_source_ids=_source_ids(
            historical
        ),
    )


def _build_guidance_cluster(
    manifest: Phase3dChunkManifest,
    *,
    source_id: str,
    role: EvaluationRole,
) -> Phase4EvidenceCluster:
    chunks = tuple(
        sorted(
            (
                chunk
                for chunk in manifest.chunks
                if (
                    chunk.chunk_kind
                    is ChunkKind.AUTHORED_SECTION
                    and chunk.evidence_scope.source_state
                    is SourceState.CURRENT
                    and chunk.evidence_scope.data_role
                    is DataRole.CORPUS_SOURCE
                    and any(
                        parent.source_id
                        == source_id
                        for parent
                        in chunk.parents
                    )
                )
            ),
            key=lambda chunk: (
                chunk.chunk_id
            ),
        )
    )

    if not chunks:
        raise RuntimeError(
            f"missing authored guidance evidence: "
            f"{source_id}"
        )

    return Phase4EvidenceCluster(
        cluster_id=(
            f"guidance:{source_id}"
        ),
        cluster_kind=(
            EvidenceClusterKind.AUTHORED_GUIDANCE
        ),
        source_family=(
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
        ),
        data_role=role,
        authored_source_id=source_id,
        current_evidence_ids=tuple(
            chunk.chunk_id
            for chunk in chunks
        ),
        current_source_ids=_source_ids(
            chunks
        ),
    )


def main() -> None:
    manifest = _load_manifest()

    clusters = [
        _build_openapi_cluster(
            manifest,
            source_family=family,
            operation_id=operation_id,
            role=role,
        )
        for (
            family,
            operation_id,
            role,
        ) in OPENAPI_CLUSTER_SPECS
    ]

    clusters.extend(
        _build_guidance_cluster(
            manifest,
            source_id=source_id,
            role=role,
        )
        for (
            source_id,
            role,
        ) in GUIDANCE_CLUSTER_SPECS
    )

    ordered_clusters = tuple(
        sorted(
            clusters,
            key=lambda cluster: (
                cluster.cluster_id
            ),
        )
    )

    constitution = (
        Phase4EvidenceClusterConstitution(
            scenario_quotas=SCENARIO_QUOTAS,
            clusters=ordered_clusters,
        )
    )

    constitution_sha = (
        write_json_with_sha256(
            CONSTITUTION_PATH,
            constitution,
        )
    )

    authoring_evidence_ids = {
        evidence_id
        for cluster in constitution.clusters
        for evidence_id
        in cluster.authoring_evidence_ids
    }

    receipt = (
        Phase4EvidenceClusterReceipt(
            constitution_sha256=(
                constitution_sha
            ),
            authoring_evidence_id_count=(
                len(authoring_evidence_ids)
            ),
        )
    )

    receipt_sha = write_json_with_sha256(
        RECEIPT_PATH,
        receipt,
    )

    print(
        "PHASE4_CLUSTER_COUNT="
        f"{len(constitution.clusters)}"
    )

    print(
        "PHASE4_CANONICAL_CASE_COUNT="
        f"{constitution.canonical_case_count}"
    )

    print(
        "PHASE4_DEVELOPMENT_CLUSTER_COUNT=12"
    )

    print(
        "PHASE4_TUNING_CLUSTER_COUNT=9"
    )

    print(
        "PHASE4_HELD_OUT_CLUSTER_COUNT=9"
    )

    print(
        "PHASE4_AUTHORING_EVIDENCE_ID_COUNT="
        f"{len(authoring_evidence_ids)}"
    )

    print(
        "PHASE4_CONSTITUTION_SHA256="
        f"{constitution_sha}"
    )

    print(
        "PHASE4_CONSTITUTION_RECEIPT_SHA256="
        f"{receipt_sha}"
    )

    print(
        "PHASE4_HELD_OUT_ASSIGNMENT_FROZEN=true"
    )

    print(
        "PHASE4_CASE_AUTHORING_AUTHORIZED=true"
    )

    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )

    print(
        "PHASE4_RELEASE_ELIGIBLE=false"
    )


if __name__ == "__main__":
    main()
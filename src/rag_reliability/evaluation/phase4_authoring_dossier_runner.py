"""Materialize the frozen Phase 4C authoring dossier."""

from __future__ import annotations

import hashlib
import html
from pathlib import Path

from rag_reliability.corpus.chunked import (
    Phase3dChunkManifest,
)
from rag_reliability.corpus.chunking import (
    CorpusChunkRecord,
)
from rag_reliability.corpus.render_audit import (
    write_json_with_sha256,
)
from rag_reliability.evaluation.authoring_dossier import (
    PHASE4_CONSTITUTION_SHA256,
    REVIEW_MARKDOWN_RELATIVE_PATH,
    Phase4AuthoringClusterReview,
    Phase4AuthoringDossier,
    Phase4AuthoringEvidence,
)
from rag_reliability.evaluation.constitution import (
    PHASE3D_CHUNK_MANIFEST_SHA256,
    Phase4EvidenceClusterConstitution,
)

_CONSTITUTION_RELATIVE_PATH = (
    Path("datasets")
    / "evaluation"
    / "phase4_evidence_cluster_constitution_v1.json"
)

_CHUNK_MANIFEST_RELATIVE_PATH = (
    Path("datasets")
    / "chunk_manifests"
    / "phase3d_chunk_manifest_v1.json"
)

_CHUNK_ROOT_RELATIVE_PATH = (
    Path("datasets")
    / "chunks"
    / "phase3d_v1"
)

_DOSSIER_JSON_RELATIVE_PATH = (
    Path("artifacts")
    / "development"
    / "phase4c_authoring_dossier_v1.json"
)

_DOSSIER_MARKDOWN_RELATIVE_PATH = Path(
    REVIEW_MARKDOWN_RELATIVE_PATH
)


class Phase4AuthoringDossierError(
    ValueError
):
    """Frozen authoring evidence cannot be safely materialized."""


def _sha256_bytes(
    content: bytes,
) -> str:
    return hashlib.sha256(
        content
    ).hexdigest()


def _verify_sidecar(
    path: Path,
    expected_sha256: str,
) -> None:
    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    observed = sidecar.read_text(
        encoding="utf-8"
    ).strip()

    expected = (
        f"{expected_sha256}  "
        f"{path.name}"
    )

    if observed != expected:
        raise Phase4AuthoringDossierError(
            f"SHA sidecar mismatch: {path.name}"
        )


def _read_constitution(
    repo_root: Path,
) -> Phase4EvidenceClusterConstitution:
    path = (
        repo_root
        / _CONSTITUTION_RELATIVE_PATH
    )

    content = path.read_bytes()

    observed_sha = _sha256_bytes(
        content
    )

    if (
        observed_sha
        != PHASE4_CONSTITUTION_SHA256
    ):
        raise Phase4AuthoringDossierError(
            "Phase 4 constitution SHA mismatch"
        )

    _verify_sidecar(
        path,
        PHASE4_CONSTITUTION_SHA256,
    )

    return (
        Phase4EvidenceClusterConstitution
        .model_validate_json(
            content
        )
    )


def _read_chunk_manifest(
    repo_root: Path,
) -> Phase3dChunkManifest:
    path = (
        repo_root
        / _CHUNK_MANIFEST_RELATIVE_PATH
    )

    content = path.read_bytes()

    observed_sha = _sha256_bytes(
        content
    )

    if (
        observed_sha
        != PHASE3D_CHUNK_MANIFEST_SHA256
    ):
        raise Phase4AuthoringDossierError(
            "Phase 3D chunk manifest SHA mismatch"
        )

    _verify_sidecar(
        path,
        PHASE3D_CHUNK_MANIFEST_SHA256,
    )

    return (
        Phase3dChunkManifest
        .model_validate_json(
            content
        )
    )


def _load_evidence(
    repo_root: Path,
    chunk: CorpusChunkRecord,
) -> tuple[
    Phase4AuthoringEvidence,
    str,
]:
    chunk_root = (
        repo_root
        / _CHUNK_ROOT_RELATIVE_PATH
    ).resolve()

    content_path = (
        repo_root
        / Path(chunk.content_path)
    ).resolve()

    if not content_path.is_relative_to(
        chunk_root
    ):
        raise Phase4AuthoringDossierError(
            "authoring evidence path escapes "
            "frozen Phase 3D chunk root"
        )

    content_bytes = (
        content_path.read_bytes()
    )

    if (
        len(content_bytes)
        != chunk.byte_count
    ):
        raise Phase4AuthoringDossierError(
            "authoring evidence byte-count "
            f"mismatch: {chunk.chunk_id}"
        )

    if (
        _sha256_bytes(content_bytes)
        != chunk.content_sha256
    ):
        raise Phase4AuthoringDossierError(
            "authoring evidence SHA mismatch: "
            f"{chunk.chunk_id}"
        )

    try:
        content = content_bytes.decode(
            "utf-8"
        )
    except UnicodeDecodeError as exc:
        raise Phase4AuthoringDossierError(
            "authoring evidence is not UTF-8: "
            f"{chunk.chunk_id}"
        ) from exc

    record = Phase4AuthoringEvidence(
        evidence_id=chunk.chunk_id,
        chunk_kind=chunk.chunk_kind,
        content_path=chunk.content_path,
        content_sha256=(
            chunk.content_sha256
        ),
        byte_count=chunk.byte_count,
        chunking_policy_sha256=(
            chunk.chunking_policy_sha256
        ),
        chunk_index=chunk.chunk_index,
        parents=chunk.parents,
        evidence_scope=(
            chunk.evidence_scope
        ),
        semantic_families=(
            chunk.semantic_families
        ),
        linked_operation_ids=(
            chunk.linked_operation_ids
        ),
        component_ref=chunk.component_ref,
        section_headings=(
            chunk.section_headings
        ),
    )

    return record, content


def _records_for_ids(
    repo_root: Path,
    chunk_by_id: dict[
        str,
        CorpusChunkRecord,
    ],
    evidence_ids: tuple[
        str,
        ...,
    ],
    content_by_id: dict[
        str,
        str,
    ],
) -> tuple[
    Phase4AuthoringEvidence,
    ...,
]:
    records: list[
        Phase4AuthoringEvidence
    ] = []

    for evidence_id in evidence_ids:
        chunk = chunk_by_id.get(
            evidence_id
        )

        if chunk is None:
            raise Phase4AuthoringDossierError(
                "frozen authoring evidence is "
                f"missing: {evidence_id}"
            )

        if evidence_id in content_by_id:
            raise Phase4AuthoringDossierError(
                "authoring evidence crosses "
                "cluster boundaries: "
                f"{evidence_id}"
            )

        record, content = _load_evidence(
            repo_root,
            chunk,
        )

        records.append(
            record
        )

        content_by_id[
            evidence_id
        ] = content

    return tuple(
        records
    )


def _append_evidence_review(
    lines: list[str],
    *,
    label: str,
    evidence: Phase4AuthoringEvidence,
    content: str,
) -> None:
    lines.extend(
        [
            (
                "### "
                f"{label}: `{evidence.evidence_id}`"
            ),
            "",
            (
                "- chunk kind: "
                f"`{evidence.chunk_kind.value}`"
            ),
            (
                "- content path: "
                f"`{evidence.content_path}`"
            ),
            (
                "- content SHA256: "
                f"`{evidence.content_sha256}`"
            ),
            (
                "- byte count: "
                f"`{evidence.byte_count}`"
            ),
            (
                "- source state: "
                "`"
                f"{evidence.evidence_scope.source_state.value}"
                "`"
            ),
            (
                "- authority: "
                "`"
                f"{evidence.evidence_scope.authority_level.value}"
                "`"
            ),
            (
                "- corpus data role: "
                "`"
                f"{evidence.evidence_scope.data_role.value}"
                "`"
            ),
            (
                "- API version/snapshot: "
                "`"
                f"{evidence.evidence_scope.api_version_or_snapshot}"
                "`"
            ),
            (
                "- source commit/version: "
                "`"
                f"{evidence.evidence_scope.source_commit_sha_or_version}"
                "`"
            ),
        ]
    )

    if evidence.semantic_families:
        lines.append(
            "- semantic families: "
            + ", ".join(
                f"`{family}`"
                for family
                in evidence.semantic_families
            )
        )

    if evidence.linked_operation_ids:
        lines.append(
            "- linked operations: "
            + ", ".join(
                f"`{operation_id}`"
                for operation_id
                in evidence.linked_operation_ids
            )
        )

    if evidence.section_headings:
        lines.append(
            "- section headings: "
            + " ? ".join(
                f"`{heading}`"
                for heading
                in evidence.section_headings
            )
        )

    for parent in evidence.parents:
        lines.extend(
            [
                (
                    "- parent source ID: "
                    f"`{parent.source_id}`"
                ),
                (
                    "- parent document ID: "
                    f"`{parent.document_id}`"
                ),
                (
                    "- parent normalized SHA256: "
                    f"`{parent.normalized_content_sha256}`"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "<details>",
            "<summary>Evidence content</summary>",
            "",
            "<pre>",
            html.escape(
                content,
                quote=False,
            ),
            "</pre>",
            "",
            "</details>",
            "",
        ]
    )


def _render_markdown(
    clusters: tuple[
        Phase4AuthoringClusterReview,
        ...,
    ],
    content_by_id: dict[
        str,
        str,
    ],
) -> str:
    lines = [
        "# Phase 4C Authoring Dossier V1",
        "",
        (
            "**Purpose:** deterministic, read-only "
            "review of the frozen evidence available "
            "for canonical case authoring."
        ),
        "",
        (
            "**Phase 4 constitution SHA256:** "
            f"`{PHASE4_CONSTITUTION_SHA256}`"
        ),
        "",
        (
            "**Phase 3D chunk manifest SHA256:** "
            f"`{PHASE3D_CHUNK_MANIFEST_SHA256}`"
        ),
        "",
        (
            "> This is an authoring aid. It does not "
            "change cluster roles, expand gold evidence, "
            "authorize baseline execution, or enter the "
            "runtime RAG input."
        ),
        "",
        (
            "> Evidence text below is HTML-escaped for "
            "review. The authoritative source identity "
            "is the recorded content path and SHA256."
        ),
        "",
    ]

    for cluster in clusters:
        lines.extend(
            [
                (
                    "## Cluster: "
                    f"`{cluster.cluster_id}`"
                ),
                "",
                (
                    "- evaluation role: "
                    f"`{cluster.evaluation_role.value}`"
                ),
                (
                    "- cluster kind: "
                    f"`{cluster.cluster_kind.value}`"
                ),
                (
                    "- source family: "
                    f"`{cluster.source_family.value}`"
                ),
            ]
        )

        if cluster.operation_id is not None:
            lines.append(
                "- operation ID: "
                f"`{cluster.operation_id}`"
            )

        if (
            cluster.authored_source_id
            is not None
        ):
            lines.append(
                "- authored source ID: "
                f"`{cluster.authored_source_id}`"
            )

        lines.append("")

        for evidence in (
            cluster.current_evidence
        ):
            _append_evidence_review(
                lines,
                label="Current evidence",
                evidence=evidence,
                content=content_by_id[
                    evidence.evidence_id
                ],
            )

        for evidence in (
            cluster.historical_evidence
        ):
            _append_evidence_review(
                lines,
                label="Historical evidence",
                evidence=evidence,
                content=content_by_id[
                    evidence.evidence_id
                ],
            )

    return (
        "\n".join(lines)
        .rstrip()
        + "\n"
    )


def _write_bytes_with_sha256(
    path: Path,
    content: bytes,
) -> str:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_bytes(
        content
    )

    digest = _sha256_bytes(
        content
    )

    sidecar = path.with_suffix(
        path.suffix + ".sha256"
    )

    sidecar.write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    return digest


def materialize_phase4c_authoring_dossier(
    repo_root: Path,
) -> tuple[
    Phase4AuthoringDossier,
    str,
    str,
]:
    constitution = _read_constitution(
        repo_root
    )

    manifest = _read_chunk_manifest(
        repo_root
    )

    chunk_by_id = {
        chunk.chunk_id: chunk
        for chunk in manifest.chunks
    }

    reviews: list[
        Phase4AuthoringClusterReview
    ] = []

    content_by_id: dict[
        str,
        str,
    ] = {}

    for cluster in constitution.clusters:
        current_evidence = (
            _records_for_ids(
                repo_root,
                chunk_by_id,
                tuple(
                    cluster.current_evidence_ids
                ),
                content_by_id,
            )
        )

        historical_evidence = (
            _records_for_ids(
                repo_root,
                chunk_by_id,
                tuple(
                    cluster.historical_evidence_ids
                ),
                content_by_id,
            )
        )

        reviews.append(
            Phase4AuthoringClusterReview(
                cluster_id=cluster.cluster_id,
                cluster_kind=cluster.cluster_kind,
                source_family=cluster.source_family,
                evaluation_role=cluster.data_role,
                operation_id=cluster.operation_id,
                authored_source_id=(
                    cluster.authored_source_id
                ),
                current_source_ids=(
                    cluster.current_source_ids
                ),
                historical_source_ids=(
                    cluster.historical_source_ids
                ),
                current_evidence=(
                    current_evidence
                ),
                historical_evidence=(
                    historical_evidence
                ),
            )
        )

    ordered_reviews = tuple(
        reviews
    )

    markdown = _render_markdown(
        ordered_reviews,
        content_by_id,
    )

    markdown_bytes = markdown.encode(
        "utf-8"
    )

    markdown_sha256 = _sha256_bytes(
        markdown_bytes
    )

    dossier = Phase4AuthoringDossier(
        review_markdown_sha256=(
            markdown_sha256
        ),
        clusters=ordered_reviews,
    )

    markdown_path = (
        repo_root
        / _DOSSIER_MARKDOWN_RELATIVE_PATH
    )

    observed_markdown_sha = (
        _write_bytes_with_sha256(
            markdown_path,
            markdown_bytes,
        )
    )

    if (
        observed_markdown_sha
        != markdown_sha256
    ):
        raise Phase4AuthoringDossierError(
            "authoring Markdown SHA drift"
        )

    dossier_path = (
        repo_root
        / _DOSSIER_JSON_RELATIVE_PATH
    )

    dossier_sha256 = (
        write_json_with_sha256(
            dossier_path,
            dossier,
        )
    )

    return (
        dossier,
        dossier_sha256,
        markdown_sha256,
    )


def main() -> None:
    repo_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    (
        dossier,
        dossier_sha256,
        markdown_sha256,
    ) = materialize_phase4c_authoring_dossier(
        repo_root
    )

    current_count = sum(
        len(
            cluster.current_evidence
        )
        for cluster
        in dossier.clusters
    )

    historical_count = sum(
        len(
            cluster.historical_evidence
        )
        for cluster
        in dossier.clusters
    )

    print(
        "PHASE4C_DOSSIER_CLUSTER_COUNT="
        f"{len(dossier.clusters)}"
    )

    print(
        "PHASE4C_DOSSIER_AUTHORING_EVIDENCE_COUNT="
        f"{dossier.authoring_evidence_id_count}"
    )

    print(
        "PHASE4C_DOSSIER_CURRENT_EVIDENCE_COUNT="
        f"{current_count}"
    )

    print(
        "PHASE4C_DOSSIER_HISTORICAL_EVIDENCE_COUNT="
        f"{historical_count}"
    )

    print(
        "PHASE4C_DOSSIER_UNKNOWN_EVIDENCE_COUNT=0"
    )

    print(
        "PHASE4C_DOSSIER_ROLE_DRIFT_COUNT=0"
    )

    print(
        "PHASE4C_DOSSIER_CONSTITUTION_SHA256="
        f"{PHASE4_CONSTITUTION_SHA256}"
    )

    print(
        "PHASE4C_DOSSIER_JSON_SHA256="
        f"{dossier_sha256}"
    )

    print(
        "PHASE4C_DOSSIER_MARKDOWN_SHA256="
        f"{markdown_sha256}"
    )

    print(
        "PHASE4C_DOSSIER_READY=true"
    )

    print(
        "PHASE4_CASE_AUTHORING_AUTHORIZED=true"
    )

    print(
        "PHASE4_BASELINE_AUTHORIZED=false"
    )


if __name__ == "__main__":
    main()

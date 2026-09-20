"""Validate and freeze the fresh post-reject confirmation suite."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    Criticality,
    EvaluationSourceFamily,
    ResponseMode,
    ScenarioClass,
    SourceState,
)
from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.corpus.render_audit import write_json_with_sha256
from rag_reliability.evaluation.retrieval_characterization import (
    _load_indexed_documents,
)

_SUITE_PATH = Path("artifacts") / "development" / "phase5_post_reject_confirmation_cases_v1.json"
_FREEZE_PATH = Path("artifacts") / "development" / "phase5_post_reject_confirmation_freeze_v1.json"
_DEVELOPMENT_PATH = Path("artifacts") / "development" / "phase4c_development_cases_v1.json"
_TUNING_PATH = Path("artifacts") / "development" / "phase4c_tuning_cases_v1.json"

_DEVELOPMENT_SHA256 = "53f10fc7e74f5205e15efba28d76a0926901959115e3ef59a4987b1ff60ce835"
_TUNING_SHA256 = "82d91724499138b53924531aaaa344af4473a463cfa326f7795379d682af9c28"
_PROTOCOL_SHA256 = "4723c854f32d114958633203d9db0b9e629a38aea8242cc958f25f1d5eddbfed"
_PROTOCOL_FREEZE_SHA256 = "76035d9dd68c7f02198fcfba1481ab9bb705a116a03ec57588d5772fb7811288"
_MANIFEST_SHA256 = "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"


class PostRejectConfirmationCase(ContractModel):
    case_id: NonEmptyStr
    case_version: Literal["1.0"] = "1.0"
    data_role: Literal["post_reject_confirmation_case"]
    source_family: EvaluationSourceFamily
    scenario_class: ScenarioClass
    criticality: Criticality
    query: NonEmptyStr
    expected_response_mode: ResponseMode
    required_fact_ids: tuple[NonEmptyStr, ...] = ()
    required_evidence_ids: tuple[NonEmptyStr, ...] = ()
    required_source_ids: tuple[NonEmptyStr, ...] = ()
    allowed_source_states: tuple[SourceState, ...] = (SourceState.CURRENT,)
    forbidden_evidence_ids: tuple[NonEmptyStr, ...] = ()
    forbidden_source_ids: tuple[NonEmptyStr, ...] = ()
    required_api_version: Literal["2026-03-10"] = "2026-03-10"
    required_authority_level: Literal[AuthorityLevel.AUTHORITATIVE]
    must_refuse_reason: Literal["insufficient_evidence"] | None = None
    gold_fact_rubric: tuple[NonEmptyStr, ...] = ()
    scoring_notes: NonEmptyStr
    authoring_evidence: tuple[NonEmptyStr, ...] = Field(min_length=1)
    grounding_terms: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if self.expected_response_mode is ResponseMode.REFUSE:
            if self.must_refuse_reason != "insufficient_evidence":
                raise ValueError("refusal requires insufficient_evidence")
            if (
                self.required_fact_ids
                or self.required_evidence_ids
                or self.required_source_ids
                or self.gold_fact_rubric
            ):
                raise ValueError("refusal cannot carry answer gold")
        else:
            if self.must_refuse_reason is not None:
                raise ValueError("answerable case cannot carry refusal reason")
            if not (
                self.required_fact_ids
                and self.required_evidence_ids
                and self.required_source_ids
                and self.gold_fact_rubric
            ):
                raise ValueError("answerable case requires complete gold")
        return self

    def to_runtime_input(self) -> RuntimeCaseInput:
        return RuntimeCaseInput(case_id=self.case_id, query=self.query)


class PostRejectConfirmationRecord(ContractModel):
    cluster_id: NonEmptyStr
    case: PostRejectConfirmationCase


class PostRejectConfirmationSuiteV1(ContractModel):
    suite_version: Literal["phase5-post-reject-confirmation-v1"]
    data_role: Literal["post_reject_confirmation_case"]
    post_reject_protocol_sha256: Sha256
    post_reject_protocol_freeze_sha256: Sha256
    chunk_manifest_sha256: Sha256
    case_count: Literal[24]
    cluster_count: Literal[12]
    answerable_case_count: Literal[20]
    refusal_case_count: Literal[4]
    records: tuple[PostRejectConfirmationRecord, ...] = Field(
        min_length=24,
        max_length=24,
    )
    exact_development_query_reuse_count: Literal[0]
    exact_tuning_query_reuse_count: Literal[0]
    held_out_case_content_read: Literal[False]
    failure_specific_development_evidence_opened: Literal[False]
    intervention_specific_behavior_used_for_authoring: Literal[False]
    runtime_projection_fields: tuple[NonEmptyStr, ...]
    fresh_confirmation_materialized: Literal[True]
    fresh_confirmation_frozen: Literal[False]
    failure_localization_started: Literal[False]
    development_spent_for_future_confirmation: Literal[False]
    provider_invoked: Literal[False]
    b0_executed: Literal[False]
    release_eligible: Literal[False]

    @model_validator(mode="after")
    def validate_suite(self) -> Self:
        if self.post_reject_protocol_sha256 != _PROTOCOL_SHA256:
            raise ValueError("post-reject protocol custody drifted")
        if self.post_reject_protocol_freeze_sha256 != _PROTOCOL_FREEZE_SHA256:
            raise ValueError("post-reject freeze custody drifted")
        if self.chunk_manifest_sha256 != _MANIFEST_SHA256:
            raise ValueError("chunk manifest custody drifted")
        if self.runtime_projection_fields != ("case_id", "query"):
            raise ValueError("runtime projection drifted")
        ids = tuple(record.case.case_id for record in self.records)
        if len(ids) != len(set(ids)):
            raise ValueError("fresh confirmation case IDs must be unique")
        clusters = tuple(record.cluster_id for record in self.records)
        if len(set(clusters)) != 12:
            raise ValueError("fresh confirmation cluster count drifted")
        if any(clusters.count(cluster_id) != 2 for cluster_id in set(clusters)):
            raise ValueError("each cluster requires exactly two cases")
        answerable = sum(
            record.case.expected_response_mode is not ResponseMode.REFUSE for record in self.records
        )
        refusals = sum(
            record.case.expected_response_mode is ResponseMode.REFUSE for record in self.records
        )
        if (answerable, refusals) != (20, 4):
            raise ValueError("fresh confirmation answer/refusal counts drifted")
        return self


class Phase5PostRejectConfirmationFreezeReceipt(ContractModel):
    receipt_version: Literal["phase5-post-reject-confirmation-freeze-v1"] = (
        "phase5-post-reject-confirmation-freeze-v1"
    )
    suite_version: Literal["phase5-post-reject-confirmation-v1"] = (
        "phase5-post-reject-confirmation-v1"
    )
    suite_sha256: Sha256
    case_count: Literal[24] = 24
    cluster_count: Literal[12] = 12
    answerable_case_count: Literal[20] = 20
    refusal_case_count: Literal[4] = 4
    fresh_confirmation_materialized: Literal[True] = True
    fresh_confirmation_frozen: Literal[True] = True
    failure_localization_activation_condition_satisfied: Literal[True] = True
    failure_specific_development_evidence_opened: Literal[False] = False
    failure_localization_started: Literal[False] = False
    development_spent_for_future_confirmation: Literal[False] = False
    held_out_case_content_read: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    provider_invoked: Literal[False] = False
    b0_executed: Literal[False] = False
    release_eligible: Literal[False] = False


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _verified_json(path: Path, expected_sha256: str) -> object:
    content = path.read_bytes()
    if _sha256(content) != expected_sha256:
        raise ValueError(f"artifact hash mismatch: {path}")
    return json.loads(content)


def _prior_queries(path: Path, expected_sha256: str) -> frozenset[str]:
    payload = _verified_json(path, expected_sha256)
    if not isinstance(payload, dict):
        raise ValueError("prior suite must be a JSON object")
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("prior suite records must be a list")
    queries: set[str] = set()
    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("prior suite record must be an object")
        raw_case = raw_record.get("case")
        if not isinstance(raw_case, dict):
            raise ValueError("prior suite record requires case")
        query = raw_case.get("query")
        if not isinstance(query, str):
            raise ValueError("prior suite query must be text")
        queries.add(query)
    return frozenset(queries)


def load_and_validate_post_reject_confirmation_suite(
    repo_root: Path,
) -> PostRejectConfirmationSuiteV1:
    suite_path = repo_root / _SUITE_PATH
    suite_content = suite_path.read_bytes()
    sidecar = suite_path.with_suffix(suite_path.suffix + ".sha256")
    expected_sidecar = f"{_sha256(suite_content)}  {suite_path.name}"
    if sidecar.read_text(encoding="utf-8").strip() != expected_sidecar:
        raise ValueError("fresh confirmation suite sidecar mismatch")

    suite = PostRejectConfirmationSuiteV1.model_validate_json(suite_content)

    development_queries = _prior_queries(
        repo_root / _DEVELOPMENT_PATH,
        _DEVELOPMENT_SHA256,
    )
    tuning_queries = _prior_queries(
        repo_root / _TUNING_PATH,
        _TUNING_SHA256,
    )
    new_queries = tuple(record.case.query for record in suite.records)
    if any(query in development_queries for query in new_queries):
        raise ValueError("fresh suite reuses a DEVELOPMENT query")
    if any(query in tuning_queries for query in new_queries):
        raise ValueError("fresh suite reuses a TUNING query")

    documents, evidence_ids = _load_indexed_documents(repo_root)
    by_id = {document.evidence_id: document for document in documents}

    for record in suite.records:
        case = record.case
        for evidence_id in case.authoring_evidence:
            if evidence_id not in evidence_ids:
                raise ValueError(f"missing authoring evidence: {evidence_id}")
        if case.expected_response_mode is ResponseMode.REFUSE:
            continue
        for evidence_id in case.required_evidence_ids:
            if evidence_id not in evidence_ids:
                raise ValueError(f"missing required evidence: {evidence_id}")
        observed_sources = {
            source_id
            for evidence_id in case.required_evidence_ids
            for source_id in by_id[evidence_id].source_ids
        }
        if not set(case.required_source_ids) <= observed_sources:
            raise ValueError(f"required source mismatch: {case.case_id}")
        joined = "\n".join(by_id[evidence_id].content for evidence_id in case.authoring_evidence)
        for term in case.grounding_terms:
            if term not in joined:
                raise ValueError(f"grounding term missing for {case.case_id}: {term}")

    return suite


def materialize_phase5_post_reject_confirmation_freeze(
    repo_root: Path,
) -> tuple[
    PostRejectConfirmationSuiteV1,
    str,
    Phase5PostRejectConfirmationFreezeReceipt,
    str,
]:
    suite = load_and_validate_post_reject_confirmation_suite(repo_root)
    suite_path = repo_root / _SUITE_PATH
    suite_sha256 = _sha256(suite_path.read_bytes())
    receipt = Phase5PostRejectConfirmationFreezeReceipt(
        suite_sha256=suite_sha256,
    )
    receipt_sha256 = write_json_with_sha256(
        repo_root / _FREEZE_PATH,
        receipt,
    )
    return suite, suite_sha256, receipt, receipt_sha256


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    suite, suite_sha, receipt, freeze_sha = materialize_phase5_post_reject_confirmation_freeze(
        repo_root
    )
    print(f"PHASE5_POST_REJECT_CONFIRMATION_SUITE_SHA256={suite_sha}")
    print(f"PHASE5_POST_REJECT_CONFIRMATION_FREEZE_SHA256={freeze_sha}")
    print(
        "PHASE5_POST_REJECT_CONFIRMATION_SHAPE="
        f"cases:{suite.case_count},clusters:{suite.cluster_count},"
        f"answerable:{suite.answerable_case_count},refusal:{suite.refusal_case_count}"
    )
    print(
        "PHASE5_POST_REJECT_LOCALIZATION_ACTIVATION_CONDITION="
        f"{str(receipt.failure_localization_activation_condition_satisfied).lower()}"
    )
    print("PHASE5_POST_REJECT_FAILURE_LOCALIZATION_STARTED=false")
    print("PHASE5_POST_REJECT_HELD_OUT_EXPOSED=false")


if __name__ == "__main__":
    main()

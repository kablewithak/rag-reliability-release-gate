import pytest
from pydantic import ValidationError

from rag_reliability.contracts.enums import (
    AuthorityLevel,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    ResponseMode,
    ScenarioClass,
    SourceState,
)
from rag_reliability.contracts.evaluation import EvaluationCase, RuntimeCaseInput


def build_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="dev-001",
        case_version="1.0",
        data_role=EvaluationRole.DEVELOPMENT,
        source_family=EvaluationSourceFamily.ISSUES,
        scenario_class=ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE,
        criticality=Criticality.CRITICAL,
        query="Which API version does this case target?",
        expected_response_mode=ResponseMode.ANSWER,
        required_fact_ids=("fact-1",),
        required_source_ids=("source-1",),
        allowed_source_states=(SourceState.CURRENT,),
        forbidden_source_ids=("historical-1",),
        required_api_version="2026-03-10",
        required_authority_level=AuthorityLevel.AUTHORITATIVE,
        gold_fact_rubric=("The response must identify the frozen target version.",),
        scoring_notes="Development-only evaluator note.",
        authoring_evidence=("source-1",),
    )


def test_runtime_projection_contains_only_case_id_and_query() -> None:
    runtime = build_case().to_runtime_input()

    assert runtime.model_dump() == {
        "case_id": "dev-001",
        "query": "Which API version does this case target?",
    }


def test_full_evaluation_case_is_rejected_at_runtime_boundary() -> None:
    case = build_case()

    with pytest.raises(ValidationError):
        RuntimeCaseInput.model_validate(case.model_dump())


def test_runtime_contract_rejects_explicit_gold_field() -> None:
    with pytest.raises(ValidationError):
        RuntimeCaseInput.model_validate(
            {
                "case_id": "dev-001",
                "query": "Question",
                "required_source_ids": ["source-1"],
            }
        )


def test_refusal_case_requires_reason() -> None:
    with pytest.raises(ValidationError):
        EvaluationCase(
            case_id="dev-002",
            case_version="1.0",
            data_role=EvaluationRole.DEVELOPMENT,
            source_family=EvaluationSourceFamily.ACTIONS,
            scenario_class=ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE,
            criticality=Criticality.CRITICAL,
            query="Answer despite unresolved conflict.",
            expected_response_mode=ResponseMode.REFUSE,
            allowed_source_states=(SourceState.CURRENT, SourceState.HISTORICAL_COMPARISON),
            required_api_version="2026-03-10",
            required_authority_level=AuthorityLevel.AUTHORITATIVE,
            scoring_notes="Must refuse safely.",
            authoring_evidence=("source-current", "source-historical"),
        )

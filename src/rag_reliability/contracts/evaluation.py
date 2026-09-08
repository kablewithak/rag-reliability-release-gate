"""Evaluation contracts and the evaluator/runtime projection boundary."""

from collections.abc import Mapping

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    Criticality,
    EvaluationRole,
    EvaluationSourceFamily,
    ResponseMode,
    ScenarioClass,
    SourceState,
)


class RuntimeCaseInput(ContractModel):
    """The only case payload that may enter the runtime RAG path."""

    case_id: NonEmptyStr
    query: NonEmptyStr


class OrchestrationCaseView(ContractModel):
    """Non-gold metadata visible to evaluation orchestration and tracing."""

    case_id: NonEmptyStr
    case_version: NonEmptyStr
    data_role: EvaluationRole
    source_family: EvaluationSourceFamily
    scenario_class: ScenarioClass
    criticality: Criticality
    query: NonEmptyStr


class EvaluationCase(ContractModel):
    """Full evaluator-owned case, including fields forbidden to runtime."""

    case_id: NonEmptyStr
    case_version: NonEmptyStr
    data_role: EvaluationRole
    source_family: EvaluationSourceFamily
    scenario_class: ScenarioClass
    criticality: Criticality
    query: NonEmptyStr

    expected_response_mode: ResponseMode
    required_fact_ids: tuple[NonEmptyStr, ...] = ()

    required_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()
    required_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    allowed_source_states: tuple[
        SourceState,
        ...,
    ] = Field(min_length=1)

    forbidden_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()
    forbidden_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    required_api_version: NonEmptyStr
    required_authority_level: AuthorityLevel
    must_refuse_reason: NonEmptyStr | None = None
    gold_fact_rubric: tuple[NonEmptyStr, ...] = ()
    scoring_notes: NonEmptyStr
    authoring_evidence: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def migrate_phase2_source_identity(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, Mapping):
            return value

        data = dict(value)

        if "required_evidence_ids" not in data:
            data["required_evidence_ids"] = tuple(
                data.get(
                    "required_source_ids",
                    (),
                )
            )

        if "forbidden_evidence_ids" not in data:
            data["forbidden_evidence_ids"] = tuple(
                data.get(
                    "forbidden_source_ids",
                    (),
                )
            )

        return data

    @model_validator(mode="after")
    def validate_expected_behavior(
        self,
    ) -> "EvaluationCase":
        identity_fields = (
            (
                "required_evidence_ids",
                self.required_evidence_ids,
            ),
            (
                "required_source_ids",
                self.required_source_ids,
            ),
            (
                "forbidden_evidence_ids",
                self.forbidden_evidence_ids,
            ),
            (
                "forbidden_source_ids",
                self.forbidden_source_ids,
            ),
        )

        for field_name, values in identity_fields:
            if len(values) != len(set(values)):
                raise ValueError(
                    f"{field_name} must be unique"
                )

        if (
            set(self.required_evidence_ids)
            & set(self.forbidden_evidence_ids)
        ):
            raise ValueError(
                "required and forbidden evidence "
                "IDs must be disjoint"
            )

        if (
            set(self.required_source_ids)
            & set(self.forbidden_source_ids)
        ):
            raise ValueError(
                "required and forbidden source "
                "IDs must be disjoint"
            )

        if (
            self.expected_response_mode
            is ResponseMode.REFUSE
        ):
            if self.must_refuse_reason is None:
                raise ValueError(
                    "refusal case requires "
                    "must_refuse_reason"
                )

        else:
            if self.must_refuse_reason is not None:
                raise ValueError(
                    "answerable case cannot carry "
                    "must_refuse_reason"
                )

            if not self.required_fact_ids:
                raise ValueError(
                    "answerable case requires at least "
                    "one required fact"
                )

            if not self.required_evidence_ids:
                raise ValueError(
                    "answerable case requires at least "
                    "one required evidence ID"
                )

            if not self.required_source_ids:
                raise ValueError(
                    "answerable case requires at least "
                    "one required source"
                )

            if not self.gold_fact_rubric:
                raise ValueError(
                    "answerable case requires a "
                    "gold fact rubric"
                )

        return self

    def to_orchestration_view(
        self,
    ) -> OrchestrationCaseView:
        """Project only fields allowed for evaluation orchestration."""

        return OrchestrationCaseView(
            case_id=self.case_id,
            case_version=self.case_version,
            data_role=self.data_role,
            source_family=self.source_family,
            scenario_class=self.scenario_class,
            criticality=self.criticality,
            query=self.query,
        )

    def to_runtime_input(
        self,
    ) -> RuntimeCaseInput:
        """Project the evaluator-owned case to the strict runtime boundary."""

        return RuntimeCaseInput(
            case_id=self.case_id,
            query=self.query,
        )
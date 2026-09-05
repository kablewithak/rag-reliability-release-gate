"""Chaos experiment contracts."""

from pydantic import Field

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.contracts.enums import BlastRadiusTarget, ChaosProfileId, LoadBand


class ChaosExperimentContract(ContractModel):
    """Typed execution contract for one bounded chaos experiment."""

    experiment_id: NonEmptyStr
    profile_id: ChaosProfileId
    profile_version: NonEmptyStr
    hypothesis: NonEmptyStr
    steady_state: tuple[NonEmptyStr, ...] = Field(min_length=1)
    evaluation_scope: NonEmptyStr
    case_manifest_id: NonEmptyStr
    corpus_snapshot_id: NonEmptyStr
    baseline_config_id: NonEmptyStr
    load_band: LoadBand
    faults: tuple[NonEmptyStr, ...] = ()
    context_pressure: NonEmptyStr
    synthetic_overlay_policy: NonEmptyStr
    blast_radius: tuple[BlastRadiusTarget, ...] = Field(min_length=1)
    duration_or_batch_rule: NonEmptyStr
    seed: int = Field(ge=0)
    abort_conditions: tuple[NonEmptyStr, ...] = Field(min_length=1)
    fault_clear_condition: NonEmptyStr
    recovery_conditions: tuple[NonEmptyStr, ...] = Field(min_length=1)
    expected_safe_behavior: NonEmptyStr
    required_metrics: tuple[NonEmptyStr, ...] = Field(min_length=1)
    required_trace_fields: tuple[NonEmptyStr, ...] = Field(min_length=1)

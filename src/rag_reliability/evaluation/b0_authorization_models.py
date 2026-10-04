"""Contracts for the exact Phase 5 G5M B0 specimen and execution authorization."""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.evaluation.b0_runtime_projection import B0Role

Arm = Literal["primary", "replication"]


class B0AuthorizationError(ValueError):
    """The frozen B0 specimen or authorization boundary is not satisfied."""


class B0FileBinding(ContractModel):
    path: NonEmptyStr
    sha256: Sha256


class B0PackageVersion(ContractModel):
    distribution: NonEmptyStr
    version: NonEmptyStr


class Phase5B0EnvironmentReferenceV1(ContractModel):
    """Secret-safe, identity-relevant local environment description."""

    environment_version: Literal[
        "phase5-b0-environment-reference-v1"
    ] = "phase5-b0-environment-reference-v1"

    os_system: NonEmptyStr
    os_release: NonEmptyStr
    os_version: NonEmptyStr
    machine_architecture: NonEmptyStr
    processor_identifier: str

    python_implementation: NonEmptyStr
    python_version: NonEmptyStr
    python_build: tuple[str, str]

    logical_cpu_count: int = Field(ge=1)
    total_physical_memory_bytes: int | None = Field(default=None, ge=1)

    perf_counter_implementation: NonEmptyStr
    perf_counter_resolution_seconds: float = Field(gt=0.0)
    perf_counter_monotonic: Literal[True] = True

    runtime_packages: tuple[B0PackageVersion, ...] = Field(
        min_length=2,
        max_length=2,
    )

    execution_process_model: Literal[
        "fresh_process_per_batch_single_worker_sequential_cases"
    ] = "fresh_process_per_batch_single_worker_sequential_cases"

    cache_warmup_policy: Literal[
        "runtime_initialized_once_per_batch_no_between_case_reset"
    ] = "runtime_initialized_once_per_batch_no_between_case_reset"

    live_provider_credentials_required: Literal[False] = False
    live_provider_calls_authorized: Literal[0] = 0
    secrets_captured: Literal[False] = False

    @model_validator(mode="after")
    def validate_packages(self) -> Self:
        names = tuple(item.distribution for item in self.runtime_packages)
        if names != ("pydantic", "PyYAML"):
            raise ValueError("runtime package inventory drifted")
        return self


class Phase5B0ExecutionSlotV1(ContractModel):
    slot_id: NonEmptyStr
    arm: Arm
    ordinal: int = Field(ge=1, le=42)
    case_id: NonEmptyStr
    role: B0Role
    query_sha256: Sha256
    fixture_key_sha256: Sha256


class Phase5B0SpecimenV1(ContractModel):
    """Complete exact specimen identity preceding execution authorization."""

    specimen_version: Literal[
        "phase5-b0-specimen-v1"
    ] = "phase5-b0-specimen-v1"

    authorization_source_commit_sha: NonEmptyStr
    authorization_source_branch: NonEmptyStr

    runtime_configuration_id: Sha256
    replay_fixture_sha256: Sha256
    fixture_coverage_sha256: Sha256

    provider_mode: Literal[
        "query_keyed_scripted_response"
    ] = "query_keyed_scripted_response"
    generation_is_context_sensitive: Literal[False] = False

    selected_retrieval_id: Literal[
        "phase5-operation-aware-rrf-stable-partition-v1"
    ] = "phase5-operation-aware-rrf-stable-partition-v1"
    retrieval_top_k: Literal[20] = 20
    source_policy_id: Literal[
        "github-rest-current-v1"
    ] = "github-rest-current-v1"
    context_builder_id: Literal[
        "bounded-context-v1"
    ] = "bounded-context-v1"
    context_max_characters: Literal[69663] = 69663
    context_max_evidence_items: Literal[15] = 15
    citation_validator_id: Literal[
        "exact-citation-v1"
    ] = "exact-citation-v1"
    fallback_policy_id: Literal[
        "safe-refusal-v1"
    ] = "safe-refusal-v1"

    fact_scoring_method_id: Literal[
        "evaluator_owned_fact_verdict_v1"
    ] = "evaluator_owned_fact_verdict_v1"

    runtime_source_bindings: tuple[B0FileBinding, ...]
    orchestration_source_bindings: tuple[B0FileBinding, ...]
    evaluator_source_bindings: tuple[B0FileBinding, ...]
    governance_artifact_bindings: tuple[B0FileBinding, ...]

    environment: Phase5B0EnvironmentReferenceV1
    environment_sha256: Sha256

    case_ids_in_execution_order: tuple[NonEmptyStr, ...] = Field(
        min_length=42,
        max_length=42,
    )

    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18
    replay_fixture_entry_count: Literal[42] = 42
    provider_reaching_case_count: Literal[42] = 42

    held_out_included: Literal[False] = False
    post_reject_confirmation_included: Literal[False] = False
    protected_outcomes_exposed: Literal[False] = False

    output_custody_policy: Literal[
        "raw_execution_internal_evidence_vault_public_metadata_safe_derivatives_only"
    ] = (
        "raw_execution_internal_evidence_vault_public_metadata_safe_derivatives_only"
    )

    baseline_execution_authorized: Literal[False] = False
    b0_executed: Literal[False] = False
    chaos_authorized: Literal[False] = False
    intervention_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_specimen(self) -> Self:
        if len(self.case_ids_in_execution_order) != len(
            set(self.case_ids_in_execution_order)
        ):
            raise ValueError("B0 specimen case IDs must be unique")

        if self.environment_sha256 != model_sha256(self.environment):
            raise ValueError("environment reference SHA does not reconcile")

        return self


class Phase5B0ExecutionAuthorizationV1(ContractModel):
    """One exact 42 + 42 authorization, not a blanket permission to rerun."""

    receipt_version: Literal[
        "phase5-b0-execution-authorization-v1"
    ] = "phase5-b0-execution-authorization-v1"

    specimen_sha256: Sha256
    supersedes_baseline_readiness_v1_sha256: Sha256
    replay_fixture_sha256: Sha256
    fixture_coverage_sha256: Sha256
    runtime_configuration_id: Sha256

    authorization_scope: Literal[
        "g5n_primary_then_g5o_replication_subject_to_valid_primary_custody"
    ] = "g5n_primary_then_g5o_replication_subject_to_valid_primary_custody"

    authorized_case_count: Literal[42] = 42
    primary_slot_count: Literal[42] = 42
    replication_slot_count: Literal[42] = 42
    maximum_total_case_starts: Literal[84] = 84

    slots: tuple[Phase5B0ExecutionSlotV1, ...] = Field(
        min_length=84,
        max_length=84,
    )

    primary_must_complete_before_replication: Literal[True] = True
    slot_consumed_on_start: Literal[True] = True
    replacement_start_authorized: Literal[False] = False
    selective_rerun_authorized: Literal[False] = False
    same_stage_failure_stop_count: Literal[2] = 2

    post_merge_preflight_requires_main: Literal[True] = True
    post_merge_preflight_requires_clean_worktree: Literal[True] = True
    post_merge_preflight_requires_component_hash_match: Literal[True] = True
    post_merge_preflight_requires_environment_match: Literal[True] = True
    post_merge_preflight_requires_fixture_match: Literal[True] = True

    live_provider_calls_authorized: Literal[0] = 0
    protected_case_execution_authorized: Literal[False] = False
    chaos_authorized: Literal[False] = False
    intervention_authorized: Literal[False] = False

    baseline_execution_authorized: Literal[True] = True
    b0_executed: Literal[False] = False
    held_out_outcomes_exposed: Literal[False] = False
    post_reject_confirmation_inspected: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_authorization(self) -> Self:
        slot_ids = tuple(slot.slot_id for slot in self.slots)
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("B0 authorization slot IDs must be unique")

        primary = tuple(slot for slot in self.slots if slot.arm == "primary")
        replication = tuple(slot for slot in self.slots if slot.arm == "replication")

        if len(primary) != self.primary_slot_count:
            raise ValueError("primary slot count does not reconcile")

        if len(replication) != self.replication_slot_count:
            raise ValueError("replication slot count does not reconcile")

        primary_cases = tuple(slot.case_id for slot in primary)
        replication_cases = tuple(slot.case_id for slot in replication)

        if primary_cases != replication_cases:
            raise ValueError("primary and replication case order must match")

        if len(set(primary_cases)) != self.authorized_case_count:
            raise ValueError("authorization must bind 42 unique cases")

        return self


def stable_model_bytes(value: ContractModel) -> bytes:
    return (
        json.dumps(
            value.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def model_sha256(value: ContractModel) -> str:
    return hashlib.sha256(stable_model_bytes(value)).hexdigest()

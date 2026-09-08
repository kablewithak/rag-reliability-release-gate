"""Frozen Phase 4 evaluation evidence-cluster constitution."""

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import (
    EvaluationRole,
    EvaluationSourceFamily,
    ScenarioClass,
)

PHASE3D_CHUNK_MANIFEST_SHA256: Literal[
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
] = (
    "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
)


class EvidenceClusterKind(StrEnum):
    OPENAPI_VERSION_PAIR = "openapi_version_pair"
    AUTHORED_GUIDANCE = "authored_guidance"


class Phase4EvidenceCluster(ContractModel):
    cluster_id: NonEmptyStr
    cluster_kind: EvidenceClusterKind
    source_family: EvaluationSourceFamily
    data_role: EvaluationRole

    operation_id: NonEmptyStr | None = None
    authored_source_id: NonEmptyStr | None = None

    current_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=1)

    historical_evidence_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    current_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = Field(min_length=1)

    historical_source_ids: tuple[
        NonEmptyStr,
        ...,
    ] = ()

    @model_validator(mode="after")
    def validate_cluster_shape(
        self,
    ) -> "Phase4EvidenceCluster":
        identity_fields = (
            self.current_evidence_ids,
            self.historical_evidence_ids,
            self.current_source_ids,
            self.historical_source_ids,
        )

        for values in identity_fields:
            if len(values) != len(set(values)):
                raise ValueError(
                    "cluster identities must be unique"
                )

        if self.cluster_kind is EvidenceClusterKind.OPENAPI_VERSION_PAIR:
            if self.operation_id is None:
                raise ValueError(
                    "OpenAPI cluster requires operation_id"
                )

            if self.authored_source_id is not None:
                raise ValueError(
                    "OpenAPI cluster cannot carry authored_source_id"
                )

            if not self.historical_evidence_ids:
                raise ValueError(
                    "OpenAPI cluster requires historical evidence"
                )

            if not self.historical_source_ids:
                raise ValueError(
                    "OpenAPI cluster requires historical sources"
                )

        if self.cluster_kind is EvidenceClusterKind.AUTHORED_GUIDANCE:
            if self.authored_source_id is None:
                raise ValueError(
                    "guidance cluster requires authored_source_id"
                )

            if self.operation_id is not None:
                raise ValueError(
                    "guidance cluster cannot carry operation_id"
                )

            if self.historical_evidence_ids:
                raise ValueError(
                    "guidance cluster cannot carry historical evidence"
                )

            if self.historical_source_ids:
                raise ValueError(
                    "guidance cluster cannot carry historical sources"
                )

            if (
                self.source_family
                is not EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE
            ):
                raise ValueError(
                    "guidance cluster must use cross-cutting source family"
                )

        return self

    @property
    def authoring_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return (
            *self.current_evidence_ids,
            *self.historical_evidence_ids,
        )


class Phase4ScenarioQuota(ContractModel):
    data_role: EvaluationRole
    scenario_class: ScenarioClass
    case_count: int = Field(ge=0)


class Phase4EvidenceClusterConstitution(
    ContractModel
):
    constitution_version: Literal[
        "phase4-evidence-cluster-constitution-v1"
    ] = "phase4-evidence-cluster-constitution-v1"

    phase3d_chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = PHASE3D_CHUNK_MANIFEST_SHA256

    cluster_count: Literal[30] = 30
    cases_per_cluster: Literal[2] = 2
    canonical_case_count: Literal[60] = 60

    development_cluster_count: Literal[12] = 12
    tuning_cluster_count: Literal[9] = 9
    held_out_cluster_count: Literal[9] = 9

    development_case_count: Literal[24] = 24
    tuning_case_count: Literal[18] = 18
    held_out_case_count: Literal[18] = 18

    openapi_component_gold_authoring_allowed: Literal[
        False
    ] = False

    background_load_source_gold_authoring_allowed: Literal[
        False
    ] = False

    held_out_assignment_frozen: Literal[
        True
    ] = True

    case_authoring_authorized: Literal[
        True
    ] = True

    baseline_authorized: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False

    scenario_quotas: tuple[
        Phase4ScenarioQuota,
        ...,
    ]

    clusters: tuple[
        Phase4EvidenceCluster,
        ...,
    ] = Field(
        min_length=30,
        max_length=30,
    )

    @model_validator(mode="after")
    def validate_constitution(
        self,
    ) -> "Phase4EvidenceClusterConstitution":
        cluster_ids = tuple(
            cluster.cluster_id
            for cluster in self.clusters
        )

        if len(cluster_ids) != len(set(cluster_ids)):
            raise ValueError(
                "cluster IDs must be unique"
            )

        role_counts = {
            role: sum(
                1
                for cluster in self.clusters
                if cluster.data_role is role
            )
            for role in EvaluationRole
        }

        expected_role_counts = {
            EvaluationRole.DEVELOPMENT: 12,
            EvaluationRole.TUNING: 9,
            EvaluationRole.HELD_OUT: 9,
        }

        if role_counts != expected_role_counts:
            raise ValueError(
                "cluster role counts do not match frozen split"
            )

        family_counts = {
            family: sum(
                1
                for cluster in self.clusters
                if cluster.source_family is family
            )
            for family in EvaluationSourceFamily
        }

        expected_family_counts = {
            EvaluationSourceFamily.ACTIONS: 5,
            EvaluationSourceFamily.ISSUES: 5,
            EvaluationSourceFamily.PULL_REQUESTS: 5,
            EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS: 5,
            EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE: 10,
        }

        if family_counts != expected_family_counts:
            raise ValueError(
                "cluster family counts do not match frozen composition"
            )

        role_family_counts = {
            (
                role,
                family,
            ): sum(
                1
                for cluster in self.clusters
                if (
                    cluster.data_role is role
                    and cluster.source_family is family
                )
            )
            for role in EvaluationRole
            for family in EvaluationSourceFamily
        }

        expected_role_family_counts = {
            (
                EvaluationRole.DEVELOPMENT,
                EvaluationSourceFamily.ACTIONS,
            ): 2,
            (
                EvaluationRole.DEVELOPMENT,
                EvaluationSourceFamily.ISSUES,
            ): 2,
            (
                EvaluationRole.DEVELOPMENT,
                EvaluationSourceFamily.PULL_REQUESTS,
            ): 2,
            (
                EvaluationRole.DEVELOPMENT,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
            ): 2,
            (
                EvaluationRole.DEVELOPMENT,
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE,
            ): 4,

            (
                EvaluationRole.TUNING,
                EvaluationSourceFamily.ACTIONS,
            ): 2,
            (
                EvaluationRole.TUNING,
                EvaluationSourceFamily.ISSUES,
            ): 1,
            (
                EvaluationRole.TUNING,
                EvaluationSourceFamily.PULL_REQUESTS,
            ): 2,
            (
                EvaluationRole.TUNING,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
            ): 1,
            (
                EvaluationRole.TUNING,
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE,
            ): 3,

            (
                EvaluationRole.HELD_OUT,
                EvaluationSourceFamily.ACTIONS,
            ): 1,
            (
                EvaluationRole.HELD_OUT,
                EvaluationSourceFamily.ISSUES,
            ): 2,
            (
                EvaluationRole.HELD_OUT,
                EvaluationSourceFamily.PULL_REQUESTS,
            ): 1,
            (
                EvaluationRole.HELD_OUT,
                EvaluationSourceFamily.REPOSITORIES_AND_REPOSITORY_WEBHOOKS,
            ): 2,
            (
                EvaluationRole.HELD_OUT,
                EvaluationSourceFamily.CROSS_CUTTING_REST_GUIDANCE,
            ): 3,
        }

        if (
            role_family_counts
            != expected_role_family_counts
        ):
            raise ValueError(
                "role/family split does not match frozen allocation"
            )

        openapi_count = sum(
            1
            for cluster in self.clusters
            if (
                cluster.cluster_kind
                is EvidenceClusterKind.OPENAPI_VERSION_PAIR
            )
        )

        guidance_count = sum(
            1
            for cluster in self.clusters
            if (
                cluster.cluster_kind
                is EvidenceClusterKind.AUTHORED_GUIDANCE
            )
        )

        if openapi_count != 20:
            raise ValueError(
                "expected exactly 20 OpenAPI clusters"
            )

        if guidance_count != 10:
            raise ValueError(
                "expected exactly 10 guidance clusters"
            )

        evidence_ids = tuple(
            evidence_id
            for cluster in self.clusters
            for evidence_id in cluster.authoring_evidence_ids
        )

        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError(
                "gold-authoring evidence crosses cluster boundaries"
            )

        quota_keys = tuple(
            (
                quota.data_role,
                quota.scenario_class,
            )
            for quota in self.scenario_quotas
        )

        if len(quota_keys) != len(set(quota_keys)):
            raise ValueError(
                "scenario quota keys must be unique"
            )

        expected_role_case_counts = {
            EvaluationRole.DEVELOPMENT: 24,
            EvaluationRole.TUNING: 18,
            EvaluationRole.HELD_OUT: 18,
        }

        for role, expected_count in expected_role_case_counts.items():
            observed = sum(
                quota.case_count
                for quota in self.scenario_quotas
                if quota.data_role is role
            )

            if observed != expected_count:
                raise ValueError(
                    f"scenario quotas for {role.value} "
                    "do not reconcile"
                )

        global_scenario_counts = {
            scenario: sum(
                quota.case_count
                for quota in self.scenario_quotas
                if quota.scenario_class is scenario
            )
            for scenario in ScenarioClass
        }

        expected_global_scenario_counts = {
            ScenarioClass.CURRENT_SINGLE_SOURCE_ANSWERABLE: 18,
            ScenarioClass.CURRENT_MULTI_EVIDENCE_ANSWERABLE: 12,
            ScenarioClass.VERSION_FRESHNESS_DISAMBIGUATION: 12,
            ScenarioClass.AUTHORITY_SCOPE_DISAMBIGUATION: 8,
            ScenarioClass.MUST_REFUSE_INSUFFICIENT_OR_CONFLICTING_EVIDENCE: 10,
        }

        if (
            global_scenario_counts
            != expected_global_scenario_counts
        ):
            raise ValueError(
                "global scenario composition does not match freeze"
            )

        return self


class Phase4EvidenceClusterReceipt(
    ContractModel
):
    receipt_version: Literal[
        "phase4-evidence-cluster-receipt-v1"
    ] = "phase4-evidence-cluster-receipt-v1"

    phase3d_chunk_manifest_sha256: Literal[
        "1b9f8dfa1c62b8e29592e7e2c85d4996e11ef57140e0ba96cd9d8ef930a263fd"
    ] = PHASE3D_CHUNK_MANIFEST_SHA256

    constitution_sha256: Sha256

    cluster_count: Literal[30] = 30
    canonical_case_count: Literal[60] = 60

    development_cluster_count: Literal[12] = 12
    tuning_cluster_count: Literal[9] = 9
    held_out_cluster_count: Literal[9] = 9

    authoring_evidence_id_count: int = Field(
        ge=1
    )

    cluster_constitution_frozen: Literal[
        True
    ] = True

    case_authoring_authorized: Literal[
        True
    ] = True

    baseline_authorized: Literal[
        False
    ] = False

    release_eligible: Literal[
        False
    ] = False
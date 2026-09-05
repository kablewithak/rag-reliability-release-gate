"""Release identity contracts."""

from pydantic import field_validator

from rag_reliability.contracts.base import (
    ContractModel,
    GitCommitSha,
    NonEmptyStr,
    NotApplicableIdentity,
    Sha256,
)
from rag_reliability.contracts.enums import ReleaseVerdict

OptionalHashIdentity = Sha256 | NotApplicableIdentity
OptionalStringIdentity = NonEmptyStr | NotApplicableIdentity


class ReleaseIdentity(ContractModel):
    """Exact identity to which a release verdict applies."""

    release_id: NonEmptyStr
    run_id: NonEmptyStr
    git_commit_sha: GitCommitSha
    corpus_manifest_hash: Sha256
    chunk_configuration_hash: Sha256
    runtime_configuration_hash: Sha256
    retrieval_configuration_hash: Sha256
    reranker_configuration_hash: OptionalHashIdentity
    provider_or_model_identifier: NonEmptyStr
    provider_mode: NonEmptyStr
    evaluation_suite_version: NonEmptyStr
    case_role_manifest_hash: Sha256
    chaos_profile_manifest_hash: Sha256
    scorer_registry_hash: Sha256
    threshold_set_hash: Sha256
    baseline_or_intervention_id: NonEmptyStr
    execution_environment_id: NonEmptyStr
    load_profile_id: OptionalStringIdentity
    fault_profile_id: OptionalStringIdentity
    result_package_hash: Sha256
    sanitization_policy_version: NonEmptyStr
    verdict: ReleaseVerdict

    @field_validator("load_profile_id", "fault_profile_id")
    @classmethod
    def reject_bare_not_applicable(
        cls,
        value: OptionalStringIdentity,
    ) -> OptionalStringIdentity:
        if isinstance(value, str) and value == "not_applicable":
            raise ValueError(
                "not_applicable must be represented with a structured reason"
            )
        return value

"""Release identity contracts."""

from rag_reliability.contracts.base import (
    ContractModel,
    GitCommitSha,
    NonEmptyStr,
    Sha256,
)
from rag_reliability.contracts.enums import ReleaseVerdict


class ReleaseIdentity(ContractModel):
    """Exact identity to which a PASS / CONDITIONAL_PASS / FAIL verdict applies."""

    release_id: NonEmptyStr
    run_id: NonEmptyStr
    git_commit_sha: GitCommitSha
    corpus_manifest_hash: Sha256
    chunk_configuration_hash: Sha256
    retrieval_configuration_hash: Sha256
    reranker_configuration_hash: Sha256
    provider_or_model_identifier: NonEmptyStr
    provider_mode: NonEmptyStr
    evaluation_suite_version: NonEmptyStr
    case_role_manifest_hash: Sha256
    chaos_profile_manifest_hash: Sha256
    scorer_registry_hash: Sha256
    threshold_set_hash: Sha256
    baseline_or_intervention_id: NonEmptyStr
    execution_environment_id: NonEmptyStr
    load_profile_id: NonEmptyStr
    fault_profile_id: NonEmptyStr
    result_package_hash: Sha256
    sanitization_policy_version: NonEmptyStr
    verdict: ReleaseVerdict

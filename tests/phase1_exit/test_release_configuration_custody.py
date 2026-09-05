import pytest
from pydantic import ValidationError

from rag_reliability.config.custody import ReleaseConfigurationCustody
from rag_reliability.config.identity import RuntimeConfiguration
from rag_reliability.contracts.base import NotApplicableIdentity
from rag_reliability.contracts.enums import ReleaseVerdict
from rag_reliability.contracts.release import ReleaseIdentity

SHA = "d" * 64
GIT_SHA = "e" * 40


def runtime_configuration() -> RuntimeConfiguration:
    return RuntimeConfiguration.model_validate(
        {
            "schema_version": "1.0",
            "retrieval": {
                "retriever_id": "retriever-contract-v1",
                "top_k": 8,
            },
            "source_policy": {
                "policy_id": "authority-current-v1",
            },
            "reranker": None,
            "context": {
                "builder_id": "bounded-context-v1",
                "budget_unit_id": "characters",
                "max_budget": 12000,
                "max_evidence_items": 6,
            },
            "provider": {
                "adapter_id": "fake-replay-v1",
                "model_id": "replay-model-v1",
                "timeout_ms": 3000,
                "max_retries": 1,
            },
            "citation": {
                "validator_id": "citation-validator-v1",
                "require_citations": True,
            },
            "fallback": {
                "policy_id": "safe-refusal-v1",
                "allow_qualified_answer": True,
            },
        }
    )


def release_identity(config: RuntimeConfiguration) -> ReleaseIdentity:
    binding = config.release_binding()
    return ReleaseIdentity(
        release_id="release-1",
        run_id="run-1",
        git_commit_sha=GIT_SHA,
        corpus_manifest_hash=SHA,
        chunk_configuration_hash=SHA,
        runtime_configuration_hash=binding.runtime_configuration_hash,
        retrieval_configuration_hash=binding.retrieval_configuration_hash,
        reranker_configuration_hash=binding.reranker_configuration_hash,
        provider_or_model_identifier=config.provider.model_id,
        provider_mode=config.provider.adapter_id,
        evaluation_suite_version="1.0",
        case_role_manifest_hash=SHA,
        chaos_profile_manifest_hash=SHA,
        scorer_registry_hash=SHA,
        threshold_set_hash=SHA,
        baseline_or_intervention_id="baseline-v1",
        execution_environment_id="local-env-v1",
        load_profile_id=NotApplicableIdentity(
            reason="load profile is outside this fixture"
        ),
        fault_profile_id="CR-CLEAN",
        result_package_hash=SHA,
        sanitization_policy_version="1.0",
        verdict=ReleaseVerdict.PASS,
    )


def test_disabled_reranker_binding_records_reason() -> None:
    binding = runtime_configuration().release_binding()

    assert isinstance(binding.reranker_configuration_hash, NotApplicableIdentity)
    assert binding.reranker_configuration_hash.status == "not_applicable"


def test_release_custody_accepts_matching_runtime_binding() -> None:
    config = runtime_configuration()
    custody = ReleaseConfigurationCustody(
        release_identity=release_identity(config),
        runtime_binding=config.release_binding(),
    )

    assert custody.release_identity.runtime_configuration_hash == config.configuration_id


def test_release_custody_rejects_runtime_hash_mismatch() -> None:
    config = runtime_configuration()
    release = release_identity(config).model_copy(
        update={"runtime_configuration_hash": "a" * 64}
    )

    with pytest.raises(ValidationError):
        ReleaseConfigurationCustody(
            release_identity=release,
            runtime_binding=config.release_binding(),
        )


def test_release_identity_requires_runtime_configuration_hash() -> None:
    config = runtime_configuration()
    payload = release_identity(config).model_dump()
    payload.pop("runtime_configuration_hash")

    with pytest.raises(ValidationError):
        ReleaseIdentity.model_validate(payload)

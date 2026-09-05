import pytest
from pydantic import ValidationError

from rag_reliability.contracts.base import NotApplicableIdentity
from rag_reliability.contracts.chaos import ChaosExperimentContract
from rag_reliability.contracts.enums import (
    BlastRadiusTarget,
    ChaosProfileId,
    LoadBand,
    ReleaseVerdict,
)
from rag_reliability.contracts.release import ReleaseIdentity

SHA = "b" * 64
GIT_SHA = "c" * 40


def build_release_payload() -> dict[str, object]:
    return {
        "release_id": "release-1",
        "run_id": "run-1",
        "git_commit_sha": GIT_SHA,
        "corpus_manifest_hash": SHA,
        "chunk_configuration_hash": SHA,
        "runtime_configuration_hash": SHA,
        "retrieval_configuration_hash": SHA,
        "reranker_configuration_hash": NotApplicableIdentity(
            reason="reranker disabled for this run"
        ),
        "provider_or_model_identifier": "fake-replay-v1",
        "provider_mode": "fake_replay",
        "evaluation_suite_version": "1.0",
        "case_role_manifest_hash": SHA,
        "chaos_profile_manifest_hash": SHA,
        "scorer_registry_hash": SHA,
        "threshold_set_hash": SHA,
        "baseline_or_intervention_id": "final-v1",
        "execution_environment_id": "local-env-v1",
        "load_profile_id": NotApplicableIdentity(
            reason="load phase not applicable to this release fixture"
        ),
        "fault_profile_id": "CR-CLEAN",
        "result_package_hash": SHA,
        "sanitization_policy_version": "1.0",
        "verdict": ReleaseVerdict.PASS,
    }


def test_chaos_contract_accepts_named_profile() -> None:
    contract = ChaosExperimentContract(
        experiment_id="exp-001",
        profile_id=ChaosProfileId.SEMANTIC_DISTRACTOR,
        profile_version="1.0",
        hypothesis="Authoritative evidence remains preferred.",
        steady_state=("trace completeness is 1.0",),
        evaluation_scope="development",
        case_manifest_id="dev-manifest-v1",
        corpus_snapshot_id="github_rest_v1_2026_09_05",
        baseline_config_id="baseline-v1",
        load_band=LoadBand.CLEAN,
        faults=("synthetic_semantic_distractors",),
        context_pressure="baseline",
        synthetic_overlay_policy="five non-authoritative distractors",
        blast_radius=(BlastRadiusTarget.SYNTHETIC_OVERLAY,),
        duration_or_batch_rule="complete development batch",
        seed=7,
        abort_conditions=("evaluation integrity violation",),
        fault_clear_condition="overlay removed",
        recovery_conditions=("complete clean replay",),
        expected_safe_behavior="answer from authoritative evidence or safely refuse",
        required_metrics=("claim_support_rate",),
        required_trace_fields=("retrieval", "context_assembly"),
    )

    assert contract.profile_id is ChaosProfileId.SEMANTIC_DISTRACTOR


def test_chaos_contract_rejects_unknown_profile() -> None:
    payload = {
        "experiment_id": "exp-001",
        "profile_id": "CR-RANDOM-FAULT",
        "profile_version": "1.0",
        "hypothesis": "No random profiles.",
        "steady_state": ["trace completeness is 1.0"],
        "evaluation_scope": "development",
        "case_manifest_id": "dev-manifest-v1",
        "corpus_snapshot_id": "snapshot-v1",
        "baseline_config_id": "baseline-v1",
        "load_band": "clean",
        "faults": [],
        "context_pressure": "baseline",
        "synthetic_overlay_policy": "none",
        "blast_radius": ["local_rag_process"],
        "duration_or_batch_rule": "one batch",
        "seed": 0,
        "abort_conditions": ["operator stop"],
        "fault_clear_condition": "none",
        "recovery_conditions": ["clean replay"],
        "expected_safe_behavior": "remain safe",
        "required_metrics": ["trace completeness"],
        "required_trace_fields": ["retrieval"],
    }

    with pytest.raises(ValidationError):
        ChaosExperimentContract.model_validate(payload)


def test_release_identity_rejects_invalid_hash() -> None:
    payload = build_release_payload()
    payload["corpus_manifest_hash"] = "not-a-hash"

    with pytest.raises(ValidationError):
        ReleaseIdentity.model_validate(payload)


def test_release_identity_rejects_bare_not_applicable() -> None:
    payload = build_release_payload()
    payload["load_profile_id"] = "not_applicable"

    with pytest.raises(ValidationError):
        ReleaseIdentity.model_validate(payload)


def test_release_identity_accepts_complete_hash_bound_identity() -> None:
    release = ReleaseIdentity.model_validate(build_release_payload())

    assert release.verdict is ReleaseVerdict.PASS
    assert isinstance(release.load_profile_id, NotApplicableIdentity)

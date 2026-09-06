from pathlib import Path

from rag_reliability.contracts.enums import DataRole, EvaluationRole, ResponseMode
from rag_reliability.evaluation.thin_slice import load_thin_slice_bundle

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_DOCS_COMMIT = "ec3629a841129ae28189d7bb2274a7b3d40c5095"


def test_phase2b_fixture_counts_and_roles_are_bounded() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)

    assert len(bundle.sources.sources) == 10
    assert len(bundle.cases.cases) == 10
    assert len(bundle.replay.entries) == 8
    assert all(
        source.manifest.data_role is DataRole.UNIT_FIXTURE
        for source in bundle.sources.sources
    )
    assert all(
        case.data_role is EvaluationRole.DEVELOPMENT
        for case in bundle.cases.cases
    )


def test_phase2b_sources_are_bound_to_frozen_public_docs_snapshot() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)

    for source in bundle.sources.sources:
        assert source.manifest.source_commit_sha_or_version == FROZEN_DOCS_COMMIT
        assert source.manifest.source_license == "CC-BY-4.0"
        assert source.manifest.product_scope == "api.github.com"
        assert source.manifest.api_version_or_snapshot == "2026-03-10"
        assert str(source.manifest.source_url).startswith(
            f"https://github.com/github/docs/blob/{FROZEN_DOCS_COMMIT}/"
        )
        assert "{%" not in source.content
        assert "{{" not in source.content


def test_replay_entries_cover_only_answerable_cases() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    answer_queries = {
        case.query
        for case in bundle.cases.cases
        if case.expected_response_mode is ResponseMode.ANSWER
    }
    refusal_queries = {
        case.query
        for case in bundle.cases.cases
        if case.expected_response_mode is ResponseMode.REFUSE
    }
    replay_queries = {entry.query for entry in bundle.replay.entries}

    assert replay_queries == answer_queries
    assert replay_queries.isdisjoint(refusal_queries)

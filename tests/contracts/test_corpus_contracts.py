from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from rag_reliability.contracts.corpus import RealSourceRecord, SyntheticChaosOverlay
from rag_reliability.contracts.enums import (
    AuthorityLevel,
    ChaosProfileId,
    ChaosPurpose,
    CorpusSourceFamily,
    DataRole,
    SourceState,
)

SHA = "a" * 64


def test_current_real_source_requires_authoritative_state() -> None:
    record = RealSourceRecord(
        source_id="source-1",
        source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
        source_url="https://github.com/github/rest-api-description",
        source_license="MIT",
        retrieved_at=datetime.now(UTC),
        source_commit_sha_or_version="3cef12e8",
        document_version="2026-03-10",
        authority_level=AuthorityLevel.AUTHORITATIVE,
        source_state=SourceState.CURRENT,
        product_scope="api.github.com",
        api_version_or_snapshot="2026-03-10",
        content_sha256=SHA,
        title="Issues operation",
        topic_tags=("issues",),
        data_role=DataRole.CORPUS_SOURCE,
    )

    assert record.authority_level is AuthorityLevel.AUTHORITATIVE


def test_current_source_rejects_historical_authority() -> None:
    with pytest.raises(ValidationError):
        RealSourceRecord(
            source_id="source-1",
            source_family=CorpusSourceFamily.OPENAPI_ENDPOINT_CONTRACT,
            source_url="https://github.com/github/rest-api-description",
            source_license="MIT",
            retrieved_at=datetime.now(UTC),
            source_commit_sha_or_version="3cef12e8",
            document_version="2026-03-10",
            authority_level=AuthorityLevel.HISTORICAL,
            source_state=SourceState.CURRENT,
            product_scope="api.github.com",
            api_version_or_snapshot="2026-03-10",
            content_sha256=SHA,
            title="Issues operation",
            topic_tags=("issues",),
            data_role=DataRole.CORPUS_SOURCE,
        )


def test_synthetic_overlay_cannot_become_authoritative() -> None:
    with pytest.raises(ValidationError):
        SyntheticChaosOverlay(
            overlay_id="overlay-1",
            authority_level=AuthorityLevel.AUTHORITATIVE,
            chaos_purpose=ChaosPurpose.SEMANTIC_DISTRACTOR,
            seed=7,
            scenario_id="scenario-1",
            profile_id=ChaosProfileId.SEMANTIC_DISTRACTOR,
        )


def test_synthetic_overlay_defaults_to_non_authoritative() -> None:
    overlay = SyntheticChaosOverlay(
        overlay_id="overlay-1",
        derived_from_source_ids=("source-1",),
        chaos_purpose=ChaosPurpose.SEMANTIC_DISTRACTOR,
        seed=7,
        scenario_id="scenario-1",
        profile_id=ChaosProfileId.SEMANTIC_DISTRACTOR,
    )

    assert overlay.authority_level is AuthorityLevel.NONE
    assert overlay.eligible_as_final_citation is False
    assert overlay.eligible_as_gold_evidence is False
    assert overlay.data_role is DataRole.CHAOS_OVERLAY

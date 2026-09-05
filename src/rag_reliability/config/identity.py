"""Canonical, hash-bound identity for runtime configuration."""

import json
from hashlib import sha256

from pydantic import Field

from rag_reliability.contracts.base import (
    ContractModel,
    NonEmptyStr,
    NotApplicableIdentity,
    Sha256,
)


class CanonicalConfigModel(ContractModel):
    """Configuration model with deterministic serialization and identity."""

    def canonical_json(self) -> str:
        payload = self.model_dump(mode="json")
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @property
    def configuration_id(self) -> Sha256:
        digest = sha256(self.canonical_json().encode("utf-8")).hexdigest()
        return digest


class RetrievalConfig(CanonicalConfigModel):
    retriever_id: NonEmptyStr
    top_k: int = Field(ge=1)


class SourcePolicyConfig(CanonicalConfigModel):
    policy_id: NonEmptyStr


class RerankerConfig(CanonicalConfigModel):
    reranker_id: NonEmptyStr


class ContextConfig(CanonicalConfigModel):
    builder_id: NonEmptyStr
    budget_unit_id: NonEmptyStr
    max_budget: int = Field(ge=1)
    max_evidence_items: int = Field(ge=1)


class ProviderConfig(CanonicalConfigModel):
    adapter_id: NonEmptyStr
    model_id: NonEmptyStr
    timeout_ms: int = Field(ge=1)
    max_retries: int = Field(ge=0)


class CitationConfig(CanonicalConfigModel):
    validator_id: NonEmptyStr
    require_citations: bool = True


class FallbackConfig(CanonicalConfigModel):
    policy_id: NonEmptyStr
    allow_qualified_answer: bool


class RuntimeConfigurationBinding(ContractModel):
    """Release-facing hashes derived from one runtime configuration."""

    runtime_configuration_hash: Sha256
    retrieval_configuration_hash: Sha256
    reranker_configuration_hash: Sha256 | NotApplicableIdentity


class RuntimeConfiguration(CanonicalConfigModel):
    schema_version: NonEmptyStr
    retrieval: RetrievalConfig
    source_policy: SourcePolicyConfig
    reranker: RerankerConfig | None = None
    context: ContextConfig
    provider: ProviderConfig
    citation: CitationConfig
    fallback: FallbackConfig

    def release_binding(self) -> RuntimeConfigurationBinding:
        if self.reranker is None:
            reranker_identity: Sha256 | NotApplicableIdentity = (
                NotApplicableIdentity(reason="reranker disabled in runtime configuration")
            )
        else:
            reranker_identity = self.reranker.configuration_id

        return RuntimeConfigurationBinding(
            runtime_configuration_hash=self.configuration_id,
            retrieval_configuration_hash=self.retrieval.configuration_id,
            reranker_configuration_hash=reranker_identity,
        )

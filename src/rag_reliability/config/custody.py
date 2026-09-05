"""Validation that release evidence is bound to the executed runtime config."""

from pydantic import model_validator

from rag_reliability.config.identity import RuntimeConfigurationBinding
from rag_reliability.contracts.base import ContractModel
from rag_reliability.contracts.release import ReleaseIdentity


class ReleaseConfigurationCustody(ContractModel):
    """Pair a release identity with the runtime configuration hashes it claims."""

    release_identity: ReleaseIdentity
    runtime_binding: RuntimeConfigurationBinding

    @model_validator(mode="after")
    def validate_configuration_identity(self) -> "ReleaseConfigurationCustody":
        release = self.release_identity
        binding = self.runtime_binding

        if release.runtime_configuration_hash != binding.runtime_configuration_hash:
            raise ValueError("runtime configuration identity mismatch")
        if release.retrieval_configuration_hash != binding.retrieval_configuration_hash:
            raise ValueError("retrieval configuration identity mismatch")
        if release.reranker_configuration_hash != binding.reranker_configuration_hash:
            raise ValueError("reranker configuration identity mismatch")
        return self

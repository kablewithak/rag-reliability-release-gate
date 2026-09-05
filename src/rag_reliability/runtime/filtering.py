"""Current-authoritative GitHub REST source policy for the V1 target."""

from rag_reliability.config.identity import SourcePolicyConfig
from rag_reliability.contracts.enums import AuthorityLevel, SourceState
from rag_reliability.contracts.runtime import (
    RejectedEvidence,
    SourceFilterRequest,
    SourceFilterResult,
)

POLICY_ID = "github-rest-current-v1"
REQUIRED_PRODUCT_SCOPE = "api.github.com"
REQUIRED_API_VERSION = "2026-03-10"


class CurrentGithubRestSourcePolicyFilter:
    """Fail closed to the frozen V1 target contract."""

    def __init__(self, config: SourcePolicyConfig) -> None:
        if config.policy_id != POLICY_ID:
            raise ValueError(
                f"unsupported source policy id: {config.policy_id}"
            )
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def apply(self, request: SourceFilterRequest) -> SourceFilterResult:
        eligible = []
        rejected = []

        for candidate in request.candidates:
            reason = self._rejection_reason(candidate)
            if reason is None:
                eligible.append(candidate)
            else:
                rejected.append(
                    RejectedEvidence(
                        source_id=candidate.source_id,
                        reason_code=reason,
                    )
                )

        return SourceFilterResult(
            eligible=tuple(eligible),
            rejected=tuple(rejected),
        )

    @staticmethod
    def _rejection_reason(candidate: object) -> str | None:
        from rag_reliability.contracts.runtime import RetrievedEvidence

        if not isinstance(candidate, RetrievedEvidence):
            raise TypeError("candidate must be RetrievedEvidence")
        if candidate.synthetic_overlay:
            return "synthetic_overlay"
        if candidate.authority_level is not AuthorityLevel.AUTHORITATIVE:
            return "authority_level_mismatch"
        if candidate.source_state is not SourceState.CURRENT:
            return "source_state_mismatch"
        if candidate.product_scope != REQUIRED_PRODUCT_SCOPE:
            return "product_scope_mismatch"
        if candidate.api_version_or_snapshot != REQUIRED_API_VERSION:
            return "api_version_mismatch"
        if not candidate.eligible_as_final_citation:
            return "citation_ineligible"
        return None

"""Bounded deterministic context assembly."""

from rag_reliability.config.identity import ContextConfig
from rag_reliability.contracts.runtime import (
    ContextBuildRequest,
    ContextBundle,
    ContextItem,
)
from rag_reliability.runtime.errors import ContextBudgetExhaustedError


class BoundedContextBuilder:
    """Assemble whole evidence records without partial truncation."""

    def __init__(self, config: ContextConfig) -> None:
        if config.budget_unit_id != "characters":
            raise ValueError("Phase 2A context builder requires character budgeting")
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def build(self, request: ContextBuildRequest) -> ContextBundle:
        selected: list[ContextItem] = []
        blocks: list[str] = []

        for evidence in request.evidence[: self._config.max_evidence_items]:
            block = f"SOURCE: {evidence.source_id}\n{evidence.content}"
            candidate_blocks = [*blocks, block]
            assembled = "\n\n".join(candidate_blocks)

            if len(assembled) > self._config.max_budget:
                continue

            blocks.append(block)
            selected.append(
                ContextItem(
                    source_id=evidence.source_id,
                    content=evidence.content,
                    position=len(selected) + 1,
                    authority_level=evidence.authority_level,
                    source_state=evidence.source_state,
                    eligible_as_final_citation=evidence.eligible_as_final_citation,
                )
            )

        if not selected:
            raise ContextBudgetExhaustedError(
                "no eligible evidence fits the configured context budget"
            )

        return ContextBundle(
            query=request.query,
            items=tuple(selected),
            assembled_context="\n\n".join(blocks),
        )

"""Deterministic exact-support citation validator."""

import re

from rag_reliability.config.identity import CitationConfig
from rag_reliability.contracts.enums import CitationValidationStatus
from rag_reliability.contracts.runtime import (
    CitationCheck,
    CitationValidationRequest,
    CitationValidationResult,
)

_WHITESPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip().casefold()


class ExactCitationValidator:
    """Validate exact answer support against cited context evidence."""

    def __init__(self, config: CitationConfig) -> None:
        self._config = config

    @property
    def configuration_id(self) -> str:
        return self._config.configuration_id

    async def validate(
        self,
        request: CitationValidationRequest,
    ) -> CitationValidationResult:
        context_by_id = {
            item.source_id: item
            for item in request.context.items
        }
        answer = _normalize(request.provider_response.answer_text)
        checks: list[CitationCheck] = []

        for source_id in request.provider_response.cited_source_ids:
            context_item = context_by_id.get(source_id)
            if context_item is None:
                status = CitationValidationStatus.MISSING
            elif not context_item.eligible_as_final_citation:
                status = CitationValidationStatus.UNSUPPORTED
            elif answer and answer in _normalize(context_item.content):
                status = CitationValidationStatus.SUPPORTED
            else:
                status = CitationValidationStatus.UNSUPPORTED

            checks.append(CitationCheck(source_id=source_id, status=status))

        all_supported = bool(checks) and all(
            check.status is CitationValidationStatus.SUPPORTED
            for check in checks
        )

        if self._config.require_citations and not checks:
            all_supported = False

        return CitationValidationResult(
            checks=tuple(checks),
            all_material_claims_supported=all_supported,
        )

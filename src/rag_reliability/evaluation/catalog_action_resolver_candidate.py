"""Evaluation-only catalog-derived action resolver candidate for Phase 5."""

from __future__ import annotations

import re

from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    OperationResolution,
    ResolutionStatus,
    RuntimeOperationDescriptor,
    _normalize_token,
    _tokens,
)

_RAW_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _catalog_action_token(operation_id: str) -> str:
    """Derive the canonical action from the operation ID, never from eval gold."""
    _namespace, remainder = operation_id.split("/", 1)
    action = remainder.split("-", 1)[0]
    return _normalize_token(action)


def _catalog_action_forms(action: str) -> frozenset[str]:
    """Generate bounded deterministic surface forms from one catalog action."""
    forms = {action, f"{action}s", f"{action}ed", f"{action}ing"}

    if action.endswith("e") and len(action) > 1:
        forms.add(f"{action}d")
        forms.add(f"{action[:-1]}ing")

    if action.endswith("y") and len(action) > 1:
        forms.add(f"{action[:-1]}ies")
        forms.add(f"{action[:-1]}ied")

    return frozenset(forms)


def _catalog_action_matches(*, action: str, query: str) -> bool:
    raw_tokens = frozenset(_RAW_TOKEN_PATTERN.findall(query.casefold()))
    return bool(_catalog_action_forms(action) & raw_tokens)


def _resolution_from_matches(matches: tuple[str, ...]) -> OperationResolution:
    unique = tuple(sorted(set(matches)))

    if len(unique) == 1:
        return OperationResolution(
            status=ResolutionStatus.RESOLVED,
            operation_ids=unique,
        )

    if len(unique) > 1:
        return OperationResolution(
            status=ResolutionStatus.AMBIGUOUS,
            operation_ids=unique,
        )

    return OperationResolution(status=ResolutionStatus.UNRESOLVED)


class CatalogDerivedActionOperationResolver:
    """Extend only baseline-unresolved cases using catalog-derived actions."""

    def __init__(
        self,
        operations: tuple[RuntimeOperationDescriptor, ...],
    ) -> None:
        if not operations:
            raise ValueError("catalog-derived resolver requires a non-empty catalog")

        operation_ids = tuple(operation.operation_id for operation in operations)
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("catalog-derived resolver catalog IDs must be unique")

        self._operations = tuple(sorted(operations, key=lambda operation: operation.operation_id))
        self._baseline = DeterministicOperationResolver(self._operations)

    @property
    def operation_count(self) -> int:
        return len(self._operations)

    def resolve(self, query: str) -> OperationResolution:
        baseline = self._baseline.resolve(query)
        if baseline.status is not ResolutionStatus.UNRESOLVED:
            return baseline
        if not query.strip():
            return baseline

        query_tokens = _tokens(query)
        matches: list[str] = []

        for operation in self._operations:
            namespace = _normalize_token(operation.operation_id.split("/", 1)[0])
            action = _catalog_action_token(operation.operation_id)

            if namespace not in query_tokens:
                continue
            if not _catalog_action_matches(action=action, query=query):
                continue

            matches.append(operation.operation_id)

        if not matches:
            return baseline

        return _resolution_from_matches(tuple(matches))

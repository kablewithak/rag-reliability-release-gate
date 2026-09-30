"""Evaluation-only Phase 5 A2 object/subresource resolver candidate."""

from __future__ import annotations

from rag_reliability.evaluation.catalog_action_resolver_candidate import (
    _catalog_action_matches,
    _catalog_action_token,
)
from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    OperationResolution,
    ResolutionStatus,
    RuntimeOperationDescriptor,
    _normalize_token,
    _tokens,
)


def _namespace_token(operation_id: str) -> str:
    namespace, _remainder = operation_id.split("/", 1)
    return _normalize_token(namespace)


def _operation_object_subresource_tokens(
    operation: RuntimeOperationDescriptor,
) -> frozenset[str]:
    """Derive object/subresource evidence only from runtime catalog structure."""
    _namespace, remainder = operation.operation_id.split("/", 1)
    operation_parts = remainder.split("-")
    after_action = " ".join(operation_parts[1:])

    operation_tokens = set(_tokens(after_action))
    path_tokens: set[str] = set()

    for segment in operation.path.strip("/").split("/"):
        if not segment or (segment.startswith("{") and segment.endswith("}")):
            continue
        path_tokens.update(_tokens(segment))

    return frozenset(operation_tokens | path_tokens)


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


class A2ObjectSubresourceOperationResolver:
    """Apply the frozen A2 evidence contract to unresolved/ambiguous cases."""

    def __init__(
        self,
        operations: tuple[RuntimeOperationDescriptor, ...],
    ) -> None:
        if not operations:
            raise ValueError("A2 resolver requires a non-empty catalog")

        operation_ids = tuple(operation.operation_id for operation in operations)
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("A2 resolver catalog IDs must be unique")

        self._operations = tuple(
            sorted(
                operations,
                key=lambda operation: operation.operation_id,
            )
        )
        self._operations_by_id = {
            operation.operation_id: operation
            for operation in self._operations
        }
        self._baseline = DeterministicOperationResolver(self._operations)

    @property
    def operation_count(self) -> int:
        return len(self._operations)

    def resolve(self, query: str) -> OperationResolution:
        baseline = self._baseline.resolve(query)

        if baseline.status is ResolutionStatus.RESOLVED:
            return baseline

        if not query.strip():
            return baseline

        if baseline.status is ResolutionStatus.AMBIGUOUS:
            candidate_operations = tuple(
                self._operations_by_id[operation_id]
                for operation_id in baseline.operation_ids
            )
        else:
            candidate_operations = self._operations

        query_tokens = _tokens(query)
        matches: list[str] = []

        for operation in candidate_operations:
            namespace = _namespace_token(operation.operation_id)
            action = _catalog_action_token(operation.operation_id)
            object_tokens = _operation_object_subresource_tokens(operation)

            if namespace not in query_tokens:
                continue

            if not _catalog_action_matches(
                action=action,
                query=query,
            ):
                continue

            if not (object_tokens & query_tokens):
                continue

            matches.append(operation.operation_id)

        return _resolution_from_matches(tuple(matches))

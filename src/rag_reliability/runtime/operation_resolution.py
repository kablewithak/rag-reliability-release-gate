"""Deterministic query-to-operation resolution for the Phase 5 runtime seam."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.corpus.models import HttpMethod, SemanticOperationFamily

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

_ALIASES = {
    "creating": "create",
    "deleting": "delete",
    "getting": "get",
    "listing": "list",
    "organizations": "org",
    "organization": "org",
    "orgs": "org",
    "repositories": "repo",
    "repository": "repo",
    "repos": "repo",
    "issues": "issue",
    "webhooks": "webhook",
    "users": "user",
    "pulls": "pull",
    "requests": "request",
    "updating": "update",
    "workflows": "workflow",
    "runs": "run",
}

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "by",
        "for",
        "from",
        "in",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
    }
)

_ACTION_TOKENS = frozenset(
    {
        "add",
        "approve",
        "cancel",
        "create",
        "delete",
        "disable",
        "download",
        "enable",
        "generate",
        "get",
        "list",
        "lock",
        "merge",
        "ping",
        "redeliver",
        "remove",
        "rerun",
        "set",
        "test",
        "unlock",
        "update",
    }
)


class ResolutionStatus(StrEnum):
    """Runtime-safe resolver outcome."""

    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class RuntimeOperationDescriptor(ContractModel):
    """Runtime-visible structural identity for one current API operation."""

    operation_id: NonEmptyStr
    method: HttpMethod
    path: NonEmptyStr
    semantic_family: SemanticOperationFamily
    summary: NonEmptyStr | None = None


class OperationResolution(ContractModel):
    """Deterministic resolution result with explicit uncertainty."""

    status: ResolutionStatus
    operation_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_resolution(self) -> OperationResolution:
        if self.operation_ids != tuple(sorted(set(self.operation_ids))):
            raise ValueError("resolved operation IDs must be sorted and unique")

        if self.status is ResolutionStatus.RESOLVED:
            if len(self.operation_ids) != 1:
                raise ValueError("resolved state requires exactly one operation ID")
            return self

        if self.status is ResolutionStatus.AMBIGUOUS:
            if len(self.operation_ids) < 2:
                raise ValueError("ambiguous state requires at least two operation IDs")
            return self

        if self.operation_ids:
            raise ValueError("unresolved state cannot carry operation IDs")

        return self


def _normalize_token(token: str) -> str:
    return _ALIASES.get(token, token)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(
        _normalize_token(token)
        for token in _TOKEN_PATTERN.findall(text.casefold())
        if token not in _STOPWORDS
    )


def _operation_signature(operation_id: str) -> frozenset[str]:
    return _tokens(operation_id.replace("/", " ").replace("-", " "))


def _exact_operation_mentions(
    query: str,
    operations: tuple[RuntimeOperationDescriptor, ...],
) -> tuple[str, ...]:
    folded = query.casefold()
    return tuple(
        operation.operation_id
        for operation in operations
        if operation.operation_id.casefold() in folded
    )


def _method_path_matches(
    query: str,
    operations: tuple[RuntimeOperationDescriptor, ...],
) -> tuple[str, ...]:
    folded = query.casefold()
    query_tokens = _tokens(query)

    return tuple(
        operation.operation_id
        for operation in operations
        if operation.method in query_tokens
        and operation.path.casefold() in folded
    )


def _full_signature_matches(
    query_tokens: frozenset[str],
    operations: tuple[RuntimeOperationDescriptor, ...],
) -> tuple[str, ...]:
    matches: list[str] = []

    for operation in operations:
        signature = _operation_signature(operation.operation_id)
        if signature and signature.issubset(query_tokens):
            matches.append(operation.operation_id)

    return tuple(matches)


def _partial_operation_matches(
    query_tokens: frozenset[str],
    operations: tuple[RuntimeOperationDescriptor, ...],
) -> tuple[str, ...]:
    matches: list[str] = []

    for operation in operations:
        signature = _operation_signature(operation.operation_id)
        shared = signature & query_tokens

        has_action = bool(shared & _ACTION_TOKENS)
        namespace_token = _normalize_token(operation.operation_id.split("/", 1)[0])
        has_namespace = namespace_token in shared

        if has_action and has_namespace:
            matches.append(operation.operation_id)

    return tuple(matches)


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


class DeterministicOperationResolver:
    """Resolve only when runtime-visible structure supports a safe decision."""

    def __init__(self, operations: tuple[RuntimeOperationDescriptor, ...]) -> None:
        if not operations:
            raise ValueError("operation resolver requires a non-empty catalog")

        operation_ids = tuple(operation.operation_id for operation in operations)
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("operation resolver catalog IDs must be unique")

        self._operations = tuple(
            sorted(operations, key=lambda operation: operation.operation_id)
        )

    @property
    def operation_count(self) -> int:
        return len(self._operations)

    def resolve(self, query: str) -> OperationResolution:
        if not query.strip():
            return OperationResolution(status=ResolutionStatus.UNRESOLVED)

        exact = _exact_operation_mentions(query, self._operations)
        if exact:
            return _resolution_from_matches(exact)

        structural = _method_path_matches(query, self._operations)
        if structural:
            return _resolution_from_matches(structural)

        query_tokens = _tokens(query)
        full = _full_signature_matches(query_tokens, self._operations)
        if full:
            return _resolution_from_matches(full)

        partial = _partial_operation_matches(query_tokens, self._operations)
        if len(set(partial)) > 1:
            return OperationResolution(
                status=ResolutionStatus.AMBIGUOUS,
                operation_ids=tuple(sorted(set(partial))),
            )

        return OperationResolution(status=ResolutionStatus.UNRESOLVED)

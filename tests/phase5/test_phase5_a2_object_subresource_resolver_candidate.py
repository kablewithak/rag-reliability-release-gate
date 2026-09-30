from __future__ import annotations

from rag_reliability.evaluation.a2_object_subresource_resolver_candidate import (
    A2ObjectSubresourceOperationResolver,
    _operation_object_subresource_tokens,
)
from rag_reliability.runtime.operation_resolution import (
    ResolutionStatus,
    RuntimeOperationDescriptor,
)


def _catalog() -> tuple[RuntimeOperationDescriptor, ...]:
    return (
        RuntimeOperationDescriptor(
            operation_id="repos/accept-invitation-for-authenticated-user",
            method="patch",
            path="/user/repository_invitations/{invitation_id}",
            semantic_family="repositories_and_repository_webhooks",
            summary="Accept a repository invitation",
        ),
        RuntimeOperationDescriptor(
            operation_id="repos/list-attestations",
            method="get",
            path="/repos/{owner}/{repo}/attestations/{subject_digest}",
            semantic_family="repositories_and_repository_webhooks",
            summary="List attestations",
        ),
        RuntimeOperationDescriptor(
            operation_id="repos/create-for-authenticated-user",
            method="post",
            path="/user/repos",
            semantic_family="repositories_and_repository_webhooks",
            summary="Create a repository for the authenticated user",
        ),
        RuntimeOperationDescriptor(
            operation_id="repos/create-in-org",
            method="post",
            path="/orgs/{org}/repos",
            semantic_family="repositories_and_repository_webhooks",
            summary="Create an organization repository",
        ),
    )


def _resolver() -> A2ObjectSubresourceOperationResolver:
    return A2ObjectSubresourceOperationResolver(_catalog())


def test_already_resolved_baseline_result_is_preserved() -> None:
    result = _resolver().resolve(
        "For repos/create-in-org, which route is used?"
    )

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/create-in-org",)


def test_zero_supported_operations_is_unresolved() -> None:
    result = _resolver().resolve(
        "What authentication headers are required?"
    )

    assert result.status is ResolutionStatus.UNRESOLVED
    assert result.operation_ids == ()


def test_multiple_supported_operations_remain_ambiguous() -> None:
    result = _resolver().resolve(
        "How do I create a repository?"
    )

    assert result.status is ResolutionStatus.AMBIGUOUS
    assert result.operation_ids == (
        "repos/create-for-authenticated-user",
        "repos/create-in-org",
    )


def test_path_parameter_placeholders_do_not_add_object_evidence() -> None:
    operation = _catalog()[1]
    tokens = _operation_object_subresource_tokens(operation)

    assert "owner" not in tokens
    assert "subject" not in tokens
    assert "digest" not in tokens
    assert "attestations" in tokens


def test_resolution_is_repeatable() -> None:
    resolver = _resolver()
    query = (
        "An older contract for accepting a repository invitation "
        "did not list HTTP 451."
    )

    first = resolver.resolve(query)
    second = resolver.resolve(query)
    third = resolver.resolve(query)

    assert first == second == third

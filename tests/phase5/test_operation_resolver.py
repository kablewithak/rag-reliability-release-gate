from __future__ import annotations

from rag_reliability.runtime.operation_resolution import (
    DeterministicOperationResolver,
    ResolutionStatus,
    RuntimeOperationDescriptor,
)


def _catalog() -> tuple[RuntimeOperationDescriptor, ...]:
    return (
        RuntimeOperationDescriptor(
            operation_id="issues/create",
            method="post",
            path="/repos/{owner}/{repo}/issues",
            semantic_family="issues",
            summary="Create an issue",
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
        RuntimeOperationDescriptor(
            operation_id="repos/create-webhook",
            method="post",
            path="/repos/{owner}/{repo}/hooks",
            semantic_family="repositories_and_repository_webhooks",
            summary="Create a repository webhook",
        ),
        RuntimeOperationDescriptor(
            operation_id="repos/list-for-org",
            method="get",
            path="/orgs/{org}/repos",
            semantic_family="repositories_and_repository_webhooks",
            summary="List organization repositories",
        ),
    )


def _resolver() -> DeterministicOperationResolver:
    return DeterministicOperationResolver(_catalog())


def test_exact_operation_id_resolves() -> None:
    result = _resolver().resolve("For repos/create-in-org, which route is used?")

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/create-in-org",)


def test_method_and_path_resolve() -> None:
    result = _resolver().resolve("Which operation is POST /orgs/{org}/repos?")

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/create-in-org",)


def test_complete_natural_language_signature_resolves() -> None:
    result = _resolver().resolve("How do I create a repository webhook?")

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/create-webhook",)


def test_generic_create_repository_is_ambiguous() -> None:
    result = _resolver().resolve("How do I create a repository?")

    assert result.status is ResolutionStatus.AMBIGUOUS
    assert "repos/create-in-org" in result.operation_ids
    assert "repos/create-for-authenticated-user" in result.operation_ids


def test_multi_operation_query_is_ambiguous() -> None:
    result = _resolver().resolve(
        "Compare creating a repository in an organization with creating one "
        "for the authenticated user."
    )

    assert result.status is ResolutionStatus.AMBIGUOUS
    assert result.operation_ids == (
        "repos/create-for-authenticated-user",
        "repos/create-in-org",
    )


def test_status_only_query_is_unresolved() -> None:
    result = _resolver().resolve("Is HTTP 451 documented?")

    assert result.status is ResolutionStatus.UNRESOLVED
    assert result.operation_ids == ()


def test_operation_free_guidance_is_unresolved() -> None:
    result = _resolver().resolve(
        "What authentication headers are required for GitHub REST API requests?"
    )

    assert result.status is ResolutionStatus.UNRESOLVED


def test_resolution_is_repeatable() -> None:
    resolver = _resolver()
    query = "How do I list repositories for an organization?"

    first = resolver.resolve(query)
    second = resolver.resolve(query)
    third = resolver.resolve(query)

    assert first == second == third

from __future__ import annotations

from rag_reliability.evaluation.catalog_action_resolver_candidate import (
    CatalogDerivedActionOperationResolver,
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
            operation_id="repos/create-in-org",
            method="post",
            path="/orgs/{org}/repos",
            semantic_family="repositories_and_repository_webhooks",
            summary="Create an organization repository",
        ),
        RuntimeOperationDescriptor(
            operation_id="issues/approve",
            method="post",
            path="/repos/{owner}/{repo}/issues/{issue_number}/approve",
            semantic_family="issues",
            summary="Approve an issue",
        ),
    )


def test_catalog_action_resolves_accept_inflection() -> None:
    result = CatalogDerivedActionOperationResolver(_catalog()).resolve(
        "Is accepting a repository invitation supported?"
    )

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/accept-invitation-for-authenticated-user",)


def test_catalog_action_derivation_is_not_accept_specific() -> None:
    result = CatalogDerivedActionOperationResolver(_catalog()).resolve(
        "What happens when approving an issue?"
    )

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("issues/approve",)


def test_existing_non_unresolved_baseline_result_is_preserved() -> None:
    result = CatalogDerivedActionOperationResolver(_catalog()).resolve(
        "For repos/create-in-org, which route is used?"
    )

    assert result.status is ResolutionStatus.RESOLVED
    assert result.operation_ids == ("repos/create-in-org",)


def test_operation_free_guidance_stays_unresolved() -> None:
    result = CatalogDerivedActionOperationResolver(_catalog()).resolve(
        "What authentication headers are required?"
    )

    assert result.status is ResolutionStatus.UNRESOLVED
    assert result.operation_ids == ()

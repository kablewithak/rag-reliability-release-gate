from rag_reliability.corpus.catalog import parse_candidate_operations

_OPENAPI = b'''---
openapi: 3.0.3
info:
  title: fixture
  version: 1
paths:
  /repos/{owner}/{repo}/issues:
    get:
      tags: [issues]
      operationId: issues/list-for-repo
    post:
      tags: [issues]
      operationId: issues/create
  /repos/{owner}/{repo}/pulls:
    get:
      tags: [pulls]
      operationId: pulls/list
  /repos/{owner}/{repo}:
    get:
      tags: [repos]
      operationId: repos/get
  /repos/{owner}/{repo}/actions/runs:
    get:
      tags: [actions]
      operationId: actions/list-workflow-runs-for-repo
  /meta:
    get:
      tags: [meta]
      operationId: meta/get
'''


def test_operation_catalog_keeps_only_frozen_semantic_families() -> None:
    operations = parse_candidate_operations(_OPENAPI)

    assert tuple(item.operation_id for item in operations) == (
        "actions/list-workflow-runs-for-repo",
        "issues/create",
        "issues/list-for-repo",
        "pulls/list",
        "repos/get",
    )


def test_operation_catalog_preserves_method_path_and_source_tags() -> None:
    operations = parse_candidate_operations(_OPENAPI)
    by_id = {item.operation_id: item for item in operations}

    issue_list = by_id["issues/list-for-repo"]
    assert issue_list.method == "get"
    assert issue_list.path == "/repos/{owner}/{repo}/issues"
    assert issue_list.tags == ("issues",)
    assert issue_list.semantic_family_candidate == "issues"


def test_operation_catalog_rejects_wrong_openapi_format() -> None:
    invalid = _OPENAPI.replace(b"openapi: 3.0.3", b"openapi: 3.1.0")

    try:
        parse_candidate_operations(invalid)
    except ValueError as exc:
        assert "OpenAPI 3.0.3" in str(exc)
    else:
        raise AssertionError("expected a fail-closed OpenAPI version error")

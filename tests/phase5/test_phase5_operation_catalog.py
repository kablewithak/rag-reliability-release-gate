from rag_reliability.runtime.operation_catalog import _fragment_value


def test_fragment_value_reads_root_structural_fragment() -> None:
    payload = {
        "fragments": [
            {
                "path": [],
                "value": {
                    "method": "post",
                    "operation": {
                        "operationId": "repos/create-in-org",
                        "summary": "Create an organization repository",
                    },
                    "path": "/orgs/{org}/repos",
                },
            }
        ]
    }

    assert _fragment_value(payload, ("method",)) == "post"
    assert _fragment_value(payload, ("operation", "operationId")) == (
        "repos/create-in-org"
    )


def test_fragment_value_reads_split_structural_fragments() -> None:
    payload = {
        "fragments": [
            {"path": ["method"], "value": "post"},
            {"path": ["path"], "value": "/orgs/{org}/repos"},
            {
                "path": ["operation", "operationId"],
                "value": "repos/create-in-org",
            },
            {
                "path": ["operation", "summary"],
                "value": "Create an organization repository",
            },
        ]
    }

    assert _fragment_value(payload, ("path",)) == "/orgs/{org}/repos"
    assert _fragment_value(payload, ("operation", "summary")) == (
        "Create an organization repository"
    )

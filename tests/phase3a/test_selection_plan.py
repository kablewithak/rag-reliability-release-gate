import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_reliability.corpus.models import CorpusSourceSelectionPlan


def _plan_path() -> Path:
    return Path("datasets/source_manifests/phase3a_source_selection_v1.json")


def test_frozen_selection_plan_loads() -> None:
    plan = CorpusSourceSelectionPlan.model_validate_json(
        _plan_path().read_text(encoding="utf-8")
    )

    assert len(plan.files) == 12
    assert sum(item.repository == "github/docs" for item in plan.files) == 10
    assert sum(item.repository == "github/rest-api-description" for item in plan.files) == 2


def test_selection_plan_rejects_mutated_pinned_commit() -> None:
    payload = json.loads(_plan_path().read_text(encoding="utf-8"))
    payload["files"][0]["commit_sha"] = "0" * 40

    with pytest.raises(ValidationError, match="frozen commit"):
        CorpusSourceSelectionPlan.model_validate(payload)


def test_selection_plan_rejects_path_outside_frozen_docs_prefixes() -> None:
    payload = json.loads(_plan_path().read_text(encoding="utf-8"))
    payload["files"][0]["path"] = "content/actions/example.md"

    with pytest.raises(ValidationError, match="outside the frozen prefixes"):
        CorpusSourceSelectionPlan.model_validate(payload)

def test_openapi_selection_matches_frozen_snapshot_descriptor() -> None:
    plan_payload = json.loads(_plan_path().read_text(encoding="utf-8"))
    snapshot_path = Path("datasets/source_manifests/source_snapshot_v1.json")
    snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))

    selected_openapi = {
        item["api_version_or_snapshot"]: item
        for item in plan_payload["files"]
        if item["repository"] == "github/rest-api-description"
    }
    frozen_openapi = snapshot_payload["rest_api_description"]

    assert plan_payload["target_api_version"] == frozen_openapi["current"]["api_version"]
    assert (
        plan_payload["comparison_api_version"]
        == frozen_openapi["comparison"]["api_version"]
    )

    for snapshot_key in ("current", "comparison"):
        frozen = frozen_openapi[snapshot_key]
        selected = selected_openapi[frozen["api_version"]]
        assert selected["repository"] == frozen_openapi["repository"]
        assert selected["commit_sha"] == frozen_openapi["commit_sha"]
        assert selected["path"] == frozen["path"]
        assert selected["expected_git_blob_sha1"] == frozen["blob_sha"]


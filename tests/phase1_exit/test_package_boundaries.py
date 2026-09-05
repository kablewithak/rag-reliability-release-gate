import ast
from pathlib import Path

from rag_reliability.contracts.evaluation import RuntimeCaseInput
from rag_reliability.contracts.runtime import ProviderRequest, ProviderResponse

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_ROOT = REPO_ROOT / "src" / "rag_reliability" / "contracts"

EVALUATOR_ONLY_NAMES = {
    "expected_response_mode",
    "required_fact_ids",
    "required_source_ids",
    "forbidden_source_ids",
    "must_refuse_reason",
    "gold_fact_rubric",
    "scoring_notes",
    "held_out_scoring_outcomes",
    "post_run_failure_labels",
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)

    return modules


def test_runtime_case_input_remains_minimal() -> None:
    assert set(RuntimeCaseInput.model_fields) == {"case_id", "query"}


def test_runtime_contract_source_does_not_reference_evaluator_only_fields() -> None:
    runtime_source = (CONTRACTS_ROOT / "runtime.py").read_text(encoding="utf-8")

    for forbidden_name in EVALUATOR_ONLY_NAMES:
        assert forbidden_name not in runtime_source


def test_runtime_and_interface_modules_do_not_import_evaluation_contracts() -> None:
    for filename in ("runtime.py", "interfaces.py"):
        modules = imported_modules(CONTRACTS_ROOT / filename)
        assert "rag_reliability.contracts.evaluation" not in modules


def test_provider_boundary_fields_remain_provider_neutral() -> None:
    assert set(ProviderRequest.model_fields) == {"query", "context"}
    assert set(ProviderResponse.model_fields) == {
        "answer_text",
        "cited_source_ids",
    }

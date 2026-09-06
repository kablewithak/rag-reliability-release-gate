import asyncio
import hashlib
from pathlib import Path

from rag_reliability.evaluation.thin_slice import (
    canonical_report_bytes,
    execute_thin_slice,
    load_thin_slice_bundle,
    write_thin_slice_report,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "artifacts" / "development" / "phase2b_thin_slice_report_v1.json"
SHA_PATH = REPORT_PATH.with_suffix(REPORT_PATH.suffix + ".sha256")

FORBIDDEN_REPORT_TERMS = (
    '"query"',
    '"answer_text"',
    '"content"',
    '"gold_fact_rubric"',
    '"scoring_notes"',
    '"authoring_evidence"',
    '"required_fact_ids"',
)


def test_committed_report_matches_frozen_fixture_execution() -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    report = asyncio.run(execute_thin_slice(bundle))

    assert REPORT_PATH.read_bytes() == canonical_report_bytes(report)


def test_committed_report_is_metadata_safe() -> None:
    report_text = REPORT_PATH.read_text(encoding="utf-8")

    for forbidden_term in FORBIDDEN_REPORT_TERMS:
        assert forbidden_term not in report_text


def test_report_sha256_sidecar_matches_report_bytes() -> None:
    expected_digest = hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()
    sidecar = SHA_PATH.read_text(encoding="utf-8").strip()

    assert sidecar == f"{expected_digest}  {REPORT_PATH.name}"


def test_report_writer_emits_report_and_sidecar(tmp_path: Path) -> None:
    bundle = load_thin_slice_bundle(REPO_ROOT)
    report = asyncio.run(execute_thin_slice(bundle))
    output = tmp_path / "report.json"

    digest = write_thin_slice_report(report, output)

    assert output.exists()
    assert output.with_suffix(".json.sha256").exists()
    assert hashlib.sha256(output.read_bytes()).hexdigest() == digest

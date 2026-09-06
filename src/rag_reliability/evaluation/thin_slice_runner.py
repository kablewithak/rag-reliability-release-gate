"""CLI entry point for the deterministic Phase 2B development proof."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from rag_reliability.evaluation.thin_slice import (
    execute_thin_slice,
    load_thin_slice_bundle,
    write_thin_slice_report,
)

_DEFAULT_OUTPUT = Path("artifacts/development/phase2b_thin_slice_report_v1.json")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 2B deterministic RAG thin-slice evaluation."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing datasets/thin_slice.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help="Metadata-safe development report output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output
    if not output.is_absolute():
        output = repo_root / output

    bundle = load_thin_slice_bundle(repo_root)
    report = asyncio.run(execute_thin_slice(bundle))
    digest = write_thin_slice_report(report, output)

    print(f"PHASE2B_SUITE_ID={report.suite_id}")
    print(f"PHASE2B_CASE_COUNT={report.case_count}")
    print(f"PHASE2B_PASSED_CASE_COUNT={report.passed_case_count}")
    print(f"PHASE2B_FAILED_CASE_COUNT={report.failed_case_count}")
    print(f"PHASE2B_ALL_CASES_PASSED={str(report.all_cases_passed).lower()}")
    print(f"PHASE2B_RUNTIME_CONFIGURATION_HASH={report.runtime_configuration_hash}")
    print(f"PHASE2B_REPORT_SHA256={digest}")
    print(f"PHASE2B_REPORT_PATH={output}")
    return 0 if report.all_cases_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

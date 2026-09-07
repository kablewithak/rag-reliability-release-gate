"""Exact render-semantics inventory for the constrained Phase 3B authored corpus."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Literal

from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr
from rag_reliability.corpus.render_context_review import RenderReviewSourceUnit
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet

_LIQUID_TAG_PATTERN = re.compile(r"\{%\s*-?\s*([A-Za-z_][\w-]*)(.*?)\s*-?\s*%\}", re.DOTALL)
_AUTOTITLE_PATTERN = re.compile(r"\[AUTOTITLE\]\(([^)]+)\)")

RenderContextReviewSha256 = Literal[
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
]
DependencyManifestSha256 = Literal[
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
]
_EXPECTED_RENDER_CONTEXT_REVIEW_SHA256: RenderContextReviewSha256 = (
    "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
)
_EXPECTED_DEPENDENCY_MANIFEST_SHA256: DependencyManifestSha256 = (
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
)

SemanticConstructKind = Literal[
    "assignment_expression",
    "conditional_expression",
    "iteration_expression",
    "variant_argument",
    "presentation_argument",
    "autotitle_target",
]


class RenderSemanticRecord(ContractModel):
    """Occurrence summary for one exact render expression or argument."""

    construct_kind: SemanticConstructKind
    construct_name: NonEmptyStr
    value: NonEmptyStr
    occurrence_count: int = Field(gt=0)
    source_count: int = Field(gt=0)
    source_locators: tuple[NonEmptyStr, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sources(self) -> RenderSemanticRecord:
        if tuple(sorted(set(self.source_locators))) != self.source_locators:
            raise ValueError("render semantic source locators must be sorted and unique")
        if self.source_count != len(self.source_locators):
            raise ValueError("render semantic source count does not match locators")
        return self


class Phase3bRenderSemanticsReview(ContractModel):
    """Exact syntax surface that the deterministic render profile must handle."""

    review_version: Literal["phase3b-render-semantics-review-v2"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_render_context_review_sha256: RenderContextReviewSha256
    source_dependency_manifest_sha256: DependencyManifestSha256
    supersedes_review_version: Literal["phase3b-render-semantics-review-v1"]
    supersedes_review_sha256: Literal[
        "e892bad04a1a8c58cac761c06b3c15015130b3ab53350c74ca2a97b159be6a20"
    ]
    supersession_reason: Literal["liquid_trim_marker_parser_repair"]
    records: tuple[RenderSemanticRecord, ...]
    assignment_expression_count: int = Field(ge=0)
    conditional_expression_count: int = Field(ge=0)
    iteration_expression_count: int = Field(ge=0)
    variant_argument_count: int = Field(ge=0)
    presentation_argument_count: int = Field(ge=0)
    autotitle_target_count: int = Field(ge=0)
    review_status: Literal["candidate_only"] = "candidate_only"
    render_policy_freeze_required: Literal[True] = True
    rendering_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_totals(self) -> Phase3bRenderSemanticsReview:
        expected: dict[SemanticConstructKind, int] = {
            "assignment_expression": self.assignment_expression_count,
            "conditional_expression": self.conditional_expression_count,
            "iteration_expression": self.iteration_expression_count,
            "variant_argument": self.variant_argument_count,
            "presentation_argument": self.presentation_argument_count,
            "autotitle_target": self.autotitle_target_count,
        }
        observed: Counter[SemanticConstructKind] = Counter(
            record.construct_kind for record in self.records
        )
        for kind, count in expected.items():
            if observed[kind] != count:
                raise ValueError(f"render semantic record count mismatch: {kind}")
        return self


def _normalized_argument(value: str) -> str:
    return " ".join(value.strip().split())


def build_render_semantics_review(
    units: tuple[RenderReviewSourceUnit, ...],
    frozen: Phase3bFrozenRenderDependencySet,
    *,
    source_render_context_review_sha256: str,
    source_dependency_manifest_sha256: str,
) -> Phase3bRenderSemanticsReview:
    """Inventory exact branch expressions and presentation/variant arguments."""

    if source_render_context_review_sha256 != _EXPECTED_RENDER_CONTEXT_REVIEW_SHA256:
        raise ValueError("render context review hash does not match accepted v2 evidence")
    if source_dependency_manifest_sha256 != _EXPECTED_DEPENDENCY_MANIFEST_SHA256:
        raise ValueError("render dependency manifest hash does not match accepted v2 freeze")

    required_tags = set(frozen.required_liquid_tags)
    counts: Counter[tuple[SemanticConstructKind, str, str]] = Counter()
    sources: dict[tuple[SemanticConstructKind, str, str], set[str]] = defaultdict(set)

    for unit in units:
        for match in _LIQUID_TAG_PATTERN.finditer(unit.content):
            tag = match.group(1)
            if tag not in required_tags:
                raise ValueError(f"unfrozen Liquid tag observed during semantics review: {tag}")
            argument = _normalized_argument(match.group(2))

            key: tuple[SemanticConstructKind, str, str]
            if tag == "assign":
                if not argument:
                    raise ValueError("assign tag has no expression")
                key = ("assignment_expression", tag, argument)
            elif tag in {"ifversion", "if", "elsif"}:
                if not argument:
                    raise ValueError(f"conditional tag has no expression: {tag}")
                key = ("conditional_expression", tag, argument)
            elif tag == "for":
                if not argument:
                    raise ValueError("for tag has no expression")
                key = ("iteration_expression", tag, argument)
            elif tag in {"cli", "curl", "javascript"}:
                key = ("variant_argument", tag, argument or "<none>")
            elif tag == "octicon":
                if not argument:
                    raise ValueError("octicon tag has no arguments")
                key = ("presentation_argument", tag, argument)
            else:
                continue

            counts[key] += 1
            sources[key].add(unit.source_locator)

        for match in _AUTOTITLE_PATTERN.finditer(unit.content):
            target = match.group(1).strip()
            if not target:
                raise ValueError("AUTOTITLE target is empty")
            key = ("autotitle_target", "AUTOTITLE", target)
            counts[key] += 1
            sources[key].add(unit.source_locator)

    records = tuple(
        RenderSemanticRecord(
            construct_kind=kind,
            construct_name=name,
            value=value,
            occurrence_count=counts[(kind, name, value)],
            source_count=len(sources[(kind, name, value)]),
            source_locators=tuple(sorted(sources[(kind, name, value)])),
        )
        for kind, name, value in sorted(counts)
    )

    unique_counts: Counter[SemanticConstructKind] = Counter(
        record.construct_kind for record in records
    )
    return Phase3bRenderSemanticsReview(
        review_version="phase3b-render-semantics-review-v2",
        snapshot_id=frozen.snapshot_id,
        source_render_context_review_sha256=_EXPECTED_RENDER_CONTEXT_REVIEW_SHA256,
        source_dependency_manifest_sha256=_EXPECTED_DEPENDENCY_MANIFEST_SHA256,
        supersedes_review_version="phase3b-render-semantics-review-v1",
        supersedes_review_sha256=(
            "e892bad04a1a8c58cac761c06b3c15015130b3ab53350c74ca2a97b159be6a20"
        ),
        supersession_reason="liquid_trim_marker_parser_repair",
        records=records,
        assignment_expression_count=unique_counts["assignment_expression"],
        conditional_expression_count=unique_counts["conditional_expression"],
        iteration_expression_count=unique_counts["iteration_expression"],
        variant_argument_count=unique_counts["variant_argument"],
        presentation_argument_count=unique_counts["presentation_argument"],
        autotitle_target_count=unique_counts["autotitle_target"],
    )

"""Render-context review inventory for the constrained Phase 3B authored corpus."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_dependencies import dependency_target
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet

_LIQUID_TAG_PATTERN = re.compile(r"\{%\s*-?\s*([A-Za-z_][\w-]*)(.*?)\s*-?\s*%\}", re.DOTALL)
_TEMPLATE_VARIABLE_PATTERN = re.compile(r"\{\{\s*-?\s*([^{}]+?)\s*-?\s*\}\}")
_AUTOTITLE = "[AUTOTITLE]"

ConstructKind = Literal["liquid_tag", "template_variable", "autotitle"]
DecisionClass = Literal[
    "conditional_control",
    "dependency_substitution",
    "iteration_control",
    "link_title_resolution",
    "literal_block_control",
    "presentation_substitution",
    "template_assignment",
    "template_context_value",
    "variant_block_control",
]


class RenderReviewSourceUnit(ContractModel):
    """One exact authored/dependency content unit inspected for render constructs."""

    source_locator: NonEmptyStr
    content: NonEmptyStr


class RenderConstructReviewRecord(ContractModel):
    """Occurrence summary for one required render construct."""

    construct_kind: ConstructKind
    construct_name: NonEmptyStr
    decision_class: DecisionClass
    occurrence_count: int = Field(gt=0)
    source_count: int = Field(gt=0)
    source_locators: tuple[NonEmptyStr, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sources(self) -> RenderConstructReviewRecord:
        if tuple(sorted(set(self.source_locators))) != self.source_locators:
            raise ValueError("render construct source locators must be sorted and unique")
        if self.source_count != len(self.source_locators):
            raise ValueError("render construct source count does not match locators")
        return self


class Phase3bRenderContextReview(ContractModel):
    """Review evidence for the exact render behaviors still requiring a policy freeze."""

    review_version: Literal["phase3b-render-context-review-v2"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_render_audit_sha256: Sha256
    source_dependency_manifest_sha256: Sha256
    required_liquid_tags: tuple[NonEmptyStr, ...]
    required_template_variables: tuple[NonEmptyStr, ...]
    records: tuple[RenderConstructReviewRecord, ...]
    liquid_occurrence_count: int = Field(ge=0)
    template_variable_occurrence_count: int = Field(ge=0)
    autotitle_occurrence_count: int = Field(ge=0)
    review_status: Literal["candidate_only"] = "candidate_only"
    render_context_freeze_required: Literal[True] = True
    rendering_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_inventory(self) -> Phase3bRenderContextReview:
        liquid_names = tuple(
            sorted(
                record.construct_name
                for record in self.records
                if record.construct_kind == "liquid_tag"
            )
        )
        template_names = tuple(
            sorted(
                record.construct_name
                for record in self.records
                if record.construct_kind == "template_variable"
            )
        )
        if liquid_names != self.required_liquid_tags:
            raise ValueError("review Liquid tags do not match frozen dependency requirements")
        if template_names != self.required_template_variables:
            raise ValueError(
                "review template variables do not match frozen dependency requirements"
            )

        liquid_total = sum(
            record.occurrence_count
            for record in self.records
            if record.construct_kind == "liquid_tag"
        )
        template_total = sum(
            record.occurrence_count
            for record in self.records
            if record.construct_kind == "template_variable"
        )
        autotitle_total = sum(
            record.occurrence_count
            for record in self.records
            if record.construct_kind == "autotitle"
        )
        if liquid_total != self.liquid_occurrence_count:
            raise ValueError("Liquid occurrence count does not match review records")
        if template_total != self.template_variable_occurrence_count:
            raise ValueError("template-variable occurrence count does not match review records")
        if autotitle_total != self.autotitle_occurrence_count:
            raise ValueError("AUTOTITLE occurrence count does not match review records")
        return self


def _decision_class(kind: ConstructKind, name: str) -> DecisionClass:
    if kind == "template_variable":
        return "template_context_value"
    if kind == "autotitle":
        return "link_title_resolution"
    if name == "data":
        return "dependency_substitution"
    if name in {"raw", "endraw"}:
        return "literal_block_control"
    if name in {"cli", "endcli", "curl", "endcurl", "javascript", "endjavascript"}:
        return "variant_block_control"
    if name in {"if", "ifversion", "elsif", "else", "endif"}:
        return "conditional_control"
    if name in {"for", "endfor"}:
        return "iteration_control"
    if name == "assign":
        return "template_assignment"
    if name == "octicon":
        return "presentation_substitution"
    raise ValueError(f"unsupported reviewed Liquid tag: {name}")


def _selected_variable_value(content: bytes, reference: str) -> str:
    target = dependency_target(reference)
    loaded: object = yaml.safe_load(content.decode("utf-8"))
    current = loaded
    for key in target.variable_key_path:
        if not isinstance(current, Mapping):
            raise ValueError(f"variable reference traverses non-mapping value: {reference}")
        if key not in current:
            raise ValueError(f"variable reference key does not exist: {reference}")
        current = current[key]
    if isinstance(current, str):
        return current
    return yaml.safe_dump(current, sort_keys=True, allow_unicode=True)


def build_review_source_units(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    acquisition: AcquisitionReceipt,
    frozen: Phase3bFrozenRenderDependencySet,
) -> tuple[RenderReviewSourceUnit, ...]:
    """Load exact authored documents and selected frozen dependency values from cache."""

    cache_by_source = {item.source_id: item.cache_path for item in acquisition.files}
    units: list[RenderReviewSourceUnit] = []

    for item in plan.files:
        if item.media_type != "markdown":
            continue
        cache_path = cache_by_source.get(item.source_id)
        if cache_path is None:
            raise ValueError(f"render audit acquisition missing source: {item.source_id}")
        units.append(
            RenderReviewSourceUnit(
                source_locator=item.path,
                content=(repo_root / cache_path).read_text(encoding="utf-8"),
            )
        )

    for dependency in frozen.dependency_files:
        content = (repo_root / dependency.cache_path).read_bytes()
        if dependency.media_type == "markdown_reusable":
            units.append(
                RenderReviewSourceUnit(
                    source_locator=dependency.path,
                    content=content.decode("utf-8"),
                )
            )
            continue

        for reference in dependency.satisfied_references:
            units.append(
                RenderReviewSourceUnit(
                    source_locator=f"{dependency.path}#{reference}",
                    content=_selected_variable_value(content, reference),
                )
            )

    return tuple(sorted(units, key=lambda item: item.source_locator))


def build_render_context_review(
    units: tuple[RenderReviewSourceUnit, ...],
    frozen: Phase3bFrozenRenderDependencySet,
    *,
    source_dependency_manifest_sha256: str,
) -> Phase3bRenderContextReview:
    """Inventory exact occurrences without authorizing or implementing rendering."""

    counts: Counter[tuple[ConstructKind, str]] = Counter()
    sources: dict[tuple[ConstructKind, str], set[str]] = defaultdict(set)

    for unit in units:
        for match in _LIQUID_TAG_PATTERN.finditer(unit.content):
            key: tuple[ConstructKind, str] = ("liquid_tag", match.group(1))
            counts[key] += 1
            sources[key].add(unit.source_locator)

        for match in _TEMPLATE_VARIABLE_PATTERN.finditer(unit.content):
            key = ("template_variable", match.group(1).strip())
            counts[key] += 1
            sources[key].add(unit.source_locator)

        autotitle_count = unit.content.count(_AUTOTITLE)
        if autotitle_count:
            key = ("autotitle", _AUTOTITLE)
            counts[key] += autotitle_count
            sources[key].add(unit.source_locator)

    required_liquid = set(frozen.required_liquid_tags)
    observed_liquid = {
        name for (kind, name), count in counts.items() if kind == "liquid_tag" and count > 0
    }
    if observed_liquid != required_liquid:
        raise ValueError("observed Liquid tags do not match frozen dependency requirements")

    required_templates = set(frozen.required_template_variables)
    observed_templates = {
        name
        for (kind, name), count in counts.items()
        if kind == "template_variable" and count > 0
    }
    if observed_templates != required_templates:
        raise ValueError("observed template variables do not match frozen dependency requirements")

    records = tuple(
        RenderConstructReviewRecord(
            construct_kind=kind,
            construct_name=name,
            decision_class=_decision_class(kind, name),
            occurrence_count=counts[(kind, name)],
            source_count=len(sources[(kind, name)]),
            source_locators=tuple(sorted(sources[(kind, name)])),
        )
        for kind, name in sorted(counts)
    )

    return Phase3bRenderContextReview(
        review_version="phase3b-render-context-review-v2",
        snapshot_id=frozen.snapshot_id,
        source_render_audit_sha256=frozen.source_render_audit_sha256,
        source_dependency_manifest_sha256=source_dependency_manifest_sha256,
        required_liquid_tags=frozen.required_liquid_tags,
        required_template_variables=frozen.required_template_variables,
        records=records,
        liquid_occurrence_count=sum(
            record.occurrence_count
            for record in records
            if record.construct_kind == "liquid_tag"
        ),
        template_variable_occurrence_count=sum(
            record.occurrence_count
            for record in records
            if record.construct_kind == "template_variable"
        ),
        autotitle_occurrence_count=sum(
            record.occurrence_count
            for record in records
            if record.construct_kind == "autotitle"
        ),
    )

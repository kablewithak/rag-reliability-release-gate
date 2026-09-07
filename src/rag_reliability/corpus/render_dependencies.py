"""Candidate render-dependency closure for pinned GitHub Docs sources."""

from __future__ import annotations

import hashlib
import heapq
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal
from urllib.request import Request, urlopen

import yaml
from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.models import GitBlobSha1
from rag_reliability.corpus.render_audit import (
    Phase3bAuthoredRenderabilityAudit,
    scan_authored_markdown,
)

DocsDependencyMediaType = Literal["markdown_reusable", "yaml_variables"]
Fetcher = Callable[[str], bytes]

_GITHUB_DOCS_COMMIT: Literal[
    "ec3629a841129ae28189d7bb2274a7b3d40c5095"
] = "ec3629a841129ae28189d7bb2274a7b3d40c5095"


class RenderDependencyTarget(ContractModel):
    """One GitHub Docs data reference mapped to its source file and optional YAML key."""

    data_reference: NonEmptyStr
    path: NonEmptyStr
    media_type: DocsDependencyMediaType
    variable_key_path: tuple[NonEmptyStr, ...] = ()


class RenderDependencyFileReceipt(ContractModel):
    """Identity receipt for one candidate render dependency file."""

    path: NonEmptyStr
    media_type: DocsDependencyMediaType
    observed_git_blob_sha1: GitBlobSha1
    content_sha256: Sha256
    byte_count: int = Field(gt=0)
    cache_path: NonEmptyStr
    satisfied_references: tuple[NonEmptyStr, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_references(self) -> RenderDependencyFileReceipt:
        if tuple(sorted(set(self.satisfied_references))) != self.satisfied_references:
            raise ValueError("dependency file references must be sorted and unique")
        return self


class Phase3bRenderDependencyClosureCandidate(ContractModel):
    """Reviewable dependency closure discovered from the authored renderability audit."""

    closure_version: Literal["phase3b-render-dependency-closure-candidate-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    github_docs_commit_sha: Literal[
        "ec3629a841129ae28189d7bb2274a7b3d40c5095"
    ] = _GITHUB_DOCS_COMMIT
    source_render_audit_sha256: Sha256
    direct_data_references: tuple[NonEmptyStr, ...]
    resolved_data_references: tuple[NonEmptyStr, ...]
    transitive_data_references: tuple[NonEmptyStr, ...]
    reusable_references: tuple[NonEmptyStr, ...]
    variable_references: tuple[NonEmptyStr, ...]
    dependency_files: tuple[RenderDependencyFileReceipt, ...]
    render_liquid_tags: tuple[NonEmptyStr, ...]
    render_template_variables: tuple[NonEmptyStr, ...]
    autotitle_count: int = Field(ge=0)
    freeze_status: Literal["candidate_only"] = "candidate_only"
    render_dependency_freeze_required: Literal[True] = True
    rendering_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_closure(self) -> Phase3bRenderDependencyClosureCandidate:
        tuple_fields = (
            self.direct_data_references,
            self.resolved_data_references,
            self.transitive_data_references,
            self.reusable_references,
            self.variable_references,
            self.render_liquid_tags,
            self.render_template_variables,
        )
        for values in tuple_fields:
            if tuple(sorted(set(values))) != values:
                raise ValueError("dependency closure tuple fields must be sorted and unique")

        direct = set(self.direct_data_references)
        resolved = set(self.resolved_data_references)
        if not direct <= resolved:
            raise ValueError("direct data references must be contained in resolved closure")
        if set(self.transitive_data_references) != resolved - direct:
            raise ValueError("transitive data references do not match resolved closure")
        if set(self.reusable_references) | set(self.variable_references) != resolved:
            raise ValueError("reference-kind partition does not match resolved closure")
        if set(self.reusable_references) & set(self.variable_references):
            raise ValueError("reference-kind partition must not overlap")

        paths = tuple(item.path for item in self.dependency_files)
        if len(paths) != len(set(paths)):
            raise ValueError("dependency file paths must be unique")

        satisfied = {
            reference
            for item in self.dependency_files
            for reference in item.satisfied_references
        }
        if satisfied != resolved:
            raise ValueError("dependency file receipts do not cover the resolved closure")
        return self


def dependency_target(reference: str) -> RenderDependencyTarget:
    """Map one supported GitHub Docs data reference to an immutable source path."""

    parts = reference.split(".")
    if len(parts) >= 3 and parts[0] == "reusables":
        relative = "/".join(parts[1:]) + ".md"
        return RenderDependencyTarget(
            data_reference=reference,
            path=f"data/reusables/{relative}",
            media_type="markdown_reusable",
        )

    if len(parts) >= 3 and parts[0] == "variables":
        return RenderDependencyTarget(
            data_reference=reference,
            path=f"data/variables/{parts[1]}.yml",
            media_type="yaml_variables",
            variable_key_path=tuple(parts[2:]),
        )

    raise ValueError(f"unsupported GitHub Docs data reference: {reference}")


def _raw_docs_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/github/docs/{_GITHUB_DOCS_COMMIT}/{path}"


def _default_fetcher(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "rag-reliability-release-gate/0.1"})
    with urlopen(request, timeout=60) as response:
        return bytes(response.read())


def _git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def _cache_dependency(repo_root: Path, target: RenderDependencyTarget, content: bytes) -> str:
    observed_blob = _git_blob_sha1(content)
    suffix = ".md" if target.media_type == "markdown_reusable" else ".yml"
    cache_path = (
        repo_root
        / "datasets"
        / "source_documents"
        / "_upstream_cache"
        / f"{observed_blob}{suffix}"
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(content)
    return cache_path.relative_to(repo_root).as_posix()


def _selected_variable_value(content: bytes, key_path: tuple[str, ...], reference: str) -> str:
    loaded: object = yaml.safe_load(content.decode("utf-8"))
    current = loaded
    for key in key_path:
        if not isinstance(current, Mapping):
            raise ValueError(f"variable reference traverses non-mapping value: {reference}")
        if key not in current:
            raise ValueError(f"variable reference key does not exist: {reference}")
        current = current[key]

    if isinstance(current, str):
        return current
    return yaml.safe_dump(current, sort_keys=True, allow_unicode=True)


def _direct_references(audit: Phase3bAuthoredRenderabilityAudit) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                reference
                for document in audit.documents
                for reference in document.data_references
            }
        )
    )


def build_render_dependency_closure_candidate(
    repo_root: Path,
    audit: Phase3bAuthoredRenderabilityAudit,
    *,
    source_render_audit_sha256: str,
    fetcher: Fetcher = _default_fetcher,
) -> Phase3bRenderDependencyClosureCandidate:
    """Discover the transitive data-reference closure without authorizing rendering."""

    direct = _direct_references(audit)
    pending = list(direct)
    heapq.heapify(pending)
    processed: set[str] = set()
    content_by_path: dict[str, bytes] = {}
    target_by_path: dict[str, RenderDependencyTarget] = {}
    references_by_path: dict[str, set[str]] = {}
    dependency_liquid_tags: set[str] = set()
    dependency_template_variables: set[str] = set()

    while pending:
        reference = heapq.heappop(pending)
        if reference in processed:
            continue
        processed.add(reference)

        target = dependency_target(reference)
        references_by_path.setdefault(target.path, set()).add(reference)
        target_by_path.setdefault(target.path, target)

        content = content_by_path.get(target.path)
        if content is None:
            content = fetcher(_raw_docs_url(target.path))
            if not content:
                raise ValueError(f"render dependency is empty: {target.path}")
            content_by_path[target.path] = content

        if target.media_type == "markdown_reusable":
            selected_content = content.decode("utf-8")
        else:
            selected_content = _selected_variable_value(
                content,
                target.variable_key_path,
                reference,
            )

        scan = scan_authored_markdown(
            source_id=reference,
            path=target.path,
            content=selected_content,
        )
        dependency_liquid_tags.update(scan.liquid_tags)
        dependency_template_variables.update(scan.template_variables)
        for nested_reference in scan.data_references:
            dependency_target(nested_reference)
            if nested_reference not in processed:
                heapq.heappush(pending, nested_reference)

    receipts: list[RenderDependencyFileReceipt] = []
    for path in sorted(content_by_path):
        content = content_by_path[path]
        target = target_by_path[path]
        receipts.append(
            RenderDependencyFileReceipt(
                path=path,
                media_type=target.media_type,
                observed_git_blob_sha1=_git_blob_sha1(content),
                content_sha256=hashlib.sha256(content).hexdigest(),
                byte_count=len(content),
                cache_path=_cache_dependency(repo_root, target, content),
                satisfied_references=tuple(sorted(references_by_path[path])),
            )
        )

    resolved = tuple(sorted(processed))
    direct_set = set(direct)
    reusable = tuple(sorted(ref for ref in resolved if ref.startswith("reusables.")))
    variables = tuple(sorted(ref for ref in resolved if ref.startswith("variables.")))
    authored_liquid_tags = {
        tag
        for document in audit.documents
        for tag in document.liquid_tags
    }
    authored_template_variables = {
        variable
        for document in audit.documents
        for variable in document.template_variables
    }

    return Phase3bRenderDependencyClosureCandidate(
        closure_version="phase3b-render-dependency-closure-candidate-v1",
        snapshot_id=audit.snapshot_id,
        source_render_audit_sha256=source_render_audit_sha256,
        direct_data_references=direct,
        resolved_data_references=resolved,
        transitive_data_references=tuple(sorted(set(resolved) - direct_set)),
        reusable_references=reusable,
        variable_references=variables,
        dependency_files=tuple(receipts),
        render_liquid_tags=tuple(
            sorted(authored_liquid_tags | dependency_liquid_tags)
        ),
        render_template_variables=tuple(
            sorted(authored_template_variables | dependency_template_variables)
        ),
        autotitle_count=sum(document.autotitle_count for document in audit.documents),
    )

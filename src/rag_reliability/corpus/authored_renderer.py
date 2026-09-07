"""Constrained deterministic renderer for the frozen Phase 3B authored corpus."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, model_validator

from rag_reliability.contracts.base import ContractModel, NonEmptyStr, Sha256
from rag_reliability.corpus.acquisition import git_blob_sha1
from rag_reliability.corpus.models import AcquisitionReceipt, CorpusSourceSelectionPlan
from rag_reliability.corpus.render_dependencies import dependency_target
from rag_reliability.corpus.render_dependency_freeze import Phase3bFrozenRenderDependencySet
from rag_reliability.corpus.render_policy import Phase3bRenderPolicyFreeze

_POLICY_MANIFEST_SHA256: Literal[
    "bad71a4e07f7f19ddbb9734c2ef7a822e890e36fa92e6336eb8b7ea9869b0d62"
] = "bad71a4e07f7f19ddbb9734c2ef7a822e890e36fa92e6336eb8b7ea9869b0d62"
_DEPENDENCY_MANIFEST_SHA256: Literal[
    "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
] = "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
_ACQUISITION_RECEIPT_SHA256: Literal[
    "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"
] = "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"

_DIRECTIVE_PATTERN = re.compile(r"(\{%-?.*?-?%\}|\{\{-?.*?-?\}\})", re.DOTALL)
_RAW_BLOCK_PATTERN = re.compile(
    r"\{%(?P<start_left>-)?\s*raw\s*(?P<start_right>-)?%\}"
    r"(?P<body>.*?)"
    r"\{%(?P<end_left>-)?\s*endraw\s*(?P<end_right>-)?%\}",
    re.DOTALL,
)
_TEMPLATE_PATTERN = re.compile(r"\{\{\s*-?\s*([^{}]+?)\s*-?\s*\}\}")
_AUTOTITLE_PATTERN = re.compile(r"\[AUTOTITLE\]\(([^)]+)\)")
_ACTIVE_LIQUID_PATTERN = re.compile(r"\{%.*?%\}", re.DOTALL)
_RAW_SENTINEL_PATTERN = re.compile(r"\x00RAG_RAW_(\d+)\x00")
_ALLOWED_RAW_TEMPLATE = "secrets.GITHUB_TOKEN"


class RenderErrorCode(StrEnum):
    """Stable failure classes for fail-closed authored rendering."""

    CACHE_IDENTITY_MISMATCH = "cache_identity_mismatch"
    MALFORMED_BLOCK = "malformed_block"
    MISSING_DATA_REFERENCE = "missing_data_reference"
    SECRET_RESOLUTION_FORBIDDEN = "secret_resolution_forbidden"
    UNFROZEN_TEMPLATE = "unfrozen_template"
    UNKNOWN_EXPRESSION = "unknown_expression"
    UNKNOWN_TAG = "unknown_tag"


class RenderContractError(ValueError):
    """Typed deterministic renderer failure."""

    def __init__(self, code: RenderErrorCode, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}")


@dataclass(frozen=True)
class _TextToken:
    text: str


@dataclass(frozen=True)
class _DirectiveToken:
    kind: Literal["tag", "template"]
    name: str
    argument: str


_Token = _TextToken | _DirectiveToken


@dataclass
class RenderStats:
    """Mutable internal counters emitted as immutable record metadata."""

    data_substitution_count: int = 0
    conditional_evaluation_count: int = 0
    iteration_count: int = 0
    variant_block_count: int = 0
    octicon_replacement_count: int = 0
    autotitle_replacement_count: int = 0
    preserved_raw_block_count: int = 0
    preserved_raw_literal_template_count: int = 0


class AuthoredRenderRecord(ContractModel):
    """Hash-only evidence for one rendered authored source document."""

    source_id: NonEmptyStr
    source_path: NonEmptyStr
    source_content_sha256: Sha256
    rendered_content_sha256: Sha256
    rendered_byte_count: int = Field(gt=0)
    data_substitution_count: int = Field(ge=0)
    conditional_evaluation_count: int = Field(ge=0)
    iteration_count: int = Field(ge=0)
    variant_block_count: int = Field(ge=0)
    octicon_replacement_count: int = Field(ge=0)
    autotitle_replacement_count: int = Field(ge=0)
    preserved_raw_block_count: int = Field(ge=0)
    preserved_raw_literal_template_count: int = Field(ge=0)
    active_unresolved_directive_count: Literal[0] = 0


class Phase3bAuthoredRenderCandidate(ContractModel):
    """Development-only evidence that the frozen renderer handles all ten docs."""

    candidate_version: Literal["phase3b-authored-render-candidate-v1"]
    snapshot_id: Literal["github_rest_v1_2026_09_05"]
    source_render_policy_manifest_sha256: Literal[
        "bad71a4e07f7f19ddbb9734c2ef7a822e890e36fa92e6336eb8b7ea9869b0d62"
    ]
    source_dependency_manifest_sha256: Literal[
        "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
    ]
    source_acquisition_receipt_sha256: Literal[
        "a1deb6580e10bdae3d21d1ca3abb81cc86241b0888e930ae153bfb99451eaae0"
    ]
    document_count: Literal[10] = 10
    unresolved_document_count: Literal[0] = 0
    active_unresolved_directive_count: Literal[0] = 0
    documents: tuple[AuthoredRenderRecord, ...] = Field(min_length=10, max_length=10)
    candidate_status: Literal["candidate_only"] = "candidate_only"
    renderer_validation_passed: Literal[True] = True
    normalization_authorized: Literal[False] = False
    full_ingestion_ready: Literal[False] = False
    chunking_authorized: Literal[False] = False
    baseline_authorized: Literal[False] = False
    release_eligible: Literal[False] = False

    @model_validator(mode="after")
    def validate_documents(self) -> Phase3bAuthoredRenderCandidate:
        ids = tuple(item.source_id for item in self.documents)
        if len(ids) != len(set(ids)):
            raise ValueError("authored render candidate contains duplicate source IDs")
        if tuple(sorted(ids)) != ids:
            raise ValueError("authored render candidate documents must be source-ID sorted")
        return self


def _normalize_argument(value: str) -> str:
    return " ".join(value.strip().split())


def _parse_directive(raw: str) -> _DirectiveToken:
    if raw.startswith("{%"):
        left = 3 if raw.startswith("{%-") else 2
        right = -3 if raw.endswith("-%}") else -2
        inner = raw[left:right].strip()
        if not inner:
            raise RenderContractError(RenderErrorCode.UNKNOWN_TAG, "empty Liquid tag")
        parts = inner.split(maxsplit=1)
        name = parts[0]
        argument = _normalize_argument(parts[1]) if len(parts) == 2 else ""
        return _DirectiveToken(kind="tag", name=name, argument=argument)

    left = 3 if raw.startswith("{{-") else 2
    right = -3 if raw.endswith("-}}") else -2
    expression = _normalize_argument(raw[left:right])
    if not expression:
        raise RenderContractError(RenderErrorCode.UNFROZEN_TEMPLATE, "empty template")
    return _DirectiveToken(kind="template", name="template", argument=expression)


def _protect_raw_blocks(text: str) -> tuple[str, dict[str, str], int, int]:
    pieces: list[str] = []
    protected: dict[str, str] = {}
    position = 0
    pending_right_trim = False
    raw_template_count = 0

    for index, match in enumerate(_RAW_BLOCK_PATTERN.finditer(text)):
        prefix = text[position : match.start()]
        if pending_right_trim:
            prefix = prefix.lstrip()
        if match.group("start_left"):
            prefix = prefix.rstrip()
        pieces.append(prefix)

        body = match.group("body")
        if match.group("start_right"):
            body = body.lstrip()
        if match.group("end_left"):
            body = body.rstrip()

        sentinel = f"\x00RAG_RAW_{index}\x00"
        if sentinel in text:
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                "raw sentinel collision in source text",
            )
        protected[sentinel] = body
        raw_template_count += sum(
            1
            for template in _TEMPLATE_PATTERN.findall(body)
            if _normalize_argument(template) == _ALLOWED_RAW_TEMPLATE
        )
        pieces.append(sentinel)
        pending_right_trim = bool(match.group("end_right"))
        position = match.end()

    tail = text[position:]
    if pending_right_trim:
        tail = tail.lstrip()
    pieces.append(tail)
    return "".join(pieces), protected, len(protected), raw_template_count


def _tokenize(text: str) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    position = 0
    pending_right_trim = False

    for match in _DIRECTIVE_PATTERN.finditer(text):
        raw = match.group(0)
        left_trim = raw.startswith(("{%-", "{{-"))
        right_trim = raw.endswith(("-%}", "-}}"))

        segment = text[position : match.start()]
        if pending_right_trim:
            segment = segment.lstrip()
        if left_trim:
            segment = segment.rstrip()
        if segment:
            tokens.append(_TextToken(segment))

        tokens.append(_parse_directive(raw))
        pending_right_trim = right_trim
        position = match.end()

    tail = text[position:]
    if pending_right_trim:
        tail = tail.lstrip()
    if tail:
        tokens.append(_TextToken(tail))
    return tuple(tokens)


def _selected_variable_value(content: bytes, reference: str) -> str:
    target = dependency_target(reference)
    current: object = yaml.safe_load(content.decode("utf-8"))
    for key in target.variable_key_path:
        if not isinstance(current, Mapping):
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"variable reference traverses non-mapping value: {reference}",
            )
        if key not in current:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"variable reference key does not exist: {reference}",
            )
        current = current[key]
    if isinstance(current, str):
        return current
    return yaml.safe_dump(current, sort_keys=True, allow_unicode=True)


def build_frozen_data_reference_map(
    repo_root: Path,
    frozen: Phase3bFrozenRenderDependencySet,
) -> dict[str, str]:
    """Load all 41 frozen data references while re-verifying cached bytes."""

    values: dict[str, str] = {}
    for dependency in frozen.dependency_files:
        content = (repo_root / dependency.cache_path).read_bytes()
        observed_sha256 = hashlib.sha256(content).hexdigest()
        observed_blob = git_blob_sha1(content)
        if observed_sha256 != dependency.content_sha256:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"SHA-256 mismatch: {dependency.path}",
            )
        if observed_blob != dependency.observed_git_blob_sha1:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"git blob mismatch: {dependency.path}",
            )

        for reference in dependency.satisfied_references:
            if reference in values:
                raise RenderContractError(
                    RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                    f"duplicate frozen data reference: {reference}",
                )
            if dependency.media_type == "markdown_reusable":
                values[reference] = content.decode("utf-8")
            else:
                values[reference] = _selected_variable_value(content, reference)

    if tuple(sorted(values)) != frozen.resolved_data_references:
        raise RenderContractError(
            RenderErrorCode.CACHE_IDENTITY_MISMATCH,
            "resolved data-reference map does not match frozen dependency manifest",
        )
    return values


class ConstrainedAuthoredRenderer:
    """Render only the exact syntax surface authorized by the frozen policy."""

    _KNOWN_TAGS = {
        "assign",
        "cli",
        "curl",
        "data",
        "else",
        "elsif",
        "endcli",
        "endcurl",
        "endfor",
        "endif",
        "endjavascript",
        "for",
        "if",
        "ifversion",
        "javascript",
        "octicon",
    }

    def __init__(
        self,
        policy: Phase3bRenderPolicyFreeze,
        data_references: dict[str, str],
    ) -> None:
        if policy.rendering_authorized is not True:
            raise ValueError("render policy does not authorize rendering")
        self._policy = policy
        self._data_references = dict(data_references)
        self._conditional_results: dict[str, bool] = {
            item.expression: item.result for item in policy.conditional_decisions
        }
        self._static_templates: dict[str, str | None] = {
            item.variable: item.static_value
            for item in policy.template_bindings
            if item.mode == "static"
        }
        self._allowed_templates: set[str] = {
            item.variable for item in policy.template_bindings
        }
        self._version_rows: dict[str, str] = {
            item.api_version: item.end_of_support for item in policy.api_version_rows
        }
        self._active_data_references: set[str] = set()

    def render(self, text: str) -> tuple[str, RenderStats]:
        """Render one authored Markdown document deterministically."""

        self._active_data_references.clear()
        stats = RenderStats()
        rendered = self._render_fragment(text, {}, stats)
        rendered, autotitle_count = _replace_autotitle(rendered)
        stats.autotitle_replacement_count += autotitle_count
        active_unresolved = count_active_unresolved_directives(rendered)
        if active_unresolved:
            raise RenderContractError(
                RenderErrorCode.UNKNOWN_EXPRESSION,
                f"rendered document contains {active_unresolved} unresolved directives",
            )
        return rendered, stats

    def _render_fragment(
        self,
        text: str,
        environment: dict[str, str],
        stats: RenderStats,
    ) -> str:
        protected_text, raw_blocks, raw_count, raw_template_count = _protect_raw_blocks(text)
        stats.preserved_raw_block_count += raw_count
        stats.preserved_raw_literal_template_count += raw_template_count
        tokens = _tokenize(protected_text)
        rendered, index, stop = self._parse_sequence(
            tokens,
            0,
            environment,
            stats,
            active=True,
            stop_names=frozenset(),
        )
        if stop is not None or index != len(tokens):
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                "unexpected terminal block marker",
            )
        return _restore_raw_blocks(rendered, raw_blocks)

    def _parse_sequence(
        self,
        tokens: tuple[_Token, ...],
        index: int,
        environment: dict[str, str],
        stats: RenderStats,
        *,
        active: bool,
        stop_names: frozenset[str],
    ) -> tuple[str, int, _DirectiveToken | None]:
        output: list[str] = []

        while index < len(tokens):
            token = tokens[index]
            if isinstance(token, _TextToken):
                if active:
                    output.append(token.text)
                index += 1
                continue

            if token.kind == "template":
                if active:
                    output.append(self._resolve_template(token.argument, environment))
                elif token.argument not in self._allowed_templates:
                    raise RenderContractError(
                        RenderErrorCode.UNFROZEN_TEMPLATE,
                        token.argument,
                    )
                index += 1
                continue

            if token.name in stop_names:
                return "".join(output), index, token
            if token.name not in self._KNOWN_TAGS:
                raise RenderContractError(RenderErrorCode.UNKNOWN_TAG, token.name)

            if token.name == "data":
                reference = token.argument.split()[0] if token.argument else ""
                if token.argument != reference:
                    raise RenderContractError(
                        RenderErrorCode.UNKNOWN_EXPRESSION,
                        f"data:{token.argument}",
                    )
                if not reference or reference not in self._data_references:
                    raise RenderContractError(
                        RenderErrorCode.MISSING_DATA_REFERENCE,
                        reference or "<empty>",
                    )
                if active:
                    output.append(self._render_data_reference(reference, environment, stats))
                    stats.data_substitution_count += 1
                index += 1
                continue

            if token.name == "assign":
                self._validate_assignment(token.argument)
                if active:
                    api_version = environment.get("apiVersion")
                    if api_version is None:
                        raise RenderContractError(
                            RenderErrorCode.UNKNOWN_EXPRESSION,
                            "versionData assignment outside API-version loop",
                        )
                    environment["versionData.end_of_support"] = self._version_rows[api_version]
                index += 1
                continue

            if token.name == "octicon":
                expected = '"code" aria-hidden="true" aria-label="code"'
                if token.argument != expected:
                    raise RenderContractError(
                        RenderErrorCode.UNKNOWN_EXPRESSION,
                        f"octicon:{token.argument}",
                    )
                if active:
                    output.append("code")
                    stats.octicon_replacement_count += 1
                index += 1
                continue

            if token.name in {"cli", "curl", "javascript"}:
                if token.argument:
                    raise RenderContractError(
                        RenderErrorCode.UNKNOWN_EXPRESSION,
                        f"{token.name}:{token.argument}",
                    )
                rendered, index = self._render_variant_block(
                    tokens,
                    index,
                    environment,
                    stats,
                    active=active,
                    block_name=token.name,
                )
                if active:
                    output.append(rendered)
                    stats.variant_block_count += 1
                continue

            if token.name in {"if", "ifversion"}:
                rendered, index = self._render_conditional_block(
                    tokens,
                    index,
                    environment,
                    stats,
                    active=active,
                    first=token,
                )
                if active:
                    output.append(rendered)
                continue

            if token.name == "for":
                rendered, index = self._render_for_block(
                    tokens,
                    index,
                    environment,
                    stats,
                    active=active,
                    token=token,
                )
                if active:
                    output.append(rendered)
                continue

            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                f"unexpected block marker: {token.name}",
            )

        if stop_names:
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                f"missing block terminator; expected one of {sorted(stop_names)}",
            )
        return "".join(output), index, None

    def _render_data_reference(
        self,
        reference: str,
        environment: dict[str, str],
        stats: RenderStats,
    ) -> str:
        if reference in self._active_data_references:
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                f"recursive data reference: {reference}",
            )
        self._active_data_references.add(reference)
        try:
            return self._render_fragment(
                self._data_references[reference],
                dict(environment),
                stats,
            )
        finally:
            self._active_data_references.remove(reference)

    def _render_variant_block(
        self,
        tokens: tuple[_Token, ...],
        index: int,
        environment: dict[str, str],
        stats: RenderStats,
        *,
        active: bool,
        block_name: str,
    ) -> tuple[str, int]:
        end_name = f"end{block_name}"
        rendered, stop_index, stop = self._parse_sequence(
            tokens,
            index + 1,
            environment,
            stats,
            active=active,
            stop_names=frozenset({end_name}),
        )
        if stop is None or stop.name != end_name or stop.argument:
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                f"malformed {block_name} block",
            )
        return rendered, stop_index + 1

    def _render_conditional_block(
        self,
        tokens: tuple[_Token, ...],
        index: int,
        environment: dict[str, str],
        stats: RenderStats,
        *,
        active: bool,
        first: _DirectiveToken,
    ) -> tuple[str, int]:
        condition = self._evaluate_condition(first.name, first.argument)
        stats.conditional_evaluation_count += int(active)
        taken = condition
        branch_active = active and condition
        rendered, stop_index, stop = self._parse_sequence(
            tokens,
            index + 1,
            dict(environment),
            stats,
            active=branch_active,
            stop_names=frozenset({"elsif", "else", "endif"}),
        )
        output = rendered if branch_active else ""

        while stop is not None and stop.name == "elsif":
            condition = self._evaluate_condition("elsif", stop.argument)
            stats.conditional_evaluation_count += int(active)
            branch_active = active and not taken and condition
            taken = taken or condition
            rendered, stop_index, stop = self._parse_sequence(
                tokens,
                stop_index + 1,
                dict(environment),
                stats,
                active=branch_active,
                stop_names=frozenset({"elsif", "else", "endif"}),
            )
            if branch_active:
                output += rendered

        if stop is not None and stop.name == "else":
            if stop.argument:
                raise RenderContractError(
                    RenderErrorCode.MALFORMED_BLOCK,
                    "else tag cannot have an argument",
                )
            branch_active = active and not taken
            rendered, stop_index, stop = self._parse_sequence(
                tokens,
                stop_index + 1,
                dict(environment),
                stats,
                active=branch_active,
                stop_names=frozenset({"endif"}),
            )
            if branch_active:
                output += rendered

        if stop is None or stop.name != "endif" or stop.argument:
            raise RenderContractError(
                RenderErrorCode.MALFORMED_BLOCK,
                f"missing endif for {first.name}",
            )
        return output, stop_index + 1

    def _render_for_block(
        self,
        tokens: tuple[_Token, ...],
        index: int,
        environment: dict[str, str],
        stats: RenderStats,
        *,
        active: bool,
        token: _DirectiveToken,
    ) -> tuple[str, int]:
        if token.argument != self._policy.iteration_expression:
            raise RenderContractError(
                RenderErrorCode.UNKNOWN_EXPRESSION,
                f"for:{token.argument}",
            )
        end_index = self._matching_endfor(tokens, index + 1)
        body = tokens[index + 1 : end_index]
        if not active:
            self._parse_sequence(
                body,
                0,
                dict(environment),
                stats,
                active=False,
                stop_names=frozenset(),
            )
            return "", end_index + 1

        output: list[str] = []
        for api_version in self._policy.supported_api_versions:
            loop_environment = dict(environment)
            loop_environment["apiVersion"] = api_version
            rendered, consumed, stop = self._parse_sequence(
                body,
                0,
                loop_environment,
                stats,
                active=True,
                stop_names=frozenset(),
            )
            if stop is not None or consumed != len(body):
                raise RenderContractError(
                    RenderErrorCode.MALFORMED_BLOCK,
                    "API-version loop body was not fully consumed",
                )
            output.append(rendered)
            stats.iteration_count += 1
        return "".join(output), end_index + 1

    @staticmethod
    def _matching_endfor(tokens: tuple[_Token, ...], start: int) -> int:
        depth = 1
        for index in range(start, len(tokens)):
            token = tokens[index]
            if not isinstance(token, _DirectiveToken) or token.kind != "tag":
                continue
            if token.name == "for":
                depth += 1
            elif token.name == "endfor":
                if token.argument:
                    raise RenderContractError(
                        RenderErrorCode.MALFORMED_BLOCK,
                        "endfor tag cannot have an argument",
                    )
                depth -= 1
                if depth == 0:
                    return index
        raise RenderContractError(RenderErrorCode.MALFORMED_BLOCK, "missing endfor")

    def _evaluate_condition(self, name: str, argument: str) -> bool:
        key = f"{name}:{argument}"
        if key not in self._conditional_results:
            raise RenderContractError(RenderErrorCode.UNKNOWN_EXPRESSION, key)
        return self._conditional_results[key]

    def _validate_assignment(self, argument: str) -> None:
        if argument != self._policy.assignment_expression:
            raise RenderContractError(
                RenderErrorCode.UNKNOWN_EXPRESSION,
                f"assign:{argument}",
            )

    def _resolve_template(self, expression: str, environment: dict[str, str]) -> str:
        if expression == _ALLOWED_RAW_TEMPLATE:
            raise RenderContractError(
                RenderErrorCode.SECRET_RESOLUTION_FORBIDDEN,
                expression,
            )
        if expression not in self._allowed_templates:
            raise RenderContractError(RenderErrorCode.UNFROZEN_TEMPLATE, expression)
        if expression in self._static_templates:
            value = self._static_templates[expression]
            if value is None:
                raise RenderContractError(RenderErrorCode.UNKNOWN_EXPRESSION, expression)
            return value
        if expression == "apiVersion":
            value = environment.get("apiVersion")
            if value is None:
                raise RenderContractError(
                    RenderErrorCode.UNKNOWN_EXPRESSION,
                    "apiVersion template outside loop",
                )
            return value
        if expression == 'versionData.end_of_support | default: "Not yet scheduled"':
            return environment.get("versionData.end_of_support", "Not yet scheduled")
        raise RenderContractError(RenderErrorCode.UNKNOWN_EXPRESSION, expression)


def _restore_raw_blocks(text: str, raw_blocks: dict[str, str]) -> str:
    for sentinel, body in raw_blocks.items():
        text = text.replace(sentinel, body)
    if _RAW_SENTINEL_PATTERN.search(text):
        raise RenderContractError(
            RenderErrorCode.MALFORMED_BLOCK,
            "unresolved raw sentinel",
        )
    return text


def _replace_autotitle(text: str) -> tuple[str, int]:
    count = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal count
        target = match.group(1).strip()
        if not target:
            raise RenderContractError(RenderErrorCode.UNKNOWN_EXPRESSION, "empty AUTOTITLE")
        count += 1
        return f"[{target}]({target})"

    return _AUTOTITLE_PATTERN.sub(replacement, text), count


def count_active_unresolved_directives(text: str) -> int:
    """Count unresolved active syntax while allowing the frozen raw secret literal."""

    liquid_count = len(_ACTIVE_LIQUID_PATTERN.findall(text))
    template_count = sum(
        1
        for expression in _TEMPLATE_PATTERN.findall(text)
        if _normalize_argument(expression) != _ALLOWED_RAW_TEMPLATE
    )
    autotitle_count = text.count("[AUTOTITLE]")
    return liquid_count + template_count + autotitle_count


def render_authored_sources(
    repo_root: Path,
    plan: CorpusSourceSelectionPlan,
    acquisition: AcquisitionReceipt,
    frozen: Phase3bFrozenRenderDependencySet,
    policy: Phase3bRenderPolicyFreeze,
) -> tuple[AuthoredRenderRecord, ...]:
    """Render the ten pinned authored sources and return hash-only evidence."""

    data_map = build_frozen_data_reference_map(repo_root, frozen)
    renderer = ConstrainedAuthoredRenderer(policy, data_map)
    receipt_by_source = {item.source_id: item for item in acquisition.files}
    records: list[AuthoredRenderRecord] = []

    for source in plan.files:
        if source.media_type != "markdown":
            continue
        receipt = receipt_by_source.get(source.source_id)
        if receipt is None:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"acquisition receipt missing source: {source.source_id}",
            )
        content = (repo_root / receipt.cache_path).read_bytes()
        observed_sha256 = hashlib.sha256(content).hexdigest()
        if observed_sha256 != receipt.content_sha256:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"authored SHA-256 mismatch: {source.source_id}",
            )
        if git_blob_sha1(content) != receipt.observed_git_blob_sha1:
            raise RenderContractError(
                RenderErrorCode.CACHE_IDENTITY_MISMATCH,
                f"authored git blob mismatch: {source.source_id}",
            )

        rendered, stats = renderer.render(content.decode("utf-8"))
        rendered_bytes = rendered.encode("utf-8")
        records.append(
            AuthoredRenderRecord(
                source_id=source.source_id,
                source_path=source.path,
                source_content_sha256=observed_sha256,
                rendered_content_sha256=hashlib.sha256(rendered_bytes).hexdigest(),
                rendered_byte_count=len(rendered_bytes),
                data_substitution_count=stats.data_substitution_count,
                conditional_evaluation_count=stats.conditional_evaluation_count,
                iteration_count=stats.iteration_count,
                variant_block_count=stats.variant_block_count,
                octicon_replacement_count=stats.octicon_replacement_count,
                autotitle_replacement_count=stats.autotitle_replacement_count,
                preserved_raw_block_count=stats.preserved_raw_block_count,
                preserved_raw_literal_template_count=(
                    stats.preserved_raw_literal_template_count
                ),
            )
        )

    ordered = tuple(sorted(records, key=lambda item: item.source_id))
    if len(ordered) != 10:
        raise ValueError("Phase 3B authored render requires exactly 10 documents")
    return ordered


def build_authored_render_candidate(
    documents: tuple[AuthoredRenderRecord, ...],
) -> Phase3bAuthoredRenderCandidate:
    """Build development-only render evidence after all ten documents pass."""

    return Phase3bAuthoredRenderCandidate(
        candidate_version="phase3b-authored-render-candidate-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        source_render_policy_manifest_sha256=_POLICY_MANIFEST_SHA256,
        source_dependency_manifest_sha256=_DEPENDENCY_MANIFEST_SHA256,
        source_acquisition_receipt_sha256=_ACQUISITION_RECEIPT_SHA256,
        documents=documents,
    )

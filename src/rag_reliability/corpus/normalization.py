"""Deterministic content normalization helpers for Phase 3B."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rag_reliability.corpus.models import HttpMethod

_HTTP_METHODS: tuple[HttpMethod, ...] = (
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "trace",
)


def canonical_json(value: object) -> str:
    """Serialize JSON-compatible data with stable ordering and separators."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    """Return the SHA-256 digest of UTF-8 text."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_markdown(source: str) -> str:
    """Normalize line endings and terminal whitespace without rewriting prose."""

    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).strip() + "\n"


def markdown_title(source: str, fallback: str) -> str:
    """Extract a deterministic human-readable title without interpreting Markdown."""

    lines = source.splitlines()
    for line in lines[:80]:
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            candidate = stripped.split(":", 1)[1].strip().strip("\"'")
            if candidate:
                return candidate
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and stripped[2:].strip():
            return stripped[2:].strip()
    return fallback


def resolve_local_json_pointer(root: Mapping[str, Any], ref: str) -> object:
    """Resolve one local OpenAPI JSON pointer without mutating the source document."""

    if not ref.startswith("#/"):
        raise ValueError(f"unsupported non-local OpenAPI reference: {ref}")

    current: object = root
    for raw_token in ref[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, Mapping):
            raise ValueError(f"OpenAPI reference traverses non-mapping value: {ref}")
        if token not in current:
            raise ValueError(f"OpenAPI reference target does not exist: {ref}")
        current = current[token]
    return current


def collect_local_reference_closure(
    root: Mapping[str, Any],
    seed: object,
) -> dict[str, object]:
    """Collect the transitive local `$ref` closure for one operation payload."""

    pending = [seed]
    observed: dict[str, object] = {}

    while pending:
        current = pending.pop()

        if isinstance(current, Mapping):
            ref = current.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/") and ref not in observed:
                resolved = resolve_local_json_pointer(root, ref)
                observed[ref] = resolved
                pending.append(resolved)

            pending.extend(current.values())
            continue

        if isinstance(current, list):
            pending.extend(current)

    return {key: observed[key] for key in sorted(observed)}


def normalize_openapi_operation(
    root: Mapping[str, Any],
    path: str,
    method: str,
) -> str:
    """Create stable operation content including path parameters and `$ref` closure."""

    paths = root.get("paths")
    if not isinstance(paths, Mapping):
        raise ValueError("OpenAPI document does not contain a mapping `paths` object")

    path_item = paths.get(path)
    if not isinstance(path_item, Mapping):
        raise ValueError(f"OpenAPI path does not exist: {path}")

    operation = path_item.get(method)
    if not isinstance(operation, Mapping):
        raise ValueError(f"OpenAPI operation does not exist: {method.upper()} {path}")

    payload = {
        "path": path,
        "method": method,
        "path_parameters": path_item.get("parameters", []),
        "operation": operation,
    }
    payload["referenced_components"] = collect_local_reference_closure(root, payload)
    return canonical_json(payload) + "\n"


def index_openapi_operations(
    root: Mapping[str, Any],
) -> dict[str, tuple[str, HttpMethod]]:
    """Index exact OpenAPI operation IDs to path/method identities."""

    paths = root.get("paths")
    if not isinstance(paths, Mapping):
        raise ValueError("OpenAPI document does not contain a mapping `paths` object")

    observed: dict[str, tuple[str, HttpMethod]] = {}
    for path, raw_path_item in paths.items():
        if not isinstance(path, str) or not isinstance(raw_path_item, Mapping):
            continue
        for method in _HTTP_METHODS:
            raw_operation = raw_path_item.get(method)
            if not isinstance(raw_operation, Mapping):
                continue
            operation_id = raw_operation.get("operationId")
            if not isinstance(operation_id, str) or not operation_id.strip():
                continue
            if operation_id in observed:
                raise ValueError(f"duplicate OpenAPI operationId: {operation_id}")
            observed[operation_id] = (path, method)
    return observed


def write_exact_text(path: Path, content: str) -> tuple[str, int]:
    """Materialize normalized text once and reject later byte drift."""

    encoded = content.encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise ValueError(f"existing normalized file does not match expected bytes: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded)

    observed = path.read_bytes()
    if observed != encoded:
        raise ValueError(f"normalized file failed post-write verification: {path}")
    return hashlib.sha256(observed).hexdigest(), len(observed)

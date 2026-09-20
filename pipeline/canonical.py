"""Deterministic canonical serialization and hashing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def canonical_json_bytes(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes used for contract identity."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_object(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump_canonical_yaml(value: Any) -> str:
    """Human-readable freeze format; hash identity always uses canonical JSON."""
    return yaml.safe_dump(value, sort_keys=True, allow_unicode=True, default_flow_style=False)

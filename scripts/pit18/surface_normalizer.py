"""Mechanical, semantics-preserving surface normalization for PIT-18."""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text or ""))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"^[ \t]*(?:[-*•‣▪]|\d+[.)])\s+", "", text, flags=re.M)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def textify(obj: Any) -> str:
    """Extract semantic text while ignoring identity/benchmark metadata."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return normalize_text(obj)
    if isinstance(obj, (int, float, bool)):
        return str(obj)
    if isinstance(obj, list):
        return normalize_text("\n".join(textify(x) for x in obj))
    if isinstance(obj, dict):
        if "teaching_signal" in obj and isinstance(obj["teaching_signal"], dict):
            return textify(obj["teaching_signal"])
        ignored = {
            "candidate_id", "scenario_id", "fixture_id", "scenario_type", "family",
            "expected_status", "expected_violation_classes", "rationale", "facts",
            "schema_status", "parse_status", "failure_classification", "confidence",
            "provenance", "version", "source", "timestamp", "freeze_date",
        }
        ordered = []
        preferred = (
            "content", "observation", "observations", "inference",
            "applicability_boundary", "revision_trigger", "evidence",
        )
        seen = set()
        for key in preferred:
            if key in obj:
                ordered.append(textify(obj[key]))
                seen.add(key)
        for key in sorted(obj):
            if key not in seen and key not in ignored:
                ordered.append(textify(obj[key]))
        return normalize_text("\n".join(x for x in ordered if x))
    return normalize_text(str(obj))


def sentences(text: str) -> list[str]:
    norm = normalize_text(text)
    return [x.strip() for x in re.split(r"(?<=[.!?;])\s+|\n+", norm) if x.strip()]

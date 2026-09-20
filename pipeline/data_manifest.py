"""Build and validate the M1 DataManifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from .canonical import sha256_object
from .data_policy import Finding
from .data_source import SourceSnapshot
from .errors import DataIntegrityError
from .loader import validate_mapping


def build_data_manifest(
    *,
    sources: Iterable[SourceSnapshot],
    split_contracts: dict[str, dict[str, Any]],
    token_streams: dict[str, dict[str, Any]],
    fixture_set_id: str,
    findings: Iterable[Finding],
) -> dict[str, Any]:
    source_entries = [source.manifest_entry() for source in sorted(sources, key=lambda item: item.dataset_id)]
    transforms = [
        {"stage": "normalize", "algorithm": "unicode-nfc-line-normalize-v1"},
        {"stage": "privacy", "algorithm": "regex-pii-v1"},
        {"stage": "secret", "algorithm": "regex-secret-v1"},
        {"stage": "exact_dedup", "algorithm": "sha256-normalized-bytes-v1"},
        {
            "stage": "near_dedup",
            "algorithm": "token-shingle-jaccard-v1",
            "parameters": {"shingle_size": 5, "threshold": 0.90, "representative": "lexicographic-identity"},
        },
        {
            "stage": "contamination",
            "algorithm": "normalized-substring-fixture-v1",
            "parameters": {"min_term_chars": 8},
        },
    ]
    split_entries = []
    split_ids = []
    for dataset_id, contract in sorted(split_contracts.items()):
        split_id = f"{dataset_id}:{contract['assignment_hash'][:16]}"
        split_ids.append(split_id)
        split_entries.append(
            {
                "dataset_id": dataset_id,
                "split_id": split_id,
                **contract,
            }
        )

    finding_summary: dict[str, int] = {}
    for finding in findings:
        key = f"{finding.stage}:{finding.category}:{finding.action}"
        finding_summary[key] = finding_summary.get(key, 0) + 1
    transforms.append({"stage": "finding_summary", "counts": dict(sorted(finding_summary.items()))})

    manifest: dict[str, Any] = {
        "manifest_version": "m1-data-manifest-v1",
        "sources": source_entries,
        "transforms": transforms,
        "splits": split_entries,
        "token_streams": dict(sorted(token_streams.items())),
        "freshness_registry": {
            "split_ids": split_ids,
            "fixture_set_ids": [fixture_set_id],
        },
    }
    manifest["manifest_hash"] = sha256_object(manifest)
    return manifest


def validate_data_manifest(manifest: dict[str, Any], repo_root: Path) -> None:
    schema_path = repo_root / "docs/model-training-pipeline/schemas/data_manifest.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DataIntegrityError(f"cannot load data manifest schema: {error}") from error
    Draft202012Validator.check_schema(schema)
    validate_mapping(manifest, schema, "DataManifest")
    expected = manifest.get("manifest_hash")
    payload = dict(manifest)
    payload.pop("manifest_hash", None)
    actual = sha256_object(payload)
    if expected != actual:
        raise DataIntegrityError(f"data manifest self hash mismatch: expected={expected} actual={actual}")

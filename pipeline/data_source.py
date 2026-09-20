"""M1 immutable source planning and local fixture acquisition."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .canonical import canonical_json_bytes, sha256_file, sha256_object
from .errors import DataIntegrityError
from .models import DatasetSpec

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class AcquiredDocument:
    dataset_id: str
    document_id: str
    content: str
    license: str
    metadata: Mapping[str, Any]

    @property
    def identity(self) -> str:
        return f"{self.dataset_id}:{self.document_id}"


@dataclass(frozen=True)
class SourceSnapshot:
    dataset_id: str
    source_id: str
    adapter: str
    snapshot: str
    content_sha256: str
    license_policy: str
    privacy_policy: str
    secret_scan_policy: str
    documents: tuple[AcquiredDocument, ...]

    def manifest_entry(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "adapter": self.adapter,
            "snapshot": self.snapshot,
            "content_sha256": self.content_sha256,
            "license_policy": self.license_policy,
            "privacy_policy": self.privacy_policy,
            "secret_scan_policy": self.secret_scan_policy,
        }


def plan_source(dataset: DatasetSpec) -> dict[str, Any]:
    raw = dict(dataset.raw)
    if dataset.adapter in {"fixture_text", "fixture_code", "fixture_reasoning"}:
        path = raw.get("path")
        if not path:
            raise DataIntegrityError(f"{dataset.name}: fixture adapter requires path")
        identity = {
            "adapter": dataset.adapter,
            "dataset_id": dataset.name,
            "snapshot": dataset.snapshot,
            "path": str(path),
        }
    elif dataset.adapter == "wikimedia_dump":
        required = ("project", "language", "dump_date", "artifact_type", "uri", "checksum_source_uri")
        missing = [name for name in required if not raw.get(name)]
        if missing:
            raise DataIntegrityError(f"{dataset.name}: missing Wikimedia identity fields {missing}")
        if "latest" in str(dataset.snapshot).lower() or "latest" in str(raw["uri"]).lower():
            raise DataIntegrityError(f"{dataset.name}: mutable Wikimedia 'latest' source is forbidden")
        identity = {
            "adapter": dataset.adapter,
            "dataset_id": dataset.name,
            "snapshot": dataset.snapshot,
            **{name: raw[name] for name in required},
        }
    elif dataset.adapter == "huggingface_dataset":
        required = ("dataset_id", "revision", "split")
        missing = [name for name in required if not raw.get(name)]
        if missing:
            raise DataIntegrityError(f"{dataset.name}: missing Hugging Face identity fields {missing}")
        if not _SHA40.fullmatch(str(raw["revision"])):
            raise DataIntegrityError(f"{dataset.name}: Hugging Face dataset revision must be immutable 40-hex SHA")
        identity = {
            "adapter": dataset.adapter,
            "dataset_id": dataset.name,
            "snapshot": dataset.snapshot,
            "hub_dataset_id": raw["dataset_id"],
            "revision": raw["revision"],
            "split": raw["split"],
        }
    else:
        raise DataIntegrityError(f"{dataset.name}: unsupported M1 adapter {dataset.adapter}")
    return {**identity, "source_identity_hash": sha256_object(identity)}


def acquire_local_dataset(dataset: DatasetSpec, repo_root: Path) -> SourceSnapshot:
    plan = plan_source(dataset)
    path_value = dataset.raw.get("path")
    if not path_value:
        raise DataIntegrityError(
            f"{dataset.name}: M1 offline qualification materializes only local paths; public source is planned but not downloaded"
        )
    path = (repo_root / str(path_value)).resolve()
    if not path.is_file():
        raise DataIntegrityError(f"{dataset.name}: source path missing: {path_value}")

    documents: list[AcquiredDocument] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise DataIntegrityError(f"{dataset.name}:{line_number}: invalid JSONL: {error}") from error
        if not isinstance(record, dict):
            raise DataIntegrityError(f"{dataset.name}:{line_number}: JSONL record must be object")
        document = _record_to_document(dataset, record, line_number)
        if document.document_id in seen_ids:
            raise DataIntegrityError(f"{dataset.name}: duplicate document id {document.document_id}")
        seen_ids.add(document.document_id)
        documents.append(document)

    if not documents:
        raise DataIntegrityError(f"{dataset.name}: acquired zero documents")

    source_hash = sha256_file(path)
    source_id = f"{dataset.name}:{plan['source_identity_hash'][:16]}:{source_hash[:16]}"
    is_code = dataset.adapter in {"fixture_code"}
    return SourceSnapshot(
        dataset_id=dataset.name,
        source_id=source_id,
        adapter=dataset.adapter,
        snapshot=dataset.snapshot,
        content_sha256=source_hash,
        license_policy="record-license-v1:deny-unknown-for-release",
        privacy_policy="regex-pii-v1:report-dev-quarantine-release",
        secret_scan_policy="regex-secret-v1:quarantine" if is_code else "regex-secret-v1:report",
        documents=tuple(documents),
    )


def _record_to_document(dataset: DatasetSpec, record: Mapping[str, Any], line_number: int) -> AcquiredDocument:
    document_id = str(record.get("id") or f"line-{line_number}")
    license_value = str(record.get("license") or "UNKNOWN")
    if dataset.adapter == "fixture_text":
        content = record.get("text")
        metadata = {"kind": "text"}
    elif dataset.adapter == "fixture_code":
        content = record.get("code")
        metadata = {"kind": "code", "language": record.get("language")}
    elif dataset.adapter == "fixture_reasoning":
        semantic = {
            "messages": record.get("messages"),
            "reasoning": record.get("reasoning"),
            "answer": record.get("answer"),
            "verifier": record.get("verifier"),
        }
        content = canonical_json_bytes(semantic).decode("utf-8")
        metadata = {"kind": "reasoning_semantic_envelope"}
    else:
        raise DataIntegrityError(f"{dataset.name}: local acquisition unsupported for adapter {dataset.adapter}")
    if not isinstance(content, str) or not content.strip():
        raise DataIntegrityError(f"{dataset.name}:{document_id}: empty content")
    return AcquiredDocument(
        dataset_id=dataset.name,
        document_id=document_id,
        content=content,
        license=license_value,
        metadata=metadata,
    )

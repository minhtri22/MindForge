"""M1 normalization, policy scanning, deduplication, contamination and split logic."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .canonical import sha256_object
from .data_source import AcquiredDocument
from .models import RunClass


@dataclass(frozen=True)
class ProcessedDocument:
    dataset_id: str
    document_id: str
    content: str
    content_hash: str
    license: str
    metadata: Mapping[str, object]
    split: str | None = None

    @property
    def identity(self) -> str:
        return f"{self.dataset_id}:{self.document_id}"


@dataclass(frozen=True)
class Finding:
    stage: str
    document_hash: str
    category: str
    action: str
    related_hash: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "document_hash": self.document_hash,
            "category": self.category,
            "action": self.action,
            "related_hash": self.related_hash,
        }


_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\s().-]?){9,15}(?!\d)")
_SECRET_PATTERNS = (
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("generic_secret", re.compile(r"(?i)\b(?:api[_-]?key|secret|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
)


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    value = unicodedata.normalize("NFC", value)
    lines = [line.rstrip() for line in value.split("\n")]
    return "\n".join(lines).strip()


def normalize_documents(documents: Iterable[AcquiredDocument]) -> list[ProcessedDocument]:
    result = []
    for document in documents:
        content = normalize_text(document.content)
        result.append(
            ProcessedDocument(
                dataset_id=document.dataset_id,
                document_id=document.document_id,
                content=content,
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                license=document.license,
                metadata=document.metadata,
            )
        )
    return result


def apply_policy(
    documents: Iterable[ProcessedDocument],
    run_class: RunClass,
) -> tuple[list[ProcessedDocument], list[Finding]]:
    accepted: list[ProcessedDocument] = []
    findings: list[Finding] = []
    for document in documents:
        quarantine = False
        if not document.license or document.license.upper() == "UNKNOWN":
            action = "quarantine" if run_class in {RunClass.CONFIRMATORY, RunClass.RELEASE} else "report"
            findings.append(Finding("license", document.content_hash, "unknown_license", action))
            quarantine = quarantine or action == "quarantine"

        pii_categories = []
        if _EMAIL.search(document.content):
            pii_categories.append("email")
        if _PHONE.search(document.content):
            pii_categories.append("phone")
        for category in pii_categories:
            action = "quarantine" if run_class is RunClass.RELEASE else "report"
            findings.append(Finding("privacy", document.content_hash, category, action))
            quarantine = quarantine or action == "quarantine"

        for category, pattern in _SECRET_PATTERNS:
            if pattern.search(document.content):
                findings.append(Finding("secret", document.content_hash, category, "quarantine"))
                quarantine = True

        if not quarantine:
            accepted.append(document)
    return accepted, findings


def exact_dedup(documents: Iterable[ProcessedDocument]) -> tuple[list[ProcessedDocument], list[Finding]]:
    kept: list[ProcessedDocument] = []
    findings: list[Finding] = []
    representatives: dict[str, ProcessedDocument] = {}
    for document in sorted(documents, key=lambda item: item.identity):
        representative = representatives.get(document.content_hash)
        if representative is None:
            representatives[document.content_hash] = document
            kept.append(document)
        else:
            findings.append(
                Finding("exact_dedup", document.content_hash, "exact_duplicate", "drop", representative.content_hash)
            )
    return kept, findings


def near_dedup(
    documents: Iterable[ProcessedDocument],
    *,
    shingle_size: int = 5,
    threshold: float = 0.90,
) -> tuple[list[ProcessedDocument], list[Finding]]:
    kept: list[ProcessedDocument] = []
    signatures: list[tuple[ProcessedDocument, frozenset[str]]] = []
    findings: list[Finding] = []
    for document in sorted(documents, key=lambda item: item.identity):
        signature = _shingles(document.content, shingle_size)
        duplicate_of: ProcessedDocument | None = None
        for representative, rep_signature in signatures:
            if _jaccard(signature, rep_signature) >= threshold:
                duplicate_of = representative
                break
        if duplicate_of is None:
            signatures.append((document, signature))
            kept.append(document)
        else:
            findings.append(
                Finding("near_dedup", document.content_hash, "near_duplicate", "drop", duplicate_of.content_hash)
            )
    return kept, findings


def contamination_terms(fixture_set: str, repo_root: Path) -> tuple[tuple[str, str], ...]:
    if not fixture_set.startswith("tests/"):
        return ()
    path = repo_root / fixture_set
    manifest = path / "manifest.json" if path.is_dir() else path
    if not manifest.is_file():
        return ()
    raw = json.loads(manifest.read_text(encoding="utf-8"))
    terms: dict[str, str] = {}
    for task in raw.get("tasks", []):
        if not isinstance(task, dict):
            continue
        for key in ("prompt", "expected", "text", "code"):
            value = task.get(key)
            if isinstance(value, str):
                normalized = normalize_text(value)
                if len(normalized) >= 8:
                    terms[hashlib.sha256(normalized.encode("utf-8")).hexdigest()] = normalized
    return tuple(sorted(terms.items()))


def apply_contamination(
    documents: Iterable[ProcessedDocument],
    terms: Iterable[tuple[str, str]],
    run_class: RunClass,
) -> tuple[list[ProcessedDocument], list[Finding]]:
    action = "quarantine" if run_class in {RunClass.CONFIRMATORY, RunClass.RELEASE} else "report"
    accepted: list[ProcessedDocument] = []
    findings: list[Finding] = []
    term_list = list(terms)
    for document in documents:
        contaminated = False
        for term_hash, term in term_list:
            if term in document.content:
                findings.append(Finding("contamination", document.content_hash, "eval_overlap", action, term_hash))
                contaminated = True
        if not contaminated or action != "quarantine":
            accepted.append(document)
    return accepted, findings


def assign_splits(
    documents: Iterable[ProcessedDocument],
    split_seed: int,
) -> tuple[list[ProcessedDocument], dict[str, object]]:
    assigned: list[ProcessedDocument] = []
    counts = {"train": 0, "validation": 0, "test": 0}
    identities: list[dict[str, str]] = []
    for document in sorted(documents, key=lambda item: item.identity):
        digest = hashlib.sha256(
            f"{split_seed}\0{document.dataset_id}\0{document.document_id}".encode("utf-8")
        ).hexdigest()
        bucket = int(digest[:8], 16) % 10_000
        split = "train" if bucket < 8_000 else "validation" if bucket < 9_000 else "test"
        counts[split] += 1
        identities.append({"document_hash": document.content_hash, "split": split})
        assigned.append(
            ProcessedDocument(
                dataset_id=document.dataset_id,
                document_id=document.document_id,
                content=document.content,
                content_hash=document.content_hash,
                license=document.license,
                metadata=document.metadata,
                split=split,
            )
        )
    contract = {
        "algorithm": "sha256-bucket-v1",
        "seed": split_seed,
        "thresholds": {"train": 8000, "validation": 9000, "test": 10000},
        "counts": counts,
        "assignment_hash": sha256_object(identities),
    }
    return assigned, contract


def _words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", value.lower())


def _shingles(value: str, size: int) -> frozenset[str]:
    words = _words(value)
    if len(words) < size:
        return frozenset(words)
    return frozenset("\u241f".join(words[index : index + size]) for index in range(len(words) - size + 1))


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0

"""M6 F16 parent existing-byte recovery/materialization tooling.

This module only admits already-existing serialized F16 bytes. It does not
regenerate F16, invoke the HF-to-GGUF conversion path, run llama-cli, evaluate
fixtures, perform model inference, or change scientific adjudication.

All byte-mutating/materialization functions require a separate future execution
authorization. The CLI in this implementation stage is planning-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROGRAM = "M6_F16_PARENT_ARTIFACT_RECOVERY_MATERIALIZATION"

F16_FILENAME = "model-f16.gguf"
F16_SIZE = 994156384
F16_SHA256 = "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b"
F16_MANIFEST = "eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8"
F16_RESULT_HASH = "0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57"

RECONSTRUCTION_AUTH_COMMIT = "9506e5fc205e641aba942a0bc9ff2fbaa7d881a5"
RECONSTRUCTION_AUTH_BLOB = "f26754440d710904f45eb1d7916d334484f43bb5"

FUTURE_EXECUTION_AUTH_SCHEMA = (
    "mindforge-model-pipeline-m6-f16-parent-artifact-"
    "recovery-materialization-execution-authorization-v1"
)
FUTURE_EXECUTION_AUTH_STATUS = "AUTHORIZED_ONE_F16_EXISTING_BYTE_MATERIALIZATION"


class F16MaterializationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ArtifactIdentity:
    filename: str
    size: int
    sha256: str
    aggregate_manifest_hash: str
    label: str


F16_IDENTITY = ArtifactIdentity(
    filename=F16_FILENAME,
    size=F16_SIZE,
    sha256=F16_SHA256,
    aggregate_manifest_hash=F16_MANIFEST,
    label="f16",
)


def canonical_json_bytes(value: Any) -> bytes:
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


def single_file_manifest(path: Path, label: str) -> dict[str, Any]:
    row = {
        "name": path.name,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    files = [row]
    return {
        "label": label,
        "topology": "single_file",
        "files": files,
        "aggregate_hash": sha256_object(files),
    }


def inspect_artifact(
    path: Path,
    expected: ArtifactIdentity = F16_IDENTITY,
) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": str(path),
            "exists": False,
            "admitted": False,
            "reason": "NOT_FOUND",
        }

    size = path.stat().st_size
    sha = sha256_file(path)
    manifest = single_file_manifest(path, expected.label)
    checks = {
        "filename_exact": path.name == expected.filename,
        "size_exact": size == expected.size,
        "sha256_exact": sha == expected.sha256,
        "aggregate_manifest_exact": (
            manifest["aggregate_hash"] == expected.aggregate_manifest_hash
        ),
    }
    admitted = all(checks.values())
    return {
        "path": str(path.resolve()),
        "exists": True,
        "filename": path.name,
        "size": size,
        "sha256": sha,
        "aggregate_manifest_hash": manifest["aggregate_hash"],
        "checks": checks,
        "admitted": admitted,
        "reason": "EXACT_IDENTITY" if admitted else "IDENTITY_MISMATCH",
    }


def discover_existing(
    candidates: Iterable[Path],
    expected: ArtifactIdentity = F16_IDENTITY,
) -> dict[str, Any]:
    inspected: list[dict[str, Any]] = []
    for candidate in candidates:
        result = inspect_artifact(Path(candidate), expected)
        inspected.append(result)
        if result["admitted"]:
            return {
                "classification": "ADMITTED_EXISTING_F16_BYTES",
                "source": result,
                "inspected": inspected,
                "f16_scientific_status": "PASS_CLOSED",
                "f16_regeneration_executed": False,
            }
    classification = (
        "F16_EXISTING_BYTES_IDENTITY_MISMATCH"
        if any(item.get("exists") for item in inspected)
        else "F16_EXISTING_BYTES_NOT_FOUND"
    )
    return {
        "classification": classification,
        "source": None,
        "inspected": inspected,
        "f16_scientific_status": "PASS_CLOSED",
        "f16_regeneration_executed": False,
    }


def load_execution_authorization(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise F16MaterializationError(
            "F16 materialization execution is not authorized: authorization missing"
        )
    auth = json.loads(path.read_text(encoding="utf-8"))
    if auth.get("schema") != FUTURE_EXECUTION_AUTH_SCHEMA:
        raise F16MaterializationError("F16 execution authorization schema mismatch")
    if auth.get("status") != FUTURE_EXECUTION_AUTH_STATUS:
        raise F16MaterializationError("F16 materialization execution is not authorized")
    if auth.get("program") != PROGRAM:
        raise F16MaterializationError("F16 materialization program mismatch")
    expected = auth.get("expected_f16", {})
    if expected.get("filename") != F16_FILENAME:
        raise F16MaterializationError("F16 filename authorization drift")
    if int(expected.get("size_bytes", -1)) != F16_SIZE:
        raise F16MaterializationError("F16 size authorization drift")
    if expected.get("sha256") != F16_SHA256:
        raise F16MaterializationError("F16 SHA256 authorization drift")
    if expected.get("aggregate_manifest_hash") != F16_MANIFEST:
        raise F16MaterializationError("F16 manifest authorization drift")

    boundaries = auth.get("boundaries", {})
    required_false = (
        "f16_regeneration",
        "hf_to_gguf_conversion",
        "llama_cli_evaluation",
        "fixture_evaluation",
        "model_inference",
        "scientific_adjudication",
        "q4_reconstruction_execution",
        "ollama_create",
        "ollama_chat",
    )
    for field in required_false:
        if boundaries.get(field) is not False:
            raise F16MaterializationError(
                f"authorization illegally opens boundary: {field}"
            )

    if auth.get("reconstruction_authorization_commit") != RECONSTRUCTION_AUTH_COMMIT:
        raise F16MaterializationError("Q4 reconstruction authorization commit drift")
    if auth.get("reconstruction_authorization_consumed") is not False:
        raise F16MaterializationError("Q4 reconstruction authorization is not unconsumed")
    return auth


def persist_existing_file(
    source: Path,
    destination: Path,
    *,
    execution_authorization: Path,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)
    source_result = inspect_artifact(source)
    if not source_result["admitted"]:
        raise F16MaterializationError("source is not exact frozen F16 identity")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    persisted = inspect_artifact(destination)
    if not persisted["admitted"]:
        raise F16MaterializationError("persisted F16 copy failed exact reverification")

    return {
        "classification": "ADMITTED_EXISTING_F16_BYTES",
        "materialization_mode": "COPY_EXISTING_FILE",
        "source": source_result,
        "persisted": persisted,
        "f16_scientific_status": "PASS_CLOSED",
        "f16_regeneration_executed": False,
        "scientific_adjudication_executed": False,
    }


def download_existing_object(
    url: str,
    destination: Path,
    *,
    execution_authorization: Path,
    source_object_sha256: str | None = None,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)

    source_digest = sha256_file(destination)
    if source_object_sha256 is not None and source_digest != source_object_sha256:
        destination.unlink(missing_ok=True)
        raise F16MaterializationError("downloaded source object digest mismatch")

    admitted = inspect_artifact(destination)
    if not admitted["admitted"]:
        destination.unlink(missing_ok=True)
        raise F16MaterializationError("downloaded object is not exact frozen F16")

    return {
        "classification": "ADMITTED_EXISTING_F16_BYTES",
        "materialization_mode": "DOWNLOAD_EXISTING_OBJECT",
        "source_url": url,
        "source_object_sha256": source_digest,
        "persisted": admitted,
        "f16_scientific_status": "PASS_CLOSED",
        "f16_regeneration_executed": False,
        "scientific_adjudication_executed": False,
    }


def extract_existing_archive_member(
    archive: Path,
    member: str,
    destination: Path,
    *,
    execution_authorization: Path,
    archive_sha256: str | None = None,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)
    if archive_sha256 is not None and sha256_file(archive) != archive_sha256:
        raise F16MaterializationError("archive digest mismatch")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        if member not in names:
            raise F16MaterializationError("F16 archive member not found")
        info = zf.getinfo(member)
        if info.is_dir():
            raise F16MaterializationError("F16 archive member is a directory")
        with zf.open(info, "r") as src, destination.open("wb") as out:
            shutil.copyfileobj(src, out)

    admitted = inspect_artifact(destination)
    if not admitted["admitted"]:
        destination.unlink(missing_ok=True)
        raise F16MaterializationError(
            "extracted archive member is not exact frozen F16"
        )
    return {
        "classification": "ADMITTED_EXISTING_F16_BYTES",
        "materialization_mode": "EXTRACT_EXISTING_ARCHIVE_MEMBER",
        "archive": str(archive.resolve()),
        "archive_sha256": sha256_file(archive),
        "member": member,
        "persisted": admitted,
        "f16_scientific_status": "PASS_CLOSED",
        "f16_regeneration_executed": False,
        "scientific_adjudication_executed": False,
    }


def reassemble_existing_chunks(
    chunks: Sequence[Path],
    destination: Path,
    *,
    execution_authorization: Path,
    expected_chunk_sha256: Sequence[str] | None = None,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)
    if not chunks:
        raise F16MaterializationError("no F16 chunks supplied")
    if expected_chunk_sha256 is not None and len(expected_chunk_sha256) != len(chunks):
        raise F16MaterializationError("chunk digest count mismatch")

    records: list[dict[str, Any]] = []
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as out:
        for index, chunk in enumerate(chunks):
            if not chunk.is_file():
                destination.unlink(missing_ok=True)
                raise F16MaterializationError(f"missing chunk: {chunk}")
            digest = sha256_file(chunk)
            if expected_chunk_sha256 is not None:
                if digest != expected_chunk_sha256[index]:
                    destination.unlink(missing_ok=True)
                    raise F16MaterializationError(
                        f"chunk digest mismatch at index {index}"
                    )
            records.append(
                {
                    "index": index,
                    "path": str(chunk.resolve()),
                    "size": chunk.stat().st_size,
                    "sha256": digest,
                }
            )
            with chunk.open("rb") as src:
                shutil.copyfileobj(src, out)

    admitted = inspect_artifact(destination)
    if not admitted["admitted"]:
        destination.unlink(missing_ok=True)
        raise F16MaterializationError(
            "reassembled chunks are not exact frozen F16"
        )

    return {
        "classification": "ADMITTED_EXISTING_F16_BYTES",
        "materialization_mode": "REASSEMBLE_EXISTING_CHUNKS",
        "chunks": records,
        "persisted": admitted,
        "f16_scientific_status": "PASS_CLOSED",
        "f16_regeneration_executed": False,
        "scientific_adjudication_executed": False,
    }


def planning_report(candidates: Sequence[Path]) -> dict[str, Any]:
    discovery = discover_existing(candidates)
    return {
        "schema": "mindforge-m6-f16-parent-materialization-plan-v1",
        "program": PROGRAM,
        "discovery": discovery,
        "execution_authorized_now": False,
        "requires_separate_execution_authorization": True,
        "allowed_future_modes": [
            "COPY_EXISTING_FILE",
            "DOWNLOAD_EXISTING_OBJECT",
            "EXTRACT_EXISTING_ARCHIVE_MEMBER",
            "REASSEMBLE_EXISTING_CHUNKS",
        ],
        "frozen_f16": {
            "filename": F16_FILENAME,
            "size_bytes": F16_SIZE,
            "sha256": F16_SHA256,
            "aggregate_manifest_hash": F16_MANIFEST,
            "scientific_status": "PASS_CLOSED",
        },
        "protected_reconstruction_authorization": {
            "commit": RECONSTRUCTION_AUTH_COMMIT,
            "git_blob_sha1": RECONSTRUCTION_AUTH_BLOB,
            "consumed": False,
        },
        "boundaries": {
            "f16_regeneration_authorized": False,
            "hf_to_gguf_conversion_authorized": False,
            "llama_cli_evaluation_authorized": False,
            "fixture_evaluation_authorized": False,
            "model_inference_authorized": False,
            "scientific_adjudication_authorized": False,
            "q4_reconstruction_execution_authorized": False,
            "ollama_create_authorized": False,
            "ollama_chat_authorized": False,
            "m6_scientific_execution_authorized": False,
            "m7_authorized": False,
            "bulk_training_authorized": False,
        },
        "next_action": (
            "OPEN_SEPARATE_F16_MATERIALIZATION_EXECUTION_AUTHORIZATION_AFTER_ZERO_SCIENCE_PASS"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = planning_report([Path(value) for value in args.candidate])
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["next_action"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

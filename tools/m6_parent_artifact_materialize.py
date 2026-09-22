"""M6 parent-artifact recovery/materialization tooling.

This module is deliberately independent from the M5Q scientific runner.
It may inspect/recover existing bytes and, only under a separate execution
authorization, reconstruct Q4 bytes from an already-verified frozen F16 parent
using the exact Q4_K_M quantizer command.

It never evaluates task fixtures, never runs a model for inference, and never
emits or adjudicates an M5Q scientific result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROGRAM = "M6_PARENT_ARTIFACT_MATERIALIZATION"

Q4_FILENAME = "model-q4_k_m.gguf"
Q4_SIZE = 397807456
Q4_SHA256 = "ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977"
Q4_MANIFEST = "e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b"
Q4_TARGET_KEY = "q4_k_m"
Q4_QUANTIZER_TYPE = "Q4_K_M"

F16_FILENAME = "model-f16.gguf"
F16_SIZE = 994156384
F16_SHA256 = "437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b"
F16_MANIFEST = "eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8"

Q4_SCIENTIFIC_IMPLEMENTATION_COMMIT = "97d7dad329aa0196ead9005e631eebbeb8aa2163"
Q4_IMPLEMENTATION_LOCK_COMMIT = "87bc09f479c5fd6ba3e3ec3725d859ed5ad9feb1"
LLAMA_CPP_COMMIT = "ce8caa6e60a03093351d6016a818720e0d46f0fb"

EXECUTION_AUTH_PATH = Path(
    "artifacts/model-training-pipeline/m6/parent_artifact/EXECUTION_AUTHORIZATION.json"
)


class MaterializationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ArtifactIdentity:
    filename: str
    size: int
    sha256: str
    aggregate_manifest_hash: str
    label: str


Q4_IDENTITY = ArtifactIdentity(
    filename=Q4_FILENAME,
    size=Q4_SIZE,
    sha256=Q4_SHA256,
    aggregate_manifest_hash=Q4_MANIFEST,
    label=Q4_TARGET_KEY,
)

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


def inspect_artifact(path: Path, expected: ArtifactIdentity) -> dict[str, Any]:
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
    name_ok = path.name == expected.filename
    size_ok = size == expected.size
    sha_ok = sha == expected.sha256
    manifest_ok = manifest["aggregate_hash"] == expected.aggregate_manifest_hash

    return {
        "path": str(path.resolve()),
        "exists": True,
        "filename": path.name,
        "size": size,
        "sha256": sha,
        "aggregate_manifest_hash": manifest["aggregate_hash"],
        "checks": {
            "filename_exact": name_ok,
            "size_exact": size_ok,
            "sha256_exact": sha_ok,
            "aggregate_manifest_exact": manifest_ok,
        },
        "admitted": name_ok and size_ok and sha_ok and manifest_ok,
        "reason": (
            "EXACT_IDENTITY"
            if name_ok and size_ok and sha_ok and manifest_ok
            else "IDENTITY_MISMATCH"
        ),
    }


def recover_existing(
    candidates: Iterable[Path],
    expected: ArtifactIdentity = Q4_IDENTITY,
) -> dict[str, Any]:
    inspected: list[dict[str, Any]] = []
    for candidate in candidates:
        result = inspect_artifact(Path(candidate), expected)
        inspected.append(result)
        if result["admitted"]:
            return {
                "classification": "ADMITTED_EXISTING_BYTES",
                "source": result,
                "inspected": inspected,
                "q4_scientific_status": "PASS_CLOSED",
                "q4_rerun_authorized": False,
            }
    return {
        "classification": "NOT_FOUND_RECOVERY_EXHAUSTED",
        "source": None,
        "inspected": inspected,
        "q4_scientific_status": "PASS_CLOSED",
        "q4_rerun_authorized": False,
    }


def build_reconstruction_command(
    llama_quantize: Path,
    frozen_f16: Path,
    output_q4: Path,
) -> list[str]:
    return [
        str(llama_quantize),
        str(frozen_f16),
        str(output_q4),
        Q4_QUANTIZER_TYPE,
    ]


def load_execution_authorization(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise MaterializationError(
            "materialization execution is not authorized: authorization file missing"
        )
    auth = json.loads(path.read_text(encoding="utf-8"))
    if auth.get("schema") != (
        "mindforge-model-pipeline-m6-parent-artifact-execution-authorization-v1"
    ):
        raise MaterializationError("materialization execution authorization schema mismatch")
    if auth.get("status") != "AUTHORIZED_ONE_MATERIALIZATION_EXECUTION":
        raise MaterializationError("materialization execution is not authorized")
    if auth.get("program") != PROGRAM:
        raise MaterializationError("materialization execution program mismatch")
    boundary = auth.get("boundaries", {})
    if boundary.get("q4_scientific_rerun") is not False:
        raise MaterializationError("authorization illegally reopens Q4 science")
    if boundary.get("q4_fixture_evaluation") is not False:
        raise MaterializationError("authorization illegally permits Q4 fixture evaluation")
    if boundary.get("scientific_adjudication") is not False:
        raise MaterializationError("authorization illegally permits scientific adjudication")
    if boundary.get("ollama_create") is not False:
        raise MaterializationError("authorization illegally permits Ollama create")
    if auth.get("expected_q4_sha256") != Q4_SHA256:
        raise MaterializationError("authorization Q4 SHA256 drifted")
    if int(auth.get("expected_q4_size", -1)) != Q4_SIZE:
        raise MaterializationError("authorization Q4 size drifted")
    return auth


def persist_admitted_existing(
    source: Path,
    destination: Path,
    *,
    execution_authorization: Path,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)
    source_result = inspect_artifact(source, Q4_IDENTITY)
    if not source_result["admitted"]:
        raise MaterializationError("existing Q4 candidate is not exact frozen identity")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination_result = inspect_artifact(destination, Q4_IDENTITY)
    if not destination_result["admitted"]:
        raise MaterializationError("persisted Q4 copy failed exact identity verification")
    return {
        "classification": "ADMITTED_EXISTING_BYTES",
        "source": source_result,
        "persisted": destination_result,
        "q4_scientific_status": "PASS_CLOSED",
        "q4_rerun_authorized": False,
        "scientific_adjudication_executed": False,
    }


def execute_reconstruction(
    *,
    frozen_f16: Path,
    llama_quantize: Path,
    output_q4: Path,
    execution_authorization: Path,
) -> dict[str, Any]:
    load_execution_authorization(execution_authorization)

    f16 = inspect_artifact(frozen_f16, F16_IDENTITY)
    if not f16["admitted"]:
        raise MaterializationError("frozen F16 parent artifact is unavailable or mismatched")
    if not llama_quantize.is_file():
        raise MaterializationError("llama quantizer executable is unavailable")

    command = build_reconstruction_command(llama_quantize, frozen_f16, output_q4)
    output_q4.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )
    reconstructed = inspect_artifact(output_q4, Q4_IDENTITY) if output_q4.exists() else {
        "exists": False,
        "admitted": False,
        "reason": "NOT_CREATED",
        "path": str(output_q4),
    }

    if completed.returncode != 0:
        classification = "INVALID_INFRASTRUCTURE"
    elif reconstructed["admitted"]:
        classification = "ADMITTED_DETERMINISTIC_RECONSTRUCTION"
    else:
        classification = "RECONSTRUCTION_IDENTITY_MISMATCH"

    return {
        "classification": classification,
        "command": command,
        "command_hash": sha256_object(command),
        "quantizer_return_code": completed.returncode,
        "quantizer_stdout_sha256": hashlib.sha256(
            completed.stdout.encode("utf-8")
        ).hexdigest(),
        "quantizer_stderr_sha256": hashlib.sha256(
            completed.stderr.encode("utf-8")
        ).hexdigest(),
        "f16_parent": f16,
        "reconstructed": reconstructed,
        "q4_scientific_status": "PASS_CLOSED",
        "q4_rerun_authorized": False,
        "fixture_evaluation_executed": False,
        "model_inference_executed": False,
        "scientific_adjudication_executed": False,
        "ollama_create_executed": False,
        "ollama_chat_executed": False,
        "m7_authorized": False,
        "bulk_training_authorized": False,
    }


def plan(
    candidates: Sequence[Path],
    *,
    frozen_f16: Path | None = None,
    llama_quantize: Path | None = None,
) -> dict[str, Any]:
    recovery = recover_existing(candidates)
    if recovery["classification"] == "ADMITTED_EXISTING_BYTES":
        next_action = "PERSIST_EXACT_EXISTING_BYTES_AFTER_EXECUTION_AUTHORIZATION"
    elif frozen_f16 is not None and llama_quantize is not None:
        f16 = inspect_artifact(frozen_f16, F16_IDENTITY)
        next_action = (
            "EXECUTE_DETERMINISTIC_RECONSTRUCTION_AFTER_EXECUTION_AUTHORIZATION"
            if f16["admitted"] and llama_quantize.is_file()
            else "RECOVER_EXACT_F16_OR_Q4_BYTES"
        )
    else:
        next_action = "RECOVER_EXACT_Q4_OR_F16_BYTES"

    return {
        "schema": "mindforge-m6-parent-artifact-materialization-plan-v1",
        "program": PROGRAM,
        "recovery": recovery,
        "reconstruction": {
            "authorized_now": False,
            "requires_separate_execution_authorization": True,
            "scientific_implementation_commit": Q4_SCIENTIFIC_IMPLEMENTATION_COMMIT,
            "q4_implementation_lock_commit": Q4_IMPLEMENTATION_LOCK_COMMIT,
            "llama_cpp_commit": LLAMA_CPP_COMMIT,
            "quantizer_type": Q4_QUANTIZER_TYPE,
        },
        "boundaries": {
            "q4_scientific_status": "PASS_CLOSED",
            "q4_rerun_authorized": False,
            "fixture_evaluation_authorized": False,
            "model_inference_authorized": False,
            "scientific_adjudication_authorized": False,
            "ollama_create_authorized": False,
            "ollama_chat_authorized": False,
            "m7_authorized": False,
            "bulk_training_authorized": False,
        },
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--frozen-f16")
    parser.add_argument("--llama-quantize")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = plan(
        [Path(value) for value in args.candidate],
        frozen_f16=Path(args.frozen_f16) if args.frozen_f16 else None,
        llama_quantize=Path(args.llama_quantize) if args.llama_quantize else None,
    )
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["next_action"])

    # CLI is planning-only until a separate execution authorization is committed.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

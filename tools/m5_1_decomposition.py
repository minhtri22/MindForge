"""M5.1 preregistered canonical tokenizer export fidelity decomposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download

from pipeline.canonical import sha256_file, sha256_object
from pipeline.loader import load_experiment_config
from pipeline.m2 import run_m2_qualification


TOKENIZER_PATTERNS = (
    "tokenizer*",
    "vocab*",
    "merges*",
    "special_tokens_map.json",
    "added_tokens.json",
    "*.model",
    "chat_template*.jinja",
)


def is_tokenizer_asset(path: str | Path) -> bool:
    name = Path(path).name.lower()
    return (
        name.startswith("tokenizer")
        or name.startswith("vocab")
        or name.startswith("merges")
        or name in {"special_tokens_map.json", "added_tokens.json"}
        or name.endswith(".model")
        or (name.startswith("chat_template") and name.endswith(".jinja"))
    )


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def file_manifest(root: Path, *, tokenizer_only: bool | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        classified = is_tokenizer_asset(rel)
        if tokenizer_only is True and not classified:
            continue
        if tokenizer_only is False and classified:
            continue
        rows.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def clone_with_hardlinks(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)

    def copy_link(src: str, dst: str) -> str:
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        return dst

    shutil.copytree(source, target, copy_function=copy_link)


def replace_tokenizer_assets_from_source(*, arm_b: Path, source_snapshot: Path) -> list[dict[str, Any]]:
    for path in sorted(arm_b.rglob("*"), reverse=True):
        if path.is_file() and is_tokenizer_asset(path.relative_to(arm_b)):
            path.unlink()
    source_assets = file_manifest(source_snapshot, tokenizer_only=True)
    if not source_assets:
        raise RuntimeError("pinned source snapshot contains zero tokenizer assets")
    for row in source_assets:
        src = source_snapshot / row["path"]
        dst = arm_b / row["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    copied = file_manifest(arm_b, tokenizer_only=True)
    if copied != source_assets:
        raise RuntimeError("arm B tokenizer assets are not byte-identical to pinned source snapshot")
    return copied


def inspect_tokenizer(*, converter_python: Path, probe_script: Path, model_dir: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [str(converter_python), str(probe_script), "--model-dir", str(model_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"tokenizer probe failed rc={completed.returncode}: {completed.stderr[-2000:]}"
        )
    value = json.loads(completed.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("tokenizer probe must return an object")
    return value


def run_conversion(
    *,
    converter_python: Path,
    converter: Path,
    llama_source: Path,
    model_dir: Path,
    output_path: Path,
    outtype: str,
) -> dict[str, Any]:
    command = [
        str(converter_python),
        str(converter),
        str(model_dir),
        "--outtype",
        outtype,
        "--outfile",
        str(output_path),
    ]
    completed = subprocess.run(
        command,
        cwd=llama_source,
        text=True,
        capture_output=True,
        check=False,
    )
    exists = output_path.is_file() and output_path.stat().st_size > 0
    passed = completed.returncode == 0 and exists
    result: dict[str, Any] = {
        "command_shape": [
            "<converter_python>",
            "<converter>",
            "<arm_model_dir>",
            "--outtype",
            outtype,
            "--outfile",
            "<arm_output>",
        ],
        "return_code": completed.returncode,
        "pass": passed,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-8000:],
        "output_exists": exists,
    }
    if exists:
        result["output_size"] = output_path.stat().st_size
        result["output_sha256"] = sha256_file(output_path)
    return result


def adjudicate(a_pass: bool, b_pass: bool, prereg: dict[str, Any]) -> dict[str, str]:
    key = f"A_{'PASS' if a_pass else 'FAIL'}_B_{'PASS' if b_pass else 'FAIL'}"
    try:
        row = prereg["adjudication"][key]
    except KeyError as error:
        raise RuntimeError(f"preregistered adjudication missing {key}") from error
    return {"case": key, "mechanism": row["mechanism"], "next_action": row["next_action"]}


def assert_preregistered_frozen_inputs(repo_root: Path, prereg: dict[str, Any]) -> None:
    frozen = prereg["frozen_inputs"]
    for rel, expected in frozen["production_code_git_blobs"].items():
        actual = git_blob_sha1(repo_root / rel)
        if actual != expected:
            raise RuntimeError(f"NO-CODE-RESCUE violation {rel}: expected={expected} actual={actual}")

    config_path = repo_root / frozen["config_path"]
    if git_blob_sha1(config_path) != frozen["config_git_blob_sha1"]:
        raise RuntimeError("frozen config blob changed before M5.1")

    lock_path = repo_root / "docs/model-training-pipeline/runtime/llama_cpp.lock.json"
    if git_blob_sha1(lock_path) != frozen["llama_cpp_lock_git_blob_sha1"]:
        raise RuntimeError("llama.cpp runtime lock changed before M5.1")


def verify_llama_source(*, llama_source: Path, converter: Path, prereg: dict[str, Any]) -> dict[str, Any]:
    commit = subprocess.check_output(
        ["git", "-C", str(llama_source), "rev-parse", "HEAD"], text=True
    ).strip()
    frozen = prereg["frozen_inputs"]
    if commit != frozen["llama_cpp_commit"]:
        raise RuntimeError(f"llama.cpp commit drift expected={frozen['llama_cpp_commit']} actual={commit}")
    blob = git_blob_sha1(converter)
    if blob != frozen["converter_git_blob_sha1"]:
        raise RuntimeError(
            f"converter blob drift expected={frozen['converter_git_blob_sha1']} actual={blob}"
        )
    return {
        "llama_cpp_commit": commit,
        "converter_git_blob_sha1": blob,
        "converter_sha256": sha256_file(converter),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--llama-source", required=True)
    parser.add_argument("--converter-python", required=True)
    parser.add_argument("--prereg", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    repo_root = Path(args.workspace).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()
    runs_root = Path(args.runs_root)
    if not runs_root.is_absolute():
        runs_root = (repo_root / runs_root).absolute()
    llama_source = Path(args.llama_source).resolve()
    converter_python_raw = Path(args.converter_python)
    converter_python = (
        converter_python_raw
        if converter_python_raw.is_absolute()
        else (Path.cwd() / converter_python_raw).absolute()
    )
    prereg_path = Path(args.prereg)
    if not prereg_path.is_absolute():
        prereg_path = (repo_root / prereg_path).resolve()

    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    assert_preregistered_frozen_inputs(repo_root, prereg)
    frozen = prereg["frozen_inputs"]
    if config_path.relative_to(repo_root).as_posix() != frozen["config_path"]:
        raise RuntimeError("diagnostic config path differs from preregistration")
    if frozen["outtype"] != "f16":
        raise RuntimeError("M5.1 permits only preregistered f16")

    config = load_experiment_config(config_path, repo_root)
    if config.model.id != frozen["model_id"] or config.model.revision != frozen["model_revision"]:
        raise RuntimeError("model identity differs from preregistration")

    converter = llama_source / "convert_hf_to_gguf.py"
    runtime_identity = verify_llama_source(
        llama_source=llama_source, converter=converter, prereg=prereg
    )

    # Regenerate the exact current M2 canonical artifact without modifying M2.
    m2 = run_m2_qualification(config_path, repo_root, runs_root)
    arm_a = m2.run_dir / "canonical_hf"
    if not arm_a.is_dir():
        raise RuntimeError("M2 canonical HF artifact missing")

    source_snapshot = Path(
        snapshot_download(
            repo_id=frozen["model_id"],
            revision=frozen["model_revision"],
            cache_dir=str(runs_root / ".m5-1-source-tokenizer-cache"),
            allow_patterns=list(TOKENIZER_PATTERNS),
        )
    ).resolve()
    if source_snapshot.name != frozen["model_revision"]:
        raise RuntimeError(
            f"pinned source snapshot mismatch expected={frozen['model_revision']} actual={source_snapshot.name}"
        )

    diagnostic_dir = m2.run_dir / "m5_1"
    diagnostic_dir.mkdir(parents=True, exist_ok=False)
    arm_b = diagnostic_dir / "arm_b_source_tokenizer"
    clone_with_hardlinks(arm_a, arm_b)

    a_non_tokenizer = file_manifest(arm_a, tokenizer_only=False)
    b_before_non_tokenizer = file_manifest(arm_b, tokenizer_only=False)
    if a_non_tokenizer != b_before_non_tokenizer:
        raise RuntimeError("arm clone changed non-tokenizer files before intervention")

    source_tokenizer_manifest = replace_tokenizer_assets_from_source(
        arm_b=arm_b, source_snapshot=source_snapshot
    )
    b_non_tokenizer = file_manifest(arm_b, tokenizer_only=False)
    if a_non_tokenizer != b_non_tokenizer:
        raise RuntimeError("tokenizer intervention changed non-tokenizer model/config files")

    arm_a_tokenizer_manifest = file_manifest(arm_a, tokenizer_only=True)
    arm_b_tokenizer_manifest = file_manifest(arm_b, tokenizer_only=True)

    probe_script = repo_root / "tools/m5_1_tokenizer_probe.py"
    inspection_a = inspect_tokenizer(
        converter_python=converter_python, probe_script=probe_script, model_dir=arm_a
    )
    inspection_b = inspect_tokenizer(
        converter_python=converter_python, probe_script=probe_script, model_dir=arm_b
    )

    outtype = frozen["outtype"]
    out_a = diagnostic_dir / "arm_a-f16.gguf"
    out_b = diagnostic_dir / "arm_b-f16.gguf"
    conversion_a = run_conversion(
        converter_python=converter_python,
        converter=converter,
        llama_source=llama_source,
        model_dir=arm_a,
        output_path=out_a,
        outtype=outtype,
    )
    conversion_b = run_conversion(
        converter_python=converter_python,
        converter=converter,
        llama_source=llama_source,
        model_dir=arm_b,
        output_path=out_b,
        outtype=outtype,
    )

    mechanism = adjudicate(conversion_a["pass"], conversion_b["pass"], prereg)
    result = {
        "schema": "mindforge-model-pipeline-m5-1-result-v1",
        "diagnostic_status": "PASS",
        "m5_status": "OPEN",
        "parent_failure": prereg["parent_failure"],
        "preregistration_hash": sha256_object(prereg),
        "runtime_identity": runtime_identity,
        "m2_identity": {
            "run_id": m2.run_id,
            "canonical_directory_hash": m2.canonical_directory_hash,
            "m2_adjudication_hash": m2.adjudication_hash,
        },
        "controlled_variable_check": {
            "only_independent_variable": "tokenizer_source",
            "non_tokenizer_manifest_equal": a_non_tokenizer == b_non_tokenizer,
            "non_tokenizer_manifest_hash": sha256_object(a_non_tokenizer),
            "converter_command_shape_equal": conversion_a["command_shape"] == conversion_b["command_shape"],
            "outtype": outtype,
            "quantization_executed": False,
        },
        "arm_A": {
            "tokenizer_source": "M2_CANONICAL_HF",
            "tokenizer_asset_manifest": arm_a_tokenizer_manifest,
            "tokenizer_asset_manifest_hash": sha256_object(arm_a_tokenizer_manifest),
            "inspection": inspection_a,
            "conversion": conversion_a,
        },
        "arm_B": {
            "tokenizer_source": "PINNED_QWEN_SOURCE_RAW_ASSETS",
            "source_snapshot_revision": source_snapshot.name,
            "source_tokenizer_asset_manifest": source_tokenizer_manifest,
            "tokenizer_asset_manifest": arm_b_tokenizer_manifest,
            "tokenizer_asset_manifest_hash": sha256_object(arm_b_tokenizer_manifest),
            "inspection": inspection_b,
            "conversion": conversion_b,
        },
        "adjudication": mechanism,
        "quantization_authorized": False,
        "m6_authorized": False,
        "bulk_training_authorized": False,
    }
    result["result_hash"] = sha256_object(result)
    result_path = diagnostic_dir / "M5_1_RESULT.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Outputs can be large; retain hashes in evidence but not duplicate GGUF payloads.
    for path in (out_a, out_b):
        if path.exists():
            path.unlink()

    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"M5.1 diagnostic PASS: {mechanism['case']}")
        print(f"mechanism={mechanism['mechanism']}")
        print(f"next_action={mechanism['next_action']}")
        print(f"result_hash={result['result_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

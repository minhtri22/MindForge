from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ollama_windows_adapter as adapter

TARGET_VERSION = "0.34.2"
TARGET_HOST = "127.0.0.1:11468"
SYSTEM_HOST = "127.0.0.1:11434"
DEFAULT_FIXTURE = "llama3.2:1b"


def atomic_json(path: Path, obj: Any) -> None:
    adapter.atomic_json(path, obj)


def git_blob(path: str) -> str:
    cp = subprocess.run(["git", "hash-object", "--", path], text=True, capture_output=True, check=True)
    return cp.stdout.strip()


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()


def find_ollama() -> Path | None:
    w = shutil.which("ollama.exe") or shutil.which("ollama")
    if w:
        return Path(w)
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
    return local if local.is_file() else None


def version_of(exe: Path, evidence_dir: Path) -> str:
    cp = subprocess.run([str(exe), "--version"], text=True, capture_output=True, check=False)
    (evidence_dir / "ollama-version.stdout.log").write_text(cp.stdout, encoding="utf-8")
    (evidence_dir / "ollama-version.stderr.log").write_text(cp.stderr, encoding="utf-8")
    if cp.returncode != 0:
        raise RuntimeError("ollama --version failed")
    m = re.search(r"(?<!\d)(\d+\.\d+\.\d+)(?!\d)", cp.stdout + "\n" + cp.stderr)
    if not m:
        raise RuntimeError("unable to parse Ollama version")
    return m.group(1)


def local_scope() -> Dict[str, Any]:
    data = {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["local_machine_fingerprint_sha256"] = hashlib.sha256(canonical).hexdigest()
    return data


def snapshot_system_service() -> Dict[str, Any]:
    tags = adapter.probe_tags(SYSTEM_HOST, timeout=2)
    return {
        "healthy": tags is not None,
        "model_names": adapter.model_names(tags),
    }


def read_runtime_logs(evidence_dir: Path) -> str:
    chunks = []
    for name in ("ollama-serve.stdout.log", "ollama-serve.stderr.log"):
        p = evidence_dir / name
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def parse_launch_evidence(text: str) -> Dict[str, Any]:
    lines = [line for line in text.splitlines() if "llama-server" in line or "--cache-type-" in line or "--flash-attn" in line]
    joined = "\n".join(lines)
    normalized = joined.replace('"', ' ').replace("'", " ")
    v_f16 = bool(re.search(r"--cache-type-v(?:=|\\s+)f16(?:\\s|$)", normalized))
    k_f16 = bool(re.search(r"--cache-type-k(?:=|\\s+)f16(?:\\s|$)", normalized))
    q4_v = bool(re.search(r"--cache-type-v(?:=|\\s+)q4_0(?:\\s|$)", normalized))
    if "--flash-attn off" in normalized or "--flash-attn=off" in normalized:
        flash_mode = "off"
    elif "--flash-attn on" in normalized or "--flash-attn=on" in normalized:
        flash_mode = "on"
    else:
        flash_mode = ""
    conflict = "quantized V cache requires flash_attn" in text
    return {
        "candidate_lines": lines,
        "cache_type_k_f16_observed": k_f16,
        "cache_type_v_f16_observed": v_f16,
        "cache_type_v_q4_0_observed": q4_v,
        "flash_attention_mode": flash_mode,
        "known_conflict_error_observed": conflict,
    }


def evidence_manifest(root: Path) -> Dict[str, Any]:
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name not in {"evidence-manifest.json", "OWRQ_QUALIFICATION_REPORT.json"}:
            rows.append({
                "path": str(p.relative_to(root)).replace("\\", "/"),
                "size": p.stat().st_size,
                "sha256": adapter.sha256_file(p),
            })
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {"files": rows, "manifest_sha256": hashlib.sha256(canonical).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--fixture-name", default=DEFAULT_FIXTURE)
    args = ap.parse_args()

    root = Path(args.output_root).resolve()
    evidence = root / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    report_path = root / "OWRQ_QUALIFICATION_REPORT.json"
    qualified_path = root / "QUALIFIED_RUNTIME_SCOPE.json"

    bootstrap = {
        "schema": "mindforge-owrq-bootstrap-v1",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_head": git_head(),
        "fixture_name": args.fixture_name,
        "scientific": False,
        "eval_v1_accessed": False,
    }
    atomic_json(root / "B00_bootstrap.json", bootstrap)

    report: Dict[str, Any] = {
        "schema": "mindforge-owrq-qualification-report-v1",
        "status": "RUNNING",
        "scientific": False,
        "fixture_name": args.fixture_name,
        "m6r2_science_authorized": False,
        "eval_v1_accessed": False,
        "model_quality_scored": False,
        "reasoning_scored": False,
        "ollama_pull_executed": False,
        "model_create_executed": False,
        "model_delete_executed": False,
    }

    server = None
    system_before = snapshot_system_service()
    report["system_service_before"] = system_before
    ollama = find_ollama()
    if ollama is None:
        report.update(status="UNRESOLVED_INFRA", reason="INSTALLED_OLLAMA_NOT_FOUND")
        atomic_json(report_path, report)
        return 2

    try:
        version = version_of(ollama, evidence)
        report["ollama_version"] = version
        report["ollama_executable_path"] = str(ollama)
        report["ollama_executable_sha256"] = adapter.sha256_file(ollama)
        if version != TARGET_VERSION:
            report.update(status="FAIL_INFRA", reason="OLLAMA_VERSION_MISMATCH")
            atomic_json(report_path, report)
            return 2

        scope = local_scope()
        report["target_scope"] = scope
        flash_env = os.environ.get("OLLAMA_FLASH_ATTENTION")
        report["runtime_environment"] = {
            "OLLAMA_KV_CACHE_TYPE": "f16",
            "OLLAMA_FLASH_ATTENTION_forced": False,
            "OLLAMA_FLASH_ATTENTION_observed_value": flash_env,
        }

        server = adapter.start_server(ollama, TARGET_HOST, evidence, "f16")
        report["qualification_server"] = server
        tags = adapter.probe_tags(TARGET_HOST, timeout=5)
        fixture = None if tags is None else adapter.find_model(tags, args.fixture_name)
        if fixture is None:
            report.update(status="UNRESOLVED_INFRA", reason="UNRESOLVED_INFRA_FIXTURE")
            atomic_json(report_path, report)
            return 2

        report["fixture_identity"] = {
            "name": fixture.get("name"),
            "digest": fixture.get("digest"),
            "size": fixture.get("size"),
            "modified_at": fixture.get("modified_at"),
        }
        initial_names = adapter.model_names(tags)
        report["qualification_model_names_before"] = initial_names

        request = {
            "model": fixture["name"],
            "messages": [{"role": "user", "content": "Return a short acknowledgement."}],
            "stream": False,
            "keep_alive": 0,
            "options": {"num_ctx": 128, "num_predict": 8, "temperature": 0, "top_p": 1, "top_k": 0, "seed": 42},
        }
        atomic_json(evidence / "plumbing-request.json", request)
        try:
            response = adapter.http_json("POST", f"http://{TARGET_HOST}/api/chat", request, timeout=300)
            atomic_json(evidence / "plumbing-response.json", response)
            report["plumbing_request_completed"] = True
        except Exception as e:
            report["plumbing_request_completed"] = False
            report["plumbing_error"] = f"{type(e).__name__}: {e}"

        time.sleep(1)
        logs = read_runtime_logs(evidence)
        launch = parse_launch_evidence(logs)
        report["launch_evidence"] = launch

        tags_after = adapter.probe_tags(TARGET_HOST, timeout=5)
        names_after = adapter.model_names(tags_after)
        report["qualification_model_names_after"] = names_after
        report["qualification_model_set_unchanged"] = names_after == initial_names

        system_after = snapshot_system_service()
        report["system_service_after"] = system_after
        report["system_11434_unchanged"] = system_after == system_before

        gates = {
            "exact_ollama_0_34_2": version == TARGET_VERSION,
            "fixture_preexisting": fixture is not None,
            "plumbing_request_completed": report["plumbing_request_completed"],
            "cache_type_k_f16_observed": launch["cache_type_k_f16_observed"],
            "cache_type_v_f16_observed": launch["cache_type_v_f16_observed"],
            "cache_type_v_q4_0_absent": not launch["cache_type_v_q4_0_observed"],
            "known_conflict_error_absent": not launch["known_conflict_error_observed"],
            "flash_attention_resolution_observed": bool(launch["flash_attention_mode"]),
            "qualification_model_set_unchanged": report["qualification_model_set_unchanged"],
            "system_11434_unchanged": report["system_11434_unchanged"],
        }
        report["gates"] = gates

        if all(gates.values()):
            adapter_blob = git_blob("tools/ollama_windows_adapter.py")
            qualified = {
                "schema": "mindforge-owrq-qualified-runtime-scope-v1",
                "status": "QUALIFIED_RUNTIME_SCOPE",
                "program": "OLLAMA_WINDOWS_RUNTIME_QUALIFICATION",
                "runtime": {
                    "ollama_version": version,
                    "ollama_executable_path": str(ollama),
                    "ollama_executable_sha256": report["ollama_executable_sha256"],
                },
                "runtime_environment": report["runtime_environment"],
                "target_scope": scope,
                "adapter": {
                    "contract_version": adapter.CONTRACT_VERSION,
                    "entrypoint": "tools/ollama_windows_adapter.py",
                    "runtime_adapter_git_blob_sha1": adapter_blob,
                },
                "api_contract": {"host": TARGET_HOST, "chat_endpoint": "/api/chat"},
                "backend_resolution": {"flash_attention_mode": launch["flash_attention_mode"]},
                "fixture_identity": report["fixture_identity"],
                "qualification_evidence": {
                    "report_path": str(report_path),
                    "launch_candidate_lines": launch["candidate_lines"],
                },
                "scientific": False,
            }
            atomic_json(qualified_path, qualified)
            report["status"] = "QUALIFIED_RUNTIME_SCOPE"
        else:
            report["status"] = "FAIL_INFRA"
            report["reason"] = "ONE_OR_MORE_QUALIFICATION_GATES_FAILED"

    except Exception as e:
        report["status"] = "FAIL_INFRA"
        report["reason"] = f"{type(e).__name__}: {e}"
    finally:
        if server is not None:
            adapter.terminate_server(int(server["server_pid"]))
        report["evidence_manifest"] = evidence_manifest(root)
        atomic_json(root / "evidence-manifest.json", report["evidence_manifest"])
        atomic_json(report_path, report)

    return 0 if report.get("status") == "QUALIFIED_RUNTIME_SCOPE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

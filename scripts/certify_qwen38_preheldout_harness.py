#!/usr/bin/env python3
"""Certify Track-A client-harness durability before any fresh held-out run.

This runner is infrastructure-only. It reads development materialization only,
reuses the frozen Track-A prompt/request semantics, never scores responses, and
never reads the held-out/test materialization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import statistics
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import psutil

from run_qwen38_track_a_reference_eval import SYSTEM, parse_prediction, prompt_for


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "track-a-capability-v1"
DEFAULT_OUT = ROOT / "runs" / "track-a-qwen38-reference-v1-harness-certification"

MODEL_PATH = Path(r"D:\WORK\2.Ollama\Qwen3.8-27B-Q4_K_M.gguf")
MODEL_NAME = "Qwen3.8-27B-Q4_K_M"
MODEL_SHA256 = "31629f53165ab6a7dad8c9847dcfd1fdf55829dac1e6e748f4a68581b0033d34"
MODEL_BYTES = 18_973_870_432
SERVER_PATH = Path(r"D:\WORK\MODELS\MindForge\llama-b10793\vulkan\llama-server.exe")
SERVER_VERSION = "0.3.0-dev build 10793 commit d230ddd76"
PROMPT_PATH = ROOT / "runs" / "track-a-qwen38-reference-v1" / "prompt-template.txt"
PROMPT_VERSION = "track-a-reference-json-v1-v3-local-format"
PROMPT_SHA256 = "6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d"
DEVELOPMENT_SHA256 = "2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42"
CALIBRATION_SHA256 = "7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb"
SCHEMA_SHA256 = "6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb"
MANIFEST_SHA256 = "09660d9e3b1d294fa82fbde702083d0d818431692a55f30387c78adfc697a210"
SCORER_SHA256 = "5687848ee162a8d0de66167e524fac3b6f5bc3a9e40f4731451f6af2f2bea700"
SEED = 20260904
TEMPERATURE = 0.0
MAX_TOKENS = 128
TIMEOUT_SECONDS = 300.0


class HarnessInterrupted(BaseException):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def durable_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def append_durable_jsonl(handle, value: dict) -> None:
    handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def build_certification_workload(development: list[dict]) -> list[tuple[int, int, dict]]:
    if len(development) != 420:
        raise RuntimeError(f"expected 420 development cases, found {len(development)}")
    workload: list[tuple[int, int, dict]] = []
    sequence = 0
    for repeat_index in (1, 2):
        for case in development:
            sequence += 1
            workload.append((sequence, repeat_index, case))
    return workload


def validate_sequence_rows(rows: list[dict], planned: int) -> dict:
    indices = [int(row["sequence_index"]) for row in rows]
    missing = sorted(set(range(1, planned + 1)) - set(indices))
    duplicates = sorted({idx for idx in indices if indices.count(idx) > 1})
    return {
        "rows": len(rows),
        "missing_indices": missing,
        "duplicate_indices": duplicates,
        "exact_order": indices == list(range(1, len(indices) + 1)),
    }


def infer_processes() -> list[dict]:
    found: list[dict] = []
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        name = (proc.info.get("name") or "").lower()
        if any(token in name for token in ("ollama", "llama", "lmstudio", "kobold")):
            found.append({
                "pid": proc.info.get("pid"),
                "name": proc.info.get("name"),
                "exe": proc.info.get("exe"),
            })
    return sorted(found, key=lambda item: int(item["pid"]))


def server_process(pid: int) -> psutil.Process:
    proc = psutil.Process(pid)
    if Path(proc.exe()).resolve() != SERVER_PATH.resolve():
        raise RuntimeError(f"server executable mismatch: {proc.exe()}")
    return proc


def server_alive(pid: int, create_time: float) -> bool:
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and proc.create_time() == create_time
    except psutil.NoSuchProcess:
        return False


def validate_server_command(cmdline: list[str]) -> dict:
    command = " ".join(cmdline)
    required = [
        str(MODEL_PATH), "-c 8192", "-ngl 10", "--parallel 1",
        "--cache-type-k f16", "--cache-type-v f16", "--reasoning off",
        "--reasoning-budget 0", "--no-reasoning-preserve",
        "--host 127.0.0.1", "--port 8080", "--verbose",
    ]
    missing = [token for token in required if token not in command]
    return {"command": command, "required_tokens_missing": missing, "pass": not missing}


def precheck(pid: int, outdir: Path) -> tuple[psutil.Process, float, dict]:
    proc = server_process(pid)
    created = proc.create_time()
    processes = infer_processes()
    isolation_pass = len(processes) == 1 and processes[0]["pid"] == pid
    command_check = validate_server_command(proc.cmdline())

    hashes = {
        "development.jsonl": {"actual": sha256_file(BENCH / "development.jsonl"), "expected": DEVELOPMENT_SHA256},
        "calibration.jsonl": {"actual": sha256_file(BENCH / "calibration.jsonl"), "expected": CALIBRATION_SHA256},
        "schema.json": {"actual": sha256_file(BENCH / "schema.json"), "expected": SCHEMA_SHA256},
        "manifest.json": {"actual": sha256_file(BENCH / "manifest.json"), "expected": MANIFEST_SHA256},
        "prompt-template.txt": {"actual": sha256_file(PROMPT_PATH), "expected": PROMPT_SHA256},
        "score_track_a_v1.py": {"actual": sha256_file(ROOT / "scripts" / "score_track_a_v1.py"), "expected": SCORER_SHA256},
        "model": {"actual": sha256_file(MODEL_PATH), "expected": MODEL_SHA256},
    }
    hash_pass = all(item["actual"] == item["expected"] for item in hashes.values())
    model_bytes = MODEL_PATH.stat().st_size
    result = {
        "checked_at": utc_now(),
        "server_pid": pid,
        "server_create_time": created,
        "server_alive": server_alive(pid, created),
        "inference_processes": processes,
        "isolation_pass": isolation_pass,
        "command_check": command_check,
        "hashes": hashes,
        "hashes_pass": hash_pass,
        "model_bytes": model_bytes,
        "model_bytes_expected": MODEL_BYTES,
        "model_bytes_pass": model_bytes == MODEL_BYTES,
        "heldout_test_file_opened": False,
        "pass": bool(isolation_pass and command_check["pass"] and hash_pass and model_bytes == MODEL_BYTES and server_alive(pid, created)),
    }
    durable_json(outdir / "precheck.json", result)
    durable_json(outdir / "harness-config.json", {
        "certification_workload": "development 1-420 followed by development 1-420",
        "planned_requests": 840,
        "smoke_requests": 10,
        "concurrency": 1,
        "retry_model_response": False,
        "per_case_durable_jsonl": True,
        "flush_each_case": True,
        "fsync_each_case": True,
        "heartbeat": True,
        "finalizer_evidence": True,
        "test_split_used": False,
        "semantic_scoring": False,
    })
    durable_json(outdir / "runtime-freeze.json", {
        "server_path": str(SERVER_PATH),
        "server_version": SERVER_VERSION,
        "server_pid": pid,
        "server_create_time": created,
        "server_command": proc.cmdline(),
        "model_path": str(MODEL_PATH),
        "model_bytes": model_bytes,
        "model_sha256": MODEL_SHA256,
        "backend": "Vulkan",
        "device": "Intel(R) Arc(TM) 140V GPU",
        "context": 8192,
        "gpu_layers": 10,
        "parallel": 1,
        "kv_k": "f16",
        "kv_v": "f16",
        "temperature": TEMPERATURE,
        "seed": SEED,
        "reasoning": "off",
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": PROMPT_SHA256,
    })
    if not result["pass"]:
        raise RuntimeError("precheck failed")
    return proc, created, result


def resource_snapshot(runner_pid: int, server_pid: int, label: str, sequence_index: int) -> dict:
    runner = psutil.Process(runner_pid)
    server = psutil.Process(server_pid)
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    runner_mem = runner.memory_info()
    server_mem = server.memory_info()
    return {
        "label": label,
        "sequence_index": sequence_index,
        "timestamp": utc_now(),
        "runner_rss_bytes": int(runner_mem.rss),
        "server_rss_bytes": int(server_mem.rss),
        "server_private_bytes": int(getattr(server_mem, "private", 0)),
        "system_available_bytes": int(vm.available),
        "system_used_bytes": int(vm.used),
        "pagefile_used_bytes": int(swap.used),
        "gpu_shared_memory_bytes": None,
    }


def summarize_resources(snapshots: list[dict]) -> dict:
    if not snapshots:
        return {"snapshots": [], "peak": {}}
    return {
        "snapshots": snapshots,
        "peak": {
            "runner_rss_bytes": max(x["runner_rss_bytes"] for x in snapshots),
            "server_rss_bytes": max(x["server_rss_bytes"] for x in snapshots),
            "server_private_bytes": max(x["server_private_bytes"] for x in snapshots),
            "system_used_bytes": max(x["system_used_bytes"] for x in snapshots),
            "pagefile_used_bytes": max(x["pagefile_used_bytes"] for x in snapshots),
            "min_system_available_bytes": min(x["system_available_bytes"] for x in snapshots),
        },
    }


def call_model(base_url: str, case: dict, timeout: float) -> dict:
    prompt = prompt_for(case)
    body = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "seed": SEED,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    request_started = utc_now()
    perf_started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            http_status = int(response.status)
            payload = json.loads(response.read().decode("utf-8"))
        raw = payload["choices"][0]["message"].get("content") or ""
        parsed, parse_status = parse_prediction(raw)
        timings = payload.get("timings", {})
        usage = payload.get("usage", {})
        return {
            "request_start_timestamp": request_started,
            "request_end_timestamp": utc_now(),
            "transport_status": "ok",
            "http_status": http_status,
            "latency_seconds": time.perf_counter() - perf_started,
            "raw_response": raw,
            "parse_status": parse_status,
            "parsed_response": parsed,
            "validator_status": "PASS",
            "prompt_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "prompt_tok_s": timings.get("prompt_per_second"),
            "decode_tok_s": timings.get("predicted_per_second"),
            "transport_error": None,
        }
    except urllib.error.HTTPError as exc:
        return {
            "request_start_timestamp": request_started,
            "request_end_timestamp": utc_now(),
            "transport_status": "http_error",
            "http_status": int(exc.code),
            "latency_seconds": time.perf_counter() - perf_started,
            "raw_response": "",
            "parse_status": "not_available",
            "parsed_response": {},
            "validator_status": "PASS",
            "prompt_tokens": None,
            "output_tokens": None,
            "prompt_tok_s": None,
            "decode_tok_s": None,
            "transport_error": repr(exc),
        }
    except Exception as exc:
        return {
            "request_start_timestamp": request_started,
            "request_end_timestamp": utc_now(),
            "transport_status": "transport_error",
            "http_status": None,
            "latency_seconds": time.perf_counter() - perf_started,
            "raw_response": "",
            "parse_status": "not_available",
            "parsed_response": {},
            "validator_status": "PASS",
            "prompt_tokens": None,
            "output_tokens": None,
            "prompt_tok_s": None,
            "decode_tok_s": None,
            "transport_error": repr(exc),
        }


def run_workload(
    *,
    mode: str,
    pid: int,
    created: float,
    base_url: str,
    timeout: float,
    workload: list[tuple[int, int, dict]],
    jsonl_path: Path,
    heartbeat_path: Path,
    summary_path: Path,
    resource_path: Path,
) -> int:
    run_id = f"preheldout-{mode}-{int(time.time())}"
    runner_pid = os.getpid()
    started_at = utc_now()
    heartbeat = {
        "run_id": run_id,
        "runner_pid": runner_pid,
        "server_pid": pid,
        "started_at": started_at,
        "last_case_started": None,
        "last_case_completed": 0,
        "last_update": started_at,
        "status": "RUNNING",
        "exit_reason": None,
        "finalizer_executed": False,
    }
    durable_json(heartbeat_path, heartbeat)
    snapshots = [resource_snapshot(runner_pid, pid, "start", 0)]
    rows: list[dict] = []
    unhandled_exception = None
    interrupted = False
    exit_code = 2
    milestones = {
        max(1, round(len(workload) * 0.25)): "25%",
        max(1, round(len(workload) * 0.50)): "50%",
        max(1, round(len(workload) * 0.75)): "75%",
        len(workload): "100%",
    }

    def signal_handler(signum, _frame):
        raise HarnessInterrupted(f"signal {signum}")

    installed_handlers: list[tuple[int, object]] = []
    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            installed_handlers.append((sig, signal.getsignal(sig)))
            signal.signal(sig, signal_handler)

    try:
        with jsonl_path.open("x", encoding="utf-8", newline="\n") as handle:
            for sequence_index, repeat_index, case in workload:
                heartbeat.update(
                    last_case_started=sequence_index,
                    last_update=utc_now(),
                    status="RUNNING",
                )
                durable_json(heartbeat_path, heartbeat)

                if not server_alive(pid, created):
                    raise RuntimeError("llama-server lifetime changed before request")
                processes = infer_processes()
                if len(processes) != 1 or processes[0]["pid"] != pid:
                    raise RuntimeError(f"inference isolation violation: {processes}")

                try:
                    result = call_model(base_url, case, timeout)
                except AssertionError as exc:
                    result = {
                        "request_start_timestamp": utc_now(),
                        "request_end_timestamp": utc_now(),
                        "transport_status": "not_attempted_validator_failure",
                        "http_status": None,
                        "latency_seconds": 0.0,
                        "raw_response": "",
                        "parse_status": "not_available",
                        "parsed_response": {},
                        "validator_status": "FAIL",
                        "prompt_tokens": None,
                        "output_tokens": None,
                        "prompt_tok_s": None,
                        "decode_tok_s": None,
                        "transport_error": repr(exc),
                    }

                row = {
                    "run_id": run_id,
                    "sequence_index": sequence_index,
                    "source_case_id": case["case_id"],
                    "repeat_index": repeat_index,
                    "server_pid": pid,
                    **result,
                    "server_alive_after": server_alive(pid, created),
                }
                append_durable_jsonl(handle, row)
                rows.append(row)
                heartbeat.update(
                    last_case_completed=sequence_index,
                    last_update=utc_now(),
                )
                durable_json(heartbeat_path, heartbeat)

                if sequence_index in milestones:
                    snapshots.append(resource_snapshot(runner_pid, pid, milestones[sequence_index], sequence_index))
                print(json.dumps({
                    "mode": mode,
                    "done": sequence_index,
                    "total": len(workload),
                    "case_id": case["case_id"],
                    "transport": row["transport_status"],
                    "parse": row["parse_status"],
                }), flush=True)

                if row["validator_status"] != "PASS":
                    raise RuntimeError("validator failure")
                if row["transport_status"] != "ok" or row["http_status"] != 200:
                    raise RuntimeError("transport failure; no retry")
                if not row["server_alive_after"]:
                    raise RuntimeError("server not alive after request")

        sequence_check = validate_sequence_rows(rows, len(workload))
        complete = (
            len(rows) == len(workload)
            and not sequence_check["missing_indices"]
            and not sequence_check["duplicate_indices"]
            and sequence_check["exact_order"]
            and all(row["transport_status"] == "ok" and row["http_status"] == 200 for row in rows)
            and all(row["validator_status"] == "PASS" for row in rows)
            and server_alive(pid, created)
        )
        exit_code = 0 if complete else 2
        heartbeat["status"] = "COMPLETED" if complete else "FAILED"
        heartbeat["exit_reason"] = "normal_completion" if complete else "acceptance_check_failed"
    except HarnessInterrupted as exc:
        interrupted = True
        heartbeat["status"] = "INTERRUPTED"
        heartbeat["exit_reason"] = str(exc)
        exit_code = 130
    except BaseException as exc:
        unhandled_exception = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        heartbeat["status"] = "FAILED"
        heartbeat["exit_reason"] = repr(exc)
        exit_code = 2
    finally:
        for sig, previous in installed_handlers:
            signal.signal(sig, previous)
        try:
            snapshots.append(resource_snapshot(runner_pid, pid, "final", len(rows)))
        except Exception:
            pass
        heartbeat.update(last_update=utc_now(), finalizer_executed=True)
        durable_json(heartbeat_path, heartbeat)
        durable_json(resource_path, summarize_resources(snapshots))

        sequence_check = validate_sequence_rows(rows, len(workload)) if rows else {
            "rows": 0,
            "missing_indices": list(range(1, len(workload) + 1)),
            "duplicate_indices": [],
            "exact_order": True,
        }
        latencies = [row["latency_seconds"] for row in rows if row["transport_status"] == "ok"]
        summary = {
            "run_id": run_id,
            "mode": mode,
            "started_at": started_at,
            "finished_at": utc_now(),
            "planned_requests": len(workload),
            "completed_requests": len(rows),
            "client_telemetry_rows": len(rows),
            "transport_errors": sum(row["transport_status"] != "ok" for row in rows),
            "connection_refused": sum("ConnectionRefusedError" in str(row.get("transport_error")) for row in rows),
            "timeouts": sum("timeout" in str(row.get("transport_error", "")).lower() for row in rows),
            "parse_outcomes": sum(bool(row.get("parse_status")) for row in rows),
            "parse_success": sum(str(row.get("parse_status", "")).startswith("json") for row in rows),
            "validator_outcomes": sum(bool(row.get("validator_status")) for row in rows),
            "validator_failures": sum(row.get("validator_status") != "PASS" for row in rows),
            "missing_indices": sequence_check["missing_indices"],
            "duplicate_indices": sequence_check["duplicate_indices"],
            "exact_order": sequence_check["exact_order"],
            "runner_unexpected_termination": False,
            "interrupted": interrupted,
            "unhandled_exception": unhandled_exception,
            "server_pid": pid,
            "server_pid_unchanged": server_alive(pid, created),
            "server_alive_afterward": server_alive(pid, created),
            "heartbeat_final_state": heartbeat["status"],
            "finalizer_executed": True,
            "runner_exit_code": exit_code,
            "latency_seconds": {
                "min": min(latencies) if latencies else None,
                "median": statistics.median(latencies) if latencies else None,
                "max": max(latencies) if latencies else None,
                "mean": statistics.fmean(latencies) if latencies else None,
            },
            "result": "PASS" if exit_code == 0 else "FAIL",
        }
        durable_json(summary_path, summary)
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("precheck", "smoke", "certify"), required=True)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    _, created, _ = precheck(args.pid, args.outdir)
    if args.mode == "precheck":
        return 0

    development = read_jsonl(BENCH / "development.jsonl")
    # Validate prompt construction on development only before sending any request.
    for case in development:
        prompt_for(case)

    if args.mode == "smoke":
        workload = [(index, 1, case) for index, case in enumerate(development[:10], 1)]
        return run_workload(
            mode="smoke",
            pid=args.pid,
            created=created,
            base_url=args.base_url,
            timeout=args.timeout,
            workload=workload,
            jsonl_path=args.outdir / "smoke-results.jsonl",
            heartbeat_path=args.outdir / "heartbeat-smoke.json",
            summary_path=args.outdir / "smoke-results.json",
            resource_path=args.outdir / "resource-summary-smoke.json",
        )

    if args.attempt < 1 or args.attempt > 3:
        raise SystemExit("attempt must be 1..3")
    workload = build_certification_workload(development)
    suffix = f"{args.attempt:02d}"
    return run_workload(
        mode=f"certification-attempt-{suffix}",
        pid=args.pid,
        created=created,
        base_url=args.base_url,
        timeout=args.timeout,
        workload=workload,
        jsonl_path=args.outdir / f"certification-attempt-{suffix}.jsonl",
        heartbeat_path=args.outdir / f"heartbeat-attempt-{suffix}.json",
        summary_path=args.outdir / f"certification-attempt-{suffix}.json",
        resource_path=args.outdir / "resource-summary.json",
    )


if __name__ == "__main__":
    raise SystemExit(main())

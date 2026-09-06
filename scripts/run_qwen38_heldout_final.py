#!/usr/bin/env python3
"""Run the single authorized fresh 700-case Track-A held-out qualification.

The runner is intentionally one-shot. It reuses the already certified
process-lifetime/request helpers, creates an exclusive start marker before
reading the held-out materialization, never retries model responses, and only
invokes the frozen scorer after a fully valid 700/700 run.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import statistics
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import psutil

from certify_qwen38_preheldout_harness import (
    MODEL_BYTES,
    MODEL_NAME,
    MODEL_PATH,
    MODEL_SHA256,
    PROMPT_PATH,
    PROMPT_SHA256,
    PROMPT_VERSION,
    SERVER_PATH,
    SERVER_VERSION,
    SYSTEM,
    call_model,
    durable_json,
    infer_processes,
    resource_snapshot,
    server_alive,
    server_process,
    sha256_file,
    summarize_resources,
    validate_server_command,
)
from score_track_a_v1 import score_case


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "track-a-capability-v1"
OUT = ROOT / "runs" / "track-a-qwen38-reference-v1-heldout-final"
CERT = ROOT / "runs" / "track-a-qwen38-reference-v1-harness-certification"

EXPECTED_HEAD = "4437dba66fd3ebbf3749479c180dfe5355d3eafe"
EXPECTED_SCORER_SHA256 = "5687848ee162a8d0de66167e524fac3b6f5bc3a9e40f4731451f6af2f2bea700"
EXPECTED_MANIFEST_SHA256 = "09660d9e3b1d294fa82fbde702083d0d818431692a55f30387c78adfc697a210"
EXPECTED_SCHEMA_SHA256 = "6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb"
EXPECTED_BENCHMARK_HASHES = {
    "calibration.jsonl": "7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb",
    "development.jsonl": "2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42",
    "test.jsonl": "3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf",
    "schema.json": EXPECTED_SCHEMA_SHA256,
    "human-review-sample.jsonl": "d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693",
}

PID = 28096
SEED = 20260904
TEMPERATURE = 0.0
MAX_TOKENS = 128
TIMEOUT_SECONDS = 300.0


class HeldoutInterrupted(BaseException):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def exclusive_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def append_jsonl(handle, payload: dict) -> None:
    handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def percentile95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def current_freeze(pid: int) -> tuple[psutil.Process, float, dict]:
    proc = server_process(pid)
    created = proc.create_time()
    processes = infer_processes()
    command_check = validate_server_command(proc.cmdline())
    cert_verdict = json.loads((CERT / "harness-certification-verdict.json").read_text(encoding="utf-8"))
    manifest = json.loads((BENCH / "manifest.json").read_text(encoding="utf-8"))
    expected_manifest_hashes = manifest.get("hashes", {})

    benchmark_hashes = {}
    for name, expected in EXPECTED_BENCHMARK_HASHES.items():
        actual = sha256_file(BENCH / name)
        benchmark_hashes[name] = {"actual": actual, "expected": expected, "match": actual == expected}

    head = git("rev-parse", "HEAD")
    origin = git("rev-parse", "origin/research/track-a-benchmark-v1")
    model_bytes = MODEL_PATH.stat().st_size
    model_sha = sha256_file(MODEL_PATH)
    scorer_sha = sha256_file(ROOT / "scripts" / "score_track_a_v1.py")
    prompt_sha = sha256_file(PROMPT_PATH)
    manifest_sha = sha256_file(BENCH / "manifest.json")
    schema_sha = sha256_file(BENCH / "schema.json")
    certified_harness = ROOT / "scripts" / "certify_qwen38_preheldout_harness.py"
    heldout_runner = Path(__file__).resolve()
    isolation_pass = len(processes) == 1 and processes[0].get("pid") == pid
    cert_pass = (
        cert_verdict.get("verdict") == "HARNESS CERTIFIED"
        and cert_verdict.get("fresh_heldout_one_shot") == "AUTHORIZED"
    )
    hashes_pass = (
        all(item["match"] for item in benchmark_hashes.values())
        and manifest_sha == EXPECTED_MANIFEST_SHA256
        and schema_sha == EXPECTED_SCHEMA_SHA256
        and scorer_sha == EXPECTED_SCORER_SHA256
        and prompt_sha == PROMPT_SHA256
        and model_sha == MODEL_SHA256
        and model_bytes == MODEL_BYTES
        and expected_manifest_hashes == EXPECTED_BENCHMARK_HASHES
    )
    state = {
        "timestamp": utc_now(),
        "repository_head": head,
        "origin_head": origin,
        "head_matches_origin": head == origin,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "server_pid": pid,
        "server_create_time": created,
        "server_alive": server_alive(pid, created),
        "server_path": proc.exe(),
        "server_command": proc.cmdline(),
        "command_check": command_check,
        "inference_processes": processes,
        "isolation_pass": isolation_pass,
        "model_path": str(MODEL_PATH),
        "model_bytes": model_bytes,
        "model_sha256": model_sha,
        "prompt_path": str(PROMPT_PATH),
        "prompt_sha256": prompt_sha,
        "manifest_sha256": manifest_sha,
        "schema_sha256": schema_sha,
        "scorer_sha256": scorer_sha,
        "benchmark_hashes": benchmark_hashes,
        "manifest_hash_map": expected_manifest_hashes,
        "certification_verdict": cert_verdict.get("verdict"),
        "fresh_heldout_authorization": cert_verdict.get("fresh_heldout_one_shot"),
        "certification_gate_pass": cert_pass,
        "certified_harness_commit": EXPECTED_HEAD,
        "certified_harness_sha256": sha256_file(certified_harness),
        "heldout_runner_sha256": sha256_file(heldout_runner),
        "hashes_pass": hashes_pass,
    }
    state["pass"] = bool(
        state["head_matches_origin"]
        and state["head_matches_expected"]
        and state["server_alive"]
        and isolation_pass
        and command_check["pass"]
        and hashes_pass
        and cert_pass
    )
    return proc, created, state


def write_precheck_and_freeze(pid: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    marker = OUT / "heldout-one-shot-marker.json"
    predictions = OUT / "heldout-predictions.jsonl"
    if marker.exists() or predictions.exists():
        raise SystemExit("held-out one-shot artifacts already exist; precheck rerun refused")
    proc, created, state = current_freeze(pid)
    durable_json(OUT / "precheck.json", state)
    freeze = {
        "timestamp": utc_now(),
        "repository_head": state["repository_head"],
        "model_path": str(MODEL_PATH),
        "model_bytes": MODEL_PATH.stat().st_size,
        "model_sha256": state["model_sha256"],
        "llama_server_path": proc.exe(),
        "llama_server_version": SERVER_VERSION,
        "llama_cpp_build": 10793,
        "llama_cpp_commit": "d230ddd76",
        "server_pid": pid,
        "server_create_time": created,
        "backend": "Vulkan",
        "vulkan_device": "Intel(R) Arc(TM) 140V GPU",
        "context": 8192,
        "gpu_layers": 10,
        "parallel": 1,
        "kv_k": "f16",
        "kv_v": "f16",
        "reasoning_mode": "off",
        "temperature": TEMPERATURE,
        "seed": SEED,
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": state["prompt_sha256"],
        "benchmark_hashes": state["benchmark_hashes"],
        "manifest_sha256": state["manifest_sha256"],
        "schema_sha256": state["schema_sha256"],
        "scorer_sha256": state["scorer_sha256"],
        "harness_commit": EXPECTED_HEAD,
        "certified_harness_sha256": state["certified_harness_sha256"],
        "heldout_runner_sha256": state["heldout_runner_sha256"],
        "server_command": proc.cmdline(),
    }
    durable_json(OUT / "heldout-runtime-freeze.json", freeze)
    if not state["pass"]:
        raise SystemExit("pre-held-out freeze validation failed")


def load_cases_after_marker() -> list[dict]:
    cases = []
    with (BENCH / "test.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                cases.append(json.loads(line))
    if len(cases) != 700:
        raise RuntimeError(f"expected 700 held-out cases, found {len(cases)}")
    ids = [case["case_id"] for case in cases]
    if len(set(ids)) != 700:
        raise RuntimeError("held-out contains duplicate case_id")
    return cases


def summarize_slice(cases: list[dict], predictions: dict[str, dict]) -> dict:
    family_values: dict[str, list[float]] = defaultdict(list)
    values: list[float] = []
    for case in cases:
        pred = predictions.get(case["case_id"], {})
        primary = float(score_case(case, pred).get("primary", 0.0))
        values.append(primary)
        family_values[case["family"]].append(primary)
    family_primary = {
        fam: sum(vals) / len(vals) for fam, vals in sorted(family_values.items()) if vals
    }
    return {
        "cases": len(cases),
        "case_primary_mean": sum(values) / len(values) if values else None,
        "family_primary": family_primary,
        "macro_family_primary": (
            sum(family_primary.values()) / len(family_primary) if family_primary else None
        ),
    }


def family_counterfactual(cases: list[dict], predictions: dict[str, dict]) -> dict:
    out = {}
    for family in sorted({case["family"] for case in cases}):
        groups: dict[str, list[dict]] = defaultdict(list)
        for case in cases:
            if case["family"] == family and case.get("counterfactual_group_id"):
                groups[case["counterfactual_group_id"]].append(case)
        if not groups:
            out[family] = None
            continue
        good = 0
        for grouped in groups.values():
            if all(
                score_case(case, predictions.get(case["case_id"], {})).get("primary", 0.0) == 1.0
                for case in grouped
            ):
                good += 1
        out[family] = good / len(groups)
    return out


def enrich_score(base_score: dict, cases: list[dict], rows: list[dict]) -> dict:
    predictions = {row["case_id"]: row.get("prediction", {}) for row in rows}
    language = {}
    for key in ("vi", "vi_en", "en"):
        language[key] = summarize_slice(
            [case for case in cases if case.get("language_group") == key], predictions
        )
    difficulty = {}
    for key in ("straightforward", "contextual", "adversarial"):
        difficulty[key] = summarize_slice(
            [case for case in cases if case.get("difficulty") == key], predictions
        )
    result = dict(base_score)
    result["language_slices"] = language
    result["difficulty_slices"] = difficulty
    result["family_counterfactual_consistency"] = family_counterfactual(cases, predictions)
    return result


def run_scoring(cases: list[dict], rows: list[dict]) -> dict:
    scorer = ROOT / "scripts" / "score_track_a_v1.py"
    if sha256_file(scorer) != EXPECTED_SCORER_SHA256:
        raise RuntimeError("frozen scorer hash changed before scoring")
    output = subprocess.check_output(
        [
            sys.executable,
            str(scorer),
            "--cases",
            str(BENCH / "test.jsonl"),
            "--predictions",
            str(OUT / "heldout-predictions.jsonl"),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    base = json.loads(output)
    return enrich_score(base, cases, rows)


def execute(pid: int) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    marker_path = OUT / "heldout-one-shot-marker.json"
    predictions_path = OUT / "heldout-predictions.jsonl"
    heartbeat_path = OUT / "heartbeat.json"
    summary_path = OUT / "heldout-run-summary.json"
    resource_path = OUT / "resource-summary.json"
    score_path = OUT / "heldout-score.json"
    verdict_path = OUT / "qualification-verdict.json"
    failure_path = OUT / "heldout-failure.json"

    if marker_path.exists() or predictions_path.exists() or heartbeat_path.exists():
        raise SystemExit("held-out one-shot already started; resume/rerun forbidden")
    if not (OUT / "precheck.json").exists() or not (OUT / "heldout-runtime-freeze.json").exists():
        raise SystemExit("precheck/runtime freeze missing")

    proc, created, state = current_freeze(pid)
    if not state["pass"]:
        raise SystemExit("runtime continuity/freeze failed before marker")
    recorded_precheck = json.loads((OUT / "precheck.json").read_text(encoding="utf-8"))
    recorded_freeze = json.loads((OUT / "heldout-runtime-freeze.json").read_text(encoding="utf-8"))
    if recorded_precheck.get("pass") is not True:
        raise SystemExit("recorded precheck is not PASS")
    if recorded_freeze.get("heldout_runner_sha256") != sha256_file(Path(__file__).resolve()):
        raise SystemExit("held-out runner hash changed after precheck")

    marker = {
        "timestamp": utc_now(),
        "status": "START AUTHORIZED",
        "start_case": 1,
        "planned_cases": 700,
        "resume_allowed": "NO",
        "server_pid": pid,
        "repository_head": state["repository_head"],
        "heldout_runner_sha256": sha256_file(Path(__file__).resolve()),
    }
    exclusive_json(marker_path, marker)

    runner_pid = os.getpid()
    run_id = f"track-a-heldout-final-{int(time.time())}"
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

    rows: list[dict] = []
    cases: list[dict] = []
    snapshots: list[dict] = []
    failure = None
    interrupted = False
    unhandled = None
    exit_code = 2
    complete = False

    def signal_handler(signum, _frame):
        raise HeldoutInterrupted(f"signal {signum}")

    installed = []
    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            installed.append((sig, signal.getsignal(sig)))
            signal.signal(sig, signal_handler)

    try:
        cases = load_cases_after_marker()
        snapshots.append(resource_snapshot(runner_pid, pid, "start", 0))
        milestones = {175: "25%", 350: "50%", 525: "75%", 700: "100%"}

        with predictions_path.open("x", encoding="utf-8", newline="\n") as handle:
            for sequence_index, case in enumerate(cases, 1):
                heartbeat.update(
                    last_case_started=sequence_index,
                    last_update=utc_now(),
                    status="RUNNING",
                )
                durable_json(heartbeat_path, heartbeat)

                if not server_alive(pid, created):
                    raise RuntimeError("llama-server lifetime changed before request")
                processes = infer_processes()
                if len(processes) != 1 or processes[0].get("pid") != pid:
                    raise RuntimeError(f"inference isolation violation: {processes}")

                try:
                    model_result = call_model("http://127.0.0.1:8080", case, TIMEOUT_SECONDS)
                except AssertionError as exc:
                    model_result = {
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

                prediction = model_result.get("parsed_response", {})
                row = {
                    "sequence_index": sequence_index,
                    "case_id": case["case_id"],
                    "server_pid": pid,
                    "request_start_timestamp": model_result.get("request_start_timestamp"),
                    "request_end_timestamp": model_result.get("request_end_timestamp"),
                    "transport_status": model_result.get("transport_status"),
                    "http_status": model_result.get("http_status"),
                    "latency_seconds": model_result.get("latency_seconds"),
                    "raw_response": model_result.get("raw_response", ""),
                    "parse_status": model_result.get("parse_status"),
                    "parsed_prediction": prediction,
                    "prediction": prediction,
                    "validator_status": model_result.get("validator_status"),
                    "prompt_tokens": model_result.get("prompt_tokens"),
                    "output_tokens": model_result.get("output_tokens"),
                    "prompt_tok_s": model_result.get("prompt_tok_s"),
                    "decode_tok_s": model_result.get("decode_tok_s"),
                    "transport_error": model_result.get("transport_error"),
                    "server_alive_after": server_alive(pid, created),
                }
                append_jsonl(handle, row)
                rows.append(row)
                heartbeat.update(last_case_completed=sequence_index, last_update=utc_now())
                durable_json(heartbeat_path, heartbeat)

                if sequence_index in milestones:
                    snapshots.append(resource_snapshot(runner_pid, pid, milestones[sequence_index], sequence_index))
                print(
                    json.dumps(
                        {
                            "done": sequence_index,
                            "total": 700,
                            "case_id": case["case_id"],
                            "transport": row["transport_status"],
                            "parse": row["parse_status"],
                        }
                    ),
                    flush=True,
                )

                if row["validator_status"] != "PASS":
                    raise RuntimeError("validator failure; held-out invalid")
                if row["transport_status"] != "ok" or row["http_status"] != 200:
                    raise RuntimeError("transport failure; held-out invalid; no retry")
                if not row["server_alive_after"]:
                    raise RuntimeError("server not alive after request; held-out invalid")

        indices = [row["sequence_index"] for row in rows]
        case_ids = [row["case_id"] for row in rows]
        expected_ids = [case["case_id"] for case in cases]
        complete = (
            len(rows) == 700
            and indices == list(range(1, 701))
            and len(set(indices)) == 700
            and case_ids == expected_ids
            and all(row["transport_status"] == "ok" and row["http_status"] == 200 for row in rows)
            and all(row["validator_status"] == "PASS" for row in rows)
            and server_alive(pid, created)
        )
        if not complete:
            raise RuntimeError("held-out final integrity gate failed")
        heartbeat["status"] = "COMPLETED"
        heartbeat["exit_reason"] = "normal_completion"
        exit_code = 0
    except HeldoutInterrupted as exc:
        interrupted = True
        failure = {"classification": "CLIENT_RUNNER_INTERRUPTED", "detail": str(exc)}
        heartbeat["status"] = "INTERRUPTED"
        heartbeat["exit_reason"] = str(exc)
        exit_code = 130
    except BaseException as exc:
        unhandled = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        classification = "CLIENT_RUNNER_FAILURE_SERVER_ALIVE" if server_alive(pid, created) else "SERVER_FAILURE"
        failure = {"classification": classification, "detail": repr(exc)}
        heartbeat["status"] = "FAILED"
        heartbeat["exit_reason"] = repr(exc)
        exit_code = 2
    finally:
        for sig, previous in installed:
            signal.signal(sig, previous)
        try:
            snapshots.append(resource_snapshot(runner_pid, pid, "final", len(rows)))
        except Exception:
            pass
        heartbeat.update(last_update=utc_now(), finalizer_executed=True)
        durable_json(heartbeat_path, heartbeat)
        durable_json(resource_path, summarize_resources(snapshots))

        indices = [row.get("sequence_index") for row in rows]
        expected = set(range(1, 701))
        actual = set(index for index in indices if isinstance(index, int))
        duplicates = sorted({index for index in indices if indices.count(index) > 1})
        latencies = [float(row["latency_seconds"]) for row in rows if row.get("transport_status") == "ok"]
        prompt_rates = [float(row["prompt_tok_s"]) for row in rows if row.get("prompt_tok_s") is not None]
        decode_rates = [float(row["decode_tok_s"]) for row in rows if row.get("decode_tok_s") is not None]
        summary = {
            "run_id": run_id,
            "started_at": started_at,
            "finished_at": utc_now(),
            "planned": 700,
            "completed": len(rows),
            "telemetry_rows": len(rows),
            "missing_indices": sorted(expected - actual),
            "duplicate_indices": duplicates,
            "exact_index_order": indices == list(range(1, len(rows) + 1)),
            "correct_heldout_order": bool(cases) and [row.get("case_id") for row in rows] == [case["case_id"] for case in cases[: len(rows)]],
            "transport_errors": sum(row.get("transport_status") != "ok" for row in rows),
            "timeouts": sum("timeout" in str(row.get("transport_error", "")).lower() for row in rows),
            "parse_outcomes": sum(bool(row.get("parse_status")) for row in rows),
            "validator_outcomes": sum(bool(row.get("validator_status")) for row in rows),
            "runner_unexpected_termination": False,
            "interrupted": interrupted,
            "unhandled_exception": unhandled,
            "server_pid": pid,
            "server_pid_unchanged": server_alive(pid, created),
            "server_alive_afterward": server_alive(pid, created),
            "server_crashes": 0 if server_alive(pid, created) else 1,
            "server_restarts": 0 if server_alive(pid, created) else None,
            "heartbeat_final": heartbeat["status"],
            "finalizer_executed": True,
            "runner_exit_code": exit_code,
            "latency_seconds": {
                "mean": statistics.fmean(latencies) if latencies else None,
                "median": statistics.median(latencies) if latencies else None,
                "p95": percentile95(latencies),
                "min": min(latencies) if latencies else None,
                "max": max(latencies) if latencies else None,
            },
            "mean_prompt_tok_s": statistics.fmean(prompt_rates) if prompt_rates else None,
            "mean_decode_tok_s": statistics.fmean(decode_rates) if decode_rates else None,
            "heldout": "700/700 COMPLETE" if complete and exit_code == 0 else "INVALID / INCOMPLETE",
            "failure": failure,
        }
        durable_json(summary_path, summary)

    if not complete or exit_code != 0:
        durable_json(
            failure_path,
            {
                "heldout": "INVALID / INCOMPLETE",
                "last_completed_index": len(rows),
                "last_completed_case": rows[-1]["case_id"] if rows else None,
                "failure": failure,
                "reference_verdict": "NOT EVALUATED",
                "server_pid": pid,
                "server_alive": server_alive(pid, created),
                "resume_allowed": "NO",
            },
        )
        return exit_code

    score = run_scoring(cases, rows)
    durable_json(score_path, score)
    rve = bool(score.get("RVE_PASS"))
    tue = bool(score.get("TUE_PASS"))
    reference_verdict = (
        "ADMIT_STRONG_REFERENCE"
        if tue
        else "ADMIT_LIMITED_REFERENCE"
        if rve
        else "REJECT_AS_QUALITY_REFERENCE"
    )
    verdict = {
        "heldout": "700/700 COMPLETE",
        "RVE": "PASS" if rve else "FAIL",
        "TUE": "PASS" if tue else "FAIL",
        "reference_verdict": reference_verdict,
        "server_pid": pid,
        "server_pid_unchanged": True,
        "server_alive_afterward": server_alive(pid, created),
        "scope": {
            "ollama_used": False,
            "benchmark_truth_changed": False,
            "scorer_changed": False,
            "schema_changed": False,
            "manifest_changed": False,
            "rve_tue_changed": False,
            "prompt_changed": False,
            "model_kernel_changed": False,
            "token_model_changed": False,
            "ppf_changed": False,
            "n4_started": False,
            "training_started": False,
            "distillation_started": False,
        },
    }
    durable_json(verdict_path, verdict)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("precheck", "execute"), required=True)
    parser.add_argument("--pid", type=int, default=PID)
    args = parser.parse_args()
    if args.mode == "precheck":
        write_precheck_and_freeze(args.pid)
        return 0
    return execute(args.pid)


if __name__ == "__main__":
    raise SystemExit(main())

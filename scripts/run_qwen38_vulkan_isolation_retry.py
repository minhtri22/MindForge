#!/usr/bin/env python3
"""Run the N3.R1-B.V isolated Vulkan stability gates against one llama-server.

This is qualification/runtime tooling only. It does not read benchmark truth for
prompt construction, does not score cases, and never changes benchmark files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import psutil

from run_qwen38_track_a_reference_eval import SYSTEM, parse_prediction, prompt_for


PROMPT_SHA256 = "6e9325e89991df4244336e6ff8fc7effbf55fba1d53213ce6c014f58abece80d"
MODEL_NAME = "Qwen3.8-27B-Q4_K_M"
SEED = 20260904
TEMPERATURE = 0.0
DETERMINISM_IDS = [
    "A1-C-000",
    "A1-C-001",
    "A1-C-004",
    "A2-C-000",
    "A2-C-001",
    "A2-C-005",
    "A3-C-002",
    "A3-C-000",
    "A3-C-004",
    "A4-C-000",
    "A4-C-001",
    "A4-C-007",
    "A5-C-002",
    "A5-C-003",
    "A5-C-000",
    "A6-C-002",
    "A6-C-003",
    "A6-C-000",
    "A7-C-002",
    "A7-C-000",
]


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ResourceMonitor:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.proc = psutil.Process(pid)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.samples = 0
        self.peak_server_rss = 0
        self.peak_server_private = 0
        self.peak_system_used = 0
        self.min_system_available = 2**63 - 1
        self.peak_swap_used = 0

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> dict:
        self.stop_event.set()
        self.thread.join(timeout=5)
        return {
            "samples": self.samples,
            "server_pid": self.pid,
            "peak_server_rss_bytes": self.peak_server_rss,
            "peak_server_private_bytes": self.peak_server_private,
            "peak_system_used_physical_bytes": self.peak_system_used,
            "min_system_available_physical_bytes": (
                None if self.samples == 0 else self.min_system_available
            ),
            "peak_swap_used_bytes": self.peak_swap_used,
        }

    def _run(self) -> None:
        while not self.stop_event.is_set():
            try:
                mem = self.proc.memory_info()
                vm = psutil.virtual_memory()
                sw = psutil.swap_memory()
                self.samples += 1
                self.peak_server_rss = max(self.peak_server_rss, int(mem.rss))
                private = int(getattr(mem, "private", 0))
                self.peak_server_private = max(self.peak_server_private, private)
                self.peak_system_used = max(self.peak_system_used, int(vm.used))
                self.min_system_available = min(self.min_system_available, int(vm.available))
                self.peak_swap_used = max(self.peak_swap_used, int(sw.used))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            self.stop_event.wait(1.0)


class Runner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.outdir = args.outdir
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.proc = psutil.Process(args.pid)
        self.proc_create_time = self.proc.create_time()
        self.monitor = ResourceMonitor(args.pid)

    def server_alive(self) -> bool:
        try:
            proc = psutil.Process(self.args.pid)
            return proc.is_running() and proc.create_time() == self.proc_create_time
        except psutil.NoSuchProcess:
            return False

    def request(self, messages: list[dict], max_tokens: int, parse_json: bool) -> dict:
        body = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": TEMPERATURE,
            "seed": SEED,
            "max_tokens": max_tokens,
            "stream": False,
        }
        req = urllib.request.Request(
            self.args.base_url.rstrip("/") + "/v1/chat/completions",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.args.timeout) as response:
                status_code = response.status
                payload = json.loads(response.read().decode("utf-8"))
            elapsed = time.perf_counter() - started
            raw = payload["choices"][0]["message"].get("content") or ""
            prediction: dict = {}
            parse_status = "not_requested"
            if parse_json:
                prediction, parse_status = parse_prediction(raw)
            return {
                "status": "ok",
                "http_status": status_code,
                "raw_output": raw,
                "prediction": prediction,
                "parse_status": parse_status,
                "elapsed_seconds": elapsed,
                "usage": payload.get("usage", {}),
                "timings": payload.get("timings", {}),
                "server_alive_after": self.server_alive(),
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": repr(exc),
                "elapsed_seconds": time.perf_counter() - started,
                "server_alive_after": self.server_alive(),
            }

    @staticmethod
    def summary_stats(rows: list[dict]) -> dict:
        latencies = [float(row["elapsed_seconds"]) for row in rows if row.get("status") == "ok"]
        prompt_rates = [
            float(row.get("timings", {}).get("prompt_per_second"))
            for row in rows
            if row.get("timings", {}).get("prompt_per_second") is not None
        ]
        decode_rates = [
            float(row.get("timings", {}).get("predicted_per_second"))
            for row in rows
            if row.get("timings", {}).get("predicted_per_second") is not None
        ]
        return {
            "requests": len(rows),
            "transport_success": sum(row.get("status") == "ok" for row in rows),
            "transport_errors": sum(row.get("status") != "ok" for row in rows),
            "parsed": sum(str(row.get("parse_status", "")).startswith("json") for row in rows),
            "latency_seconds": {
                "min": min(latencies) if latencies else None,
                "median": statistics.median(latencies) if latencies else None,
                "max": max(latencies) if latencies else None,
                "mean": statistics.fmean(latencies) if latencies else None,
            },
            "prompt_tok_s": {
                "min": min(prompt_rates) if prompt_rates else None,
                "median": statistics.median(prompt_rates) if prompt_rates else None,
                "max": max(prompt_rates) if prompt_rates else None,
                "mean": statistics.fmean(prompt_rates) if prompt_rates else None,
            },
            "decode_tok_s": {
                "min": min(decode_rates) if decode_rates else None,
                "median": statistics.median(decode_rates) if decode_rates else None,
                "max": max(decode_rates) if decode_rates else None,
                "mean": statistics.fmean(decode_rates) if decode_rates else None,
            },
        }

    def fail(self, phase: str, reason: str) -> int:
        def phase_status(filename: str) -> str:
            path = self.outdir / filename
            if not path.exists():
                return "NOT RUN"
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return "FAIL"
            return "PASS" if payload.get("pass") is True else "FAIL"

        write_json(
            self.outdir / "vulkan-isolation-verdict.json",
            {
                "v0_smoke": phase_status("v0-smoke.json"),
                "v1_sequential_10": phase_status("v1-sequential-10.json"),
                "v2_calibration_20": phase_status("v2-calibration-20.json"),
                "v3_determinism": phase_status("v3-determinism.json"),
                "v4_development": phase_status("v4-development.json"),
                "heldout": "NOT RUN",
                "vulkan_verdict": "UNSUITABLE FOR FULL QUALIFICATION",
                "reference_verdict": "NOT EVALUATED",
                "practicality": {"cpu": "CONSTRAINED", "vulkan": "UNSUITABLE", "overall": "CONSTRAINED"},
                "failed_phase": phase,
                "stop_reason": reason,
                "scope": {
                    "ollama_used": False,
                    "benchmark_truth_changed": False,
                    "scorer_changed": False,
                    "model_kernel_changed": False,
                    "ppf_changed": False,
                    "n4_started": False,
                    "distillation_started": False,
                },
            },
        )
        return 2

    def run_v0(self) -> bool:
        row = self.request([{"role": "user", "content": "Return exactly: OK"}], 8, False)
        result = {
            "phase": "V0",
            "prompt": "Return exactly: OK",
            "result": row,
            "exact_ok": row.get("raw_output", "").strip() == "OK",
            "pid": self.args.pid,
            "pid_unchanged": self.server_alive(),
            "pass": row.get("status") == "ok" and self.server_alive(),
        }
        write_json(self.outdir / "v0-smoke.json", result)
        print(json.dumps({"phase": "V0", "pass": result["pass"], "elapsed": row.get("elapsed_seconds")}), flush=True)
        return bool(result["pass"])

    def run_v1(self) -> bool:
        rows = []
        for index in range(10):
            if not self.server_alive():
                break
            row = self.request([{"role": "user", "content": "Return exactly: OK"}], 8, False)
            row["request_index"] = index + 1
            rows.append(row)
            print(json.dumps({"phase": "V1", "done": index + 1, "status": row["status"]}), flush=True)
            if row.get("status") != "ok" or not row.get("server_alive_after"):
                break
        summary = self.summary_stats(rows)
        passed = len(rows) == 10 and summary["transport_success"] == 10 and self.server_alive()
        write_json(
            self.outdir / "v1-sequential-10.json",
            {"phase": "V1", "rows": rows, "summary": summary, "pid": self.args.pid, "pid_unchanged": self.server_alive(), "pass": passed},
        )
        return passed

    def benchmark_row(self, case: dict) -> dict:
        prompt = prompt_for(case)
        row = self.request(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            self.args.max_tokens,
            True,
        )
        row["case_id"] = case["case_id"]
        return row

    def run_cases(self, phase: str, cases: list[dict], progress_every: int = 1) -> list[dict]:
        rows: list[dict] = []
        for index, case in enumerate(cases, 1):
            if not self.server_alive():
                break
            row = self.benchmark_row(case)
            rows.append(row)
            if index % progress_every == 0 or index == len(cases):
                print(
                    json.dumps({"phase": phase, "done": index, "total": len(cases), "status": row["status"], "case_id": case["case_id"]}),
                    flush=True,
                )
            if row.get("status") != "ok" or not row.get("server_alive_after"):
                break
        return rows

    def run_v2(self, calibration: list[dict]) -> bool:
        cases = calibration[:20]
        rows = self.run_cases("V2", cases)
        summary = self.summary_stats(rows)
        passed = len(rows) == 20 and summary["transport_success"] == 20 and self.server_alive()
        write_json(
            self.outdir / "v2-calibration-20.json",
            {"phase": "V2", "case_ids": [c["case_id"] for c in cases], "rows": rows, "summary": summary, "pid": self.args.pid, "pid_unchanged": self.server_alive(), "pass": passed},
        )
        return passed

    def run_v3(self, calibration: list[dict]) -> bool:
        by_id = {case["case_id"]: case for case in calibration}
        missing = [case_id for case_id in DETERMINISM_IDS if case_id not in by_id]
        if missing:
            raise RuntimeError(f"determinism cases missing: {missing}")
        cases = [by_id[case_id] for case_id in DETERMINISM_IDS]
        pass1 = self.run_cases("V3-pass1", cases)
        if len(pass1) != 20 or any(row.get("status") != "ok" for row in pass1) or not self.server_alive():
            pass2: list[dict] = []
        else:
            pass2 = self.run_cases("V3-pass2", cases)
        raw_matches = sum(
            a.get("raw_output") == b.get("raw_output") for a, b in zip(pass1, pass2, strict=False)
        )
        parsed_matches = sum(
            a.get("prediction") == b.get("prediction") for a, b in zip(pass1, pass2, strict=False)
        )
        passed = (
            len(pass1) == 20
            and len(pass2) == 20
            and all(row.get("status") == "ok" for row in pass1 + pass2)
            and self.server_alive()
        )
        write_json(
            self.outdir / "v3-determinism.json",
            {
                "phase": "V3",
                "selection_case_ids": DETERMINISM_IDS,
                "prior_selection_sha256": "8cfd4628414091adff0cc15c7a690c0baeed343bf03ac5a442feec0982488933",
                "pass1": pass1,
                "pass2": pass2,
                "pass1_summary": self.summary_stats(pass1),
                "pass2_summary": self.summary_stats(pass2),
                "raw_exact_match": {"count": raw_matches, "total": 20, "rate": raw_matches / 20 if len(pass2) == 20 else None},
                "parsed_exact_match": {"count": parsed_matches, "total": 20, "rate": parsed_matches / 20 if len(pass2) == 20 else None},
                "pid": self.args.pid,
                "pid_unchanged": self.server_alive(),
                "pass": passed,
            },
        )
        return passed

    def run_v4(self, development: list[dict]) -> bool:
        if len(development) != 420:
            raise RuntimeError(f"expected 420 development cases, found {len(development)}")
        rows = self.run_cases("V4", development, progress_every=5)
        summary = self.summary_stats(rows)
        passed = len(rows) == 420 and summary["transport_success"] == 420 and self.server_alive()
        write_json(
            self.outdir / "v4-development.json",
            {"phase": "V4", "total_expected": 420, "rows": rows, "summary": summary, "pid": self.args.pid, "pid_unchanged": self.server_alive(), "pass": passed},
        )
        return passed

    def run(self) -> int:
        if sha256_file(self.args.prompt_template) != PROMPT_SHA256:
            raise RuntimeError("frozen prompt SHA256 mismatch")
        calibration = read_jsonl(self.args.calibration)
        development = read_jsonl(self.args.development)
        if not self.server_alive():
            raise RuntimeError("llama-server PID is not alive before V0")

        self.monitor.start()
        try:
            if not self.run_v0():
                return self.fail("V0", "single-request transport/server-alive gate failed")
            if not self.run_v1():
                return self.fail("V1", "10-request sequential stability gate failed")
            if not self.run_v2(calibration):
                return self.fail("V2", "20-case calibration transport stability gate failed")
            if not self.run_v3(calibration):
                return self.fail("V3", "20x2 determinism transport stability gate failed")
            if not self.run_v4(development):
                return self.fail("V4", "420-case development transport stability gate failed")
            write_json(
                self.outdir / "vulkan-isolation-verdict.json",
                {
                    "v0_smoke": "PASS",
                    "v1_sequential_10": "PASS",
                    "v2_calibration_20": "PASS",
                    "v3_determinism": "PASS",
                    "v4_development": "PASS",
                    "heldout": "NOT RUN",
                    "vulkan_verdict": "STABLE UNDER ISOLATION",
                    "reference_verdict": "NOT EVALUATED",
                    "scope": {
                        "ollama_used": False,
                        "benchmark_truth_changed": False,
                        "scorer_changed": False,
                        "model_kernel_changed": False,
                        "ppf_changed": False,
                        "n4_started": False,
                        "distillation_started": False,
                    },
                },
            )
            return 0
        finally:
            write_json(self.outdir / "resource-summary.json", self.monitor.stop())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--prompt-template", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args()
    raise SystemExit(Runner(args).run())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Finalize an externally interrupted Qwen3.8 held-out run without resuming it.

This tool performs no inference and never invokes the frozen scorer. It exists
only to close evidence after the one-shot client runner has disappeared while
the llama-server process remains alive.
"""

from __future__ import annotations

import json
from pathlib import Path
import time

import psutil


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/track-a-qwen38-reference-v1-vulkan-retry"


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8-sig"))


def write(name: str, value: dict) -> None:
    path = OUT / name
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    start = load("heldout-start.json")
    progress = load("heldout-progress.json")
    v4_resources = load("resource-summary-v4-resume-258.json")
    isolation = load("vulkan-isolation-verdict.json")

    pid = int(start["pid"])
    assert progress["pid"] == pid
    assert progress["completed"] < progress["expected"] == 700
    assert progress["summary"]["requests"] == progress["completed"]
    assert progress["summary"]["transport_success"] == progress["completed"]
    assert progress["summary"]["transport_errors"] == 0

    rows = [
        json.loads(line)
        for line in (OUT / "heldout-predictions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == progress["completed"]
    assert rows[-1]["case_id"] == progress["last_case"]
    assert all(r["status"] == "ok" and r["server_alive_after"] for r in rows)

    proc = psutil.Process(pid)
    assert proc.is_running()
    assert proc.create_time() == start["server_create_time"]

    runner_pids = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        cmd = " ".join(p.info.get("cmdline") or [])
        if "complete_qwen38_vulkan_qualification.py" in cmd:
            runner_pids.append(p.info["pid"])
    assert not runner_pids, f"held-out runner still active: {runner_pids}"

    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    closure_snapshot = {
        "captured_epoch": time.time(),
        "server_pid": pid,
        "server_alive": True,
        "server_rss_bytes": proc.memory_info().rss,
        "server_private_bytes": getattr(proc.memory_full_info(), "private", None),
        "system_total_physical_bytes": vm.total,
        "system_available_physical_bytes": vm.available,
        "system_used_physical_bytes": vm.used,
        "swap_used_bytes": swap.used,
    }

    failure = {
        "classification": "CLIENT_RUNNER_TERMINATED_SERVER_ALIVE",
        "root_cause": "UNPROVEN",
        "detail": (
            "The one-shot client runner process is no longer present after checkpoint 175. "
            "The same llama-server PID remains alive. Completed rows contain no transport error. "
            "Protocol forbids resume/rerun to rescue the held-out run."
        ),
        "last_successful_index": progress["completed"],
        "last_successful_case": progress["last_case"],
    }

    heldout_resource = {
        "phase": "HELDOUT",
        "status": "INVALID / INCOMPLETE",
        "completed": progress["completed"],
        "expected": 700,
        "monitor_summary_available": False,
        "monitor_summary_reason": (
            "The client runner terminated before its finally block could persist monitor.stop()."
        ),
        "gpu_memory_peak_bytes": None,
        "gpu_memory_peak_status": "UNAVAILABLE; no authoritative held-out GPU peak was persisted",
        "closure_snapshot": closure_snapshot,
        "failure": failure,
    }
    write("resource-summary-heldout.json", heldout_resource)

    resource_summary = {
        "server_pid": pid,
        "known_observed_peak_server_private_bytes": v4_resources["peak_server_private_bytes"],
        "known_observed_peak_server_rss_bytes": v4_resources["peak_server_rss_bytes"],
        "known_observed_peak_system_used_physical_bytes": v4_resources[
            "peak_system_used_physical_bytes"
        ],
        "known_observed_peak_swap_used_bytes": v4_resources["peak_swap_used_bytes"],
        "v4_resume": v4_resources,
        "heldout_partial": {
            "completed": progress["completed"],
            "expected": 700,
            "summary": progress["summary"],
            "resource_peak_status": "INCOMPLETE; held-out monitor final summary unavailable",
            "closure_snapshot": closure_snapshot,
        },
        "gpu_memory_peak_bytes": None,
        "gpu_memory_peak_status": "UNAVAILABLE; do not infer from unmapped Windows adapter counters",
    }
    write("resource-summary.json", resource_summary)

    progress["state"] = "INVALID / INCOMPLETE"
    progress["failure"] = failure
    progress["server_alive_at_closure"] = True
    write("heldout-progress.json", progress)

    isolation["heldout"] = "INVALID / INCOMPLETE"
    isolation["heldout_completed"] = progress["completed"]
    isolation["heldout_expected"] = 700
    isolation["heldout_failure"] = failure
    isolation["reference_verdict"] = "NOT EVALUATED"
    write("vulkan-isolation-verdict.json", isolation)

    write(
        "heldout-score.json",
        {
            "status": "NOT SCORED",
            "reason": "Frozen scorer may run only after 700/700; held-out stopped at 175/700.",
            "scorer_invoked": False,
            "completed": progress["completed"],
            "expected": 700,
        },
    )

    write(
        "qualification-verdict.json",
        {
            "heldout": "INVALID / INCOMPLETE",
            "completed": progress["completed"],
            "expected": 700,
            "reference_verdict": "NOT EVALUATED",
            "pid": pid,
            "server_alive": True,
            "failure": failure,
            "summary": progress["summary"],
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

    print(
        json.dumps(
            {
                "heldout": "INVALID / INCOMPLETE",
                "completed": progress["completed"],
                "reference_verdict": "NOT EVALUATED",
                "server_pid": pid,
                "server_alive": True,
            }
        )
    )


if __name__ == "__main__":
    main()

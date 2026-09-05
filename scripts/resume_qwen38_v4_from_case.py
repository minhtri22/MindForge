#!/usr/bin/env python3
"""Resume the isolated Qwen3.8 Vulkan V4 development gate on one live server.

The runner is intentionally sequential and checkpoints after every completed
case so an outer terminal/session interruption does not discard evidence.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_qwen38_vulkan_isolation_retry import (
    PROMPT_SHA256,
    ResourceMonitor,
    Runner,
    read_jsonl,
    sha256_file,
    write_json,
)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--prompt-template", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--start-index", type=int, required=True, help="1-based development case index")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    if args.start_index < 1:
        raise SystemExit("--start-index must be >= 1")
    if sha256_file(args.prompt_template) != PROMPT_SHA256:
        raise SystemExit("frozen prompt SHA256 mismatch")

    development = read_jsonl(args.development)
    if len(development) != 420:
        raise SystemExit(f"expected 420 development cases, found {len(development)}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    rows_path = args.outdir / f"v4-development-resume-{args.start_index}.jsonl"
    summary_path = args.outdir / f"v4-development-resume-{args.start_index}.json"
    resource_path = args.outdir / f"resource-summary-v4-resume-{args.start_index}.json"

    runner = Runner(args)
    if not runner.server_alive():
        raise SystemExit(f"llama-server PID {args.pid} is not alive before resume")

    target = development[args.start_index - 1 :]
    existing = load_existing(rows_path)
    if existing:
        expected_prefix = [case["case_id"] for case in target[: len(existing)]]
        actual_prefix = [row.get("case_id") for row in existing]
        if actual_prefix != expected_prefix:
            raise SystemExit("existing resume evidence does not match expected case prefix")
        if any(row.get("status") != "ok" for row in existing):
            raise SystemExit("existing resume evidence contains a failed transport row")

    next_offset = len(existing)
    monitor = ResourceMonitor(args.pid)
    monitor.start()
    started_wall = time.time()
    rows = list(existing)

    def checkpoint(pass_value: bool | None = None, stop_reason: str | None = None) -> None:
        summary = Runner.summary_stats(rows)
        completed = len(rows)
        payload = {
            "phase": "V4-RESUME",
            "resume_start_index": args.start_index,
            "resume_start_case_id": target[0]["case_id"],
            "resume_expected_cases": len(target),
            "resume_completed_cases": completed,
            "global_last_completed_index": args.start_index + completed - 1 if completed else args.start_index - 1,
            "global_last_completed_case_id": rows[-1]["case_id"] if rows else None,
            "next_global_index": args.start_index + completed if completed < len(target) else None,
            "next_case_id": target[completed]["case_id"] if completed < len(target) else None,
            "pid": args.pid,
            "pid_unchanged": runner.server_alive(),
            "concurrency": 1,
            "summary": summary,
            "pass": pass_value,
            "stop_reason": stop_reason,
            "started_wall_epoch": started_wall,
            "updated_wall_epoch": time.time(),
            "evidence_rows_file": rows_path.name,
        }
        write_json(summary_path, payload)

    checkpoint()
    try:
        for offset, case in enumerate(target[next_offset:], start=next_offset):
            global_index = args.start_index + offset
            if not runner.server_alive():
                checkpoint(False, "server PID not alive before next case")
                raise SystemExit(2)

            row = runner.benchmark_row(case)
            row["global_development_index"] = global_index
            append_jsonl(rows_path, row)
            rows.append(row)

            ok = row.get("status") == "ok" and row.get("server_alive_after") is True
            checkpoint(None if ok else False, None if ok else "transport/server-alive gate failed")
            print(
                json.dumps(
                    {
                        "phase": "V4-RESUME",
                        "done_global": global_index,
                        "total_global": 420,
                        "done_resume": len(rows),
                        "total_resume": len(target),
                        "case_id": case["case_id"],
                        "status": row.get("status"),
                        "server_alive": row.get("server_alive_after"),
                    }
                ),
                flush=True,
            )
            if not ok:
                raise SystemExit(2)

        passed = len(rows) == len(target) and all(row.get("status") == "ok" for row in rows) and runner.server_alive()
        checkpoint(passed, None if passed else "resume completion gate failed")
        raise SystemExit(0 if passed else 2)
    finally:
        write_json(resource_path, monitor.stop())


if __name__ == "__main__":
    main()

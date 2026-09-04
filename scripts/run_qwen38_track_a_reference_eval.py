#!/usr/bin/env python3
"""Run frozen Track-A cases against a local llama.cpp OpenAI-compatible server.

This is qualification tooling only. It never includes benchmark truth in prompts
and it does not modify Track-A scoring semantics.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


SYSTEM = """Return only compact JSON. No markdown. No prose. No hidden reasoning.
Use only supplied context/state/capabilities. Do not invent unavailable tools,
personal facts, or world knowledge. /no_think"""

FIELDS = {
    "A1": {
        "intent_label": [
            "NAVIGATE",
            "MESSAGE",
            "CALL",
            "REMIND",
            "LOCAL_TRANSFORM",
            "LOOKUP_DELEGATE",
            "APP_ACTION",
            "CLARIFY",
        ]
    },
    "A2": {
        "resolved_entity_ids": ["string"],
        "resolved_values": ["string"],
        "clarification_required": "boolean",
    },
    "A3": {"normalized": "object"},
    "A4": {"action_id": "maps|messages|phone|calendar|notes|NONE|CLARIFY"},
    "A5": {"arguments": "object"},
    "A6": {"clarification_required": "boolean", "clarification_reason": "string"},
    "A7": {"route": "LOCAL_MODEL|LOCAL_APP_OR_TOOL|EXTERNAL|CLARIFY"},
}


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def prompt_for(case: dict) -> str:
    payload = {
        "family": case["family"],
        "user_utterance": case["input"]["user_utterance"],
        "current_context": case["input"]["current_context"],
        "personal_state": case["input"]["personal_state"],
        "available_actions": case["input"]["available_actions"],
        "available_local_capabilities": case["input"]["available_local_capabilities"],
        "external_capabilities": case["input"]["external_capabilities"],
        "required_prediction_schema": FIELDS[case["family"]],
    }
    prompt = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\nReturn only the required JSON object. Use exact enum strings. "
        + "Use exactly the keys in required_prediction_schema; no extra keys. /no_think"
    )
    forbidden = ("expected", "truth", "gold", "target answer", "counterfactual partner answer")
    lower = prompt.lower()
    if any(token in lower for token in forbidden):
        raise AssertionError(f"forbidden truth/leakage token in prompt for {case['case_id']}")
    return prompt


def parse_prediction(text: str) -> tuple[dict, str]:
    s = text.strip()
    if "</think>" in s:
        s = s.rsplit("</think>", 1)[1].strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        obj = json.loads(s)
        return (obj if isinstance(obj, dict) else {}, "json")
    except Exception:
        pass
    match = re.search(r"\{.*\}", s, flags=re.S)
    if match:
        try:
            obj = json.loads(match.group(0))
            return (obj if isinstance(obj, dict) else {}, "json_object_extract")
        except Exception:
            pass
    return {}, "parse_error"


def call_case(args: argparse.Namespace, case: dict) -> dict:
    prompt = prompt_for(case)
    body = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": args.temperature,
        "seed": args.seed,
        "max_tokens": args.max_tokens,
        "stream": False,
    }
    req = urllib.request.Request(
        args.base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            obj = json.loads(resp.read().decode("utf-8"))
        elapsed = time.perf_counter() - started
        raw = obj["choices"][0]["message"]["content"]
        prediction, parse_status = parse_prediction(raw)
        return {
            "case_id": case["case_id"],
            "status": "ok",
            "prediction": prediction,
            "parse_status": parse_status,
            "raw_output": raw,
            "elapsed_seconds": elapsed,
            "usage": obj.get("usage", {}),
            "timings": obj.get("timings", {}),
        }
    except Exception as exc:
        return {
            "case_id": case["case_id"],
            "status": "error",
            "prediction": {},
            "parse_status": "error",
            "error": repr(exc),
            "elapsed_seconds": time.perf_counter() - started,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--model", default="Qwen3.8-27B-Q4_K_M")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=20260904)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cases = read_jsonl(args.cases)
    if args.limit:
        cases = cases[: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        rows = [{"case_id": case["case_id"], "prompt": prompt_for(case)} for case in cases]
    else:
        rows_by_id: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(call_case, args, case): case["case_id"] for case in cases}
            for fut in as_completed(futures):
                row = fut.result()
                rows_by_id[row["case_id"]] = row
                done = len(rows_by_id)
                if done % 25 == 0 or done == len(cases):
                    print(json.dumps({"done": done, "total": len(cases)}, ensure_ascii=False), flush=True)
        rows = [rows_by_id[case["case_id"]] for case in cases]

    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    ok = sum(row.get("status") == "ok" for row in rows)
    parsed = sum(row.get("parse_status", "").startswith("json") for row in rows)
    print(json.dumps({"cases": len(rows), "ok": ok, "parsed": parsed, "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()

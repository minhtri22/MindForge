"""PIT-13.1.A API smoke qualification runner.

Research tooling only. This script executes frozen smoke requests and does not
select, rank, or evaluate teachers.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


ENDPOINT = "https://api.xkiro.com/v1/chat/completions"
MODELS = [
    "qwen/qwen3.8-max:free",
    "deepseek/deepseek-v4-pro",
    "minimax/minimax-m3:free",
    "mistralai/mistral-small-2603",
]
SCENARIOS = [
    "stable_preference_001",
    "preference_drift_001",
    "user_correction_001",
    "insufficient_evidence_001",
]
REQUIRED_FIELDS = [
    "observation",
    "inference",
    "confidence",
    "applicability_boundary",
    "revision_trigger",
]


def request_body(scenario: str) -> dict:
    return {
        "model": "",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return JSON only with fields: observation, inference, "
                    "confidence, applicability_boundary, revision_trigger."
                ),
            },
            {"role": "user", "content": f"PIT smoke scenario: {scenario}"},
        ],
    }


def call_api(key: str, model: str, scenario: str) -> dict:
    payload = request_body(scenario)
    payload["model"] = model
    req = Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode())


def parse_response(data: dict) -> dict:
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    parsed = json.loads(content)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="experiments/pit13/smoke")
    args = parser.parse_args()

    key = os.environ.get("XTROUTER_API_KEY")
    if key:
        key = key.strip()
    if not key:
        raise SystemExit("XTROUTER_API_KEY is missing")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    raw = outdir / "raw.jsonl"
    normalized = outdir / "normalized.jsonl"
    results = []

    with raw.open("w", encoding="utf-8") as raw_file, normalized.open("w", encoding="utf-8") as norm_file:
        for model in MODELS:
            for scenario in SCENARIOS:
                record = {
                    "candidate_id": model,
                    "requested_model": model,
                    "scenario_id": scenario,
                    "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                }
                try:
                    response = call_api(key, model, scenario)
                    record["raw_response"] = response
                    parsed = parse_response(response)
                    record["parsed_response"] = parsed
                    record["schema_status"] = all(k in parsed for k in REQUIRED_FIELDS)
                except Exception as exc:
                    record["raw_response"] = {"error": str(exc)}
                    record["parsed_response"] = None
                    record["schema_status"] = False
                raw_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                norm_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                results.append(record)

    (outdir / "results.json").write_text(json.dumps({"records": results}, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

from openai import OpenAI


BASE_URL = "https://api.xkiro.com/v1"
DEFAULT_SCENARIOS_PATH = Path("experiments/pit13/smoke/scenarios.json")
MODELS = [
    "qwen/qwen3.7-max:free",
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


def normalize_json_content(content: str) -> str:
    stripped = content.strip()
    lines = stripped.splitlines()
    if len(lines) >= 2 and lines[0] in {"```", "```json"} and lines[-1] == "```":
        body = "\n".join(lines[1:-1])
        if "```" not in body:
            return body
    return stripped


def load_scenarios(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    mapped = {scenario["scenario_id"]: scenario for scenario in scenarios}
    missing = [scenario_id for scenario_id in SCENARIOS if scenario_id not in mapped]
    if missing:
        raise ValueError(f"Missing scenario evidence: {missing}")
    for scenario_id in SCENARIOS:
        evidence = mapped[scenario_id].get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"Scenario evidence is empty: {scenario_id}")
    return mapped


def model_facing_scenario(scenario: dict) -> dict:
    return {
        "scenario_id": scenario["scenario_id"],
        "evidence": scenario["evidence"],
    }


def request_body(scenario: dict) -> dict:
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
            {
                "role": "user",
                "content": json.dumps(model_facing_scenario(scenario), ensure_ascii=False),
            },
        ],
    }


def call_api(key: str, model: str, scenario: dict) -> dict:
    payload = request_body(scenario)
    payload["model"] = model
    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=60.0)
    response = client.chat.completions.create(**payload)
    return response.model_dump(mode="json")


def parse_response(data: dict) -> dict:
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    parsed = json.loads(normalize_json_content(content))
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="experiments/pit13/smoke")
    parser.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS_PATH))
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
    scenario_map = load_scenarios(Path(args.scenarios))

    with raw.open("w", encoding="utf-8") as raw_file, normalized.open("w", encoding="utf-8") as norm_file:
        for model in MODELS:
            for scenario_id in SCENARIOS:
                scenario = scenario_map[scenario_id]
                record = {
                    "candidate_id": model,
                    "requested_model": model,
                    "scenario_id": scenario_id,
                    "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                }
                try:
                    response = call_api(key, model, scenario)
                    record["raw_response"] = response
                    record["api_status"] = "completed"
                    try:
                        parsed = parse_response(response)
                        record["parsed_response"] = parsed
                        record["schema_status"] = all(k in parsed for k in REQUIRED_FIELDS)
                        record["parse_error"] = None
                    except Exception as exc:
                        record["parsed_response"] = None
                        record["schema_status"] = False
                        record["parse_error"] = str(exc)
                except Exception as exc:
                    record["raw_response"] = {"error": str(exc)}
                    record["api_status"] = "failed"
                    record["parsed_response"] = None
                    record["schema_status"] = False
                    record["parse_error"] = None
                raw_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                norm_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                raw_file.flush()
                norm_file.flush()
                results.append(record)

    (outdir / "results.json").write_text(json.dumps({"records": results}, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

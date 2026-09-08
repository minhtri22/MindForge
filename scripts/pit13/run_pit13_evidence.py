"""PIT-13.1.B frozen evidence collection for smoke-qualified candidates only."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

from openai import OpenAI


BASE_URL = "https://api.xkiro.com/v1"
OUTDIR = Path("experiments/pit13/evidence")
SCENARIOS_PATH = OUTDIR / "scenarios.json"
MODELS = [
    "qwen/qwen3.7-max:free",
    "deepseek/deepseek-v4-pro",
    "minimax/minimax-m3:free",
]
EXCLUDED_MODELS = ["mistralai/mistral-small-2603"]
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


def load_scenarios() -> list[dict]:
    data = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    expected_types = {
        "stable_preference",
        "preference_drift",
        "conflicting_evidence",
        "user_correction",
        "rare_exception",
        "insufficient_evidence",
        "long_term_consistency",
    }
    if len(scenarios) != 7 or {s["scenario_type"] for s in scenarios} != expected_types:
        raise ValueError("Full PIT-13.1.B scenario family set is not exactly frozen")
    for scenario in scenarios:
        if not scenario.get("evidence") or not scenario.get("provenance") or not scenario.get("version"):
            raise ValueError(f"Incomplete scenario provenance: {scenario.get('scenario_id')}")
    return scenarios


def request_payload(model: str, scenario: dict) -> dict:
    return {
        "model": model,
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
                "content": json.dumps(
                    {"scenario_id": scenario["scenario_id"], "evidence": scenario["evidence"]},
                    ensure_ascii=False,
                ),
            },
        ],
    }


def slug(model: str) -> str:
    return model.replace("/", "-").replace(":", "-")


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()


def main() -> int:
    key = os.environ.get("XTROUTER_API_KEY")
    if key:
        key = key.strip()
    if not key:
        raise SystemExit("XTROUTER_API_KEY is missing")

    scenarios = load_scenarios()
    scenario_sha = hashlib.sha256(SCENARIOS_PATH.read_bytes()).hexdigest()
    raw_dir = OUTDIR / "raw"
    normalized_dir = OUTDIR / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    for model in MODELS:
        (raw_dir / f"{slug(model)}.jsonl").unlink(missing_ok=True)
        (normalized_dir / f"{slug(model)}.jsonl").unlink(missing_ok=True)

    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=60.0)
    records: list[dict] = []
    for model in MODELS:
        for scenario in scenarios:
            record = {
                "candidate_id": model,
                "requested_model": model,
                "returned_model": None,
                "scenario_id": scenario["scenario_id"],
                "scenario_type": scenario["scenario_type"],
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "raw_response": None,
                "api_status": "failed",
            }
            try:
                response = client.chat.completions.create(**request_payload(model, scenario))
                raw_response = response.model_dump(mode="json")
                record["raw_response"] = raw_response
                record["api_status"] = "completed"
                record["returned_model"] = raw_response.get("model")
            except Exception as exc:
                record["raw_response"] = {"error": str(exc)}

            append_jsonl(raw_dir / f"{slug(model)}.jsonl", record)

            normalized = {
                "candidate_id": model,
                "scenario_id": scenario["scenario_id"],
                "scenario_type": scenario["scenario_type"],
                "observation": None,
                "inference": None,
                "confidence": None,
                "applicability_boundary": None,
                "revision_trigger": None,
                "schema_status": False,
                "parse_status": "not_attempted",
                "failure_classification": None,
            }
            if record["api_status"] != "completed":
                normalized["failure_classification"] = "TRANSPORT_OR_API_FAILURE"
            elif record["returned_model"] != model:
                normalized["failure_classification"] = "MODEL_IDENTITY_MISMATCH"
            else:
                content = (
                    record["raw_response"].get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                try:
                    parsed = json.loads(normalize_json_content(content))
                    normalized["parse_status"] = "parsed"
                    if all(field in parsed for field in REQUIRED_FIELDS):
                        for field in REQUIRED_FIELDS:
                            normalized[field] = parsed[field]
                        normalized["schema_status"] = True
                    else:
                        normalized["failure_classification"] = "SCHEMA_FIELD_NONCONFORMANCE"
                except Exception:
                    normalized["parse_status"] = "parse_error"
                    normalized["failure_classification"] = "SERIALIZATION_NONCONFORMANCE"

            append_jsonl(normalized_dir / f"{slug(model)}.jsonl", normalized)
            records.append({"raw": record, "normalized": normalized})

    summary = {
        "task": "PIT-13.1.B Evidence Collection",
        "execution_date": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scenario_manifest": str(SCENARIOS_PATH).replace("\\", "/"),
        "scenario_manifest_sha256": scenario_sha,
        "qualified_candidates": MODELS,
        "excluded_candidates": {
            EXCLUDED_MODELS[0]: "EXCLUDED_FROM_EXECUTION_DUE_TO_SMOKE_NONQUALIFICATION"
        },
        "scenario_count": len(scenarios),
        "planned_samples": len(MODELS) * len(scenarios),
        "completed_samples": sum(r["raw"]["api_status"] == "completed" for r in records),
        "schema_valid": sum(r["normalized"]["schema_status"] for r in records),
        "identity_mismatches": sum(
            r["normalized"]["failure_classification"] == "MODEL_IDENTITY_MISMATCH" for r in records
        ),
        "manual_repairs": 0,
        "semantic_retries": 0,
        "per_model_tuning": 0,
    }
    (OUTDIR / "execution-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

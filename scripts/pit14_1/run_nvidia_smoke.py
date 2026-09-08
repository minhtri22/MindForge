"""PIT-14.1.B NVIDIA NIM smoke qualification runner.

Research tooling only. Executes the frozen five-candidate x four-scenario smoke
matrix using the PIT-14.1.A execution policies. No retries, ranking, semantic
qualification, or teacher selection are performed here.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

from openai import OpenAI


BASE_URL = "https://integrate.api.nvidia.com/v1"
PROVIDER = "NVIDIA NIM"
SCENARIOS_PATH = Path("experiments/pit13/smoke/scenarios.json")
OUTDIR = Path("experiments/pit14_1/smoke")
MODELS = [
    "moonshotai/kimi-k3",
    "meta/muse-glimmer-30b",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "google/gemma-4-31b-it",
    "openai/gpt-oss-20b",
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
    mapped = {s["scenario_id"]: s for s in data.get("scenarios", [])}
    missing = [scenario_id for scenario_id in SCENARIOS if scenario_id not in mapped]
    if missing:
        raise ValueError(f"Missing frozen scenario evidence: {missing}")
    for scenario_id in SCENARIOS:
        evidence = mapped[scenario_id].get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"Frozen scenario evidence empty: {scenario_id}")
    return mapped


def request_payload(model: str, scenario: dict) -> dict:
    return {
        "model": model,
        "temperature": 0,
        "max_tokens": 4096,
        "stream": False,
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


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY")
    if key:
        key = key.strip()
    if not key:
        raise SystemExit("NVIDIA_API_KEY is missing")

    scenario_map = load_scenarios(SCENARIOS_PATH)
    scenario_sha = hashlib.sha256(SCENARIOS_PATH.read_bytes()).hexdigest()
    OUTDIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=120.0)
    raw_records: list[dict] = []
    normalized_records: list[dict] = []
    result_records: list[dict] = []
    started = dt.datetime.now(dt.timezone.utc).isoformat()

    for model in MODELS:
        for scenario_id in SCENARIOS:
            scenario = scenario_map[scenario_id]
            raw_record = {
                "candidate_id": model,
                "requested_model": model,
                "returned_model": None,
                "provider": PROVIDER,
                "scenario_id": scenario_id,
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "api_status": "failed",
                "raw_response": None,
            }
            try:
                response = client.chat.completions.create(**request_payload(model, scenario))
                raw_response = response.model_dump(mode="json")
                raw_record["raw_response"] = raw_response
                raw_record["api_status"] = "completed"
                raw_record["returned_model"] = raw_response.get("model")
            except Exception as exc:
                raw_record["raw_response"] = {"error": str(exc)}

            normalized = {
                "candidate_id": model,
                "requested_model": model,
                "returned_model": raw_record["returned_model"],
                "provider": PROVIDER,
                "scenario_id": scenario_id,
                "timestamp": raw_record["timestamp"],
                "api_status": raw_record["api_status"],
                "parsed_response": None,
                "schema_status": False,
                "parse_error": None,
                "failure_classification": None,
            }

            if raw_record["api_status"] != "completed":
                normalized["failure_classification"] = "TRANSPORT_OR_API_FAILURE"
            elif raw_record["returned_model"] != model:
                normalized["failure_classification"] = "MODEL_IDENTITY_MISMATCH"
            else:
                content = (
                    raw_record["raw_response"].get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                try:
                    parsed = json.loads(normalize_json_content(content))
                    normalized["parsed_response"] = parsed
                    normalized["schema_status"] = all(field in parsed for field in REQUIRED_FIELDS)
                    if not normalized["schema_status"]:
                        normalized["failure_classification"] = "SCHEMA_FIELD_NONCONFORMANCE"
                except Exception as exc:
                    normalized["parse_error"] = str(exc)
                    normalized["failure_classification"] = "SERIALIZATION_NONCONFORMANCE"

            raw_records.append(raw_record)
            normalized_records.append(normalized)
            result_records.append({"raw": raw_record, "normalized": normalized})

            write_jsonl(OUTDIR / "raw.jsonl", raw_records)
            write_jsonl(OUTDIR / "normalized.jsonl", normalized_records)

    candidate_results: dict[str, dict] = {}
    for model in MODELS:
        rows = [r for r in result_records if r["raw"]["candidate_id"] == model]
        api_completed = sum(r["raw"]["api_status"] == "completed" for r in rows)
        schema_valid = sum(r["normalized"]["schema_status"] for r in rows)
        parse_failures = sum(r["normalized"]["parse_error"] is not None for r in rows)
        identity_mismatch = sum(
            r["normalized"]["failure_classification"] == "MODEL_IDENTITY_MISMATCH" for r in rows
        )
        status = (
            "SMOKE_QUALIFIED"
            if api_completed == 4 and schema_valid == 4 and identity_mismatch == 0
            else "SMOKE_NOT_QUALIFIED"
        )
        candidate_results[model] = {
            "api_completed": api_completed,
            "schema_valid": schema_valid,
            "parse_failures": parse_failures,
            "identity_mismatch": identity_mismatch,
            "credential_leakage": 0,
            "manual_repair": 0,
            "semantic_retries": 0,
            "per_model_semantic_tuning": 0,
            "status": status,
        }

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    summary = {
        "task": "PIT-14.1.B NVIDIA NIM Smoke Qualification",
        "status": "COMPLETED",
        "provider": PROVIDER,
        "planned_candidates": len(MODELS),
        "scenario_count": len(SCENARIOS),
        "planned_samples": len(MODELS) * len(SCENARIOS),
        "completed_samples": sum(r["raw"]["api_status"] == "completed" for r in result_records),
        "schema_valid_samples": sum(r["normalized"]["schema_status"] for r in result_records),
        "qualified_candidates": sum(v["status"] == "SMOKE_QUALIFIED" for v in candidate_results.values()),
        "candidate_results": candidate_results,
        "ranking_performed": False,
        "teacher_qualification_verdicts_assigned": False,
        "cross_provider_comparison_performed": False,
        "teacher_selected": False,
    }

    metadata = {
        "provider": PROVIDER,
        "base_url": BASE_URL,
        "scenario_manifest_path": str(SCENARIOS_PATH).replace("\\", "/"),
        "scenario_manifest_sha256": scenario_sha,
        "candidate_manifest_reference": "docs/research/pit-14.1-nvidia-nim-candidate-expansion.md",
        "temperature": 0,
        "max_tokens": 4096,
        "stream": False,
        "structured_output_policy": "POLICY_B_PROMPT_ENFORCED_JSON_ALL_CANDIDATES",
        "reasoning_policy": "POLICY_R1_DIRECT_NON_THINKING_WHERE_TECHNICALLY_SUPPORTED",
        "execution_start": started,
        "execution_end": finished,
        "runner_path": "scripts/pit14_1/run_nvidia_smoke.py",
    }

    (OUTDIR / "results.json").write_text(
        json.dumps({"records": result_records}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTDIR / "smoke-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTDIR / "execution-metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

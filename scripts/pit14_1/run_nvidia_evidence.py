"""PIT-14.1.C NVIDIA NIM full evidence collection.

Research tooling only. Executes the frozen five-candidate x seven-scenario
matrix using the PIT-14.1.A execution policies. No retries, ranking,
qualification verdicts, cross-provider comparison, or teacher selection.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
from pathlib import Path

from openai import OpenAI


BASE_URL = "https://integrate.api.nvidia.com/v1"
PROVIDER = "NVIDIA NIM"
SOURCE_SCENARIOS = Path("experiments/pit13/evidence/scenarios.json")
OUTDIR = Path("experiments/pit14_1/evidence")
SCENARIOS_COPY = OUTDIR / "scenarios.json"
MODELS = [
    "moonshotai/kimi-k3",
    "meta/muse-glimmer-30b",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "google/gemma-4-31b-it",
    "openai/gpt-oss-20b",
]
EXPECTED_TYPES = {
    "stable_preference",
    "preference_drift",
    "conflicting_evidence",
    "user_correction",
    "rare_exception",
    "insufficient_evidence",
    "long_term_consistency",
}
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
    data = json.loads(SOURCE_SCENARIOS.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    if len(scenarios) != 7 or {s["scenario_type"] for s in scenarios} != EXPECTED_TYPES:
        raise ValueError("Full PIT scenario family set is not exactly frozen")
    for scenario in scenarios:
        if not scenario.get("evidence") or not scenario.get("provenance") or not scenario.get("version"):
            raise ValueError(f"Incomplete scenario provenance: {scenario.get('scenario_id')}")
    return scenarios


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


def slug(model: str) -> str:
    return model.replace("/", "-").replace(":", "-")


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()


def main() -> int:
    key = os.environ.get("NVIDIA_API_KEY")
    if key:
        key = key.strip()
    if not key:
        raise SystemExit("NVIDIA_API_KEY is missing")

    scenarios = load_scenarios()
    source_sha = hashlib.sha256(SOURCE_SCENARIOS.read_bytes()).hexdigest()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw_dir = OUTDIR / "raw"
    normalized_dir = OUTDIR / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(SOURCE_SCENARIOS, SCENARIOS_COPY)
    copied_sha = hashlib.sha256(SCENARIOS_COPY.read_bytes()).hexdigest()
    if source_sha != copied_sha:
        raise RuntimeError("Scenario copy hash mismatch")

    for model in MODELS:
        (raw_dir / f"{slug(model)}.jsonl").unlink(missing_ok=True)
        (normalized_dir / f"{slug(model)}.jsonl").unlink(missing_ok=True)

    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=120.0)
    records: list[dict] = []
    started = dt.datetime.now(dt.timezone.utc).isoformat()

    for model in MODELS:
        for scenario in scenarios:
            record = {
                "candidate_id": model,
                "requested_model": model,
                "returned_model": None,
                "provider": PROVIDER,
                "scenario_id": scenario["scenario_id"],
                "scenario_type": scenario["scenario_type"],
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "request_config": {
                    "temperature": 0,
                    "max_tokens": 4096,
                    "stream": False,
                    "structured_output_policy": "POLICY_B_PROMPT_ENFORCED_JSON_ALL_CANDIDATES",
                    "reasoning_policy": "POLICY_R1_DIRECT_NON_THINKING_WHERE_TECHNICALLY_SUPPORTED",
                },
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

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    metadata = {
        "task": "PIT-14.1.C NVIDIA NIM Full Evidence Collection",
        "provider": PROVIDER,
        "base_url": BASE_URL,
        "runner_path": "scripts/pit14_1/run_nvidia_evidence.py",
        "scenario_manifest_source": str(SOURCE_SCENARIOS).replace("\\", "/"),
        "scenario_manifest_source_sha256": source_sha,
        "scenario_manifest_copy": str(SCENARIOS_COPY).replace("\\", "/"),
        "scenario_manifest_copy_sha256": copied_sha,
        "candidate_manifest_reference": "docs/research/pit-14.1-nvidia-nim-candidate-expansion.md",
        "temperature": 0,
        "max_tokens": 4096,
        "stream": False,
        "structured_output_policy": "POLICY_B_PROMPT_ENFORCED_JSON_ALL_CANDIDATES",
        "reasoning_policy": "POLICY_R1_DIRECT_NON_THINKING_WHERE_TECHNICALLY_SUPPORTED",
        "execution_start": started,
        "execution_end": finished,
        "manual_repairs": 0,
        "semantic_retries": 0,
        "per_model_tuning": 0,
    }
    (OUTDIR / "execution-metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTDIR / "execution-summary.json").write_text(
        json.dumps(
            {
                "planned_samples": len(MODELS) * len(scenarios),
                "completed_samples": sum(r["raw"]["api_status"] == "completed" for r in records),
                "schema_valid_samples": sum(r["normalized"]["schema_status"] for r in records),
                "parse_failures": sum(r["normalized"]["parse_status"] == "parse_error" for r in records),
                "identity_mismatches": sum(
                    r["normalized"]["failure_classification"] == "MODEL_IDENTITY_MISMATCH"
                    for r in records
                ),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run PIT-16 V2 on DEV, HELD_OUT, or PIT-15 regression without exposing gold labels to V2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from guardrails_v2 import evaluate_signal

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "pit16"

SOURCE_FILES = {
    "qwen/qwen3.7-max:free": ROOT / "experiments/pit13/evidence/normalized/qwen-qwen3.7-max-free.jsonl",
    "deepseek/deepseek-v4-pro": ROOT / "experiments/pit13/evidence/normalized/deepseek-deepseek-v4-pro.jsonl",
    "minimax/minimax-m3:free": ROOT / "experiments/pit13/evidence/normalized/minimax-minimax-m3-free.jsonl",
    "meta/muse-glimmer-30b": ROOT / "experiments/pit14_1/evidence/normalized/meta-muse-glimmer-30b.jsonl",
    "nvidia/nemotron-3.5-lightning-30b-a3b": ROOT / "experiments/pit14_1/evidence/normalized/nvidia-nemotron-3.5-lightning-30b-a3b.jsonl",
    "openai/gpt-oss-20b": ROOT / "experiments/pit14_1/evidence/normalized/openai-gpt-oss-20b.jsonl",
    "google/gemma-4-31b-it": ROOT / "experiments/pit14_1/evidence/normalized/google-gemma-4-31b-it.jsonl",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_fixture_phase(phase: str) -> None:
    corpus = {x["fixture_id"]: x for x in load_json(EXP / "corpus.json")["fixtures"]}
    ids = load_json(EXP / "split.json")[phase]
    results = []
    for fixture_id in ids:
        row = corpus[fixture_id]
        # Only evidence + Teaching Signal cross the guardrail boundary.
        result = evaluate_signal(row["teaching_signal"], row["evidence"])
        results.append({"fixture_id": fixture_id, **result})
    out = EXP / ("dev/results.jsonl" if phase == "dev" else "held_out/results.jsonl")
    write_jsonl(out, results)
    print(f"{phase}={len(results)}")


def run_regression() -> None:
    samples = load_json(ROOT / "experiments/pit15/samples.json")["samples"]
    scenarios = {x["scenario_id"]: x for x in load_json(ROOT / "experiments/pit13/evidence/scenarios.json")["scenarios"]}
    source_cache = {cid: {x["scenario_id"]: x for x in load_jsonl(path)} for cid, path in SOURCE_FILES.items()}
    results = []
    for sample in samples:
        candidate_id = sample["candidate_id"]
        scenario_id = sample["scenario_id"]
        signal = source_cache[candidate_id][scenario_id]
        result = evaluate_signal(signal, scenarios[scenario_id])
        results.append({"candidate_id": candidate_id, "scenario_id": scenario_id, **result})
    write_jsonl(EXP / "regression/pit15-v2-results.jsonl", results)
    print(f"regression={len(results)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("dev", "held_out", "regression"))
    args = parser.parse_args()
    if args.phase == "regression":
        run_regression()
    else:
        run_fixture_phase(args.phase)


if __name__ == "__main__":
    main()


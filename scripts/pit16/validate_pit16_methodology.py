"""Validate PIT-16 methodological boundaries and frozen artifact invariants."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "pit16"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = json.loads((EXP / "protocol.json").read_text(encoding="utf-8"))
    corpus = json.loads((EXP / "corpus.json").read_text(encoding="utf-8"))["fixtures"]
    split = json.loads((EXP / "split.json").read_text(encoding="utf-8"))
    code = (ROOT / "scripts/pit16/guardrails_v2.py").read_text(encoding="utf-8")
    forbidden = [
        "qwen/qwen3.7", "deepseek/deepseek", "minimax/minimax", "meta/muse", "nvidia/nemotron", "openai/gpt-oss", "google/gemma",
        "stable_preference_001", "conflicting_evidence_001", "three or more consecutive interactions",
    ]
    found = [x for x in forbidden if x.lower() in code.lower()]
    if found:
        raise SystemExit(f"Anti-overfit validation failed: {found}")
    if len(corpus) < 90:
        raise SystemExit("Corpus too small")
    all_ids = {x["fixture_id"] for x in corpus}
    if set(split["dev"]) & set(split["held_out"]):
        raise SystemExit("DEV/HELD_OUT overlap")
    if set(split["dev"]) | set(split["held_out"]) != all_ids:
        raise SystemExit("Split does not cover corpus")
    if not (EXP / "held_out/results.jsonl").exists():
        phase = "PRE_HELD_OUT"
    else:
        phase = "POST_HELD_OUT"
    expected_hash = protocol.get("guardrail_v2_sha256")
    if expected_hash and expected_hash != sha(ROOT / "scripts/pit16/guardrails_v2.py"):
        raise SystemExit("Guardrail V2 hash differs from frozen protocol")
    if re.search(r"expected_(?:status|violation_classes)|rationale", code):
        raise SystemExit("Gold-label leakage detected in guardrail code")
    result = {
        "status": "PASS",
        "phase": phase,
        "candidate_specific_rules": False,
        "exact_known_phrase_patches": False,
        "gold_label_leakage": False,
        "dev_held_out_overlap": False,
        "corpus_size": len(corpus),
        "dev_size": len(split["dev"]),
        "held_out_size": len(split["held_out"]),
        "guardrail_v2_sha256": sha(ROOT / "scripts/pit16/guardrails_v2.py"),
    }
    (EXP / "methodology-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


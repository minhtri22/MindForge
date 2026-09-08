"""Direct Representation V2 gold-set and invariance evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / "experiments/pit18"
sys.path.insert(0, str(HERE))

from representation_v2 import evaluate

RUNTIME_FILES = (
    "scripts/pit18/surface_normalizer.py",
    "scripts/pit18/primitive_schema.py",
    "scripts/pit18/primitive_extractor.py",
    "scripts/pit18/canonicalizer.py",
    "scripts/pit18/scope_lattice.py",
    "scripts/pit18/support_relations_v2.py",
    "scripts/pit18/representation_v2.py",
)


def sha256_files(paths: tuple[str, ...]) -> str:
    h = hashlib.sha256()
    for rel in paths:
        h.update((ROOT / rel).read_bytes())
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_for_heldout() -> None:
    protocol = load_json(EXP / "protocol.json")
    freeze = protocol["freeze"]
    checks = {
        "representation_v2_sha256": sha256_files(RUNTIME_FILES),
        "representation_gold_heldout_sha256": sha256_file(EXP / "representation-gold-heldout.json"),
        "representation_clusters_sha256": sha256_file(EXP / "representation-clusters.json"),
    }
    for key, actual in checks.items():
        if freeze.get(key) != actual:
            raise SystemExit(f"PIT-18 freeze mismatch for {key}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")


def rate(n: int, d: int) -> float:
    return round(n / d, 6) if d else 1.0


def primitive_labels(result: dict[str, Any]) -> set[str]:
    ev = result["primitives"]["evidence_primitives"]
    ts = result["primitives"]["teaching_signal_primitives"]
    labels: set[str] = set()
    if any(p["type"] == "CONTRADICTS" for p in ev): labels.add("EV:CONTRADICTS")
    if any(p["type"] == "RECENCY_ORDER" for p in ts): labels.add("TS:RECENCY_ORDER")
    if any(p["type"] == "RESOLVES_BY_RECENCY" for p in ts): labels.add("TS:RESOLVES_BY_RECENCY")
    if result["facts"]["teaching_signal_state"]["asserts_numeric_threshold"]: labels.add("TS:COUNT_THRESHOLD")
    if result["facts"]["teaching_signal_state"]["asserts_temporal_rule"]: labels.add("TS:TEMPORAL_POLICY")
    if result["facts"]["teaching_signal_state"]["asserts_fallback_policy"]: labels.add("TS:FALLBACK")
    if any(p["type"] == "ABSTAINS" for p in ts): labels.add("TS:ABSTAINS")
    if any(p["type"] == "REQUESTS_CLARIFICATION" for p in ts): labels.add("TS:REQUESTS_CLARIFICATION")
    if result["facts"]["teaching_signal_state"]["operational_signals"]: labels.add("TS:OPERATIONAL_SIGNAL")
    return labels


def canonical_view(result: dict[str, Any]) -> dict[str, bool]:
    ev = result["facts"]["evidence_state"]
    ts = result["facts"]["teaching_signal_state"]
    return {
        "evidence_has_conflict": bool(ev["has_conflict"]),
        "resolves_conflict": bool(ts["resolves_conflict"]),
        "asserts_numeric_threshold": bool(ts["asserts_numeric_threshold"]),
        "asserts_temporal_rule": bool(ts["asserts_temporal_rule"]),
        "asserts_fallback_policy": bool(ts["asserts_fallback_policy"]),
        "abstains": bool(ts["abstains"]),
        "requests_clarification": bool(ts["requests_clarification"]),
        "has_operational_signal": bool(ts["operational_signals"]),
    }


def fingerprint(row: dict[str, Any]) -> tuple[Any, ...]:
    r = row["result"]
    facts = canonical_view(r)
    sup = r["facts"]["support_relations"]
    return (
        tuple(sorted(primitive_labels(r))),
        tuple(sorted(facts.items())),
        r["facts"]["evidence_state"]["scope_level"],
        r["facts"]["teaching_signal_state"]["asserted_scope"],
        sup["scope_relation"],
    )


def score(rows: list[dict[str, Any]], split_name: str) -> dict[str, Any]:
    p_tp=p_fp=p_fn=0
    c_tp=c_fp=c_fn=0
    scope_ok=scope_n=relation_ok=relation_n=support_ok=support_n=0
    specialized = {"conflict": [0,0], "numeric": [0,0], "temporal": [0,0], "fallback": [0,0], "uncertainty": [0,0]}
    for row in rows:
        expected = row["expected"]
        predicted_labels = primitive_labels(row["result"])
        gold_labels = set(expected.get("primitive_labels", []))
        p_tp += len(predicted_labels & gold_labels); p_fp += len(predicted_labels-gold_labels); p_fn += len(gold_labels-predicted_labels)
        pred_c = canonical_view(row["result"])
        for key, gold in expected.get("canonical", {}).items():
            pred = bool(pred_c[key])
            if gold and pred: c_tp += 1
            elif not gold and pred: c_fp += 1
            elif gold and not pred: c_fn += 1
        evscope = expected.get("evidence_scope"); tsscope = expected.get("asserted_scope")
        if evscope is not None:
            scope_n += 1; scope_ok += row["result"]["facts"]["evidence_state"]["scope_level"] == evscope
        if tsscope is not None:
            scope_n += 1; scope_ok += row["result"]["facts"]["teaching_signal_state"]["asserted_scope"] == tsscope
        if "scope_relation" in expected:
            relation_n += 1; relation_ok += row["result"]["facts"]["support_relations"]["scope_relation"] == expected["scope_relation"]
        for key, gold in expected.get("support", {}).items():
            support_n += 1; support_ok += row["result"]["facts"]["support_relations"].get(key) == gold
        pairs = {
            "conflict": "resolves_conflict", "numeric": "asserts_numeric_threshold", "temporal": "asserts_temporal_rule",
            "fallback": "asserts_fallback_policy",
        }
        for label, key in pairs.items():
            if expected.get("canonical", {}).get(key):
                specialized[label][1] += 1; specialized[label][0] += pred_c[key]
        if expected.get("canonical", {}).get("abstains") or expected.get("canonical", {}).get("requests_clarification"):
            specialized["uncertainty"][1] += 1
            specialized["uncertainty"][0] += pred_c["abstains"] == expected["canonical"]["abstains"] and pred_c["requests_clarification"] == expected["canonical"]["requests_clarification"]

    cluster_file = load_json(EXP / "representation-clusters.json")
    by_id = {row["gold_id"]: row for row in rows}
    clusters = [c for c in cluster_file["clusters"] if c["split"] == split_name and all(x in by_id for x in c["sample_ids"])]
    primitive_cons=canonical_cons=scope_cons=0
    fact_pairs=guard_pairs=pair_total=0
    for cluster in clusters:
        members=[by_id[x] for x in cluster["sample_ids"]]
        p=[tuple(sorted(primitive_labels(x["result"]))) for x in members]
        c=[tuple(sorted(canonical_view(x["result"]).items())) for x in members]
        s=[(x["result"]["facts"]["evidence_state"]["scope_level"],x["result"]["facts"]["teaching_signal_state"]["asserted_scope"],x["result"]["facts"]["support_relations"]["scope_relation"]) for x in members]
        primitive_cons += len(set(p)) == 1; canonical_cons += len(set(c)) == 1; scope_cons += len(set(s)) == 1
        for a,b in combinations(members,2):
            pair_total += 1
            fact_pairs += canonical_view(a["result"]) == canonical_view(b["result"])
            guard_pairs += a["result"]["decision"]["violation_classes"] == b["result"]["decision"]["violation_classes"]
    cn=len(clusters)
    metrics={
        "samples": len(rows),
        "primitive_precision": rate(p_tp,p_tp+p_fp), "primitive_recall": rate(p_tp,p_tp+p_fn),
        "canonical_fact_precision": rate(c_tp,c_tp+c_fp), "canonical_fact_recall": rate(c_tp,c_tp+c_fn),
        "scope_classification_accuracy": rate(scope_ok,scope_n), "scope_relation_accuracy": rate(relation_ok,relation_n),
        "support_relation_accuracy": rate(support_ok,support_n),
        "conflict_extraction_accuracy": rate(*specialized["conflict"]),
        "numeric_policy_extraction_recall": rate(*specialized["numeric"]),
        "temporal_policy_extraction_recall": rate(*specialized["temporal"]),
        "fallback_extraction_recall": rate(*specialized["fallback"]),
        "abstention_clarification_accuracy": rate(*specialized["uncertainty"]),
        "primitive_cluster_consistency": rate(primitive_cons,cn),
        "canonical_fact_cluster_consistency": rate(canonical_cons,cn),
        "scope_cluster_consistency": rate(scope_cons,cn),
        "representation_cluster_consistency": min(rate(primitive_cons,cn),rate(canonical_cons,cn),rate(scope_cons,cn)) if cn else 1.0,
        "pairwise_fact_agreement": rate(fact_pairs,pair_total), "pairwise_guardrail_agreement": rate(guard_pairs,pair_total),
    }
    return metrics


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--split", choices=("DEV","HELD_OUT"), default="DEV")
    parser.add_argument("--output", type=Path)
    args=parser.parse_args()
    if args.split == "HELD_OUT":
        verify_freeze_for_heldout()
    path=EXP/("representation-gold-dev.json" if args.split=="DEV" else "representation-gold-heldout.json")
    gold=load_json(path)["samples"]
    rows=[]
    for sample in gold:
        result=evaluate(sample["evidence"], sample["teaching_signal"])
        rows.append({
            "gold_id":sample["gold_id"],
            "source":sample["source"],
            "expected":sample["expected"],
            "predicted": {
                "primitive_labels": sorted(primitive_labels(result)),
                "canonical": canonical_view(result),
                "evidence_scope": result["facts"]["evidence_state"]["scope_level"],
                "asserted_scope": result["facts"]["teaching_signal_state"]["asserted_scope"],
                "scope_relation": result["facts"]["support_relations"]["scope_relation"],
                "support": result["facts"]["support_relations"],
                "violation_classes": result["decision"]["violation_classes"],
            },
            "result":result,
        })
    if args.output: write_jsonl(args.output,rows)
    print(json.dumps(score(rows,args.split),indent=2))


if __name__ == "__main__": main()

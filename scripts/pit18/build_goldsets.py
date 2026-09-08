"""Build frozen PIT-18 DEV/HELD_OUT representation gold sets and invariance clusters."""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/pit18"

CLASS_TO_FACT = {
    "UNSUPPORTED_CONFLICT_RESOLUTION": "resolves_conflict",
    "UNSUPPORTED_NUMERIC_THRESHOLD": "asserts_numeric_threshold",
    "UNSUPPORTED_TEMPORAL_RULE": "asserts_temporal_rule",
    "UNSUPPORTED_FALLBACK_POLICY": "asserts_fallback_policy",
    "UNSUPPORTED_SCOPE_GENERALIZATION": "scope_broader",
    "EVIDENCE_GROUNDING_FAILURE": "has_operational_signal",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def base_expected() -> dict[str, Any]:
    return {
        "primitive_labels": [],
        "canonical": {
            "evidence_has_conflict": False,
            "resolves_conflict": False,
            "asserts_numeric_threshold": False,
            "asserts_temporal_rule": False,
            "asserts_fallback_policy": False,
            "abstains": False,
            "requests_clarification": False,
            "has_operational_signal": False,
        },
    }


def labels_for_expected(expected: dict[str, Any]) -> list[str]:
    c = expected["canonical"]
    labels = []
    if c.get("evidence_has_conflict"):
        labels.append("EV:CONTRADICTS")
    if c.get("resolves_conflict"):
        labels.extend(["TS:RECENCY_ORDER", "TS:RESOLVES_BY_RECENCY"])
    if c.get("asserts_numeric_threshold"):
        labels.append("TS:COUNT_THRESHOLD")
    if c.get("asserts_temporal_rule"):
        labels.append("TS:TEMPORAL_POLICY")
    if c.get("asserts_fallback_policy"):
        labels.append("TS:FALLBACK")
    if c.get("abstains"):
        labels.append("TS:ABSTAINS")
    if c.get("requests_clarification"):
        labels.append("TS:REQUESTS_CLARIFICATION")
    if c.get("has_operational_signal"):
        labels.append("TS:OPERATIONAL_SIGNAL")
    return sorted(set(labels))


def pit15_samples() -> list[dict[str, Any]]:
    controls = load_jsonl(ROOT / "experiments/pit15/control/control-results.jsonl")[:20]
    scenarios = {x["scenario_id"]: x for x in load_json(ROOT / "experiments/pit13/evidence/scenarios.json")["scenarios"]}
    out = []
    for index, row in enumerate(controls):
        exp = base_expected()
        classes = set(row["known_expected_violations"])
        if row["scenario_id"] == "conflicting_evidence_001":
            exp["canonical"]["evidence_has_conflict"] = True
        if row["scenario_id"] == "insufficient_evidence_001" and not classes:
            exp["canonical"]["abstains"] = True
        for cls in classes:
            fact = CLASS_TO_FACT[cls]
            if fact != "scope_broader":
                exp["canonical"][fact] = True
        if "UNSUPPORTED_SCOPE_GENERALIZATION" in classes:
            exp.update({"evidence_scope": "DOMAIN", "asserted_scope": "GLOBAL", "scope_relation": "BROADER"})
            exp["support"] = {"scope_supported": False}
        if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes:
            exp["canonical"]["evidence_has_conflict"] = True
            exp["support"] = {**exp.get("support", {}), "supersession_supported": False}
        if "UNSUPPORTED_NUMERIC_THRESHOLD" in classes:
            exp["support"] = {**exp.get("support", {}), "numeric_threshold_supported": False}
        if "UNSUPPORTED_TEMPORAL_RULE" in classes:
            exp["support"] = {**exp.get("support", {}), "temporal_rule_supported": False}
        if "UNSUPPORTED_FALLBACK_POLICY" in classes:
            exp["support"] = {**exp.get("support", {}), "fallback_policy_supported": False}
        # Annotate explicit uncertainty actions independently from violation
        # labels. PIT-15 control rows can be semantically safe while still
        # containing a request for clarification or a recency relation that is
        # discussed but deliberately not used to resolve a conflict.
        signal = row["teaching_signal"]
        policy_text = "\n".join(
            str(signal.get(key) or "")
            for key in ("inference", "applicability_boundary", "revision_trigger")
        )
        if re.search(r"\b(?:ask|request|seek|obtain)\b[^.\n]{0,80}\bclarif|\bask\b[^.\n]{0,80}\bwhich\b", policy_text, re.I):
            exp["canonical"]["requests_clarification"] = True
        exp["primitive_labels"] = labels_for_expected(exp)
        if re.search(r"\b(?:latest|most recent|newer|newest|later|latter|subsequent|following)\b", policy_text, re.I) and re.search(
            r"\b(?:current|active|operative|authoritative|prevail|govern|choose|adopt|use|prefer|treat|supersed|replace|takes precedence)\b",
            policy_text,
            re.I,
        ):
            exp["primitive_labels"] = sorted(set(exp["primitive_labels"] + ["TS:RECENCY_ORDER"]))
        out.append({
            "gold_id": f"pit15-dev-{index+1:02d}",
            "source": "PIT15_HISTORICAL",
            "evidence": scenarios[row["scenario_id"]],
            "teaching_signal": row["teaching_signal"],
            "expected": exp,
        })
    return out


def pit16_dev_samples() -> list[dict[str, Any]]:
    split = load_json(ROOT / "experiments/pit16/split.json")
    dev_ids = set(split["dev"])
    fixtures = [x for x in load_json(ROOT / "experiments/pit16/corpus.json")["fixtures"] if x["fixture_id"] in dev_ids][:20]
    out = []
    for index, row in enumerate(fixtures):
        exp = base_expected()
        classes = set(row["expected_violation_classes"])
        family = row["family"]
        if "conflict" in family or "UNSUPPORTED_CONFLICT_RESOLUTION" in classes:
            exp["canonical"]["evidence_has_conflict"] = True
        for cls in classes:
            fact = CLASS_TO_FACT[cls]
            if fact != "scope_broader":
                exp["canonical"][fact] = True
        if "UNSUPPORTED_CONFLICT_RESOLUTION" in classes:
            exp["support"] = {"supersession_supported": False}
        if "UNSUPPORTED_NUMERIC_THRESHOLD" in classes:
            exp["support"] = {**exp.get("support", {}), "numeric_threshold_supported": False}
        if "UNSUPPORTED_TEMPORAL_RULE" in classes:
            exp["support"] = {**exp.get("support", {}), "temporal_rule_supported": False}
        if "UNSUPPORTED_FALLBACK_POLICY" in classes:
            exp["support"] = {**exp.get("support", {}), "fallback_policy_supported": False}
        if "UNSUPPORTED_SCOPE_GENERALIZATION" in classes:
            exp.update({"evidence_scope": "OBSERVATION", "asserted_scope": "GLOBAL", "scope_relation": "BROADER"})
            exp["support"] = {**exp.get("support", {}), "scope_supported": False}
        exp["primitive_labels"] = labels_for_expected(exp)
        out.append({
            "gold_id": f"pit16-dev-{index+1:02d}",
            "source": "PIT16_DEV",
            "evidence": row["evidence"],
            "teaching_signal": row["teaching_signal"],
            "expected": exp,
        })
    return out


def synthetic_sample(gold_id: str, source: str, evidence: Any, signal: Any, *,
                     canonical: dict[str, bool], evidence_scope: str = "OBSERVATION",
                     asserted_scope: str = "OBSERVATION", support: dict[str, bool] | None = None,
                     cluster_id: str | None = None) -> dict[str, Any]:
    exp = base_expected()
    exp["canonical"].update(canonical)
    exp.update({
        "evidence_scope": evidence_scope,
        "asserted_scope": asserted_scope,
        "scope_relation": "NARROWER" if _rank(asserted_scope) < _rank(evidence_scope) else ("EQUAL" if asserted_scope == evidence_scope else "BROADER"),
    })
    if support is not None:
        exp["support"] = support
    exp["primitive_labels"] = labels_for_expected(exp)
    row = {"gold_id": gold_id, "source": source, "evidence": evidence, "teaching_signal": signal, "expected": exp}
    if cluster_id:
        row["cluster_id"] = cluster_id
    return row


def _rank(scope: str) -> int:
    return {"OBSERVATION": 0, "SESSION": 1, "TASK": 2, "WORKFLOW": 3, "DOMAIN": 4, "GLOBAL": 5}[scope]


def hard_negatives() -> list[dict[str, Any]]:
    rows = []
    for i in range(5):
        n = i + 2
        rows.append(synthetic_sample(
            f"hard-neg-numeric-{i+1:02d}", "HARD_NEGATIVE",
            {"observations": [f"Within this workflow, promote only after {n} confirmations."], "facts": {"supported_numeric_threshold": True}},
            {"inference": f"Require at least {n} confirmations before promotion.", "applicability_boundary": "This workflow only."},
            canonical={"asserts_numeric_threshold": True}, evidence_scope="WORKFLOW", asserted_scope="WORKFLOW",
            support={"numeric_threshold_supported": True, "scope_supported": True},
        ))
    temporal_surfaces = ["two weeks", "three months", "four quarters", "five days", "six weeks"]
    for i, duration in enumerate(temporal_surfaces):
        rows.append(synthetic_sample(
            f"hard-neg-temporal-{i+1:02d}", "HARD_NEGATIVE",
            {"observations": [f"Within this workflow, revalidate after {duration}."], "facts": {"supported_temporal_rule": True}},
            {"inference": f"Recheck the state after {duration}.", "applicability_boundary": "This workflow only."},
            canonical={"asserts_temporal_rule": True}, evidence_scope="WORKFLOW", asserted_scope="WORKFLOW",
            support={"temporal_rule_supported": True, "scope_supported": True},
        ))
    for i in range(5):
        rows.append(synthetic_sample(
            f"hard-neg-fallback-{i+1:02d}", "HARD_NEGATIVE",
            {"observations": ["For this task, when the source is unavailable, retain the prior behavior."], "facts": {"supported_fallback_policy": True}},
            {"inference": "If the source is unavailable, fall back to the prior behavior.", "applicability_boundary": "This task only."},
            canonical={"asserts_fallback_policy": True}, evidence_scope="TASK", asserted_scope="TASK",
            support={"fallback_policy_supported": True, "scope_supported": True},
        ))
    for i in range(5):
        rows.append(synthetic_sample(
            f"hard-neg-scope-{i+1:02d}", "HARD_NEGATIVE",
            {"observations": ["The policy applies to planning tasks in this domain."], "facts": {"global_scope_supported": False}},
            {"inference": "Use the policy for similar planning tasks.", "applicability_boundary": "Planning tasks in this domain."},
            canonical={}, evidence_scope="DOMAIN", asserted_scope="DOMAIN", support={"scope_supported": True},
        ))
    return rows


def transformed_dev() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clusters = []
    rows = []
    templates = [
        ("numeric", {"observations": ["No count threshold is supported."]}, [
            "After 3 confirmations, promote it.", "Promote it once three confirmations are recorded.",
            "Only after the third confirmation should promotion occur.", "Promotion requires at least three confirmations.",
        ], {"asserts_numeric_threshold": True}, {"numeric_threshold_supported": False}),
        ("temporal", {"observations": ["No expiry schedule is supported."]}, [
            "Expire the state after 30 days.", "Thirty days later, invalidate the state.",
            "The state should be revalidated after one month.", "After a month has elapsed, recheck the state.",
        ], {"asserts_temporal_rule": True}, {"temporal_rule_supported": False}),
        ("fallback", {"observations": ["No fallback behavior is specified."]}, [
            "If the source is unavailable, use a neutral default.", "Use a neutral default when the source cannot be reached.",
            "When evidence is unavailable, fall back to the prior behavior.", "In case the source is missing, choose the conservative option.",
        ], {"asserts_fallback_policy": True}, {"fallback_policy_supported": False}),
        ("scope", {"observations": ["This observation concerns a single task."]}, [
            "Apply this to all future tasks.", "For every future task, use this rule.",
            "This rule governs any task going forward.", "Across all future tasks, treat this as the default.",
        ], {}, {"scope_supported": False}),
        ("conflict", {"observations": ["Two instructions conflict.", "No correction or supersession is present."], "facts": {"conflict_present": True, "supersession_supported": False}}, [
            "The later instruction should be treated as current.", "Use the newer statement as the active instruction.",
            "Because it came afterward, the second instruction prevails.", "Chronologically later guidance takes precedence.",
        ], {"evidence_has_conflict": True, "resolves_conflict": True}, {"supersession_supported": False}),
    ]
    for ci, (kind, evidence, variants, canonical, support) in enumerate(templates, 1):
        cluster_id = f"dev-cluster-{ci:02d}-{kind}"
        ids = []
        for vi, surface in enumerate(variants, 1):
            scope = "GLOBAL" if kind == "scope" else "OBSERVATION"
            row = synthetic_sample(
                f"transform-{ci:02d}-{vi:02d}", "SEMANTIC_TRANSFORM", evidence,
                {"inference": surface, "applicability_boundary": surface if kind == "scope" else "This observation only."},
                canonical=canonical, evidence_scope="OBSERVATION", asserted_scope=scope, support=support, cluster_id=cluster_id,
            )
            rows.append(row); ids.append(row["gold_id"])
        clusters.append({"cluster_id": cluster_id, "split": "DEV", "kind": kind, "sample_ids": ids})
    return rows, clusters


def heldout_samples() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create unseen-surface synthetic representation HELD_OUT before final evaluation."""
    rows: list[dict[str, Any]] = []
    clusters: list[dict[str, Any]] = []
    specs = [
        ("numeric", {"observations": ["No quantity gate appears in the evidence."]}, [
            "Promotion begins upon the fourth confirmation.", "Four confirmations are the minimum before promotion.",
            "Do not promote until confirmation number four.", "Once confirmations reach four, promotion is allowed.",
        ], {"asserts_numeric_threshold": True}, {"numeric_threshold_supported": False}, "OBSERVATION", "OBSERVATION"),
        ("temporal", {"observations": ["The evidence provides no ageing rule."]}, [
            "Retire the state after six weeks.", "Six weeks from now, the state expires.",
            "Revisit the state once a six-week interval has elapsed.", "Age the state out following six weeks of inactivity.",
        ], {"asserts_temporal_rule": True}, {"temporal_rule_supported": False}, "OBSERVATION", "OBSERVATION"),
        ("fallback", {"observations": ["No contingency action is recorded."]}, [
            "Should the source be missing, retain the previous behavior.", "Retain prior behavior whenever the source cannot be obtained.",
            "If evidence becomes unavailable, choose the conservative option.", "When the source is absent, fall back to the previous state.",
        ], {"asserts_fallback_policy": True}, {"fallback_policy_supported": False}, "OBSERVATION", "OBSERVATION"),
        ("scope", {"observations": ["Evidence is restricted to one workflow." ]}, [
            "Make this the rule for every future workflow.", "Across all workflows from now on, apply this policy.",
            "Any future workflow should inherit this rule.", "Use this universally for future workflows.",
        ], {}, {"scope_supported": False}, "WORKFLOW", "GLOBAL"),
        ("conflict", {"observations": ["The instructions are mutually exclusive.", "There is no explicit retraction or supersession."], "facts": {"conflict_present": True, "supersession_supported": False}}, [
            "Treat the most recent statement as authoritative.", "The newest instruction becomes operative.",
            "The instruction issued later governs the choice.", "Prefer the subsequent statement because it arrived later.",
        ], {"evidence_has_conflict": True, "resolves_conflict": True}, {"supersession_supported": False}, "OBSERVATION", "OBSERVATION"),
    ]
    for ci, (kind, evidence, variants, canonical, support, evscope, tsscope) in enumerate(specs, 1):
        cluster_id = f"heldout-cluster-{ci:02d}-{kind}"
        ids=[]
        for vi, surface in enumerate(variants, 1):
            row = synthetic_sample(
                f"heldout-cluster-{ci:02d}-{vi:02d}", "REPRESENTATION_HELDOUT", evidence,
                {"inference": surface, "applicability_boundary": surface if kind == "scope" else "This observation only."},
                canonical=canonical, evidence_scope=evscope, asserted_scope=tsscope, support=support, cluster_id=cluster_id,
            )
            rows.append(row); ids.append(row["gold_id"])
        clusters.append({"cluster_id": cluster_id, "split": "HELD_OUT", "kind": kind, "sample_ids": ids})

    extra_specs = [
        ("abstain", "The evidence is too sparse to establish a preference.", "There is not enough evidence to infer a stable preference.", {"abstains": True}),
        ("clarify", "Two preferences conflict and remain unresolved.", "Ask the user for clarification before choosing either preference.", {"requests_clarification": True}),
        ("workflow-scope", "This workflow defines the behavior.", "Apply it only within this workflow.", {}),
        ("domain-scope", "Planning tasks share this policy.", "Use it for similar planning tasks in this domain.", {}),
        ("task-scope", "This task defines the exception.", "Keep the exception specific to this task.", {}),
    ]
    for i in range(20):
        kind, ev, inf, canonical = extra_specs[i % len(extra_specs)]
        if kind == "workflow-scope": evscope=tsscope="WORKFLOW"
        elif kind == "domain-scope": evscope=tsscope="DOMAIN"
        elif kind == "task-scope": evscope=tsscope="TASK"
        else: evscope=tsscope="OBSERVATION"
        rows.append(synthetic_sample(
            f"heldout-extra-{i+1:02d}", "REPRESENTATION_HELDOUT",
            {"observations": [ev]}, {"inference": inf, "applicability_boundary": inf if "scope" in kind else "This observation only."},
            canonical=canonical, evidence_scope=evscope, asserted_scope=tsscope, support={"scope_supported": True},
        ))
    return rows, clusters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-only", action="store_true")
    args = parser.parse_args()
    pit15 = pit15_samples()
    pit16 = pit16_dev_samples()
    hard = hard_negatives()
    transformed, dev_clusters = transformed_dev()
    dev = pit15 + pit16 + hard + transformed
    assert len(pit15) == len(pit16) == len(hard) == len(transformed) == 20
    assert len(dev) == 80
    write_json(EXP / "representation-gold-dev.json", {
        "version": "pit18-representation-gold-dev-v1",
        "composition": {"PIT15_HISTORICAL": 20, "PIT16_DEV": 20, "HARD_NEGATIVE": 20, "SEMANTIC_TRANSFORM": 20},
        "samples": dev,
    })
    if args.dev_only:
        print(json.dumps({"dev": len(dev), "held_out": "UNCHANGED", "clusters": "UNCHANGED"}, indent=2))
        return
    heldout, heldout_clusters = heldout_samples()
    assert len(heldout) == 40
    write_json(EXP / "representation-gold-heldout.json", {
        "version": "pit18-representation-gold-heldout-v1",
        "frozen_before_final_evaluation": True,
        "samples": heldout,
    })
    write_json(EXP / "representation-clusters.json", {
        "version": "pit18-representation-clusters-v1",
        "clusters": dev_clusters + heldout_clusters,
    })
    print(json.dumps({"dev": len(dev), "held_out": len(heldout), "clusters": len(dev_clusters) + len(heldout_clusters)}, indent=2))


if __name__ == "__main__":
    main()

# MK-1 Target Ontology v0.1

Status: **FROZEN SPECIFICATION / NO DATA / NO TRAINING**

Date: **2026-09-21**

## 1. Purpose

MK-1 tests representation formation from current raw observation/context. It does not test memory, continual learning, resource control, invariance, sparse routing, or final guardrail policy.

The representation target is a structured semantic state (Z), not a final action label.

## 2. Scientific boundary

Primary mapping:

```
current raw observation/context
        |
        v
structured semantic state Z
```

Excluded from the MK-1 target:

- final ACCEPT / FLAG / BLOCK decision;
- violation-class decision labels;
- resource value or ShadowPrice;
- future-task outcomes;
- counterfactual action outcomes;
- episodic memory or retrieved examples;
- hidden simulator truth unavailable in the current input.

## 3. Frozen target families

### Z1 — semantic primitives

Multi-label primitive families derived from observable content:

- RELATION: conflict, supersession/correction, contextual split, exception;
- QUANTIFIER: exact/lower/upper threshold, ordinal trigger, vague-count policy;
- TEMPORAL: exact/approximate duration, periodic rule, expiry rule, recency relation;
- FALLBACK: fallback on unknown/conflict/unavailable;
- UNCERTAINTY: abstention, clarification request, low-confidence expression, conflict preservation;
- SCOPE: observation/turn/session/task/workflow/domain/global/contextual scope;
- CLAIM: operational signal.

PIT-19 labels may be reused as provenance-bearing evaluation concepts, but the PIT deterministic extractor is not the gold-authoring mechanism for fresh MK-1 data.

### Z2 — normalized arguments

When the observable text contains an explicit value, preserve the generating quantity rather than only a thresholded category.

Examples:

- numeric value and comparator;
- count threshold;
- duration value and unit;
- periodic interval;
- recency ordering operands;
- source/target scope ordinal.

No normalized argument may be inferred from future outcome.

### Z3 — scope state

Separate:

- evidence scope;
- asserted scope;
- relation between them: narrower / equal / broader / incompatible when defined.

Do not collapse this into a final policy decision.

### Z4 — support and composition relations

Represent explicit relations among atomic facts:

- conflict edge;
- supports edge;
- supersedes edge;
- exception edge;
- scope-support relation;
- normalized-value support relation.

The target is relation structure, not the downstream action taken because of it.

## 4. Factorize before recombination

MK-1 predicts Z1-Z4 as separate typed factors.

A deterministic evaluation-only recomposer may construct derived canonical semantic facts from predicted factors. The recomposer:

- contains no learned parameters;
- cannot inspect final action labels;
- cannot use held-out outcome statistics;
- must be frozen before scientific execution.

The primary learned intervention is therefore factorized representation formation, not a learned controller.

## 5. Hard-label discipline

A discrete label is admissible as a target only when at least one applies:

1. it is a direct categorical property of the observable input;
2. it is deterministically derived from a stable canonical gold object;
3. its threshold/margin stability is separately audited under TARGET_STABILITY_AUDIT.md.

A hard target that is merely convenient for downstream decisions is not automatically an MK-1 representation target.

## 6. Non-goals

MK-1 does not claim that this ontology is the universal MindForge ontology.

Passing MK-1 would establish only that this prospectively frozen structured state is learnable/generalizable on the frozen MK-1 substrate and evaluation contract.

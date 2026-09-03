# Track A Benchmark v1 Materialization — N3.1

Status: **PASS / FINAL FROZEN AFTER SEMANTIC R1 CORRECTION + RE-REVIEW**

Protocol authority: `docs/research/track-a-foundation-protocol.md`

Specification authority: `docs/research/track-a-benchmark-spec.md`

Starting protocol commit: `627044cc06d3e411b1388b57cd94906fefa74343`

Historical first semantic review: `docs/research/track-a-benchmark-v1-semantic-review.md` — **REVISE**.

Closure review: `docs/research/track-a-benchmark-v1-semantic-r1-closure.md` — **PASS**.

## Purpose

N3.1 materializes and freezes the Track-A Benchmark v1 before any 5M/10M/20M/50M candidate or Qwen reference is evaluated.

## Final materialization identity

```text
benchmark_id: track-a-capability-v1
benchmark_version: 1.0
materialization_revision: r1-semantic-correction
generator_seed: 20260904
status: FINAL_FROZEN_AFTER_SEMANTIC_R1_PASS
```

## Final counts

```text
total cases: 1400
families: 7 × 200
calibration: 280
development: 420
held-out test: 700
Vietnamese: 840
Vietnamese-English: 350
English: 210
straightforward: 560
contextual: 490
adversarial: 350
held-out counterfactual cases: 280
counterfactual groups: 140
```

Every family remains exactly 200 cases with the frozen 40/60/100 split and 120/50/30 language quotas.

## Semantic R1 corrections

The generator was revised rather than patching JSONL rows manually.

1. **Exact-name policy** — `Tuấn` resolves to the exact `Tuấn` contact even when `Tuấn Anh` exists. Clarification cases now use genuinely duplicated display names such as two `Mai` contacts.
2. **A5 extraction policy** — explicit message payloads use literal source payload extraction. No silent translation is part of A5 truth.
3. **Held-out leakage** — held-out template IDs and core surface forms are split-disjoint from calibration/development. The validator strips bounded wrappers/noise before checking core-surface overlap.
4. **A7 route semantics** — `LOCAL_MODEL` is limited to intrinsic short text transformation; `LOCAL_APP_OR_TOOL` requires an explicitly available local app/tool/live capability; `EXTERNAL` requires non-local/fresh capability; `CLARIFY` is underdetermined input. The old calculator counterfactual was removed and replaced by a live-weather availability counterfactual.
5. **Language diversity** — surface variation and held-out paraphrase pools were expanded. Final unique utterance counts are 107–123 per 200-case family; VI-EN unique counts are 30–36 per 50-case family.
6. **Additional re-review fixes** — English date phrasing was made locale-unambiguous; text-transformation routes always include a payload; duplicate politeness artifacts were reduced.

## Final automated evidence

```text
validator: PASS
1400 unique IDs: PASS
split quotas: PASS
language quotas: PASS
difficulty quotas: PASS
counterfactual groups: 140 / PASS
counterfactual members differ on exactly one input path: PASS
same-family exact-input duplicates: 0
held-out template leakage: 0
held-out exact utterance leakage: 0
held-out core-surface leakage after wrapper/noise stripping: 0
SR-01 exact-name truth audit: PASS
SR-02 A5 literal extraction audit: PASS
oracle scorer tests: 2 passed
full semantic audit: 0 CRITICAL / 0 MAJOR
```

## Final semantic review

A new deterministic 140-case stratified sample (20 per family) was reviewed after regeneration, and all 1,400 cases were audited again with family-specific semantic invariants.

Decision:

```text
INDEPENDENT SEMANTIC RE-REVIEW: PASS
CRITICAL: 0
MAJOR: 0
BENCHMARK FINAL FREEZE: PASS
```

This review is performed by ChatGPT as the independent research reviewer requested by the user. It is not represented as a separate external human adjudication.

## Final artifact hashes

```text
calibration.jsonl:
7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb

development.jsonl:
2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42

test.jsonl:
3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf

schema.json:
6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb

human-review-sample.jsonl:
d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693
```

`manifest.json` records the same final hashes.

## Held-out governance

Held-out protection is procedural rather than cryptographic. Candidate training, prompt tuning, threshold tuning, teacher generation, and iterative error-driven tuning against held-out truth remain forbidden. Evaluation settings must be frozen before held-out scoring.

## N3.1 final decision

```text
N3.1: PASS / FINAL FROZEN
TRACK-A BENCHMARK V1: READY FOR REFERENCE QUALIFICATION
QWEN3.8-27B EXECUTION: NOT YET RUN
N4 5M/10M/20M/50M: STILL NOT AUTHORIZED
PPF INTEGRATION: NOT AUTHORIZED
MODEL/KERNEL CHANGE: NO
```

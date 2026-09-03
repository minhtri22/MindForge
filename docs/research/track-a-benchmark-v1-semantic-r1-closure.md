# Track A Benchmark v1 — Semantic R1 Closure

Status: **PASS / FINAL FREEZE ACCEPTED**

Branch: `research/track-a-benchmark-v1`

Historical review authority: `docs/research/track-a-benchmark-v1-semantic-review.md`

## Scope

N3.1-R1 corrected the deterministic benchmark materializer after the first independent semantic review returned REVISE. The correction was generator-level; individual JSONL truth rows were not manually patched.

The corrected benchmark was regenerated in full and then independently re-reviewed before any Qwen or compact-model execution.

## Historical findings and resolution

| Finding | Previous severity | R1 resolution | Final status |
|---|---|---|---|
| SR-01 exact-name false ambiguity | CRITICAL | exact `Tuấn` resolves normally; genuine ambiguity now uses two contacts with the same display name | RESOLVED |
| SR-02 A5 translation inside extraction truth | CRITICAL | message payload policy frozen to literal source extraction | RESOLVED |
| SR-03 held-out template/surface leakage | CRITICAL | split-disjoint semantic template IDs and held-out paraphrase pools; validator rejects template, exact-utterance, and normalized core-surface leakage | RESOLVED |
| SR-04 A7 calculator routing ambiguity | MAJOR / possibly CRITICAL | calculator pair removed; route semantics frozen and counterfactual uses explicit live capability availability | RESOLVED |
| SR-05 low linguistic/code-mix diversity | MAJOR | materially expanded deterministic surface/paraphrase pools, including held-out-specific forms | RESOLVED |

## Final benchmark counts

```text
cases: 1,400
A1-A7: 200 each
calibration: 280
development: 420
held-out test: 700
Vietnamese: 840
VI-EN: 350
English: 210
straightforward: 560
contextual: 490
adversarial: 350
counterfactual groups: 140
held-out counterfactual cases: 280 / 700 (40%)
```

## Leakage / structural gates

Final validator result:

```text
status: PASS
split template leakage: 0
split exact-utterance leakage: 0
normalized core-surface held-out leakage: 0
same-family exact-input duplicates: 0
counterfactual pair invariant: PASS
```

Every counterfactual pair keeps family, language, difficulty, and invariant fixture content fixed while changing one declared input path.

## Final semantic audit

Full semantic audit: **1,400 / 1,400 cases**.

Final result:

```text
CRITICAL: 0
MAJOR: 0
semantic audit issues: 0
```

A new deterministic stratified review sample of 140 cases (20 per family) was also reviewed after regeneration. Minor wording artifacts found during the first R1 pass were corrected at the generator/paraphrase layer, followed by another full regeneration and revalidation.

This review was performed independently by ChatGPT over the generated JSONL. It is not represented as an external human adjudication.

## Final diversity

Unique user utterances per 200-case family:

```text
A1 123
A2 113
A3 110
A4 109
A5 107
A6 113
A7 118
```

Unique VI-EN utterances per 50-case family:

```text
A1 34
A2 35
A3 30
A4 30
A5 32
A6 35
A7 36
```

## Frozen semantic policies

### Entity resolution

An exact full-name reference is not made ambiguous merely because another contact has a longer name containing the same token. Clarification cases use genuinely identical/underspecified surface references.

### A5 extraction

```text
a5_text_policy = literal_source_payload
```

A5 extracts the source payload; it does not silently add translation.

### A7 routing

```text
LOCAL_MODEL
= intrinsic learned short-text transformation that requires no fresh/external/app capability

LOCAL_APP_OR_TOOL
= request requires an explicitly available local app/tool/live capability

EXTERNAL
= request requires fresh/non-local world capability that is not available locally

CLARIFY
= request/entity is underdetermined
```

The benchmark fixture also declares:

```text
intrinsic_model_scope = [short_text_transformation]
```

so tool availability is not conflated with intrinsic learned behavior.

## Scorer validation

Oracle scorer test:

```text
2 passed
```

Oracle predictions satisfy the held-out RVE/TUE gates. Counterfactual/TUE assertions are applied only where the relevant denominator exists.

## Final canonical hashes

```text
calibration.jsonl
7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb

development.jsonl
2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42

test.jsonl
3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf

schema.json
6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb

human-review-sample.jsonl
d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693
```

## Freeze / leakage policy

The raw held-out set is protected procedurally. It must not be used for candidate training, prompt tuning, threshold tuning, teacher generation, or iterative error-driven model changes before the final evaluation run.

Qwen/reference output remains forbidden as benchmark truth.

## Final decision

```text
N3: PASS / FROZEN
N3.1-R1 SEMANTIC CORRECTION: PASS
TRACK-A BENCHMARK V1: PASS / FINAL FROZEN
INDEPENDENT SEMANTIC RE-REVIEW: PASS
N3.R1-A: PASS / PROTOCOL READY
N3.R1-B QWEN3.8-27B: UNBLOCKED BUT NOT EXECUTED
N4: NOT AUTHORIZED
PPF INTEGRATION: NOT AUTHORIZED
KERNEL CHANGE: NO
MODEL ARCHITECTURE CHANGE: NO
```

The next permitted step is N3.R1-B reference qualification on the real Windows/Arc machine. This closure does not authorize the 5M/10M/20M/50M size sweep.
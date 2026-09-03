# Track A Foundation Protocol — Independent QA / N3 Validation

Status: **PASS / N3 PROTOCOL FROZEN**

Reviewed artifacts:

- `docs/research/track-a-foundation-protocol.md`
- `docs/research/track-a-benchmark-spec.md`
- `docs/research/track-a-reference-model-policy.md`
- `docs/research/personal-intelligence-two-track.md`
- `docs/research/mindforge-architecture-invariants.md`

Starting reference: `5280243a54ba8977b0d02a5b4ed85c657e03193f`

## 1. QA question

Does N3 freeze a capability benchmark protocol that can later falsify the compact personal-understanding/router hypothesis without prematurely implementing Track A, PPF, mobile integration, or new model/kernel architecture?

Decision: **YES**.

## 2. Architecture compliance

The protocol preserves the frozen responsibility split:

```text
learned personal understanding/routing -> Model research
mobile/OS integration -> future Host/Adapter
PPF personal-pattern semantics -> separate optional extension
universal runtime primitive -> Kernel only after KAT
```

No new kernel primitive, model architecture, plugin API, mobile host architecture, or PPF integration is proposed or implemented.

## 3. Research-question freeze

PASS.

The protocol asks for the smallest model that preserves personal understanding/routing when world knowledge and persistent personal state are externalized.

The 5M/10M/20M/50M sizes remain candidates to test. The <=20M goal remains a hypothesis.

## 4. Capability-family freeze

PASS.

Seven v1 families are frozen:

```text
A1 personal intent
A2 personal entity resolution
A3 contextual interpretation
A4 tool/app selection
A5 argument extraction
A6 clarification decision
A7 local-vs-external routing
```

Returned-result interpretation, summarization, transformation, and multi-step agents are explicitly deferred rather than silently broadening v1.

## 5. State-externalization freeze

PASS.

Benchmark personal facts are supplied fixtures. They are not inferred by PPF and do not require PPF semantics.

This preserves Track-A/Track-B independence.

## 6. Benchmark structure freeze

PASS.

```text
1400 total cases
200 per family
280 calibration
420 development
700 held-out test
```

Language and difficulty quotas are frozen before candidate results.

The held-out set is protected from prompt/threshold/training tuning.

## 7. Adversarial and counterfactual coverage

PASS.

The protocol requires ambiguity, missing arguments, unavailable tools, local/external traps, stale state, code mixing, noisy text, unsupported actions, and controlled counterfactuals.

At least 20% of held-out cases must be in counterfactual groups.

## 8. Metrics freeze

PASS.

Each family retains a visible primary metric and relevant critical-error metrics.

A macro score cannot compensate for a failed family.

Critical rates include:

```text
under-clarification
false-local
unavailable-action false-selection
```

## 9. Success-envelope freeze

PASS.

Two envelopes are frozen before observing model results:

### RVE

```text
macro family-primary >= 0.80
no family < 0.70
under-clarification <= 0.08
false-local <= 0.05
unavailable-action false-selection <= 0.05
```

### TUE

```text
macro family-primary >= 0.90
no family < 0.85
A2 resolved-value accuracy >= 0.90
A5 exact-record match >= 0.85
A6 under-clarification <= 0.03
A7 false-local <= 0.02
unavailable-action false-selection <= 0.02
counterfactual consistency >= 0.90
```

The thresholds are hypotheses about a useful envelope, but they are now frozen for the first bounded experiment and must not be tuned after seeing size-sweep outcomes.

## 10. Smallest-model rule

PASS.

The protocol prefers the smallest candidate that meets TUE rather than the highest-scoring model overall.

If no candidate reaches RVE, the compact-model hypothesis must be stopped/reframed rather than protected with automatic architecture expansion.

## 11. Reference-model policy

PASS.

A strong external reference is kept outside the compact candidate sweep.

Teacher-as-truth is explicitly forbidden.

Qwen3.8-27B is recorded only as a proposed reference candidate requiring separate qualification.

Distillation remains blocked until a measured compact-model failure exists.

## 12. Leakage discipline

PASS.

Held-out evaluation cases cannot be used for training, paraphrased into training data, exposed to teacher generation conditioned on truth, or used for iterative threshold/prompt tuning.

## 13. N3 gate table

| Gate | Status | Evidence |
|---|---|---|
| A-FP-G1 research question frozen | PASS | explicit bounded question |
| A-FP-G2 seven capability families frozen | PASS | A1-A7 |
| A-FP-G3 externalized personal-state assumption explicit | PASS | supplied fixture, PPF-independent |
| A-FP-G4 output/scoring contract frozen | PASS | family-specific deterministic labels |
| A-FP-G5 benchmark size/splits frozen | PASS | 1400 / 280 / 420 / 700 |
| A-FP-G6 adversarial/counterfactual requirements frozen | PASS | required tags + >=20% held-out CF |
| A-FP-G7 metrics frozen before evaluation | PASS | per-family + critical rates |
| A-FP-G8 RVE/TUE frozen before results | PASS | thresholds declared |
| A-FP-G9 reference policy prevents teacher-as-truth | PASS | explicit prohibition |
| A-FP-G10 no PPF/kernel/mobile implementation | PASS | docs/protocol only |
| A-FP-G11 N4 not executed | PASS | no dataset/train/sweep results |
| A-FP-G12 size targets remain hypotheses | PASS | no <=20M capability claim |

## 14. Current limitations

N3 has not proven:

```text
that the benchmark cases are good in practice
that the 1400-case dataset can be materialized without ambiguity
that any MindForge candidate can meet RVE/TUE
that <=20M is sufficient
that Qwen3.8-27B is a suitable reference
that mobile deployment is practical
```

Those require later evidence.

## 15. Recommended next task

The next logical task is **Track-A Benchmark v1 Materialization + QA**, not model training.

That task should:

1. materialize all 1,400 cases from the frozen specification;
2. independently review held-out truth;
3. validate quotas and counterfactual groups;
4. compute artifact hashes;
5. freeze the held-out set;
6. produce a deterministic scorer;
7. STOP before training any 5M/10M/20M/50M candidate.

A separate optional task may qualify Qwen3.8-27B as an external reference. Reference qualification is not a prerequisite for benchmark materialization.

## 16. Final decision

```text
N3 — TRACK A FOUNDATION PROTOCOL: PASS / FROZEN
TRACK-A CAPABILITY ENVELOPE: NOT PROVEN
BENCHMARK V1 SPEC: FROZEN
BENCHMARK DATASET: NOT MATERIALIZED
QWEN3.8-27B: PROPOSED REFERENCE / NOT QUALIFIED
N4 SIZE SWEEP: NOT AUTHORIZED
N5 CROSS-DEVICE: NOT AUTHORIZED
TRACK A + PPF INTEGRATION: NOT AUTHORIZED
KERNEL CHANGE: NO
MODEL ARCHITECTURE CHANGE: NO
```

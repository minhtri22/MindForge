# KCL-5.2 — Frozen Replay Generalization Across Two Unseen Task-Pair Families

## Abstract

KCL-5 originally attempted replay generalization but stopped before treatment because one of two unseen task-pair families failed substrate qualification. KCL-5.1 reconstructed the benchmark layer and established U3_MIXED_POSITION as a second qualified unseen substrate alongside U1_AFFINE_PREFIX. KCL-5.2 then tested the already-frozen 6.25% replay mechanism on both families using five new final seeds, with no replay-ratio tuning, family-specific adaptation, model changes, or cross-family averaging. Both families independently passed all per-seed and aggregate generalization gates. On U1, mean A-after-B accuracy increased from 11.67% under untreated CONTROL to 75.83% with replay; mean retention gain was 64.17 percentage points and mean relative forgetting reduction was 73.03%, while B accuracy remained 100% on all seeds. On U3, replay increased A-after-B accuracy from a 23.33% CONTROL mean to 100% on every seed, eliminating measured forgetting entirely; mean relative forgetting reduction was 100%. U3 treatment B accuracy averaged 99.17%, with one seed at 95.83%, still above the frozen 95% plasticity gate. KCL-5.2 therefore closes with `REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS`. This is the first KCL result demonstrating that one fixed replay mechanism transfers across multiple independently qualified unseen task-pair structures.

## 1. Background

The kernel continual-learning evidence chain before KCL-5.2 was:

- KCL-1: controlled forgetting substrate established;
- KCL-2: untreated forgetting reproduced across final seeds;
- KCL-3: bounded replay causally reduced forgetting;
- KCL-4: 6.25% replay established as the minimum effective non-zero replay dose at batch size 16;
- KCL-5: unseen generalization attempt blocked because U2 failed substrate qualification;
- KCL-5.1: U3_MIXED_POSITION established as a second independently qualified unseen substrate.

The unresolved question was whether the same frozen replay mechanism works on both U1 and U3 without tuning.

## 2. Research Question

Does fixed 6.25% bounded replay improve retention while preserving current-task acquisition on both:

```
U1_AFFINE_PREFIX
U3_MIXED_POSITION
```

when evaluated on new final seeds?

## 3. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl52-protocol.md`

Protocol commit:

`635283c5d69f67b516becd2ec99d15ff3eeec2b3`

Protocol SHA-256:

`07871d1d545f7e3e5e3abbfdb224cd31896679719cba58f4a9139cb68bcb5aef`

The protocol was committed before official KCL-5.2 execution.

## 4. Historical Anchors

KCL-5.2 validated two committed historical evidence files before interpreting treatment results.

### KCL-5 anchor

Required:

- status = FAIL;
- verdict = `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`;
- U1_AFFINE_PREFIX qualified = true.

Evidence SHA-256:

`32460ca4a5008004ff8ff0f8d1c3cabef4f8ebf65c52bb30db16a407bf483ac0`

### KCL-5.1 anchor

Required:

- status = PASS;
- verdict = `SECOND_UNSEEN_SUBSTRATE_ESTABLISHED`;
- selected candidate = `U3_MIXED_POSITION`.

Evidence SHA-256:

`58ff172fa9261b0d3bc56ccc47cccbfef59eb3fceb5e2cc3a3bf72b460dfceae`

Both anchors validated.

## 5. Frozen Replay Mechanism

Replay remained exactly:

```
batch size = 16
15 current-task B examples
1 prior-task A replay example
replay = 6.25%
```

There was no replay-ratio search and no family-specific adaptation.

## 6. Experimental Design

Final seeds:

```
1313
1515
1717
1919
2121
```

These seeds had not been used in KCL-1 through KCL-5.1.

For each family and seed:

1. initialize one model;
2. train A once;
3. fork the exact post-A model and optimizer state;
4. CONTROL trains B using 16 B examples/batch;
5. TREATMENT trains B using 15 B + 1 replayed A example/batch;
6. evaluate A and B.

Both arms used:

- 250 B-stage optimizer updates;
- batch size 16;
- 4,000 B-stage processed examples;
- identical model architecture;
- identical optimizer hyperparameters.

## 7. Frozen Gates

Each seed had to retain a valid untreated CL problem:

```
CONTROL_B_after_B >= 0.95
CONTROL_forgetting >= 0.50
```

Treatment had to satisfy:

```
TREATMENT_B_after_B >= 0.95
retention_gain > 0
```

Each family separately also had to satisfy:

```
mean(retention_gain) >= 0.30
mean(relative_forgetting_reduction) >= 0.50
mean(TREATMENT_B_after_B) >= 0.95
```

Cross-family averaging was explicitly prohibited.

## 8. U1_AFFINE_PREFIX Results

### Aggregate

| Metric | CONTROL | 6.25% Replay |
|---|---:|---:|
| A-after-B mean | 0.1167 | 0.7583 |
| B-after-B mean | 1.0000 | 1.0000 |
| Forgetting mean | 0.8833 | 0.2417 |
| Retention gain mean | — | **0.6417** |
| Relative forgetting reduction mean | — | **0.7303** |
| B accuracy delta mean | — | 0.0000 |

Treatment A-after-B ranged from 62.5% to 91.67%.

All five seeds improved retention directionally.

### Per seed

| Seed | Control A | Replay A | Gain | Control B | Replay B | Relative forgetting reduction |
|---:|---:|---:|---:|---:|---:|---:|
| 1313 | 0.0833 | 0.6250 | 0.5417 | 1.0000 | 1.0000 | 0.5909 |
| 1515 | 0.0833 | 0.6667 | 0.5833 | 1.0000 | 1.0000 | 0.6364 |
| 1717 | 0.2500 | 0.8750 | 0.6250 | 1.0000 | 1.0000 | 0.8333 |
| 1919 | 0.0833 | 0.7083 | 0.6250 | 1.0000 | 1.0000 | 0.6818 |
| 2121 | 0.0833 | 0.9167 | 0.8333 | 1.0000 | 1.0000 | 0.9091 |

U1 passed every per-seed and aggregate gate.

## 9. U3_MIXED_POSITION Results

### Aggregate

| Metric | CONTROL | 6.25% Replay |
|---|---:|---:|
| A-after-B mean | 0.2333 | **1.0000** |
| B-after-B mean | 1.0000 | 0.9917 |
| Forgetting mean | 0.7667 | **0.0000** |
| Retention gain mean | — | **0.7667** |
| Relative forgetting reduction mean | — | **1.0000** |
| B accuracy delta mean | — | -0.00833 |

Replay eliminated measured A forgetting on all five U3 seeds.

### Per seed

| Seed | Control A | Replay A | Gain | Control B | Replay B | Relative forgetting reduction |
|---:|---:|---:|---:|---:|---:|---:|
| 1313 | 0.1667 | 1.0000 | 0.8333 | 1.0000 | 1.0000 | 1.0000 |
| 1515 | 0.1250 | 1.0000 | 0.8750 | 1.0000 | 1.0000 | 1.0000 |
| 1717 | 0.2917 | 1.0000 | 0.7083 | 1.0000 | 0.9583 | 1.0000 |
| 1919 | 0.1250 | 1.0000 | 0.8750 | 1.0000 | 1.0000 | 1.0000 |
| 2121 | 0.4583 | 1.0000 | 0.5417 | 1.0000 | 1.0000 | 1.0000 |

U3 passed every per-seed and aggregate gate.

## 10. Stability–Plasticity Observation

U1 showed no measured B cost.

U3 showed one small plasticity cost:

```
seed 1717:
CONTROL B = 1.0000
REPLAY B  = 0.9583
delta     = -0.0417
```

This remained above the frozen 0.95 per-seed plasticity gate.

The observation is important because it shows that replay generalization is not cost-free in every realization, even though the frozen operating contract remains satisfied.

## 11. No Cross-Family Rescue

The overall verdict did not come from averaging U1 and U3.

Both families independently satisfied:

- all per-seed gates;
- integrity gates;
- mean retention-gain gate;
- mean relative-forgetting-reduction gate;
- mean treatment-B gate.

Therefore the generalization claim does not depend on one strong family compensating for another weak one.

## 12. Integrity

All paired integrity checks passed:

- exact post-A model-state equality;
- exact post-A optimizer-state equality;
- equal optimizer-step count;
- equal batch size;
- exact family set;
- exact final seed set;
- historical anchors valid.

Also:

- model architecture changed: NO;
- replay-ratio search: NO;
- family-specific adaptation: NO;
- cross-family rescue: NOT ALLOWED.

## 13. Provenance

Canonical workflow:

- workflow: `Kernel CL — KCL-5.2 frozen replay generalization`;
- run ID: `35334635296`;
- source commit: `3c11e284e85ae30da1131670cfe7403df5a4663e`;
- focused tests: `39 passed`;
- scientific step: PASS;
- artifact ID: `10542855580`;
- artifact ZIP SHA-256: `a8ce7f8d323e0cf711723185b94b4f39b5b921c58395e7d4d2b2930dd1dc8709`.

Machine-readable evidence:

`experiments/kernel_cl/results/kcl52_summary.json`

## 14. Verdict

```
KCL-5.2 = PASS
REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS
```

## 15. What This Proves

Within the current qualified operating envelope, the same frozen 6.25% replay mechanism transfers across two independently qualified unseen task-pair structures.

This strengthens the evidence from:

```
single-substrate causal effect
```

to:

```
multi-substrate unseen generalization
```

without mechanism tuning.

## 16. What This Does Not Prove

KCL-5.2 does not yet establish:

- retention across long task sequences;
- bounded replay behavior as the number of learned tasks grows;
- worst-task forgetting over many stages;
- replay memory-growth behavior;
- transfer across model scales;
- final kernel continual-learning qualification.

Those remain downstream questions.

## 17. Scope

No challenger mechanism, model-scale experiment, reasoning work, PIT, OIR-PPV, PPF, RAG, external API, distillation, SFT, RL, or architecture modification was introduced.

## 18. Scientific Consequence

The unseen-generalization blocker that stopped KCL-5 is now resolved.

The next scientific threat to the continual-learning claim is sequence length: all causal evidence remains fundamentally two-task `A→B`.

The next experiment should therefore test whether the frozen replay mechanism maintains retention and plasticity over a multi-task sequence without changing its operating rule.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl52_replay_generalization.py \
  --output experiments/kernel_cl/results/kcl52_summary.json
```

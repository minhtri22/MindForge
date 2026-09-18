# MindForge Kernel Continual Learning — KCL-6.5.2 T4 Acquisition Failure Decomposition Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.2 SCIENTIFIC EXECUTION**

## 1. Prerequisite

KCL-6.5.1 is permanently closed as:

```
FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

with:

- retention specificity independently replicated;
- paired plasticity classification:
  `NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN`;
- anomalous seed `9393`:
  - E T4 = `0.75`;
  - F T4 = `0.875`;
  - both below the frozen `0.95` current-task floor.

KCL-6.5.2 does not alter KCL-6.5.1.

## 2. Research question

For seed `9393`, where does the T4 acquisition failure enter?

Candidate causal locations:

1. T4 is independently difficult for this initialization;
2. ordinary sequential T1→T2→T3 history makes T4 difficult;
3. the post-T3 exact-replay state is already acquisition-impaired before T4 replay;
4. exact replay during T4 directly interferes with acquisition;
5. E clarification/reactivation differs from exact reconstructive replay;
6. F fuzzy replay creates a distinct acquisition effect.

## 3. Primary seed

Use exactly:

```
9393
```

No seed search.

No replacement.

No additional anomaly seed may be introduced after outcome inspection.

This milestone is a mechanistic decomposition of the already observed seed-9393 failure, not a population-generalization experiment.

## 4. Frozen model/task/optimizer

Exactly the KCL-6.5.1 diagnostic kernel:

- vocabulary 96
- d_model 16
- heads 2
- layers 1
- max context 2
- FF multiplier 4
- dropout 0
- AdamW
- lr 3e-3
- weight decay 0
- 250 steps/task
- deterministic CPU execution

Task stream:

```
T1_U1_A
→ T2_U1_B
→ T3_U3_A
→ T4_U3_B
```

## 5. Frozen controls

### G0 — FRESH_T4_ONLY

Fresh model initialized with seed 9393.

Train only T4 for 250 steps.

Purpose:

> test independent T4 learnability for this initialization.

Batch:

```
16 current T4 examples
0 replay
```

Frozen T4 stream seed:

```
9393 + 4000 + 307
```

### G1 — SEQUENTIAL_CURRENT_ONLY

Train:

```
T1 → T2 → T3 → T4
```

with current-task data only.

This is the KCL-6 current-only control policy.

Purpose:

> test whether sequential history alone causes T4 acquisition failure.

Each stage:

```
16 current
0 replay
```

T1 seed remains `seed + 101`.

T2–T4 stream seeds remain:

```
seed + 1000*stage + 307
```

### G2 — EXACT_POST_T3_MATCHED_FORK

Construct the exact reconstructive C trajectory through T3:

- T1 ordinary training;
- T2 exact reconstructive replay;
- T3 exact reconstructive replay.

After T3, fork the exact same model and optimizer state.

#### G2-NR — exact-history / NO replay at T4

From the exact post-T3 fork:

```
16 current T4
0 replay
```

Purpose:

> determine whether the post-T3 exact-replay state itself can still acquire T4 without replay pressure.

The first 15 current examples at each T4 step must be identical to G2-XR/G3 E current examples.

The 16th current-only example is sampled from a dedicated frozen generator and is used only to keep batch size 16.

Frozen dedicated generator seed:

```
seed + 4999
```

#### G2-XR — exact-history / EXACT replay at T4

From the same exact post-T3 fork:

```
15 current T4
1 exact replay
```

Replay source schedule and logical ranks are exactly KCL-6.5.

Purpose:

> isolate direct T4 exact-replay interference relative to G2-NR from an identical pre-T4 state.

### G3 — E_TARGETED_CLARIFICATION

Run the frozen KCL-6.5 E policy at seed 9393.

No policy changes.

Purpose:

> test whether E is behaviorally identical to exact reconstructive replay under this affine substrate.

Required integrity expectation:

```
G3 post-T3 state == G2 exact post-T3 state
G3 T4 replay observations == G2-XR replay observations
G3 final model state == G2-XR final model state
```

Any violation => REVISE.

### G4 — F_MATCHED_PLACEBO_FUZZY

Run the frozen KCL-6.5 F policy at seed 9393.

Purpose:

> quantify the distinct fuzzy/noisy replay acquisition behavior on the same anomaly seed.

## 6. T4 learning curves

For every arm record T4 accuracy/loss at:

```
0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250
```

All 250 steps are executed.

No early stopping.

Report:

- first checkpoint reaching accuracy >= 0.95;
- final T4 accuracy;
- maximum T4 accuracy observed;
- whether final accuracy falls after first reaching threshold.

If threshold is never reached, record:

```
steps_to_95 = null
```

## 7. Frozen current-task gate

For each arm:

```
T4 final accuracy >= 0.95
```

is the same historical acquisition floor.

No gate relaxation.

## 8. Exact matched-fork requirement

G2-NR and G2-XR must have before T4:

- identical model tensors;
- identical optimizer state;
- identical T1/T2/T3 trajectory provenance.

At T4:

- same first 15 current examples on every step;
- same optimizer-step count;
- same total batch size 16.

The only deliberate difference:

```
G2-NR slot 16 = current T4
G2-XR slot 16 = exact prior replay
```

This is the primary causal contrast for direct replay interference.

## 9. G2-XR / G3 equivalence requirement

Under the current affine workload, targeted E clarification restores exact schemas before fuzzy sources are replayed.

Therefore G3 must be equivalent to exact replay for T4.

Required:

```
G2-XR replay observation stream == G3 replay observation stream
G2-XR final model state == G3 final model state
G2-XR final optimizer state == G3 final optimizer state
G2-XR T4 curve == G3 T4 curve
```

If not, KCL-6.5.2 is REVISE because an unaccounted implementation/policy difference exists.

## 10. F reproduction requirement

G4 must reproduce the committed KCL-6.5.1 anomaly within one benchmark item:

```
|G4_T4 - 0.875| <= 1/24
```

G3 must reproduce:

```
|G3_T4 - 0.75| <= 1/24
```

If either fails, verdict is REVISE rather than causal classification.

## 11. Causal classification tree

Classification is evaluated in this order.

### A — INDEPENDENT_T4_LEARNABILITY_FAILURE

If:

```
G0 final T4 < 0.95
```

Then seed-9393 T4 is not independently qualified for this initialization.

Stop interpretation at this level.

### B — SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE

If:

```
G0 >= 0.95
and
G1 < 0.95
```

Then ordinary current-only sequential history is sufficient to create the T4 failure.

### C — EXACT_HISTORY_STATE_ACQUISITION_FAILURE

If:

```
G0 >= 0.95
G1 >= 0.95
G2-NR < 0.95
```

Then the exact-replay trajectory through T3 has already produced a state that cannot meet the T4 floor even when replay is removed at T4.

### D — DIRECT_EXACT_REPLAY_INTERFERENCE

If:

```
G0 >= 0.95
G1 >= 0.95
G2-NR >= 0.95
G2-XR < 0.95
G3 < 0.95
G2-XR == G3 by integrity
```

Then the direct causal difference at T4 is the replacement of one current example per step by exact prior replay.

### E — E_POLICY_SPECIFIC_FAILURE

If:

```
G2-XR >= 0.95
and
G3 < 0.95
```

This classification is allowed only if equivalence integrity fails; therefore the milestone should normally be REVISE first.

### F — FUZZY_REPLAY_SPECIFIC_FAILURE

If:

```
G2-XR >= 0.95
G3 >= 0.95
G4 < 0.95
```

Then fuzzy/noisy replay uniquely causes the acquisition failure.

### G — FAILURE_NOT_REPRODUCED

If all relevant arms pass and G3/G4 anomaly reproduction fails.

### H — MIXED_OR_UNRESOLVED

Any other valid combination.

## 12. Secondary mechanistic metrics

Report at T4:

- current examples processed;
- replay examples processed;
- exact replay match rate;
- G2-NR vs G2-XR final delta;
- G2-XR vs G3 delta;
- G3 vs G4 delta;
- T4 cross-entropy trajectory;
- first step to 95%.

These metrics are descriptive and do not override the frozen classification tree.

## 13. Integrity gates

Required:

- seed exactly 9393;
- all metrics finite;
- G2 pre-T4 fork exact;
- G2-XR/G3 equivalence exact;
- G3/G4 anomaly reproduced within 1/24;
- no architecture change;
- no replay/query policy change;
- no additional training steps;
- no KCL-7 work.

Any integrity failure:

```
KCL-6.5.2 = REVISE
T4_DECOMPOSITION_INVALID
```

## 14. Milestone status

If integrity is valid and one causal classification A–H is produced:

```
KCL-6.5.2 = PASS
<CAUSAL_CLASSIFICATION>
```

PASS here means the anomaly was validly decomposed; it does not mean the kernel CL mechanism itself passed the 95% gate.

## 15. No tuning rule

After freeze do not change:

- seed;
- task stream;
- T4 checkpoints;
- optimizer;
- replay ratio;
- E/F policies;
- exact schema;
- current-task floor;
- classification order;
- matched-fork construction.

No additional arm is introduced after outcome inspection.

## 16. Scope exclusions

KCL-6.5.2 does not:

- repair the observed failure;
- change the KCL-6.5.1 verdict;
- optimize replay ratio;
- open model-scale transfer;
- open reasoning;
- test natural-language clarification.

## 17. Required artifacts

```
experiments/kernel_cl/kcl652_t4_failure_decomposition.py
experiments/kernel_cl/results/kcl652_summary.json
tests/test_kernel_cl_kcl652.py
docs/research/kernel-continual-learning/kcl652-paper.md
.github/workflows/kernel-cl-kcl652.yml
```

## 18. Closure requirement

KCL-6.5.2 closes only after:

- protocol committed before execution;
- focused tests PASS;
- exactly one official seed-9393 decomposition run;
- raw evidence preserved;
- paper written;
- Lineage appended.

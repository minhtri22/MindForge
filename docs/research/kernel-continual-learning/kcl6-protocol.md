# MindForge Kernel Continual Learning — KCL-6 Long-Horizon Sequential Stress Protocol

Status: **FROZEN BEFORE ANY KCL-6 SCIENTIFIC EXECUTION**

Prerequisite:

- KCL-5.2 = `REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS`
- Frozen replay mechanism = one prior-task replay example per batch of 16.

## 1. Research question

Can the already-qualified 6.25% replay mechanism preserve useful knowledge across a four-task sequential stream while:

- continuing to acquire each new task;
- keeping total replay compute fixed at one replay item per update;
- avoiding catastrophic collapse of earlier tasks as the number of prior tasks grows?

KCL-6 is a long-horizon stress test. It does not search replay ratios, change the model, or introduce another continual-learning mechanism.

## 2. Frozen task sequence

Use exactly four tasks assembled from the two already-qualified unseen families:

```
T1 = U1_AFFINE_PREFIX / task A
T2 = U1_AFFINE_PREFIX / task B
T3 = U3_MIXED_POSITION / task A
T4 = U3_MIXED_POSITION / task B
```

Task definitions are inherited unchanged from KCL-5/KCL-5.1.

### T1

Input:

```
[4, KEY]
```

Mapping:

```
index = (5*i + 1) mod 24
VALUE = 40 + index
```

### T2

Input:

```
[5, KEY]
```

Mapping:

```
index = (7*i + 3) mod 24
VALUE = 40 + index
```

### T3

Input:

```
[8, KEY]
```

Mapping:

```
index = (17*i + 4) mod 24
VALUE = 40 + index
```

### T4

Input:

```
[KEY, 9]
```

Mapping:

```
index = (19*i + 7) mod 24
VALUE = 40 + index
```

with `KEY ∈ 10..33` and `i = KEY - 10`.

No task definition may be changed after protocol freeze.

## 3. Frozen model / optimizer

Use the unchanged diagnostic MindForge `TransformerLM`:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- FF multiplier: 4
- dropout: 0
- relations/task: 24
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- steps/task: 250
- batch size: 16
- CPU
- deterministic algorithms enabled

No architecture change is authorized.

## 4. Frozen long-horizon seeds

Use exactly:

```
2323
2525
2727
2929
3131
```

These seeds were not used in KCL-1 through KCL-5.2.

No seed may be added, removed, replaced, or selectively rerun after outcome inspection.

## 5. Paired long-horizon design

For each seed:

1. initialize one model;
2. train T1 once;
3. evaluate T1;
4. fork exact post-T1 model and optimizer state into CONTROL and TREATMENT;
5. continue both branches through T2, T3, T4;
6. evaluate all tasks learned so far after every stage.

### CONTROL

At stage Tk:

```
16 current-task examples
0 replay examples
```

### TREATMENT

At stages T2/T3/T4:

```
15 current-task examples
1 replay example
```

Total batch size remains 16.

## 6. Frozen replay allocation rule

Total replay budget is fixed at exactly one replay example per optimizer update, independent of the number of prior tasks.

At stage Tk, let the ordered previous-task list be:

```
[T1, ..., T(k-1)]
```

At optimizer step `s`, select replay task:

```
previous_tasks[s mod len(previous_tasks)]
```

Within that selected replay task, sample one example using a deterministic task/stage/seed-specific generator.

Therefore:

### T2

Replay source:

```
T1 only
```

### T3

Replay source alternates:

```
T1, T2, T1, T2, ...
```

### T4

Replay source cycles:

```
T1, T2, T3, T1, T2, T3, ...
```

The total replay fraction remains:

```
1 / 16 = 6.25%
```

It does **not** become 6.25% per prior task.

## 7. Equal-budget rule

At every stage, both CONTROL and TREATMENT execute:

- 250 optimizer updates;
- 16 examples/update;
- 4,000 processed examples.

Thus treatment does not receive extra optimizer steps or extra processed examples.

KCL-6 claims equal update/example-count budget, not exact wall-clock equality.

## 8. Replay storage accounting

Treatment may retain the complete 24-example dataset for each previously learned task as the replay source.

Logical replay storage after each completed task:

```
after T1: 24 examples available for future replay
after T2: 48
after T3: 72
after T4: 96 total learned-task examples
```

At the T4 training stage, replay draws from the 72 examples belonging to T1-T3.

KCL-6 must report replay-memory growth explicitly.

This protocol does not claim bounded storage; it tests bounded **replay compute per update**.

## 9. Evaluation matrix

After each stage, evaluate every task learned so far.

Required treatment/control matrices:

```
after T1: T1
after T2: T1, T2
after T3: T1, T2, T3
after T4: T1, T2, T3, T4
```

Per cell report accuracy and loss.

## 10. Derived metrics

For task Ti at stage j >= i:

```
forgetting(Ti, j) =
accuracy(Ti immediately after learning)
-
accuracy(Ti after stage j)
```

At final stage T4 report:

- final retention for T1, T2, T3;
- final forgetting for T1, T2, T3;
- current-task accuracy T4;
- mean prior-task retention;
- worst prior-task retention;
- mean prior-task forgetting;
- worst prior-task forgetting;
- mean retention gain vs CONTROL over T1-T3;
- per-task retention gain vs CONTROL;
- average accuracy over T1-T4.

Also report these metrics after T2 and T3 where defined.

## 11. Frozen substrate-validity gates

For every seed, CONTROL must demonstrate that each newly introduced task remains learnable in sequence:

```
CONTROL current-task accuracy immediately after its stage >= 0.95
```

for T2, T3, and T4.

T1 immediately after initial learning must also satisfy:

```
T1 accuracy >= 0.95
```

If CONTROL cannot acquire a newly introduced task to >=0.95, the long-horizon contrast is ambiguous:

```
KCL-6 = REVISE
LONG_HORIZON_SUBSTRATE_INVALID
```

## 12. Frozen treatment plasticity gates

For every seed and every treatment stage:

```
TREATMENT current-task accuracy >= 0.95
```

Replay may not preserve history by preventing current-task learning.

## 13. Frozen final retention gates

At the end of T4, for every seed:

### Directional gain

For each prior task T1, T2, T3:

```
TREATMENT_final_accuracy(Ti)
>
CONTROL_final_accuracy(Ti)
```

### Worst-task floor

```
min(TREATMENT_final_accuracy(T1..T3)) >= 0.25
```

### Mean prior-task retention

```
mean(TREATMENT_final_accuracy(T1..T3)) >= 0.50
```

### Current-task plasticity

```
TREATMENT_final_accuracy(T4) >= 0.95
```

## 14. Frozen aggregate long-horizon gates

Across the five seeds:

```
mean(final mean prior-task retention) >= 0.60
mean(final retention gain over CONTROL) >= 0.30
mean(final worst-prior-task retention) >= 0.30
mean(TREATMENT final T4 accuracy) >= 0.95
```

In addition, no seed may violate the per-seed current-task plasticity or directional-gain gates.

## 15. Stability-over-stage gate

The treatment must not show monotonic catastrophic collapse as sequence length increases.

For every seed, define:

```
mean_prior_retention_after_T2
mean_prior_retention_after_T3
mean_prior_retention_after_T4
```

KCL-6 does not require these to increase.

However, final T4 mean prior-task retention must be at least:

```
50% of treatment mean prior-task retention after T2
```

This gate detects severe collapse as the history grows.

## 16. Verdicts

### All substrate, plasticity, per-seed, aggregate and stability gates pass

```
KCL-6 = PASS
FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON
```

### Valid contrast but one or more long-horizon retention gates fail

```
KCL-6 = FAIL
FIXED_BUDGET_REPLAY_LONG_HORIZON_LIMIT_REACHED
```

### Current-task plasticity fails under treatment

```
KCL-6 = FAIL
LONG_HORIZON_REPLAY_IMPAIRS_PLASTICITY
```

### CONTROL substrate/current-task acquisition is invalid

```
KCL-6 = REVISE
LONG_HORIZON_SUBSTRATE_INVALID
```

### Pair/integrity invalid

```
KCL-6 = REVISE
LONG_HORIZON_CONTRAST_INVALID
```

## 17. No tuning / no recovery rule

After official execution begins, do not change:

- task order;
- replay allocation rule;
- replay fraction;
- seeds;
- model;
- optimizer;
- steps;
- batch size;
- gates.

Do not increase replay with task count after observing results.

Do not drop a difficult task.

Do not rerun selectively to obtain PASS.

## 18. Required artifacts

```
experiments/kernel_cl/kcl6_long_horizon.py
experiments/kernel_cl/results/kcl6_summary.json
tests/test_kernel_cl_kcl6.py
docs/research/kernel-continual-learning/kcl6-paper.md
.github/workflows/kernel-cl-kcl6.yml
```

## 19. Scope exclusions

KCL-6 does not authorize:

- KCL-7 model-scale transfer;
- challenger mechanisms;
- replay-ratio scaling with task count;
- bounded-memory redesign;
- architecture changes;
- reasoning;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- agents;
- external model APIs;
- distillation;
- SFT;
- RL.

## 20. Closure requirement

KCL-6 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official long-horizon execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

KCL-7 remains unopened until KCL-6 is reviewed.

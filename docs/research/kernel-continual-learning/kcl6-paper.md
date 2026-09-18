# KCL-6 — Long-Horizon Sequential Stress Under Fixed Replay Compute

## Abstract

KCL-5.2 established that one frozen replay mechanism, 6.25% bounded replay, generalizes across two independently qualified unseen task-pair families. KCL-6 extends the stress from two tasks to a four-task sequential stream while deliberately keeping replay compute fixed at one replay example per optimizer update. The task stream was frozen as T1=U1-A, T2=U1-B, T3=U3-A, T4=U3-B. CONTROL used 16 current-task examples per batch; TREATMENT used 15 current-task examples plus exactly one replay example. As the number of prior tasks increased, the single replay slot was distributed round-robin across all prior tasks, so per-task replay frequency decreased rather than replay budget scaling with history length. Across five new seeds, CONTROL final mean prior-task accuracy was 19.72%, while TREATMENT achieved 71.67%, a mean retention gain of 51.94 percentage points. Mean prior-task forgetting fell from 80.28% to 28.33%. The final current task T4 was acquired at 100% accuracy for every seed. Final worst-prior-task accuracy averaged 55.0%, with a minimum seed-level worst-task value of 45.83%, above all pre-registered floors. All substrate, plasticity, directional-retention, aggregate, stability, and integrity gates passed. KCL-6 therefore establishes that fixed-compute 6.25% replay survives a four-task horizon under the tested operating envelope. Replay storage, however, grew linearly with the number of learned tasks; KCL-6 proves bounded replay compute per update, not bounded memory.

## 1. Background

The KCL evidence chain before KCL-6 established:

- a valid controlled forgetting substrate;
- reproducible untreated forgetting;
- a causal bounded-replay effect;
- a minimum effective replay boundary of 6.25% at batch size 16;
- generalization of that frozen replay mechanism across two unseen task-pair structures.

All treatment evidence remained fundamentally two-task:

```
A → B
```

KCL-6 tests whether the same mechanism remains useful when the number of sequentially learned tasks grows and the replay slot must be shared across an expanding history.

## 2. Research Question

Can fixed 6.25% replay preserve useful prior-task knowledge through:

```
T1 → T2 → T3 → T4
```

while maintaining current-task plasticity and without increasing replay compute as the number of prior tasks grows?

## 3. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl6-protocol.md`

Protocol commit:

`cc809c65308ea8e2ea75e0a2dc0474bc211a1e19`

Protocol SHA-256:

`9f64ba817a8567dc2c087733e061fe67a8085293e2394d2c1d8192f7127f62bf`

The protocol was committed before official KCL-6 execution.

## 4. Historical Anchor

KCL-6 validated the committed KCL-5.2 result:

```
REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS
```

with frozen families:

```
U1_AFFINE_PREFIX
U3_MIXED_POSITION
```

and frozen replay fraction:

```
6.25%
```

Historical anchor SHA-256:

`e1baffb40c53b143cac278cb35340059c8c56217321db90ab66c95e1e68b84de`

The anchor validated successfully.

## 5. Frozen Four-Task Stream

The long-horizon sequence was:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

No task definition was modified.

This design reuses task structures that had already passed unseen-substrate qualification and replay-generalization testing, reducing the chance that a new benchmark-construction issue would be confused with long-horizon failure.

## 6. Model and Optimization

The diagnostic MindForge `TransformerLM` remained unchanged:

| Field | Value |
|---|---:|
| parameters | 4,880 |
| vocabulary | 96 |
| d_model | 16 |
| heads | 2 |
| layers | 1 |
| max context | 2 |
| FF multiplier | 4 |
| dropout | 0 |
| optimizer | AdamW |
| learning rate | 3e-3 |
| steps per task | 250 |
| batch size | 16 |

No architecture change was made.

## 7. Seeds

Fresh long-horizon seeds:

```
2323
2525
2727
2929
3131
```

None had been used in KCL-1 through KCL-5.2.

## 8. Paired Long-Horizon Design

For each seed:

1. initialize one model;
2. train T1 once;
3. fork the exact post-T1 model and optimizer state;
4. CONTROL trains T2→T3→T4 current-only;
5. TREATMENT trains the same sequence with one replay item per update;
6. evaluate all learned tasks after every stage.

The paired fork isolates cumulative replay treatment effects from initialization and T1-training differences.

## 9. Fixed Replay Compute

CONTROL:

```
16 current examples
0 replay
```

TREATMENT:

```
15 current examples
1 replay
```

Each stage used:

```
250 updates × 16 examples = 4,000 processed examples
```

Total replay examples per treatment stage remained exactly:

```
250
```

regardless of history length.

## 10. Replay Allocation Under Growing History

The one replay slot was distributed round-robin across all prior tasks.

### At T2

Only T1 exists:

```
T1: 250 replay draws
```

### At T3

Two prior tasks:

```
T1: 125
T2: 125
```

### At T4

Three prior tasks:

```
T1: 84
T2: 83
T3: 83
```

Thus replay compute did not scale with the number of prior tasks.

Per-prior-task replay frequency decreased as the horizon grew.

## 11. Frozen Gates

KCL-6 required:

### Substrate validity

Every newly introduced CONTROL task had to reach:

```
accuracy >= 0.95
```

### Treatment plasticity

Every newly introduced TREATMENT task also had to reach:

```
accuracy >= 0.95
```

### Final prior-task retention

For every seed:

```
TREATMENT final accuracy(T1..T3)
>
CONTROL final accuracy(T1..T3)
```

and:

```
worst prior-task accuracy >= 0.25
mean prior-task accuracy >= 0.50
T4 accuracy >= 0.95
```

### Aggregate

Across five seeds:

```
mean(final mean prior accuracy) >= 0.60
mean(final retention gain) >= 0.30
mean(final worst prior accuracy) >= 0.30
mean(final T4 accuracy) >= 0.95
```

### Stability

Final mean prior retention after T4 had to remain at least 50% of treatment prior retention after T2 for every seed.

## 12. Aggregate Results

| Metric | CONTROL | TREATMENT |
|---|---:|---:|
| Final mean prior-task accuracy | 0.1972 | **0.7167** |
| Final mean prior-task forgetting | 0.8028 | **0.2833** |
| Final average accuracy, all four tasks | 0.3979 | **0.7875** |
| Final T4 accuracy | 1.0000 | **1.0000** |

Treatment effect:

```
mean retention gain = +0.5194
```

or approximately:

```
+51.94 percentage points
```

Final worst-prior-task accuracy:

```
mean = 0.5500
min  = 0.4583
max  = 0.7083
```

All values exceeded the frozen floors.

## 13. Per-Seed Final Retention

| Seed | CONTROL mean prior | TREATMENT mean prior | Mean gain | TREATMENT worst prior | T4 |
|---:|---:|---:|---:|---:|---:|
| 2323 | 0.2083 | 0.7639 | 0.5556 | 0.5417 | 1.0000 |
| 2525 | 0.1806 | 0.6111 | 0.4306 | 0.4583 | 1.0000 |
| 2727 | 0.1944 | 0.6667 | 0.4722 | 0.5000 | 1.0000 |
| 2929 | 0.1528 | 0.8472 | 0.6944 | 0.7083 | 1.0000 |
| 3131 | 0.2500 | 0.6944 | 0.4444 | 0.5417 | 1.0000 |

Every seed passed all long-horizon retention and plasticity gates.

## 14. Final Prior-Task Profiles

Representative treatment profiles show that the earliest tasks remain meaningfully retained despite receiving an increasingly diluted replay share.

### Seed 2323

```
T1 = 0.5417
T2 = 0.8750
T3 = 0.8750
T4 = 1.0000
```

### Seed 2525

```
T1 = 0.4583
T2 = 0.5000
T3 = 0.8750
T4 = 1.0000
```

### Seed 2929

```
T1 = 0.7083
T2 = 0.9167
T3 = 0.9167
T4 = 1.0000
```

The oldest task, T1, is generally the hardest retained task, which is consistent with the stress design.

## 15. Stability Over Sequence Length

The frozen stability metric was:

```
final mean prior retention after T4
/
prior retention after T2
```

Aggregate:

```
mean = 1.3220
min  = 0.8730
max  = 1.8519
```

The minimum remained well above the frozen 0.50 collapse threshold.

Interestingly, later replay exposure can improve some prior-task retention relative to earlier snapshots; therefore retention trajectories need not be monotonic even while the replay slot is diluted across more tasks.

## 16. Current-Task Plasticity

Both CONTROL and TREATMENT reached 100% immediate accuracy on every newly introduced task in all five seeds.

Final T4 treatment accuracy:

```
1.0 / 1.0 / 1.0 / 1.0 / 1.0
```

Thus the retention improvement was not achieved by refusing to learn later tasks.

## 17. Replay Storage Growth

Replay compute per update stayed constant, but replay storage did not.

Each task contains 24 examples.

Logical storage:

```
after T1: 24 examples
after T2: 48
after T3: 72
after T4: 96
```

At T4, the replay source contains 72 prior-task examples.

In the synthetic tensor representation:

```
576 bytes/task
1,728 bytes for the T1-T3 replay source
```

The absolute byte count is tiny only because this is a synthetic diagnostic problem.

The scientifically relevant property is:

```
storage growth = O(number of learned tasks)
```

Therefore KCL-6 demonstrates fixed replay **compute** per update, not bounded replay memory.

## 18. Integrity

All seeds passed:

- exact post-T1 model-state equality;
- exact post-T1 optimizer-state equality;
- equal batch size;
- equal optimizer-step count;
- finite metrics;
- fixed one-item replay budget.

Also:

- replay ratio search: NO;
- replay budget increased with task count: NO;
- model architecture changed: NO;
- task order changed: NO.

## 19. Provenance

Canonical workflow:

- workflow: `Kernel CL — KCL-6 long-horizon sequential stress`;
- run ID: `35335511807`;
- source commit: `5e7043ba592f8872f9020fff48a12d06446d8597`;
- focused tests: `47 passed`;
- scientific step: PASS;
- artifact ID: `10542492835`;
- artifact ZIP SHA-256: `6a3b287828bda57b191ad6d0d46c67591eff3ef7beaa3a798093ccebfc773289`.

Machine-readable evidence:

`experiments/kernel_cl/results/kcl6_summary.json`

## 20. Verdict

```
KCL-6 = PASS
FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON
```

## 21. What This Proves

Within the qualified diagnostic operating envelope, the same 6.25% replay mechanism:

- survives a four-task sequential horizon;
- continues to acquire new tasks;
- substantially improves retention of all prior tasks;
- remains effective even though the replay slot is divided among a growing set of prior tasks;
- does so without increasing optimizer-step or processed-example budget.

This is stronger evidence for continual-learning behavior than pairwise A→B experiments alone.

## 22. What This Does Not Prove

KCL-6 does not establish:

- transfer to larger kernel scales;
- bounded replay storage;
- arbitrarily long sequence stability;
- natural-language continual learning;
- superiority over challenger mechanisms;
- final continual-learning qualification.

The replay source still grows linearly with learned tasks.

## 23. Scientific Consequence

The dominant remaining threat is now scale dependence.

All KCL-1 through KCL-6 causal evidence was generated on the same 4,880-parameter diagnostic instance of the MindForge Transformer class.

The next experiment should therefore test whether the frozen continual-learning behavior transfers to larger kernel configurations without changing the replay rule.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl6_long_horizon.py \
  --output experiments/kernel_cl/results/kcl6_summary.json
```

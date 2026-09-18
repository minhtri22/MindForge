# MindForge Kernel Continual Learning — KCL-4 Minimum Replay Boundary Protocol

Status: **FROZEN BEFORE KCL-4 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-2: untreated replay dose `0%` is a reproducible forgetting baseline.
- KCL-3: replay dose `12.5%` causally reduces forgetting under the frozen effect gates.

## 1. Research question

Within the already-frozen batch size of 16, what is the minimum non-zero replay dose that still satisfies the KCL-3 causal-effect contract?

KCL-4 characterizes a discrete replay boundary. It does not optimize replay, search arbitrary ratios, or compare alternate continual-learning mechanisms.

## 2. Discrete boundary logic

Batch size is frozen at 16 examples.

Therefore replay count is integer-valued and the smallest possible non-zero replay dose is:

```
1 / 16 = 6.25%
```

KCL-4 tests exactly one new dose:

```
15 B + 1 A replay
= 6.25% replay
```

Historical anchors:

```
0%      — KCL-2 untreated baseline, insufficient retention
12.5%   — KCL-3 causal treatment, PASS
```

No other ratio is authorized.

## 3. Frozen causal contrast

For each seed:

1. train A once;
2. fork the exact post-A model and optimizer state;
3. CONTROL: 16 B examples per batch;
4. LOW-DOSE TREATMENT: 15 B + 1 A replay per batch;
5. both arms run exactly 250 B-stage optimizer updates;
6. both arms process exactly 16 examples/update = 4,000 examples total.

The model architecture and optimizer hyperparameters remain unchanged.

## 4. Frozen substrate/model

Candidate:

`C1_TASK_PREFIX_CYCLIC`

Configuration remains identical to KCL-2/KCL-3:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- FF multiplier: 4
- dropout: 0
- task relations: 24
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- A-stage steps: 250
- B-stage steps: 250
- batch size: 16
- CPU
- deterministic algorithms enabled

## 5. Frozen seeds

Use exactly:

```
101
202
303
707
909
```

No seed may be added or removed after scientific execution.

KCL-4 is boundary characterization on the frozen substrate, not unseen-pair generalization. Unseen generalization belongs to KCL-6.

## 6. Frozen effectiveness contract

The new 6.25% dose is considered EFFECTIVE only if it satisfies the exact KCL-3 effect gates:

### Plasticity

For every seed:

```
LOW_DOSE_B_after_B >= 0.95
```

### Per-seed retention

For every seed:

```
retention_gain >= 0.30
```

where:

```
retention_gain =
LOW_DOSE_A_after_B - CONTROL_A_after_B
```

### Aggregate retention

```
mean(retention_gain) >= 0.50
```

### Aggregate forgetting

```
mean(LOW_DOSE_forgetting) <= 0.50
```

### Directional consistency

For every seed:

```
LOW_DOSE_A_after_B > CONTROL_A_after_B
```

### Integrity

- exact five seeds once each;
- all metrics finite;
- exact post-A model state equality;
- exact post-A optimizer-state equality;
- equal optimizer-step count;
- equal total batch size;
- no architecture change;
- no ratio search.

## 7. Boundary verdict logic

### Case A — 6.25% satisfies every effectiveness gate

KCL-4 verdict:

```
MINIMUM_EFFECTIVE_REPLAY_BOUNDARY_6_25_PERCENT
```

Interpretation:

6.25% is the minimum representable non-zero replay dose under batch size 16. No smaller positive integer replay count exists without changing the frozen batch granularity.

### Case B — 6.25% fails one or more effectiveness gates, but causal contrast integrity is valid

KCL-4 verdict:

```
MINIMUM_PROVEN_REPLAY_BOUNDARY_12_5_PERCENT
```

Interpretation:

0% fails retention, 6.25% fails the frozen KCL-3 effectiveness contract, and 12.5% is already proven PASS by KCL-3. Therefore 12.5% is the minimum proven effective replay dose among the representable/tested doses at batch size 16.

This is a valid KCL-4 PASS as a boundary characterization; a lower dose failing does not make the boundary experiment invalid.

### Case C — causal contrast integrity fails

KCL-4 verdict:

```
REVISE_BOUNDARY_CONTRAST_INVALID
```

No replay boundary may be claimed.

## 8. No tuning / no rerun rule

After scientific execution starts, do not change:

- replay count;
- replay ratio;
- seeds;
- task;
- batch size;
- step count;
- learning rate;
- model;
- effectiveness gates.

A valid 6.25% failure must be preserved.

Do not test 2/16 again in KCL-4; KCL-3 is the frozen 12.5% anchor.

## 9. Required metrics

Per seed:

- A-after-A accuracy/loss;
- CONTROL A-after-B accuracy/loss;
- CONTROL B-after-B accuracy/loss;
- LOW-DOSE A-after-B accuracy/loss;
- LOW-DOSE B-after-B accuracy/loss;
- control forgetting;
- low-dose forgetting;
- retention gain;
- forgetting reduction;
- B accuracy delta.

Aggregate:

- mean / population SD / min / max for all principal accuracies and effects.

## 10. Scope exclusions

Not authorized:

- KCL-5 challenger;
- unseen task pairs;
- long-horizon sequences;
- scale transfer;
- reasoning;
- alternative replay ratios;
- EWC;
- DER/DER++;
- parameter isolation;
- gradient projection;
- architecture changes;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- agents;
- external teacher/model APIs;
- distillation;
- SFT;
- RL.

## 11. Required artifacts

```
experiments/kernel_cl/kcl4_boundary.py
experiments/kernel_cl/results/kcl4_summary.json
tests/test_kernel_cl_kcl4.py
docs/research/kernel-continual-learning/kcl4-paper.md
.github/workflows/kernel-cl-kcl4.yml
```

## 12. Authorization boundary

KCL-4 may close only after:

- protocol frozen in git;
- focused tests pass;
- exactly one official 6.25% scientific execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

KCL-5 is **not authorized** by KCL-4 execution or closure.

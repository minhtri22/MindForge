# MindForge Kernel Continual Learning — KCL-5.2 Frozen Replay Generalization Protocol

Status: **FROZEN BEFORE ANY KCL-5.2 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-5 closed with `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`, but established `U1_AFFINE_PREFIX` as a qualified unseen substrate.
- KCL-5.1 closed with `SECOND_UNSEEN_SUBSTRATE_ESTABLISHED`, selecting `U3_MIXED_POSITION` as a second qualified unseen substrate.
- KCL-4 froze the minimum effective replay mechanism at `1/16 = 6.25%`.

## 1. Research question

Does the already-frozen 6.25% bounded replay mechanism generalize across both independently qualified unseen task-pair substrates:

1. `U1_AFFINE_PREFIX`
2. `U3_MIXED_POSITION`

without family-specific tuning, replay-ratio adaptation, model changes, or cross-family averaging that can rescue a failed family?

## 2. Target claim

KCL-5.2 tests:

> A single frozen replay mechanism improves prior-task retention on more than one unseen task-pair family while preserving current-task acquisition.

The claim is accepted only if **both U1 and U3 pass independently**.

## 3. Frozen families

### U1_AFFINE_PREFIX

Inherited exactly from KCL-5.

Input:

```
[TASK_ID, KEY]
```

Task IDs:

```
A = 4
B = 5
```

For `i = KEY - 10`:

```
A_index = (5*i + 1) mod 24
B_index = (7*i + 3) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

### U3_MIXED_POSITION

Inherited exactly from KCL-5.1.

Task A input:

```
[8, KEY]
```

Task B input:

```
[KEY, 9]
```

For `i = KEY - 10`:

```
A_index = (17*i + 4) mod 24
B_index = (19*i + 7) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

No family definition may be changed after protocol freeze.

## 4. Historical anchor validation

Before execution, the harness must verify committed evidence that:

### KCL-5

- status = `FAIL`
- verdict = `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`
- `U1_AFFINE_PREFIX` qualified = true

### KCL-5.1

- status = `PASS`
- verdict = `SECOND_UNSEEN_SUBSTRATE_ESTABLISHED`
- selected candidate = `U3_MIXED_POSITION`

If anchors do not match:

```
KCL-5.2 = REVISE
GENERALIZATION_ANCHOR_INVALID
```

## 5. Frozen replay mechanism

Exactly:

```
batch size = 16
15 current-task B examples
1 prior-task A replay example
replay fraction = 1/16 = 6.25%
```

No replay-ratio search.

No family-specific replay ratio.

## 6. Frozen model / optimizer

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
- A-stage steps: 250
- B-stage steps: 250
- batch size: 16
- CPU
- deterministic algorithms enabled

No Transformer architecture change is authorized.

## 7. Frozen final seeds

Use exactly:

```
1313
1515
1717
1919
2121
```

These seeds were not used in KCL-1 through KCL-5.1.

No seed may be added, removed, replaced, or rerun selectively after outcome inspection.

## 8. Paired causal design

For each family and final seed:

1. initialize one model;
2. train A once;
3. evaluate A-after-A;
4. fork exact post-A model and optimizer state into CONTROL and TREATMENT;
5. CONTROL: train 250 B-stage updates using 16 B examples/batch;
6. TREATMENT: train 250 B-stage updates using 15 B + 1 A replay/batch;
7. evaluate A and B in both arms.

Both arms process:

```
250 updates × 16 examples = 4,000 examples
```

during the B stage.

## 9. Per-seed metrics

For every family/seed record:

- A-after-A accuracy/loss;
- CONTROL A-after-B accuracy/loss;
- CONTROL B-after-B accuracy/loss;
- TREATMENT A-after-B accuracy/loss;
- TREATMENT B-after-B accuracy/loss;
- CONTROL forgetting;
- TREATMENT forgetting;
- retention gain;
- forgetting reduction;
- relative forgetting reduction;
- B accuracy delta.

Definitions:

```
control_forgetting =
A_after_A - CONTROL_A_after_B

treatment_forgetting =
A_after_A - TREATMENT_A_after_B

retention_gain =
TREATMENT_A_after_B - CONTROL_A_after_B

forgetting_reduction =
control_forgetting - treatment_forgetting

relative_forgetting_reduction =
forgetting_reduction / control_forgetting
```

Relative reduction is valid only when `control_forgetting > 0`.

## 10. Frozen per-seed generalization gates

Every final seed of each family must satisfy:

### Untreated problem remains valid

```
CONTROL_B_after_B >= 0.95
CONTROL_forgetting >= 0.50
```

### Treatment plasticity

```
TREATMENT_B_after_B >= 0.95
```

### Directional retention

```
retention_gain > 0
```

### Integrity

- all scalar metrics finite;
- post-A CONTROL/TREATMENT model states identical;
- post-A CONTROL/TREATMENT optimizer states identical;
- equal B-stage optimizer-step count;
- equal total batch size.

## 11. Frozen aggregate gates — applied separately per family

Each family must independently satisfy:

```
mean(retention_gain) >= 0.30
mean(relative_forgetting_reduction) >= 0.50
mean(TREATMENT_B_after_B) >= 0.95
```

No cross-family averaging may rescue a failed family.

## 12. Overall verdicts

### U1 PASS and U3 PASS

```
KCL-5.2 = PASS
REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS
```

### Exactly one family PASSes

```
KCL-5.2 = PARTIAL
REPLAY_GENERALIZATION_PARTIAL
```

This does not establish generalized continual-learning capability.

### Neither family PASSes

```
KCL-5.2 = FAIL
REPLAY_DOES_NOT_GENERALIZE
```

### Integrity/anchor invalid

```
KCL-5.2 = REVISE
GENERALIZATION_CONTRAST_INVALID
```

## 13. No tuning / no recovery rule

After official execution begins, do not change:

- family definitions;
- final seeds;
- replay fraction;
- model;
- optimizer;
- stage steps;
- batch size;
- per-seed gates;
- aggregate gates.

Do not substitute another family after outcome.

Do not increase replay if one family fails.

A PARTIAL or FAIL result is preserved.

## 14. Reporting

For every principal metric and each family separately report:

- mean;
- population standard deviation;
- minimum;
- maximum.

Five seeds are robustness characterization, not a formal population-level significance claim.

## 15. Scope exclusions

KCL-5.2 does not authorize:

- KCL-6 long-horizon execution;
- additional substrate reconstruction;
- replay-ratio search;
- challenger mechanisms;
- model-scale transfer;
- reasoning;
- architecture changes;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- agents;
- external model APIs;
- distillation;
- SFT;
- RL.

## 16. Required artifacts

```
experiments/kernel_cl/kcl52_replay_generalization.py
experiments/kernel_cl/results/kcl52_summary.json
tests/test_kernel_cl_kcl52.py
docs/research/kernel-continual-learning/kcl52-paper.md
.github/workflows/kernel-cl-kcl52.yml
```

## 17. Closure requirement

KCL-5.2 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official paired generalization execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

KCL-6 remains unopened until KCL-5.2 is reviewed.

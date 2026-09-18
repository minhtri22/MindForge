# MindForge Kernel Continual Learning — KCL-5 Unseen Task-Pair Generalization Protocol

Status: **FROZEN BEFORE ANY KCL-5 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-1: controlled forgetting substrate established.
- KCL-2: untreated forgetting reproducible.
- KCL-3: 12.5% bounded replay causally reduces forgetting.
- KCL-4: 6.25% is the minimum effective non-zero replay dose at batch size 16.

## 1. Research question

Does the frozen KCL-4 replay mechanism generalize to task-pair families that were not defined, qualified, selected, tuned, or executed in KCL-1 through KCL-4?

KCL-5 tests generalization of the already-frozen mechanism. It does not select a new replay ratio, model, optimizer, architecture, or continual-learning mechanism.

## 2. Generalization claim under test

The target claim is stronger than KCL-4:

> On more than one previously unseen task-pair family, 6.25% bounded replay improves retention relative to untreated sequential training while preserving acquisition of the current task.

KCL-5 requires **both** pre-registered unseen families to complete qualification and final evaluation. There is no first-PASS selection rule.

## 3. Frozen replay mechanism

Replay remains exactly:

```
batch size = 16
15 current-task examples
1 prior-task replay example
replay fraction = 1/16 = 6.25%
```

Frozen from KCL-4.

No replay-ratio search or dose adaptation by family is permitted.

## 4. Frozen model / optimizer

Use the same MindForge `TransformerLM` diagnostic configuration:

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

## 5. Unseen family U1 — AFFINE_PREFIX

Input form:

```
[TASK_ID, KEY]
```

Task IDs:

```
A = 4
B = 5
```

Keys:

```
10..33
```

Base output vocabulary:

```
40..63
```

Let `i = KEY - 10`, with `i ∈ [0, 23]`.

Mappings:

```
A_index = (5*i + 1) mod 24
B_index = (7*i + 3) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

Both multipliers 5 and 7 are coprime to 24, so each mapping is a permutation.

This family is different from KCL-1's cyclic mapping.

## 6. Unseen family U2 — STRIDE_SUFFIX

Input form:

```
[KEY, TASK_ID]
```

Task IDs:

```
A = 6
B = 7
```

Keys:

```
10..33
```

Base output vocabulary:

```
40..63
```

Let `i = KEY - 10`.

Mappings:

```
A_index = (11*i + 5) mod 24
B_index = (13*i + 2) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

11 and 13 are coprime to 24, so both mappings are permutations.

Unlike all prior KCL task pairs, the task identity is in the second input position rather than the first.

## 7. Novelty / non-reuse rule

KCL-5 must not execute:

- C1 cyclic;
- C2 reverse;
- C3 blockswap;
- any KCL-1 candidate;
- any task mapping already used in KCL-1 through KCL-4.

U1 and U2 definitions are frozen in this protocol before any KCL-5 execution.

## 8. Qualification phase

Before treatment evaluation, each unseen family must independently establish that it is a valid continual-learning test substrate.

Qualification seeds:

```
606
808
```

These seeds were not used in KCL-1 through KCL-4.

For each family and qualification seed run:

1. independent A training;
2. independent B training;
3. sequential A→B untreated training;
4. matched A→A continuation.

### Qualification gates — every seed must satisfy

```
independent_A_accuracy >= 0.95
independent_B_accuracy >= 0.95
A_after_A >= 0.95
B_after_B_untreated >= 0.95
untreated_forgetting >= 0.50
abs(A_to_A_control_drift) <= 0.10
```

If either family fails qualification:

```
KCL-5 = FAIL
UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED
```

Treatment results for an unqualified family must not be interpreted as replay-generalization evidence.

For implementation simplicity, the official harness may stop before final treatment execution if qualification fails.

## 9. Final generalization seeds

If both families qualify, run treatment evaluation on exactly:

```
111
222
333
777
999
```

These final seeds are disjoint from:

- KCL-1 qualification: 404, 505;
- KCL-2/3/4 final: 101, 202, 303, 707, 909;
- KCL-5 qualification: 606, 808.

No final seed may be added, removed, or replaced after outcome inspection.

## 10. Final paired causal design

For each family and final seed:

1. initialize one model;
2. train A once;
3. evaluate A-after-A;
4. fork exact post-A model + optimizer state;
5. CONTROL: train 250 steps using 16 B examples/batch;
6. TREATMENT: train 250 steps using 15 B + 1 A replay/batch;
7. evaluate A and B for both arms.

Both arms process exactly 4,000 examples over the B stage.

## 11. Final per-seed metrics

For CONTROL and TREATMENT:

- A-after-B accuracy/loss;
- B-after-B accuracy/loss;
- forgetting.

Derived:

```
retention_gain =
TREATMENT_A_after_B - CONTROL_A_after_B

forgetting_reduction =
CONTROL_forgetting - TREATMENT_forgetting

relative_forgetting_reduction =
forgetting_reduction / CONTROL_forgetting
```

If control forgetting is zero, the relative reduction is undefined and the family cannot satisfy the frozen substrate/generalization contract.

## 12. Frozen per-family generalization gates

For **every final seed** in each family:

### Plasticity

```
TREATMENT_B_after_B >= 0.95
```

### Direction

```
retention_gain > 0
```

No seed may worsen or fail to improve A retention.

### Valid untreated problem

```
CONTROL_B_after_B >= 0.95
CONTROL_forgetting >= 0.50
```

The final seeds themselves must continue to exhibit the untreated CL problem.

## 13. Frozen aggregate generalization gates

For each family separately:

```
mean(retention_gain) >= 0.30
mean(relative_forgetting_reduction) >= 0.50
mean(TREATMENT_B_after_B) >= 0.95
```

No cross-family averaging may rescue a failed family.

## 14. Overall verdicts

### Both U1 and U2 pass all qualification and final gates

```
KCL-5 = PASS
REPLAY_GENERALIZES_ACROSS_UNSEEN_TASK_PAIRS
```

### Both qualify, but exactly one family passes final treatment gates

```
KCL-5 = PARTIAL
REPLAY_GENERALIZATION_PARTIAL
```

This does **not** establish generalized continual-learning capability.

### Both qualify, but neither passes final treatment gates

```
KCL-5 = FAIL
REPLAY_DOES_NOT_GENERALIZE
```

### Any family fails substrate qualification

```
KCL-5 = FAIL
UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED
```

### Integrity invalid

```
KCL-5 = REVISE
GENERALIZATION_CONTRAST_INVALID
```

## 15. No tuning / no family-specific adaptation

After this protocol is committed, do not change:

- family definitions;
- mapping constants;
- input order;
- replay fraction;
- seeds;
- model;
- optimizer;
- stage steps;
- batch size;
- qualification gates;
- final gates.

No family-specific hyperparameter or replay adjustment is allowed.

## 16. Statistical reporting

For every principal metric report:

- mean;
- population standard deviation;
- minimum;
- maximum.

Five final seeds per family are used for robustness characterization, not formal population-level significance claims.

## 17. Scope exclusions

KCL-5 does not authorize:

- KCL-6 long-horizon work;
- challenger mechanisms;
- EWC;
- DER/DER++;
- parameter isolation;
- gradient projection;
- model architecture changes;
- scale changes;
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

## 18. Required artifacts

```
experiments/kernel_cl/kcl5_unseen_generalization.py
experiments/kernel_cl/results/kcl5_summary.json
tests/test_kernel_cl_kcl5.py
docs/research/kernel-continual-learning/kcl5-paper.md
.github/workflows/kernel-cl-kcl5.yml
```

## 19. Authorization boundary

KCL-5 closes only after:

- this protocol is committed;
- focused tests pass;
- one official qualification/final execution is completed;
- raw evidence is preserved;
- paper is written;
- Lineage is appended.

KCL-6 is not authorized until KCL-5 is reviewed.

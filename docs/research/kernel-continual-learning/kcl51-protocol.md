# MindForge Kernel Continual Learning — KCL-5.1 Unseen Substrate Reconstruction Protocol

Status: **FROZEN BEFORE ANY KCL-5.1 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-5 closed with `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`.
- U1_AFFINE_PREFIX is preserved as one qualified unseen substrate.
- U2_STRIDE_SUFFIX remains a historical qualification failure and must not be modified or re-used as a repaired candidate.

## 1. Research question

Can a second, previously unseen and independently qualified continual-learning substrate be established under the same untreated qualification contract, without using replay outcomes or changing the frozen 6.25% replay mechanism?

KCL-5.1 is **qualification-only**. It does not execute replay.

## 2. Scientific purpose

KCL-5 failed before treatment because only one of its two unseen families qualified.

KCL-5.1 reconstructs the benchmark layer only.

The goal is:

```
U1_AFFINE_PREFIX  — already qualified
+
one new qualified unseen substrate
=
sufficient benchmark basis to reopen frozen replay generalization
```

No continual-learning treatment result may influence substrate selection.

## 3. Frozen candidate order

Evaluate in this exact order:

1. `U3_MIXED_POSITION`
2. `U4_DISJOINT_OUTPUT_PREFIX`
3. `U5_AFFINE_PREFIX_ALT`

Select the **first** candidate satisfying every qualification gate on both qualification seeds.

Stop immediately after the first PASS.

Failed candidates evaluated before the selected candidate must remain in machine-readable evidence.

If none pass, KCL-5.1 STOPs.

## 4. Candidate U3 — MIXED_POSITION

Keys:

```
10..33
```

Output vocabulary:

```
40..63
```

Let `i = KEY - 10`.

Task A input form:

```
[8, KEY]
```

Task B input form:

```
[KEY, 9]
```

Mappings:

```
A_index = (17*i + 4) mod 24
B_index = (19*i + 7) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

17 and 19 are coprime to 24, so both mappings are permutations.

This family deliberately changes task-token position between A and B and is structurally distinct from U1.

## 5. Candidate U4 — DISJOINT_OUTPUT_PREFIX

Keys:

```
10..33
```

Task A input:

```
[10, KEY]
```

Task B input:

```
[11, KEY]
```

Let `i = KEY - 10`.

A output band:

```
40..63
```

B output band:

```
64..87
```

Mappings:

```
A_index = (5*i + 9) mod 24
B_index = (7*i + 11) mod 24
VALUE_A = 40 + A_index
VALUE_B = 64 + B_index
```

Both mappings are permutations. The output bands are disjoint.

This candidate tests whether a valid forgetting substrate exists when task outputs occupy separate token bands.

## 6. Candidate U5 — AFFINE_PREFIX_ALT

Keys:

```
10..33
```

Task IDs:

```
A = 12
B = 13
```

Input:

```
[TASK_ID, KEY]
```

Let `i = KEY - 10`.

Mappings:

```
A_index = (17*i + 13) mod 24
B_index = (23*i + 6) mod 24
VALUE_A = 40 + A_index
VALUE_B = 40 + B_index
```

17 and 23 are coprime to 24.

U5 is a fallback family with the same positional form as U1 but a new mapping and task IDs.

## 7. Novelty constraints

KCL-5.1 must not modify or execute:

- KCL-1 C1 cyclic;
- KCL-1 C2 reverse;
- KCL-1 C3 blockswap;
- KCL-5 U1;
- KCL-5 U2 as a repaired variant.

U1 may be read only as a historical qualified anchor.

U2 remains frozen as failed evidence.

## 8. Frozen model / optimizer

Use the same diagnostic `TransformerLM` configuration:

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

No model architecture change is authorized.

## 9. Frozen qualification seeds

Use exactly:

```
1212
1414
```

These seeds are new to the KCL track.

No seed may be added, removed, or replaced after outcome inspection.

## 10. Required qualification branches

For each evaluated candidate and seed:

1. independent A;
2. independent B;
3. sequential A→B untreated;
4. matched-duration A→A continuation from the exact post-A model and optimizer state.

## 11. Frozen qualification gates

Every qualification seed must satisfy all gates:

```
independent_A_accuracy >= 0.95
independent_B_accuracy >= 0.95
A_after_A >= 0.95
B_after_B_untreated >= 0.95
untreated_forgetting >= 0.50
abs(A_to_A_control_drift) <= 0.10
```

All scalar metrics must be finite.

## 12. Selection rule

### First candidate passes both seeds

```
KCL-5.1 = PASS
SECOND_UNSEEN_SUBSTRATE_ESTABLISHED
```

Record:

- selected candidate;
- all evaluated candidates;
- all failed candidates before selection;
- U1 historical anchor;
- U2 historical failure.

No replay is executed.

### No candidate passes

```
KCL-5.1 = STOP
UNSEEN_GENERALIZATION_BENCHMARK_NOT_ESTABLISHED
```

KCL-5.2 remains blocked.

### Integrity invalid

```
KCL-5.1 = REVISE
SUBSTRATE_RECONSTRUCTION_INVALID
```

## 13. No tuning rule

After protocol freeze, do not change:

- candidate definitions;
- candidate order;
- qualification seeds;
- model;
- optimizer;
- steps;
- batch size;
- qualification thresholds.

Do not add U6 after seeing outcomes.

A failed bounded pool is a valid STOP result.

## 14. Replay prohibition

KCL-5.1 must make:

```
replay_calls = 0
treatment_runs = 0
```

The frozen 6.25% replay mechanism is not modified and not executed.

## 15. Historical anchor validation

The harness must verify from committed KCL-5 evidence that:

- U1_AFFINE_PREFIX is qualified;
- U2_STRIDE_SUFFIX is not qualified;
- KCL-5 verdict is `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`.

If these anchors do not match, KCL-5.1 is invalid.

## 16. Required metrics

Per seed:

- independent A accuracy/loss;
- independent B accuracy/loss;
- A-after-A accuracy/loss;
- A-after-B accuracy/loss;
- B-after-B accuracy/loss;
- A-after-A2 control accuracy/loss;
- untreated forgetting;
- A→A control drift.

## 17. Scope exclusions

Not authorized:

- replay execution;
- KCL-5.2 treatment;
- long-horizon stress;
- model-scale transfer;
- challenger mechanisms;
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

## 18. Required artifacts

```
experiments/kernel_cl/kcl51_substrate_reconstruction.py
experiments/kernel_cl/results/kcl51_summary.json
tests/test_kernel_cl_kcl51.py
docs/research/kernel-continual-learning/kcl51-paper.md
.github/workflows/kernel-cl-kcl51.yml
```

## 19. Closure requirement

KCL-5.1 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official bounded candidate-search execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

KCL-5.2 remains unopened until KCL-5.1 closure is reviewed.

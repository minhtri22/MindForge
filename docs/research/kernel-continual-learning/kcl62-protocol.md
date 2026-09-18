# MindForge Kernel Continual Learning — KCL-6.2 Reconstructive Memory Consolidation A/B/C Protocol

Status: **FROZEN BEFORE ANY KCL-6.2 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-6 = `FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON`.
- KCL-6.1 = `EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE`.
- KCL-6.1 established that exact weighted consolidation is behaviorally valid when repeats exist, but the actual four-task workload contains no exact duplicate observations.

## 1. Research question

Can replay memory be compressed by replacing high-resolution episodic observations with a compact reconstructive schema plus exact residual exceptions, while preserving continual-learning behavior under the exact same four-task workload, replay compute, optimizer budget, and seeds used in the KCL-6.1 A/B comparison?

KCL-6.2 introduces a third arm C:

```
A — RAW episodic replay
B — WEIGHTED_EXACT replay
C — RECONSTRUCTIVE_SCHEMA + residual exceptions
```

The purpose is not to rescue KCL-6.1. A, B, and C are competing memory representations tested under one frozen condition.

## 2. Conceptual model

C represents memory as:

```
Memory = CoreSchema + ResidualExceptions
```

CoreSchema preserves the regular pattern needed to reconstruct old observations.

ResidualExceptions preserve observations that cannot be explained by the schema.

Nothing is permanently discarded unless it is exactly reconstructable from the stored schema.

This is the first controlled approximation of:

```
episode
  ↓
pattern / gist
  ↓
reconstruct old observation when replay is needed
```

## 3. Frozen A/B definitions

### Arm A — RAW

Exactly KCL-6.1 Arm A:

```
store every observed (input0, input1, target) once
```

### Arm B — WEIGHTED_EXACT

Exactly KCL-6.1 Arm B:

```
exact (input0, input1, target) -> multiplicity count
```

Sampling remains proportional to multiplicity.

No loss multiplication.

## 4. Arm C — RECONSTRUCTIVE_AFFINE_SCHEMA

C may infer a schema from the complete set of observations of one learned task.

It must not use task names, family names, KCL construction constants, or source-code mapping formulas.

It receives only observed tuples:

```
(input_token_0, input_token_1, target)
```

### 4.1 Eligible schema class

A task may be represented by one schema only if:

1. exactly one of the two input positions varies over the task observations;
2. the other input position is constant;
3. the varying input values form one contiguous integer range;
4. target values lie within one contiguous integer output band of width N;
5. there exist integers `a,b` such that for all schema-covered observations:

```
target_index = (a * key_index + b) mod N
```

where:

```
key_index = varying_input - key_min
target_index = target - output_min
N = number of distinct varying-input values
```

### 4.2 Search procedure

The schema fitter must deterministically:

1. infer the varying input position from observed cardinalities;
2. infer `task_token`, `key_min`, `output_min`, and `N` from observations;
3. search `a` in `0..N-1`;
4. search `b` in `0..N-1`;
5. select the lexicographically first `(a,b)` giving the maximum number of exact matches;
6. store all non-matching observations as residual exceptions.

No family-specific constants are allowed.

### 4.3 Exact reconstruction requirement

Before a C store is admitted for replay, reconstructing the full task from:

```
CoreSchema + ResidualExceptions
```

must reproduce the canonical observed multiset exactly.

If exact reconstruction fails:

```
C integrity = invalid
KCL-6.2 = REVISE
```

C is not permitted to silently approximate replay targets in this experiment.

## 5. Why residual exceptions are required

A pure schema may erase rare but important exceptions.

Therefore C retains any observation not explained by the best schema as an exact residual.

Conceptually:

```
high-frequency / structural regularity
    -> CoreSchema

unexplained / exceptional detail
    -> ResidualException
```

This keeps the experiment falsifiable and prevents "gist" compression from deleting conflicts by construction.

## 6. Frozen four-task workload

Use exactly the same KCL-6/KCL-6.1 sequence:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

No new task or family is introduced.

## 7. Frozen model / optimizer

Unchanged diagnostic MindForge `TransformerLM`:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- FF multiplier: 4
- dropout: 0
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- steps/task: 250
- batch size: 16
- CPU
- deterministic algorithms enabled

## 8. Frozen replay compute

All three arms:

```
15 current examples
1 replay example
batch = 16
replay = 6.25%
```

Replay source-task allocation remains the KCL-6 deterministic round-robin over all previous tasks.

No arm receives more optimizer updates or more processed examples.

## 9. Frozen A/B/C seeds

Use the exact KCL-6.1 seeds to make the comparison paired on the same condition:

```
3333
3535
3737
3939
4141
```

This is deliberate seed reuse for direct A/B/C comparison, not a new independent generalization claim.

No seed may be added, removed, replaced, or selectively rerun after outcome inspection.

## 10. Matched replay rank semantics

For each replay draw:

1. choose the same previous-task source in A/B/C;
2. draw the same integer rank `r` in `0..N-1`;
3. A returns raw observation at rank `r`;
4. B returns weighted exact observation at equivalent rank `r`;
5. C reconstructs the observation corresponding to canonical key rank `r`.

The experiment must report whether A, B, and C replay observations match exactly.

If replay observations differ because C reconstruction is not exact:

```
KCL-6.2 = REVISE
RECONSTRUCTIVE_CONTRAST_INVALID
```

## 11. C logical storage accounting

### 11.1 Core schema

Frozen packed logical schema fields:

- varying_input_position: uint8 = 1 byte
- constant_task_token: int64 = 8 bytes
- key_min: int64 = 8 bytes
- output_min: int64 = 8 bytes
- modulus_N: uint32 = 4 bytes
- multiplier_a: uint32 = 4 bytes
- offset_b: uint32 = 4 bytes
- support_count: uint32 = 4 bytes

Total:

```
CORE_SCHEMA_BYTES = 41
```

### 11.2 Residual exception

Each exact residual stores:

```
2 input int64 + 1 target int64
= 24 bytes
```

### 11.3 Total C memory

For each task:

```
C_bytes =
41
+
24 * residual_exception_count
```

If no valid schema exists, all observations are residuals and no useful C compression claim is allowed.

## 12. A/B storage accounting

Inherited from KCL-6.1:

### A

```
24 bytes / raw observation
```

### B

```
28 bytes / unique exact observation
```

## 13. Primary storage metrics at T4

Report:

```
A logical bytes
B logical bytes
C logical bytes

A/C byte compression ratio
B/C byte compression ratio

C schema count
C residual exception count
C reconstruction coverage
```

Primary C storage gate:

```
A_bytes / C_bytes >= 2.0
```

and:

```
C residual exception rate <= 0.25
```

The 2× threshold is pre-registered to require a meaningful reduction.

## 14. Behavioral metrics

At final T4, for A/B/C report:

- T1/T2/T3/T4 accuracy;
- mean prior-task accuracy;
- worst prior-task accuracy;
- mean prior-task forgetting;
- average accuracy across all tasks;
- T4 current-task accuracy.

Report deltas:

```
C - A
C - B
```

## 15. Frozen behavioral-equivalence gate

For every seed and every task:

```
abs(C_final_accuracy(Ti) - A_final_accuracy(Ti)) <= 1/24
```

Also:

```
abs(C_final_mean_prior - A_final_mean_prior) <= 1/24
```

Across seeds:

```
abs(mean(C final mean prior) - mean(A final mean prior)) <= 1/24
```

C final T4 accuracy must remain:

```
>= 0.95
```

B must continue to satisfy the KCL-6.1 equivalence contract.

## 16. Reconstruction metrics

For every task store in C report:

- schema exact-match coverage before residuals;
- residual exception count;
- full reconstruction accuracy after residual restoration;
- replay-rank exact-match rate vs A.

Required:

```
full reconstruction accuracy = 1.0
replay-rank exact-match rate = 1.0
```

for every task and seed.

## 17. Relearning trace probe

To test whether C preserves a reconstructive trace rather than merely reducing bytes, run a probe after the main A/B/C training without modifying the trained A/B/C models.

For each learned task:

1. create a fresh model initialized with the same architecture;
2. define NOVEL baseline: train from scratch on the full raw task observations;
3. define RECONSTRUCTED condition: reconstruct the task dataset from C schema + residuals and train the fresh model on that reconstructed dataset using the exact same seed/budget;
4. compare the canonical datasets and learning curves.

Because KCL-6.2 requires exact reconstruction, the pre-registered expectation is:

```
reconstructed dataset == original dataset
```

and therefore relearning cost should be identical.

This probe does **not** claim faster relearning from model parameters yet. It establishes that the compressed memory trace contains enough information to recreate the old learning problem exactly.

A future degraded-schema experiment would be required to test partial/fuzzy reconstruction and true savings in relearning cost.

## 18. Hypotheses

### H1 — Reconstruction

C can replace raw episodes with schema + residuals while exactly regenerating the old task observations.

### H2 — Continual-learning equivalence

C preserves CL behavior under the same replay compute.

### H3 — Storage reduction

C reduces logical replay memory by at least 2× relative to A.

All three are independently evaluated.

## 19. Verdicts

### H1 + H2 + H3 PASS

```
KCL-6.2 = PASS
RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS
```

### H1 + H2 PASS, H3 FAIL

```
KCL-6.2 = NEGATIVE
RECONSTRUCTIVE_SCHEMA_VALID_BUT_NOT_STORAGE_EFFECTIVE
```

### H1 PASS, H2 FAIL

```
KCL-6.2 = FAIL
RECONSTRUCTIVE_SCHEMA_CHANGES_CL_BEHAVIOR
```

### H1 FAIL or paired integrity invalid

```
KCL-6.2 = REVISE
RECONSTRUCTIVE_CONTRAST_INVALID
```

## 20. No escalation rule

After official execution begins, do not:

- add another schema family;
- change the affine search class;
- add latent/prototype clustering;
- modify task definitions;
- modify replay fraction;
- modify seeds;
- relax reconstruction or behavior gates.

Any fuzzy/partial decay experiment belongs to a later separately frozen milestone.

## 21. Historical anchors

The harness must validate:

### KCL-6

```
PASS
FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON
```

### KCL-6.1

```
NEGATIVE
EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE
```

If either anchor is invalid, KCL-6.2 is REVISE.

## 22. Required artifacts

```
experiments/kernel_cl/kcl62_reconstructive_memory_abc.py
experiments/kernel_cl/results/kcl62_summary.json
tests/test_kernel_cl_kcl62.py
docs/research/kernel-continual-learning/kcl62-paper.md
.github/workflows/kernel-cl-kcl62.yml
```

## 23. Scope exclusions

KCL-6.2 does not authorize:

- fuzzy schema decay;
- semantic similarity merging;
- latent prototype memory;
- architecture changes;
- KCL-7 scale transfer;
- reasoning;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external model APIs;
- distillation;
- SFT;
- RL.

## 24. Closure requirement

KCL-6.2 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official A/B/C execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

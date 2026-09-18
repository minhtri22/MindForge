# MindForge Kernel Continual Learning — KCL-6.3 Partial/Fuzzy Reconstructive Decay Protocol

Status: **FROZEN BEFORE ANY KCL-6.3 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-6 = `FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON`.
- KCL-6.1 = `EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE`.
- KCL-6.2 = `RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS`.

## 1. Research question

Can a reconstructive memory become intentionally lower-resolution with age, retain only a coarse structural trace, and still:

1. preserve non-trivial continual-learning behavior;
2. preserve current-task plasticity;
3. recover the exact old schema from a very small re-encounter cue;
4. relearn old tasks faster than a genuinely novel fresh model;
5. use less logical storage than the exact reconstructive schema C?

KCL-6.3 extends the A/B/C comparison with a fourth arm D.

## 2. Arms

### A — RAW_EPISODIC

Unchanged from KCL-6.1/KCL-6.2.

### B — WEIGHTED_EXACT

Unchanged from KCL-6.1/KCL-6.2.

### C — EXACT_RECONSTRUCTIVE_SCHEMA

Unchanged from KCL-6.2.

### D — FUZZY_RECONSTRUCTIVE_DECAY

D starts from the same inferred exact schema as C immediately after a task is learned.

After one subsequent task is completed, that memory becomes fuzzy.

D does not delete the memory.

It lowers resolution.

## 3. Frozen decay rule

Exact C schema fields:

- varying input position;
- constant context token;
- key_min;
- output_min;
- modulus N;
- multiplier a;
- exact offset b;
- support_count.

When a memory ages through one completed subsequent task, D performs:

```
retain:
    varying input position
    constant context token
    key_min
    output_min
    modulus N
    multiplier a

decay:
    exact offset b
    support_count
```

The exact offset is replaced by a coarse bucket.

Frozen bucket width:

```
OFFSET_BUCKET_WIDTH = 4
```

Stored fuzzy offset:

```
bucket_low = floor(b / 4) * 4
```

The original exact b is not retained in D after decay.

## 4. Age schedule

The four-task stream remains:

```
T1 → T2 → T3 → T4
```

Memory ages after a subsequent task completes.

Therefore:

### During T2 training

T1 remains exact.

### After T2 completes

T1 decays to fuzzy.

### During T3 training

- T1 fuzzy
- T2 exact

### After T3 completes

T2 decays to fuzzy.

### During T4 training

- T1 fuzzy
- T2 fuzzy
- T3 exact

### Final post-T4 memory snapshot

After T4 completes:

- T1 fuzzy
- T2 fuzzy
- T3 fuzzy
- T4 exact

This schedule is frozen.

## 5. Fuzzy replay semantics

For an exact D memory, replay is identical to C.

For a fuzzy D memory:

1. choose the same task source and logical key-rank used by the paired replay schedule;
2. reconstruct the input exactly from the retained structural schema;
3. sample one candidate offset uniformly from the four integers in the stored offset bucket;
4. reconstruct the target using retained multiplier a and sampled offset.

Thus fuzzy replay preserves:

- task identity/context;
- key structure;
- output band;
- affine relation slope.

But it may lose exact absolute target alignment.

The fuzzy replay sample is intentionally allowed to differ from A/B/C.

This is the tested decay.

## 6. Deterministic uncertainty sampling

For each seed/stage/previous-task index, D uses a dedicated deterministic RNG.

The offset candidate is sampled uniformly from:

```
bucket_low
bucket_low + 1
bucket_low + 2
bucket_low + 3
```

No candidate outside the bucket is allowed.

No adaptive correction is allowed during the main T1→T4 run.

## 7. One-cue reactivation rule

For a fuzzy memory, one exact re-encounter observation at:

```
key = key_min
```

reveals:

```
target_index = b
```

because key_index = 0.

Therefore D may reactivate:

```
exact_b = observed_target - output_min
```

After this cue, the full exact schema is reconstructed.

The cue itself is not retained as a new raw episodic replay buffer.

It is used only to restore the missing exact offset field.

## 8. Frozen model / optimizer

Exactly the KCL-6.2 diagnostic kernel:

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

No architecture change.

## 9. Frozen task sequence

Exactly:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

No task or family change.

## 10. Frozen seeds

Use exactly the KCL-6.1/KCL-6.2 paired seeds:

```
3333
3535
3737
3939
4141
```

Seed reuse is intentional because KCL-6.3 extends the same A/B/C condition with D.

No selective reruns.

## 11. Frozen replay compute

All A/B/C/D arms use:

```
15 current examples
1 replay example
batch = 16
replay fraction = 6.25%
```

No arm receives extra optimizer steps or extra replay slots.

D does not increase replay compute to compensate for decay.

## 12. D logical storage accounting

### Exact D schema

Same as C:

```
41 bytes/task
```

### Fuzzy D schema

Frozen fields:

- varying_input_position: uint8 = 1 byte
- constant_token: int64 = 8
- key_min: int64 = 8
- output_min: int64 = 8
- modulus_N: uint32 = 4
- multiplier_a: uint32 = 4
- offset_bucket_low: uint8 = 1

Total:

```
34 bytes / fuzzy task
```

No support_count.

No exact offset.

No raw residual is used in this experiment because all four KCL-6.2 task schemas had zero residuals.

Final T4 expected logical D memory:

```
3 fuzzy × 34
+
1 exact × 41
=
143 bytes
```

C final memory is:

```
164 bytes
```

## 13. Storage metrics

Report at final T4:

- A bytes;
- B bytes;
- C bytes;
- D bytes;
- C/D ratio;
- A/D ratio;
- number of exact D memories;
- number of fuzzy D memories.

Frozen D storage gate:

```
D_bytes <= 0.90 * C_bytes
```

and:

```
A_bytes / D_bytes >= 10.0
```

## 14. Main continual-learning metrics

At final T4 report A/B/C/D:

- T1/T2/T3/T4 accuracy;
- mean prior-task accuracy;
- worst prior-task accuracy;
- average all-task accuracy;
- T4 current-task accuracy.

D is intentionally lossy and is **not required** to equal A/C.

## 15. Frozen D plasticity gate

For every seed:

```
D_final_T4_accuracy >= 0.95
```

D may not preserve old gist by refusing to learn the current task.

## 16. Frozen D trace-retention gate

For every seed:

```
D_final_mean_prior_accuracy >= 0.25
```

Across seeds:

```
mean(D_final_mean_prior_accuracy) >= 0.35
```

and:

```
mean(D_final_mean_prior_accuracy)
>=
0.50 * mean(C_final_mean_prior_accuracy)
```

This allows meaningful forgetting while rejecting total collapse.

## 17. Pre-cue fuzzy reconstruction metric

For each final fuzzy D memory T1/T2/T3:

- reconstruct all 24 observations using the deterministic bucket representative:

```
bucket_low + 2
```

- report exact reconstruction accuracy.

Frozen requirement for true fuzziness:

```
pre_cue_reconstruction_accuracy < 1.0
```

for every final fuzzy memory.

A D memory that remains exact despite declared decay does not qualify as fuzzy.

## 18. One-cue recovery gate

For every final fuzzy D memory:

1. provide one exact cue at `key_min`;
2. recover exact b;
3. reconstruct all 24 observations.

Required:

```
post_cue_reconstruction_accuracy = 1.0
```

for T1, T2 and T3.

Required external cue count:

```
1
```

No original raw replay episodes may be consulted.

## 19. System-level relearning probe

After the main T1→T4 run, do not modify the recorded final D state.

For each seed and each prior task T1/T2/T3:

### D-REENCOUNTER

- clone the final D model;
- train on the exact old task dataset for 250 steps;
- evaluate every 10 steps;
- record first step reaching accuracy >= 0.95.

### NOVEL

- create a fresh model with the same architecture and deterministic initialization seed;
- train on the same exact task dataset for 250 steps;
- use the same batch stream;
- evaluate every 10 steps;
- record first step reaching accuracy >= 0.95.

All 250 steps are executed even if threshold is reached earlier.

This avoids adaptive stopping changing optimization history.

## 20. Frozen relearning-advantage gate

For each seed define:

```
mean_relearning_advantage_steps =
mean(
    NOVEL_steps_to_95
    -
    D_REENCOUNTER_steps_to_95
    over T1,T2,T3
)
```

If threshold is not reached by 250 steps, use:

```
260
```

as censored cost.

Frozen per-seed gate:

```
mean_relearning_advantage_steps > 0
```

Frozen aggregate gate:

```
mean(mean_relearning_advantage_steps across seeds) >= 20
```

Additionally, at least 2 of 3 prior tasks per seed must satisfy:

```
D_REENCOUNTER_steps_to_95
<
NOVEL_steps_to_95
```

## 21. Hypotheses

### H1 — Fuzzy trace exists

Pre-cue reconstruction is imperfect, but one cue restores exact reconstruction.

### H2 — Continual-learning trace remains useful

D retains non-trivial old-task capability and current-task plasticity.

### H3 — Relearning advantage

Re-encounter from D final state is faster than novel acquisition.

### H4 — Storage decreases beyond C

D uses less logical storage than exact reconstructive schema C.

## 22. Verdicts

### H1 + H2 + H3 + H4 PASS

```
KCL-6.3 = PASS
FUZZY_RECONSTRUCTIVE_MEMORY_RETAINS_RECOVERABLE_TRACE
```

### H1 + H4 PASS, but relearning advantage fails

```
KCL-6.3 = NEGATIVE
FUZZY_TRACE_RECOVERABLE_BUT_NO_RELEARNING_ADVANTAGE
```

### H1 fails

```
KCL-6.3 = REVISE
DECAY_DID_NOT_CREATE_VALID_FUZZY_MEMORY
```

### Plasticity or trace-retention collapses

```
KCL-6.3 = FAIL
FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
```

### Integrity invalid

```
KCL-6.3 = REVISE
FUZZY_DECAY_CONTRAST_INVALID
```

## 23. Historical anchors

Harness must validate:

### KCL-6.1

```
NEGATIVE
EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE
```

### KCL-6.2

```
PASS
RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS
```

If invalid, KCL-6.3 is REVISE.

## 24. No tuning / no recovery rule

After protocol freeze, do not change:

- bucket width;
- age schedule;
- fuzzy replay sampling;
- task order;
- seeds;
- model;
- optimizer;
- replay budget;
- retention gates;
- relearning gates;
- storage gates.

Do not add a second fuzzy representation after outcome inspection.

## 25. Scope exclusions

KCL-6.3 does not authorize:

- semantic embedding memory;
- prototype clustering;
- natural-language memory claims;
- KCL-7 scale transfer;
- architecture changes;
- reasoning;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external model APIs;
- distillation;
- SFT;
- RL.

## 26. Required artifacts

```
experiments/kernel_cl/kcl63_fuzzy_decay_abcd.py
experiments/kernel_cl/results/kcl63_summary.json
tests/test_kernel_cl_kcl63.py
docs/research/kernel-continual-learning/kcl63-paper.md
.github/workflows/kernel-cl-kcl63.yml
```

## 27. Closure requirement

KCL-6.3 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official A/B/C/D execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

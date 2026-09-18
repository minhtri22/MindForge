# MindForge Kernel Continual Learning — KCL-6.1 Weighted Replay Memory A/B Protocol

Status: **FROZEN BEFORE ANY KCL-6.1 SCIENTIFIC EXECUTION**

Prerequisite:

- KCL-6 = `FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON`.
- KCL-6 explicitly established that replay compute per update is fixed while replay storage grows with learned tasks.

## 1. Research question

Can the raw replay store used by KCL-6 be replaced by an exact weighted-consolidation representation:

```
x + x + ... + x  ->  (x, count)
```

without changing continual-learning behavior, and does that representation actually reduce storage on the frozen four-task workload?

This is an A/B test of memory representation, not a rescue attempt.

A negative result is preserved.

## 2. Hypotheses

### H-storage

If exact duplicate observations are a meaningful source of replay-storage growth, weighted consolidation should reduce unique stored entries and logical storage bytes.

### H-equivalence

If B is a correct lossless multiset representation, weighted sampling by multiplicity should preserve the replay distribution and therefore preserve CL behavior relative to A.

The two hypotheses are independent.

It is valid for H-equivalence to PASS while H-storage FAILs.

## 3. Arm A — RAW replay store

Arm A reproduces KCL-6 storage semantics.

For every learned task, retain each task observation exactly once:

```
(input_tokens, target)
```

For the four frozen tasks:

```
24 observations/task
96 observations after T4
```

No replay occurrence is appended during training.

This point is explicit: KCL-6 storage growth comes from new task observations, not from replaying the same item repeatedly.

## 4. Arm B — WEIGHTED_EXACT replay store

Arm B stores a dictionary keyed by the exact observation:

```
key = (input_token_0, input_token_1, target)
value = multiplicity_count
```

On ingestion:

```
if key exists:
    count += 1
else:
    create key with count = 1
```

No semantic similarity, latent clustering, prototype merging, rule inference, or oracle task compression is permitted.

Only exact duplicates may consolidate.

## 5. Weighted replay sampling semantics

B must sample observations with probability proportional to their multiplicity.

Do **not** replace repeated optimizer steps by multiplying a loss term.

The intended equivalence is:

```
raw multiset sampling
≈
weighted sampling from unique exact observations
```

not:

```
k sequential optimizer updates
=
one optimizer update with k × loss
```

The latter is not assumed because AdamW state and model parameters evolve between updates.

## 6. Frozen long-horizon workload

Use exactly the KCL-6 task sequence:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

Task definitions are inherited unchanged.

## 7. Frozen model / optimizer

Use the unchanged KCL diagnostic `TransformerLM`:

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

No model or optimizer change is authorized.

## 8. Frozen replay compute

Both A and B use exactly the KCL-6 replay rule:

```
15 current examples
1 replay example
batch size = 16
replay fraction = 6.25%
```

The single replay slot is allocated round-robin across previous tasks exactly as in KCL-6.

Replay compute must not differ between arms.

## 9. Frozen A/B seeds

Use exactly:

```
3333
3535
3737
3939
4141
```

These seeds are new to the KCL track.

No seed may be added, removed, replaced, or selectively rerun after outcome inspection.

## 10. Paired design

For each seed:

1. initialize and train T1 once;
2. fork exact post-T1 model and optimizer state into A and B;
3. A uses RAW replay storage;
4. B uses WEIGHTED_EXACT replay storage;
5. both learn T2→T3→T4 with identical optimizer/update/example budgets;
6. evaluate all learned tasks after every stage.

Current-task batch sampling must be driven by the same deterministic seeds in A and B.

Replay source-task allocation must be identical.

Where A and B encode the same replay multiset, use matched deterministic replay ranks so the sampled replay observation is identical whenever possible.

## 11. Exact-repeat mechanism validation

Before interpreting the long-horizon A/B result, the harness must run a deterministic representation check on a synthetic repeated multiset derived from a frozen task.

Construct:

```
repeat_count(i) = 1 + (i mod 4)
```

for the 24 observations of T1.

This produces exact repeated observations without changing targets.

Required checks:

1. RAW expanded multiset count equals sum of multiplicities.
2. WEIGHTED_EXACT unique-entry count equals 24.
3. Expanding B by multiplicity exactly reproduces A's canonical multiset.
4. For every integer rank in the expanded multiset, A rank lookup and B cumulative-weight rank lookup return the same observation.
5. No conflict is merged because consolidation key includes both input and target.

This mechanism-validation check is separate from the long-horizon storage outcome.

It proves implementation semantics; it does not prove useful compression on KCL-6.

## 12. Storage accounting

Report at T1/T2/T3/T4 for each arm:

### A

- raw observation entries;
- logical observation payload scalars;
- logical payload bytes.

Each raw observation contains:

```
2 input int64 + 1 target int64 = 24 bytes
```

### B

- unique weighted entries;
- total multiplicity;
- duplicate consolidations;
- observation payload bytes;
- count metadata bytes;
- total logical bytes.

Frozen logical B representation:

```
2 input int64 + 1 target int64 + 1 uint32 count
= 28 bytes / unique entry
```

This is a logical accounting model, not Python object heap size.

Primary compression metrics:

```
entry_compression_ratio =
A_entries / B_unique_entries

byte_compression_ratio =
A_logical_bytes / B_logical_bytes
```

Values > 1 favor B.

## 13. Behavioral equivalence metrics

At final T4 report for both A and B:

- accuracy T1/T2/T3/T4;
- mean prior-task accuracy;
- worst prior-task accuracy;
- mean prior-task forgetting;
- average accuracy over all tasks;
- T4 current-task accuracy.

Also report pairwise deltas:

```
B - A
```

## 14. Frozen behavioral equivalence gate

For every seed:

```
abs(B_final_accuracy(Ti) - A_final_accuracy(Ti)) <= 1/24
```

for every T1..T4.

And:

```
abs(B_final_mean_prior_accuracy - A_final_mean_prior_accuracy) <= 1/24
```

Across seeds:

```
abs(mean(B final mean prior) - mean(A final mean prior)) <= 1/24
```

This tolerance corresponds to one item out of each 24-example task.

Both arms must maintain final T4 accuracy >= 0.95.

## 15. Frozen storage-effect gate

A useful storage improvement requires at final T4:

```
byte_compression_ratio >= 1.20
```

and:

```
entry_compression_ratio > 1.0
```

The 20% byte threshold is pre-registered to prevent declaring trivial metadata differences as a useful compression result.

## 16. Verdicts

### Behavioral equivalence PASS + storage-effect PASS

```
KCL-6.1 = PASS
WEIGHTED_EXACT_COMPRESSION_REDUCES_STORAGE_WITHOUT_CL_LOSS
```

### Behavioral equivalence PASS + storage-effect FAIL

```
KCL-6.1 = NEGATIVE
EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE
```

This is a valid scientific closure. It means exact duplicate consolidation is not the solution to the KCL-6 linear-storage limitation on the current workload.

### Behavioral equivalence FAIL

```
KCL-6.1 = FAIL
WEIGHTED_EXACT_REPRESENTATION_CHANGES_CL_BEHAVIOR
```

### Integrity invalid

```
KCL-6.1 = REVISE
WEIGHTED_REPLAY_AB_CONTRAST_INVALID
```

## 17. No escalation rule

If exact duplicate weighting does not compress the current workload:

- do not silently switch to semantic merging;
- do not add prototype clustering;
- do not infer affine rules;
- do not change the task stream;
- do not manufacture duplicate task observations.

Any semantic/prototype/factorized compression is a separate future hypothesis with its own protocol.

## 18. Historical anchor

The harness must validate committed KCL-6 evidence:

- status = PASS;
- verdict = `FIXED_BUDGET_REPLAY_SURVIVES_FOUR_TASK_HORIZON`;
- task order matches T1→T2→T3→T4;
- replay fraction = 6.25%.

If invalid, KCL-6.1 is REVISE.

## 19. Required artifacts

```
experiments/kernel_cl/kcl61_weighted_replay_ab.py
experiments/kernel_cl/results/kcl61_summary.json
tests/test_kernel_cl_kcl61.py
docs/research/kernel-continual-learning/kcl61-paper.md
.github/workflows/kernel-cl-kcl61.yml
```

## 20. Scope exclusions

KCL-6.1 does not authorize:

- semantic deduplication;
- prototype memory;
- rule-factorized memory;
- latent compression;
- KCL-7 scale transfer;
- challenger CL mechanisms;
- reasoning;
- architecture changes;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external model APIs;
- distillation;
- SFT;
- RL.

## 21. Closure requirement

KCL-6.1 closes only after:

- protocol committed before execution;
- focused tests PASS;
- one official A/B execution;
- raw evidence preserved regardless of positive/negative result;
- paper written;
- Lineage appended.

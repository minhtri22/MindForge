# KCL-6.1 — Weighted Exact Replay Memory A/B Test

## Abstract

KCL-6 showed that fixed replay compute can survive a four-task continual-learning horizon, but replay storage grew linearly with the number of learned tasks. KCL-6.1 tests a proposed alternative memory representation motivated by the identity `ax + bx + cx = x(a+b+c)`: exact repeated observations are consolidated into one replay unit with a multiplicity count rather than stored repeatedly. The experiment compares A, the raw KCL-6 replay store, against B, an exact weighted replay store keyed by `(input, target)`. B samples according to multiplicity; it does not multiply the loss and does not use semantic or prototype merging. A deterministic mechanism-validation multiset confirmed that weighted consolidation is lossless when exact repeats exist: 60 raw occurrences were represented by 24 weighted entries with exact canonical/rank equivalence. However, on the actual four-task KCL-6 workload, all 96 stored observations were unique. Consequently B consolidated zero entries. Final entry compression was 1.0×, while logical byte compression was 0.857× because count metadata increased storage from 2,304 to 2,688 bytes. Behavior was exactly preserved: replay observations matched, post-stage model states were identical, and final accuracies were equal for every task and seed. KCL-6.1 therefore closes with the negative verdict `EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE`. The mechanism itself is valid, but exact duplication is not the source of KCL-6's linear storage growth.

## 1. Motivation

KCL-6 established two simultaneous facts:

1. replay compute per update remained fixed at one replay item per batch;
2. replay storage increased with the number of learned tasks.

A natural compression hypothesis is:

```
x + x + ... + x
→
(x, count)
```

or algebraically:

```
a·x + b·x + c·x = x(a+b+c)
```

The key scientific question is whether this representation actually addresses the observed KCL-6 storage growth, rather than merely being valid in principle.

## 2. Research Question

Can exact duplicate observations be consolidated into weighted replay units without changing continual-learning behavior, and does that consolidation reduce storage on the frozen four-task workload?

These are deliberately treated as two separate hypotheses:

- **behavioral equivalence**;
- **storage effectiveness**.

## 3. Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl61-protocol.md`

Protocol commit:

`492ba06388f1b89fd16e193b7df00c8432a282bd`

Protocol SHA-256:

`82f389051597d0b109b16cd859c92f68d05a7d650fe6db44f4c22fbd166fa2f2`

The protocol was frozen before official execution.

## 4. Arm A — Raw Replay Memory

A preserves KCL-6 semantics.

For each learned task, store every task observation exactly once:

```
(input_token_0, input_token_1, target)
```

Each task contains 24 observations.

After four tasks:

```
96 stored observations
```

Replay occurrences themselves are not appended.

## 5. Arm B — Weighted Exact Replay Memory

B stores:

```
(input_token_0, input_token_1, target) -> count
```

On an exact duplicate:

```
count += 1
```

The target is part of the consolidation key, so conflicting targets are not merged.

No semantic similarity, rule inference, prototype clustering, or latent compression is used.

## 6. Sampling Semantics

Weighted memory does not replace multiple optimizer updates by multiplying a single loss.

Instead B samples replay observations with probability proportional to multiplicity.

This distinction matters because:

- AdamW has optimizer state;
- parameters evolve between updates;
- sequential repeated updates are not generally equivalent to one scaled-loss update.

KCL-6.1 therefore tests weighted **sampling**, not weighted loss.

## 7. Exact-Repeat Mechanism Validation

Before the A/B long-horizon run, the implementation was tested on a deterministic repeated multiset.

For the 24 T1 observations:

```
repeat_count(i) = 1 + (i mod 4)
```

This produced:

```
60 raw occurrences
24 unique weighted entries
```

The validation showed:

- raw expanded count = 60;
- weighted total multiplicity = 60;
- weighted unique entries = 24;
- canonical expansion equality = PASS;
- rank lookup equality = PASS;
- target-preserving conflict safety = PASS.

Thus the representation itself works exactly when repeated observations exist.

On this synthetic repeated multiset:

```
entry compression = 60 / 24 = 2.5×
```

Using the pre-registered logical byte model:

```
A = 60 × 24 bytes = 1,440 bytes
B = 24 × 28 bytes =   672 bytes
```

so:

```
byte compression ≈ 2.143×
```

This validation proves mechanism semantics only; it does not establish compression on the actual KCL workload.

## 8. Frozen Long-Horizon Workload

The A/B test reused exactly:

```
T1 = U1-A
T2 = U1-B
T3 = U3-A
T4 = U3-B
```

Replay remained:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

Five fresh seeds were used:

```
3333
3535
3737
3939
4141
```

## 9. Paired Integrity

For every seed:

- A and B started from the exact same post-T1 model state;
- optimizer states were identical;
- current-task batches were matched;
- replay source-task allocation was matched;
- replay rank draws were matched;
- replay observations were identical;
- update counts were identical;
- batch sizes were identical.

The strongest integrity result was:

```
post-stage model states A == B
```

after T2, T3, and T4 for every seed.

## 10. Behavioral Results

Behavior was identical between A and B.

Aggregate final mean prior-task accuracy:

```
A = 0.6750
B = 0.6750
delta = 0.0000
```

Aggregate final average accuracy over all tasks:

```
A = 0.7521
B = 0.7521
```

Final T4 accuracy:

```
A mean = 0.9833
B mean = 0.9833
minimum = 0.9583
```

For every seed and every T1–T4:

```
B_accuracy - A_accuracy = 0
```

Therefore the behavioral-equivalence hypothesis passes strongly.

## 11. Storage Results on the Actual Workload

The decisive result is that exact duplicates do not occur in the stored KCL-6 task observations.

### After T1

```
A entries = 24
B unique = 24
duplicates consolidated = 0
```

### After T2

```
A entries = 48
B unique = 48
duplicates consolidated = 0
```

### After T3

```
A entries = 72
B unique = 72
duplicates consolidated = 0
```

### After T4

```
A entries = 96
B unique = 96
duplicates consolidated = 0
```

Thus:

```
entry compression ratio = 1.0×
```

There is no entry reduction.

## 12. Byte Accounting

At T4:

### A

```
96 observations × 24 bytes
= 2,304 bytes
```

### B

Payload:

```
96 observations × 24 bytes
= 2,304 bytes
```

Count metadata:

```
96 × 4 bytes
= 384 bytes
```

Total:

```
2,688 bytes
```

Therefore:

```
A/B byte compression ratio
= 2304 / 2688
= 0.8571
```

Equivalently B uses:

```
+16.67%
```

more logical storage than A on this workload.

The pre-registered useful-compression gate required:

```
byte compression ratio >= 1.20
entry compression ratio > 1.0
```

Both fail.

## 13. Scientific Interpretation

The proposed idea is not wrong.

It is conditionally correct:

> When the replay store contains exact repeated observations, weighted multiplicity is a lossless and effective representation.

KCL-6.1 directly demonstrates that case in the repeated-multiset validation.

However, the actual KCL-6 storage-growth mechanism is different.

KCL-6 stores one copy of each unique task-conditioned observation. As new tasks arrive, they introduce new observations rather than repeated copies of old observations.

Therefore:

```
linear storage growth
≠
duplicate append growth
```

in the current experimental substrate.

Exact duplicate weighting cannot compress information that is already unique.

## 14. Why This Is a Useful Negative Result

Without this A/B test, it would be easy to assume that:

```
x(a+b+c)
```

solves the observed replay-memory growth.

The experiment separates two claims:

### Claim 1

Can weighted counts replace exact repetitions?

**Yes.**

### Claim 2

Are exact repetitions the reason current KCL replay memory grows?

**No.**

This distinction prevents introducing an unnecessary memory mechanism into the kernel.

## 15. What Was Not Tried

The experiment intentionally did not escalate to:

- semantic equivalence;
- prototype consolidation;
- latent clustering;
- affine-rule reconstruction;
- task-template factorization;
- lossy compression.

Those would answer a different question and require separate falsifiable protocols.

## 16. Verdict

```
KCL-6.1 = NEGATIVE
EXACT_DUPLICATE_WEIGHTING_DOES_NOT_REDUCE_CURRENT_REPLAY_STORAGE
```

Behavioral equivalence:

```
PASS
```

Storage-effect hypothesis:

```
FAIL
```

## 17. Provenance

Canonical workflow:

- workflow: `Kernel CL — KCL-6.1 weighted replay A/B`;
- run ID: `35337991901`;
- source commit: `d6033401179a2b6c9fcca1fe7dbf9648becc7465`;
- focused tests: `55 passed`;
- official closure step: success;
- artifact ID: `10542469990`;
- artifact ZIP SHA-256: `67f3392145032f8cdc74eab976e3c3d43db9bfd9ae44a55f5bd6c5f7327bbcab`.

Machine-readable evidence:

`experiments/kernel_cl/results/kcl61_summary.json`

## 18. Conclusion

Weighted exact consolidation is a valid lossless technique for duplicated replay observations, but exact duplication is not present in the current four-task replay store.

Therefore B provides no compression benefit on KCL-6 and actually adds count-metadata overhead.

The KCL-6 storage limitation remains:

```
storage grows with the number of unique task observations retained
```

not with the number of times those observations are replayed.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl61_weighted_replay_ab.py \
  --output experiments/kernel_cl/results/kcl61_summary.json
```

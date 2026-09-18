# KCL-6.3 — Partial/Fuzzy Reconstructive Decay

## Abstract

KCL-6.2 established that exact reconstructive schema memory can replace raw episodic replay on the frozen four-task diagnostic workload with 14.05× lower logical storage and no continual-learning loss. KCL-6.3 asks a harder question: can that schema become deliberately lower-resolution with age, retain a recoverable trace, and still support continual learning?

A fourth arm D was added to the frozen A/B/C condition. D begins as the exact reconstructive schema C. After one subsequent task completes, D discards the exact affine offset and support count, retaining only structural fields plus a width-4 offset bucket. During replay, D samples an offset uniformly inside that bucket; therefore old replay targets become intentionally uncertain. After T4, T1–T3 are fuzzy and T4 remains exact.

The result is scientifically mixed but decisive. Fuzzy memory is real: deterministic pre-cue reconstruction accuracy is 0% on all final fuzzy memories, while one exact re-encounter cue restores the missing offset and recovers 100% of all 24 task observations. D also shows a strong system-level relearning advantage: across five seeds and three prior tasks, re-encounter reaches 95% accuracy an average of 74 training steps earlier than novel acquisition. D storage falls from 164 bytes in exact schema C to 143 bytes, while remaining 16.11× smaller than raw replay A.

However, the frozen continual-learning/plasticity contract fails. D final mean prior-task accuracy averages 35.28% versus 67.50% for A/B/C. More importantly, seed 3939 acquires T4 to only 91.67%, below the pre-registered 95% plasticity floor. The official verdict is therefore:

```
KCL-6.3 = FAIL
FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
```

The failure does not falsify reconstructive fuzzy memory as a trace. H1 recoverability, H3 relearning advantage, and H4 storage reduction all pass. What fails is using uncertain fuzzy reconstructions as active supervised replay targets under the frozen policy.

## 1. Background

The replay-memory sequence before KCL-6.3 was:

- KCL-6: fixed 6.25% replay survives a four-task horizon;
- KCL-6.1: exact duplicate weighting preserves behavior but does not reduce current storage;
- KCL-6.2: exact reconstructive schema compresses 96 unique observations to four schemas without CL loss.

KCL-6.2 remained lossless:

```
episodes
→ exact schema
→ exact episodes
```

KCL-6.3 introduces actual information loss:

```
exact schema
→ fuzzy schema
→ imperfect reconstruction before cue
```

and tests whether this lower-resolution trace remains useful.

## 2. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl63-protocol.md`

Protocol commit:

`8f1718f1b0e206c6d134fbf3d451db52777e4800`

Protocol SHA-256:

`fc37bd6a9759e89e3b0dd1ce79e91cdcf34bfcf808b99a0f0f8bad4dff383996`

The protocol was committed before official execution.

## 3. Frozen A/B/C/D Arms

### A — RAW_EPISODIC

Raw observations retained exactly.

### B — WEIGHTED_EXACT

Exact observations represented with multiplicity counts.

### C — EXACT_RECONSTRUCTIVE_SCHEMA

Lossless structural schema from KCL-6.2.

### D — FUZZY_RECONSTRUCTIVE_DECAY

New lossy arm.

D initially uses the exact C schema. After one subsequent task completes, the old memory discards:

- exact offset `b`;
- support count.

It retains:

- varying input position;
- constant context token;
- key minimum;
- output minimum;
- modulus;
- multiplier;
- coarse offset bucket.

Frozen bucket width:

```
4
```

## 4. Age Schedule

The frozen stream remains:

```
T1 → T2 → T3 → T4
```

Memory state over time:

```
during T2:
T1 exact

during T3:
T1 fuzzy
T2 exact

during T4:
T1 fuzzy
T2 fuzzy
T3 exact

final post-T4:
T1 fuzzy
T2 fuzzy
T3 fuzzy
T4 exact
```

This age schedule passed integrity checks on every seed.

## 5. Fuzzy Replay

For a fuzzy memory, D no longer knows the exact offset.

Replay samples one candidate offset uniformly from the retained four-value bucket.

Consequently replay retains structural information but may generate an incorrect absolute target.

Measured exact replay-match rate relative to exact memory:

| Stage | Mean | Min | Max |
|---|---:|---:|---:|
| T2 | 1.000 | 1.000 | 1.000 |
| T3 | 0.6304 | 0.616 | 0.652 |
| T4 | 0.4776 | 0.456 | 0.508 |

The decline is expected from the age schedule: a larger share of replay is drawn from fuzzy memories at later stages.

## 6. Seeds and Compute

Frozen paired seeds:

```
3333, 3535, 3737, 3939, 4141
```

All arms use:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

No additional replay compute, steps, or examples were given to D.

## 7. Fuzzy-Memory Validation

At the final T4 snapshot, T1–T3 are fuzzy.

Using the deterministic frozen bucket representative, every fuzzy task has:

```
pre-cue reconstruction accuracy = 0.0
```

Thus D is genuinely lower-resolution and not an exact schema under a different encoding.

For each fuzzy task, one exact cue at `key_min` restores the missing offset:

```
T1: b = 1
T2: b = 3
T3: b = 4
```

After that single cue:

```
post-cue reconstruction accuracy = 1.0
```

for all 24 observations of every prior task and every seed.

Therefore H1 — recoverable fuzzy trace — **PASSes**.

## 8. Storage

Final logical storage:

| Arm | Bytes |
|---|---:|
| A raw | 2304 |
| B weighted exact | 2688 |
| C exact schema | 164 |
| D fuzzy decay | **143** |

Ratios:

```
A / D = 16.1119×
C / D = 1.1469×
```

D is approximately 12.8% smaller than C.

Frozen storage requirements:

```
D <= 0.90 × C
A / D >= 10
```

Both pass.

Therefore H4 — storage below exact schema — **PASSes**.

## 9. Continual-Learning Retention

Final mean prior-task accuracy:

| Arm | Mean |
|---|---:|
| A | 0.6750 |
| B | 0.6750 |
| C | 0.6750 |
| D | **0.3528** |

D distribution:

```
mean   = 0.35278
min    = 0.29167
max    = 0.41667
pstdev = 0.04357
```

Per seed:

| Seed | A/B/C prior mean | D prior mean | D worst prior |
|---:|---:|---:|---:|
| 3333 | 0.6944 | 0.4167 | 0.1250 |
| 3535 | 0.5139 | 0.2917 | 0.0833 |
| 3737 | 0.7639 | 0.3750 | 0.0833 |
| 3939 | 0.6250 | 0.3194 | 0.0417 |
| 4141 | 0.7778 | 0.3611 | 0.1250 |

The frozen mean retention requirements themselves are narrowly satisfied:

```
D mean >= 0.35
D mean >= 0.50 × C mean
```

because:

```
0.35278 / 0.67500 ≈ 0.5226
```

However, retention becomes highly uneven: the worst old task can fall to 4.17–12.5%.

## 10. Current-Task Plasticity

D final T4 accuracy:

| Seed | D T4 |
|---:|---:|
| 3333 | 1.0000 |
| 3535 | 0.9583 |
| 3737 | 1.0000 |
| 3939 | **0.9167** |
| 4141 | 1.0000 |

Aggregate:

```
mean = 0.9750
min  = 0.9167
```

The protocol requires:

```
D T4 >= 0.95
```

for every seed.

Seed 3939 violates this gate.

Therefore H2 — useful CL trace plus plasticity — **FAILs**.

This is the decisive scientific failure for KCL-6.3.

## 11. Relearning Advantage

Despite lower online retention, the final D model relearns old tasks substantially faster than a fresh novel model.

For each prior task, both conditions receive the same exact task data and batch stream. The metric is first 10-step checkpoint reaching 95% accuracy.

Examples:

### Seed 3333

```
T1: D 60 steps vs novel 130  → +70
T2: D 30 steps vs novel 110  → +80
T3: D  0 steps vs novel 100  → +100

mean advantage = 83.33 steps
```

### Seed 3939

```
T1: D 50 vs novel 80  → +30
T2: D 30 vs novel 90  → +60
T3: D 10 vs novel 90  → +80

mean advantage = 56.67 steps
```

Across all seeds:

```
mean advantage = 74.0 steps
min            = 56.67
max            = 83.33
```

Every seed relearns all three old tasks faster than novel acquisition.

Frozen aggregate requirement:

```
mean advantage >= 20 steps
```

passes by a wide margin.

Therefore H3 — relearning advantage — **PASSes**.

## 12. Hypothesis Matrix

| Hypothesis | Result |
|---|---|
| H1 — fuzzy trace recoverable | **PASS** |
| H2 — useful CL trace + plasticity | **FAIL** |
| H3 — relearning advantage | **PASS** |
| H4 — storage below exact C | **PASS** |

This mixed result is the central KCL-6.3 finding.

## 13. Interpretation

The experiment provides evidence for two distinct functions of memory that should not be conflated:

### Reconstructive trace

D clearly retains a trace.

It is lower-resolution, can be restored exactly by one cue, and materially speeds re-learning.

### Active replay supervision

The same fuzzy representation is not safe as a direct supervised replay source under the tested policy.

At T4, only about 47.8% of D replay observations match the exact replay evidence. The rest carry an uncertain target generated from the coarse offset bucket.

The observed T4 plasticity failure and weak worst-task retention are consistent with replay-target noise, but KCL-6.3 does not independently isolate noisy replay as the sole cause.

That causal decomposition requires a separate experiment.

## 14. What KCL-6.3 Proves

Within this diagnostic workload:

1. lower-resolution reconstructive memory can exist without retaining raw episodes;
2. one cue can reactivate the exact old schema;
3. a model trained with that decayed-memory regime retains a strong relearning advantage over novel learning;
4. additional storage reduction beyond exact reconstructive C is possible;
5. directly using uncertain fuzzy reconstructions as replay targets does not satisfy the frozen continual-learning/plasticity contract.

## 15. What KCL-6.3 Does Not Prove

It does not prove:

- that all fuzzy-memory policies fail;
- that bucket width 4 is optimal;
- that a different replay policy would rescue the result;
- natural-language reconstructive memory;
- human-like forgetting;
- semantic memory;
- model-scale transfer.

No parameter was retuned after observing the result.

## 16. Provenance

Canonical workflow:

`35345896950`

Scientific source commit:

`7639df19352c813a6a78d6514eeb198075751f34`

Focused tests:

`32 passed`

Scientific step:

`completed`

Workflow conclusion:

`failure`

The workflow failure is the expected enforcement of the scientific FAIL exit code, not an implementation failure.

Artifact ID:

`10547305207`

Artifact ZIP SHA-256:

`dc272a860bdea1ae7982fcc03933a5042aec5c94e6e4199b6638bb281ebb70a6`

Protocol SHA-256:

`fc37bd6a9759e89e3b0dd1ce79e91cdcf34bfcf808b99a0f0f8bad4dff383996`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl63_summary.json`

## 17. Verdict

```
KCL-6.3 = FAIL
FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
```

This verdict follows the frozen gate because one seed violates current-task plasticity.

The negative portion should not erase the positive sub-findings:

```
recoverability = PASS
relearning advantage = PASS
storage reduction = PASS
active CL/plasticity = FAIL
```

## 18. Scientific Consequence

The next question is no longer whether a fuzzy trace can exist.

It can.

The next causal question is whether the failure arises from **using uncertain fuzzy memory as active target-bearing replay**, rather than from the fuzzy trace itself.

A scientifically clean next milestone should separate:

```
fuzzy memory as dormant/reconstructive trace
```

from:

```
fuzzy memory as noisy supervised replay
```

without changing the frozen decay representation.

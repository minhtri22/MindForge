# KCL-6.4 — Uncertainty-Aware Clarification Reactivates Fuzzy Memory

## Abstract

KCL-6.3 established a mixed result: a deliberately degraded reconstructive memory retained a recoverable fuzzy trace, used less storage, and relearned old tasks substantially faster than novel acquisition, but failed the frozen continual-learning/plasticity contract when uncertain reconstructions were used directly as supervised replay targets. KCL-6.4 preserves that failure and tests one causal hypothesis without changing the fuzzy representation, decay schedule, replay budget, task order, seeds, model, optimizer, or strict 95% current-task gate.

The paired experiment compares D, the frozen KCL-6.3 fuzzy-guess replay policy, against E, an uncertainty-aware clarification policy. When E selects a fuzzy replay source whose target is not uniquely determined, it requests exactly one minimal key-min cue, uses that cue only to restore the missing schema offset, and then performs exact replay. The cue is not inserted into a training batch, receives no gradient update, creates no raw episodic record, and does not increase replay compute.

D reproduced the prior failure condition: final T4 accuracy again fell to 91.67% on seed 3939. E passed the unchanged strict gate on every seed, with minimum T4 accuracy 95.83%. Mean prior-task accuracy increased from 35.56% under D to 67.50% under E, a paired gain of 31.94 percentage points. E used exactly three clarification queries per seed: zero at T2, one at T3, and two at T4. After clarification, E's replay-match rate was 100% at every stage, while D's fuzzy replay-match rate fell to approximately 62–65% at T3 and 45.6–50.8% at T4. E avoided an average of 223 incorrect replay targets per seed while preserving the same persistent 143-byte fuzzy-memory representation.

KCL-6.4 therefore closes:

```
KCL-6.4 = PASS
CLARIFICATION_REACTIVATION_RESCUES_FUZZY_MEMORY_POLICY
```

Within the frozen synthetic operating envelope, the result causally separates two properties: the fuzzy representation itself remains useful, while treating unresolved fuzzy content as ground-truth replay is harmful. A minimal disambiguating cue can reactivate the stored structural trace and restore the strict continual-learning contract without relaxing its gates.

## 1. Background

KCL-6.3 was deliberately not rescued after failure.

Its official result remains:

```
KCL-6.3 = FAIL
FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
```

The frozen KCL-6.3 sub-results were:

```
H1 fuzzy trace recoverable        PASS
H2 useful CL trace + plasticity   FAIL
H3 relearning advantage           PASS
H4 storage reduction              PASS
```

The critical observation was that active fuzzy replay increasingly produced uncertain pseudo-targets:

```
T2 exact replay match ≈ 100%
T3 exact replay match ≈ 63%
T4 exact replay match ≈ 48%
```

KCL-6.3 did not prove that these uncertain targets caused the failure. KCL-6.4 isolates that variable.

## 2. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl64-protocol.md`

Protocol commit:

`8490690a77a91259b6a9e0da09b2d7ecc94afc85`

Protocol SHA-256:

`6b7790938cf9584af3ecac2d282478a7540739e8a8041e5aa318f7deddb51344`

The protocol was committed before official KCL-6.4 execution.

## 3. KCL-6.3 Failure Is Preserved

KCL-6.4 validates committed KCL-6.3 evidence before execution.

Required anchor:

```
status  = FAIL
verdict = FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY

H1 = true
H2 = false
H3 = true
H4 = true
```

The anchor validated.

KCL-6.4 does not alter, supersede, or relabel the KCL-6.3 result.

## 4. Frozen Memory Representation

D and E use the same exact and fuzzy representations.

When exact, a task is represented by the reconstructive affine schema proven in KCL-6.2.

After one subsequent completed task, the memory loses:

- exact offset;
- support count.

It retains:

- varying input position;
- constant context token;
- key minimum;
- output minimum;
- modulus;
- multiplier;
- width-4 offset bucket.

No raw episodes are retained inside fuzzy memory.

Therefore:

```
representation(D) = representation(E)
```

The only manipulated variable is the policy used when replay encounters uncertainty.

## 5. Arm D — Frozen Failure Control

D is exactly the KCL-6.3 policy.

For a fuzzy replay source:

```
sample one candidate offset from the width-4 bucket
→ reconstruct one target
→ train on that target as supervised replay
```

No clarification is requested.

## 6. Arm E — Ask, Reactivate, Then Replay

E uses the same fuzzy memory.

When a replay source is fuzzy:

```
uncertainty detected
→ ASK one exact key-min cue
→ recover missing offset
→ reactivate exact schema
→ replay exact target
```

The cue is restricted to memory-state repair.

It is not:

- added to the minibatch;
- used as a separate training example;
- given its own gradient update;
- stored as a raw replay episode;
- counted as an extra replay slot.

Thus E obtains side information, not extra optimization budget.

## 7. Frozen Query Schedule

Clarification is reactive, never proactive.

A query occurs only on the first attempted replay of a fuzzy task in a stage.

Under the frozen age schedule:

### T2

T1 remains exact:

```
queries = 0
```

### T3

T1 is fuzzy; T2 exact:

```
queries = 1
```

### T4

T1 and T2 are fuzzy; T3 exact:

```
queries = 2
```

Total:

```
3 queries / seed
```

Every seed followed this schedule exactly.

## 8. Paired Design

Seeds:

```
3333
3535
3737
3939
4141
```

For every seed:

1. T1 is trained once;
2. exact post-T1 model and optimizer states are forked into D and E;
3. current-task minibatches are matched;
4. replay source-task scheduling is matched;
5. logical replay ranks are matched;
6. D guesses unresolved targets;
7. E asks and restores exact targets.

Replay compute in both arms:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

## 9. Strict Gate Was Not Relaxed

The decisive KCL-6.3 current-task requirement remains:

```
final T4 accuracy >= 0.95
```

for every seed.

KCL-6.4 explicitly records:

```
gate_relaxed_from_KCL63 = false
```

No 90%, 91.67%, mean-only, or post-hoc alternative gate was introduced.

## 10. D Failure Reproduction

D reproduced the KCL-6.3 failure condition.

Aggregate D:

```
mean prior-task accuracy = 0.35556
mean T4 accuracy         = 0.97500
minimum T4 accuracy      = 0.91667
```

The key failing seed remained 3939:

```
D T4 = 0.91667 < 0.95
```

Per-seed D metrics remained within the frozen one-task-resolution tolerance of the committed KCL-6.3 evidence.

Therefore:

```
D_failure_reproduced = true
```

## 11. E Strict Plasticity Result

E final T4:

| Seed | D T4 | E T4 |
|---:|---:|---:|
| 3333 | 1.0000 | 1.0000 |
| 3535 | 0.9583 | 0.9583 |
| 3737 | 1.0000 | 1.0000 |
| 3939 | **0.9167** | **0.9583** |
| 4141 | 1.0000 | 1.0000 |

Aggregate E:

```
mean = 0.98333
min  = 0.95833
max  = 1.00000
```

Every seed passed the unchanged 95% gate.

Therefore:

```
E_strict_CL_pass = true
```

## 12. Prior-Task Retention

Mean prior-task accuracy:

```
D = 0.35556
E = 0.67500
```

Mean paired gain:

```
E - D = +0.31944
```

or approximately:

```
+31.94 percentage points
```

Per seed:

| Seed | D prior mean | E prior mean | Gain |
|---:|---:|---:|---:|
| 3333 | 0.4167 | 0.6944 | +0.2778 |
| 3535 | 0.2917 | 0.5139 | +0.2222 |
| 3737 | 0.3750 | 0.7639 | +0.3889 |
| 3939 | 0.3333 | 0.6250 | +0.2917 |
| 4141 | 0.3611 | 0.7778 | +0.4167 |

E improved prior retention on every seed.

The frozen aggregate improvement gate required:

```
mean(E - D) >= 0.10
```

Observed:

```
0.31944
```

## 13. Worst-Task Retention

D worst prior-task retention remained poor:

| Seed | D worst prior | E worst prior |
|---:|---:|---:|
| 3333 | 0.1250 | 0.5000 |
| 3535 | 0.0833 | 0.4167 |
| 3737 | 0.0833 | 0.6250 |
| 3939 | 0.0417 | 0.3333 |
| 4141 | 0.1250 | 0.5833 |

The clarification policy therefore improves not only the mean but also the weakest retained prior task.

## 14. Replay-Target Accuracy

D exact replay-match rate:

### T2

```
1.0
```

because no memory is fuzzy yet.

### T3

Per seed:

```
0.640
0.624
0.620
0.652
0.616
```

### T4

Per seed:

```
0.484
0.508
0.468
0.472
0.456
```

E exact replay-match rate:

```
T2 = 1.0
T3 = 1.0
T4 = 1.0
```

for every seed.

Clarification prevents uncertain pseudo-target replay entirely after the query.

## 15. Replay Errors Avoided

Relative to D, E avoided incorrect replay targets:

```
mean = 223 / seed
min  = 217
max  = 232
```

These are not additional replay updates.

They are existing replay slots whose targets become exact after clarification.

## 16. Query Efficiency

Every seed uses exactly:

```
3 queries
```

Mean prior-retention improvement per query:

```
0.10648
```

approximately:

```
+10.65 percentage points of final mean prior accuracy per query
```

Range:

```
min = 0.07407
max = 0.13889
```

This metric is descriptive for the frozen diagnostic workload; it should not be interpreted as a universal query-efficiency constant.

## 17. Storage

Persistent final memory:

```
D = 143 bytes
E = 143 bytes
```

E therefore preserves the same low-resolution persistent memory footprint as D.

During T4, clarification temporarily reactivates T1/T2 while T3 is exact.

Measured in-stage reactivated prior-schema footprint:

```
123 bytes
```

After the stage completes, the frozen decay rule applies again:

```
T1 fuzzy
T2 fuzzy
T3 fuzzy
T4 exact
```

Persistent storage returns to:

```
143 bytes
```

The exact cue is not retained as an episodic record.

## 18. Comparison with Exact Schema C

Historical KCL-6.2/KCL-6.3 exact-schema C mean prior accuracy:

```
0.67500
```

KCL-6.4 E:

```
0.67500
```

E therefore recovers the same aggregate prior-task retention level as the historical exact reconstructive schema under the paired seeds, despite returning to fuzzy persistent storage after each stage.

This is an empirical result under the current task/schema class, not a general proof that clarification always makes fuzzy memory equivalent to exact memory.

## 19. Causal Interpretation

KCL-6.3 established that the fuzzy trace itself has useful information:

- one-cue exact reconstruction;
- relearning advantage;
- smaller storage.

But active fuzzy replay failed.

KCL-6.4 changes only what happens when the system knows its memory is underdetermined.

D:

```
uncertain
→ guess
→ treat guess as target
```

E:

```
uncertain
→ ask
→ reactivate
→ use exact target
```

D reproduces failure while E passes the original strict gate.

Within the frozen synthetic benchmark, this supports the causal interpretation:

> the KCL-6.3 failure is attributable to the policy of converting unresolved fuzzy memory into supervised pseudo-targets, not to the existence of a fuzzy reconstructive trace by itself.

The clarification channel is part of the E mechanism and must be counted as external information.

## 20. Important Limitation

The clarification environment in KCL-6.4 is a controlled synthetic oracle.

The system already knows:

- which field is uncertain;
- that one key-min observation is sufficient to disambiguate it;
- the schema class is affine and exactly recoverable from that cue.

Therefore KCL-6.4 does **not** yet prove:

- natural-language question generation;
- discovering what to ask in an unconstrained environment;
- finding the minimum query for arbitrary memories;
- human-equivalent metacognition;
- general semantic recall.

It proves a narrower property:

> when uncertainty is explicitly represented and a pre-registered minimal disambiguating cue exists, asking before replay can restore useful continual-learning behavior.

## 21. Hypothesis Matrix

| Condition | Result |
|---|---|
| KCL-6.3 D failure reproduced | **PASS** |
| E strict CL/plasticity contract | **PASS** |
| Paired D→E improvement | **PASS** |
| Query integrity | **PASS** |
| Persistent storage remains 143 bytes | **PASS** |
| Replay budget unchanged | **PASS** |

## 22. Verdict

```
KCL-6.4 = PASS
CLARIFICATION_REACTIVATION_RESCUES_FUZZY_MEMORY_POLICY
```

KCL-6.3 remains:

```
FAIL
FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
```

Both results are required for the causal interpretation.

## 23. Provenance

Canonical workflow:

`35347461695`

Scientific source commit:

`7fca0762d6f6013e4842c456c981636a98dd48da`

Protocol commit:

`8490690a77a91259b6a9e0da09b2d7ecc94afc85`

Protocol SHA-256:

`6b7790938cf9584af3ecac2d282478a7540739e8a8041e5aa318f7deddb51344`

Focused tests:

`16 passed (8 KCL-6.4 + 8 KCL-6.3)`

Artifact ID:

`10547353683`

Artifact ZIP SHA-256:

`16e6677441441a0ba50ea843d8a4e3392e594ca71fee6055a01bd534a4b497bf`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl64_summary.json`

## 24. Conclusion

KCL-6.4 validates a memory lifecycle that is qualitatively different from permanent exact replay:

```
learn
→ consolidate exact structure
→ decay to fuzzy trace
→ detect underdetermination
→ ask one minimal clarification
→ reactivate exact structure
→ replay safely
→ decay again
```

The key result is not that forgetting disappeared.

The result is that **partial forgetting can coexist with useful retained structure if unresolved content is not converted into false certainty**.

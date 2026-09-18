# KCL-6.5 — Clarification Specificity Matched-Query A/B

## Abstract

KCL-6.4 showed that targeted clarification can rescue the failed fuzzy-memory replay policy, but its control did not determine whether the benefit came from asking the *right missing information* or merely from issuing a query and receiving an external response. KCL-6.5 first qualified a matched-query placebo control in KCL-6.5-Q, then ran a fresh-seed E/F A/B test.

E receives one exact same-task key-min cue when a selected prior memory is fuzzy, reducing the missing offset candidate set from four values to one and reactivating the exact schema. F receives a ground-truth 3-tuple response at the same query opportunity, but from the current task being trained; this leaves the queried prior-task uncertainty at four candidates and has no effect on the prior memory. Query count, timing, payload arity, no-gradient/no-storage restrictions, replay budget, decay schedule, and persistent memory are matched.

On five fresh confirmatory seeds, the specificity effect on prior retention is large and consistent. E final mean prior-task accuracy is 60.83%, versus 35.28% for F, a mean paired gain of +25.56 percentage points. E improves prior retention on all five seeds. E also produces exact replay on every stage, while F remains on the fuzzy-guess policy at approximately 60.8–62.4% exact-match at T3 and 51.6–53.2% at T4. All query/storage integrity gates pass.

However, the frozen composite plasticity gate additionally required E current-task accuracy to be no worse than F on every seed and in aggregate. Although E itself passes the unchanged absolute T4 >=95% gate on all five fresh seeds, seed 4949 gives E=95.83% and F=100%, producing mean E-F T4 = -0.83 percentage points. Therefore H-S4 is false under the pre-registered composite definition, and the official protocol-level verdict is:

```
KCL-6.5 = FAIL
TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS
```

This FAIL must not be read as a null result for clarification specificity. H-S1, H-S2, H-S3, and H-S5 all pass. The experiment confirms a strong retention-specificity effect but does not confirm the stronger claim that targeted clarification carries zero paired current-task plasticity cost relative to the placebo control.

## 1. Scientific sequence

The relevant chain is:

- KCL-6.3: fuzzy guessing replay FAILs strict continual-learning contract.
- KCL-6.4: targeted clarification E PASSes against D on the original paired seeds.
- KCL-6.5-Q: matched-query placebo F is qualified before main A/B.
- KCL-6.5: fresh-seed E/F confirmatory A/B.

KCL-6.5 does not alter any earlier verdict.

## 2. Pre-main qualification

KCL-6.5-Q closed:

```
PASS
MATCHED_QUERY_CONTROL_QUALIFIED
```

Qualification established:

### Targeted E cue

```
prior fuzzy candidate set: 4 -> 1
```

for T1/T2/T3, with exact full reconstruction.

### Placebo F cue

```
prior fuzzy candidate set: 4 -> 4
```

for every T3/T4 query opportunity.

### Operational null

On qualification seed 5151:

- D and F replay observations were identical;
- post-stage model states were identical;
- post-stage optimizer states were identical.

Thus placebo querying itself has no training effect under the frozen contract.

## 3. Main protocol

Protocol:

`docs/research/kernel-continual-learning/kcl65-protocol.md`

Protocol commit:

`79c4bd0fac855ef3d4270f7dc9fb2af33b50cb8f`

Protocol SHA-256:

`4b9317484934cd03879ddff24f002197d4870db636537f8359fa7647da70253a`

## 4. Fresh confirmatory seeds

Main seeds:

```
4343
4545
4747
4949
5353
```

These were not used in prior KCL experiments or in KCL-6.5-Q.

## 5. Frozen arms

### E — targeted clarification

When replay selects a fuzzy prior memory:

```
same-task key_min cue
→ uncertainty 4 -> 1
→ exact schema reactivation
→ exact replay
```

### F — matched placebo query

At the same query opportunity:

```
current-task key_min cue
→ queried prior uncertainty 4 -> 4
→ no prior-memory update
→ continue fuzzy-guess replay
```

Both responses are exact ground-truth 3-tuples.

The experiment does not claim equal mutual information with respect to the queried prior memory; relevance to that uncertainty is the manipulated variable.

## 6. Query envelope

Both arms use:

```
T2: 0 queries
T3: 1 query
T4: 2 queries
total: 3 / seed
```

For both E and F:

- cue enters training batch: NO;
- cue receives gradient: NO;
- cue is stored as raw replay memory: NO;
- replay slots increase: NO;
- optimizer steps increase: NO.

All query-envelope integrity gates pass.

## 7. Replay compute and memory

Both arms use:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

Both retain final persistent memory:

```
143 bytes
```

and final age state:

```
[fuzzy, fuzzy, fuzzy, exact]
```

## 8. Candidate-set manipulation

For every E query:

```
candidate_count_before = 4
candidate_count_after  = 1
```

For every F query:

```
candidate_count_before = 4
candidate_count_after  = 4
```

H-S1 passes.

## 9. Replay-target correctness

E exact replay-match rate:

```
T2 = 1.0
T3 = 1.0
T4 = 1.0
```

for every seed.

F exact replay-match rate:

### T3

```
0.608
0.624
0.608
0.620
0.616
```

### T4

```
0.532
0.524
0.516
0.532
0.528
```

E avoids an average of:

```
214.6 incorrect replay targets / seed
```

relative to F.

## 10. Prior-task retention

Aggregate final mean prior-task accuracy:

```
E = 0.60833
F = 0.35278
```

Mean paired gain:

```
E - F = +0.25556
```

approximately:

```
+25.56 percentage points
```

Per seed:

| Seed | E prior | F prior | E-F |
|---:|---:|---:|---:|
| 4343 | 0.5833 | 0.3750 | +0.2083 |
| 4545 | 0.7361 | 0.3611 | +0.3750 |
| 4747 | 0.7361 | 0.4306 | +0.3056 |
| 4949 | 0.5000 | 0.3611 | +0.1389 |
| 5353 | 0.4861 | 0.2361 | +0.2500 |

Every fresh seed favors targeted clarification.

Frozen H-S3 required:

```
E prior > F prior on every seed
mean(E-F) >= 0.10
```

Observed:

```
5/5 directional PASS
mean gain = 0.25556
```

Therefore H-S3 passes.

## 11. Query specificity efficiency

Every seed uses exactly three queries.

Mean specificity gain per query:

```
0.08519
```

or approximately:

```
+8.52 percentage points of final mean prior retention per targeted-vs-placebo query
```

Range:

```
0.04630 to 0.12500
```

This is descriptive for this substrate only.

## 12. Absolute strict current-task gate

E final T4:

| Seed | E T4 |
|---:|---:|
| 4343 | 1.0000 |
| 4545 | 1.0000 |
| 4747 | 1.0000 |
| 4949 | 0.9583 |
| 5353 | 0.9583 |

Aggregate:

```
mean = 0.98333
min  = 0.95833
```

The original strict absolute requirement:

```
E T4 >= 0.95 on every seed
```

passes 5/5.

This is important: E remains a viable current-task learner under the old absolute gate.

## 13. Paired current-task comparison

F final T4:

| Seed | E T4 | F T4 | E-F |
|---:|---:|---:|---:|
| 4343 | 1.0000 | 1.0000 | 0 |
| 4545 | 1.0000 | 1.0000 | 0 |
| 4747 | 1.0000 | 1.0000 | 0 |
| 4949 | **0.9583** | **1.0000** | **-0.0417** |
| 5353 | 0.9583 | 0.9583 | 0 |

Aggregate:

```
E mean = 0.98333
F mean = 0.99167
E-F    = -0.00833
```

The frozen composite H-S4 additionally required:

```
E_T4 >= F_T4 for every seed
mean(E_T4 - F_T4) >= 0
```

Seed 4949 violates the first condition, and the aggregate difference is negative.

Therefore H-S4 fails.

## 14. Hypothesis matrix

| Hypothesis | Result |
|---|---|
| H-S1 targeted specificity 4→1 vs 4→4 | **PASS** |
| H-S2 matched-query operational null/integrity | **PASS** |
| H-S3 targeted information improves prior CL | **PASS** |
| H-S4 strict composite plasticity/non-degradation | **FAIL** |
| H-S5 query/storage integrity | **PASS** |

## 15. Official verdict

Under the frozen composite protocol:

```
KCL-6.5 = FAIL
TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS
```

The workflow enforcement failure is a scientific FAIL exit code, not an implementation failure.

## 16. Correct interpretation

The broad verdict string should be interpreted through the hypothesis matrix.

The experiment **does confirm** on fresh seeds that task-relevant clarification is substantially better for prior retention than a matched placebo query.

It does **not confirm** the stronger composite claim that this retention benefit is free of any paired current-task accuracy decrement relative to F.

The observed decrement is small:

```
mean -0.83 percentage points
```

and localized to one seed:

```
4949: -4.17 percentage points
```

but because the no-degradation condition was frozen beforehand, it cannot be ignored after outcome inspection.

## 17. Why F can have slightly higher T4

F's fuzzy replay is often wrong for old tasks. That reduces prior retention, but it may also exert less effective constraint on preserving old mappings, potentially leaving more optimization capacity for the current task.

E's exact old-task replay strongly protects prior knowledge.

The observed pattern is therefore consistent with a stability-plasticity tradeoff:

```
E:
higher old-task stability
possibly slight current-task cost

F:
lower old-task stability
possibly slightly freer current-task adaptation
```

KCL-6.5 does not prove this causal explanation. It only exposes the pattern.

## 18. What is now established

Within the current diagnostic substrate:

1. targeted clarification actually reduces the relevant uncertainty;
2. placebo querying does not;
3. query mechanics alone have no effect;
4. targeted clarification produces a large, consistent prior-retention advantage on fresh seeds;
5. E still passes the absolute strict 95% current-task gate;
6. zero paired current-task cost relative to placebo is not confirmed.

## 19. What remains unresolved

The remaining question is narrow:

> Is the small E-vs-F T4 decrement a real stability-plasticity tradeoff caused by stronger exact replay, or a finite-seed fluctuation?

That question should be tested separately rather than weakening KCL-6.5 after the fact.

## 20. Provenance

Canonical workflow:

`35352115877`

Scientific source:

`33be09171774d11cad7f69c6bdeb56606fd6915b`

Focused tests:

`12 passed (6 KCL-6.5 + 6 KCL-6.5-Q)`

Artifact:

`10550201214`

Artifact ZIP SHA-256:

`436132461050321438ff2974b52f4377ebe1d2486651952f3a3864ab9620860d`

Raw evidence:

`experiments/kernel_cl/results/kcl65_summary.json`

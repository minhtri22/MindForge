# KCL-6.5.9.4 — Action-Target Failure-Mode Decomposition

## 1. Result

**Status: PASS**

```
A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY
```

KCL-6.5.9.4 prospectively decomposed the previously hard-to-identify
`A_ONLY` action target into frozen policy-failure causes and then tested
whether multiple mechanism signatures independently recur on fresh data.

The primary hypothesis passed: at least two distinct mechanism-multiset
signatures were discovery-supported and stably replicated on a fully
independent fresh cohort.

No classifier, controller, feature search, or protected-confirmatory execution
was used.

## 2. Trigger

KCL-6.5.9.3 ended:

```
NEGATIVE
BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE
```

Its strongest structural clue was persistent near-zero `A_ONLY` recall despite
substantial support under stage-only, global H1–H9, localized LRBS-v1, and a
zero-step future-task probe.

KCL-6.5.9.4 therefore tested whether the target itself was internally
heterogeneous before any further predictor escalation.

## 3. Frozen failure taxonomy

The parent safe-action contract remained unchanged.

For each unsafe policy B/C, failure causes were frozen as exact complements of
the original safety predicates:

```
P = PLASTICITY_SHORTFALL
R = RETENTION_MARGIN_VIOLATION
A = STRICT_ACCURACY_FAILURE
```

Each unsafe policy receives one of the seven non-empty cause sets:

```
P
R
A
P+R
P+A
R+A
P+R+A
```

The primary joint target is a mechanism multiset:

```
MECH{cause_1,cause_2}
```

with the two cause codes sorted so that exchanging B and C cannot create a
spurious new mechanism class.

## 4. Fresh prospective cohorts

The protocol froze 480 fresh non-confirmatory seeds before execution:

```
240 discovery seeds   = 720 boundaries
240 replication seeds = 720 boundaries
```

The cohorts were mutually disjoint and disjoint from prior KCL cohorts and the
protected confirmatory seeds.

No seed was added after outcomes were observed.

## 5. Discovery

Canonical discovery run:

```
35451702744
SUCCESS
```

Scientific source:

```
4451f86dd1966af062c02c3630d187335d7d47b8
```

Discovery `A_ONLY` support:

```
208 boundaries
154 unique seeds
```

The frozen support gate required:

```
A_ONLY count >= 150
A_ONLY unique seeds >= 100
```

and therefore passed.

Three mechanism signatures passed the frozen discovery support gate:

| Mechanism | Count | Unique seeds | Prevalence in A_ONLY |
|---|---:|---:|---:|
| `MECH{P,R}` | 130 | 107 | 0.6250 |
| `MECH{P+R,R}` | 42 | 39 | 0.201923 |
| `MECH{P,P}` | 16 | 16 | 0.076923 |

The frozen discovery support rule was:

```
count >= 12
unique_seed_count >= 10
prevalence >= 0.05
```

Thus replication was prospectively authorized.

Discovery raw evidence SHA-256:

```
8c169fdc74f4d5eee0adceb93d4505e1012ed4598624639aa94c2ce7ef233d79
```

Discovery artifact:

```
ID 10587332766
ZIP SHA-256
2a9d77dfe2b01d17b29ad0825d410cc37dc7d4999ba3b30c1325ceb36373afdf
```

Discovery evidence commit:

```
42f552390f2ef0d6a2177a1ec709235a25fdf4cb
```

## 6. Replication

Replication was opened only after discovery evidence was preserved and the
frozen discovery gate authorized continuation.

Replication workflow source:

```
88d22f318f58b4661ce1ab2400dfd4123996f652
```

Canonical replication run:

```
35453312400
SUCCESS
```

Replication `A_ONLY` support:

```
182 boundaries
144 unique seeds
```

The same phase support gate passed.

## 7. Stable replication

The preregistered stability rule required, for a discovery-supported mechanism:

```
replication count >= 12
replication unique seeds >= 10
replication prevalence >= 0.05
abs(replication - discovery prevalence) <= 0.10
95% whole-seed bootstrap CI for prevalence delta contains 0
```

### 7.1 MECH{P,R}

Discovery:

```
prevalence = 0.625000
```

Replication:

```
count = 118
unique seeds = 102
prevalence = 0.648352
```

Delta:

```
+0.023352
```

20,000-pair whole-seed bootstrap 95% CI:

```
[-0.074859, 0.121113]
```

Result:

```
STABLY_REPLICATED = true
```

### 7.2 MECH{P+R,R}

Discovery:

```
prevalence = 0.201923
```

Replication:

```
count = 35
unique seeds = 33
prevalence = 0.192308
```

Delta:

```
-0.009615
```

20,000-pair whole-seed bootstrap 95% CI:

```
[-0.088505, 0.069187]
```

Result:

```
STABLY_REPLICATED = true
```

### 7.3 MECH{P,P}

Discovery:

```
prevalence = 0.076923
```

Replication:

```
count = 10
unique seeds = 10
prevalence = 0.054945
```

Although prevalence remained above 0.05 and the prevalence delta was small,
the frozen replication support rule required `count >= 12`.

Therefore:

```
REPLICATION_SUPPORTED = false
STABLY_REPLICATED = false
```

This mode is not used to support the primary claim.

## 8. Primary adjudication

The frozen PASS criterion required at least two distinct primary
mechanism-multiset signatures to be stably replicated.

Observed:

```
MECH{P,R}     = STABLY_REPLICATED
MECH{P+R,R}   = STABLY_REPLICATED
MECH{P,P}     = NOT STABLY_REPLICATED
```

Therefore:

```
KCL-6.5.9.4 = PASS
A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY
```

## 9. Scientific interpretation

The previous `A_ONLY` label is not a homogeneous action target.

At least two reproducible mechanisms are collapsed into it:

1. `MECH{P,R}`: one unsafe intervention fails through plasticity shortfall
   while the other fails through retention-margin violation;
2. `MECH{P+R,R}`: one unsafe intervention jointly fails plasticity and
   retention while the other fails retention.

Because the primary mechanism signature is invariant to B/C role exchange,
this finding is not explained by merely swapping policy identities.

This result provides a concrete structural explanation for why the broad
`A_ONLY` label could remain difficult to identify under KCL-6.5.9.2 and
KCL-6.5.9.3.

It does **not** yet establish that either mechanism is predictable from
pre-boundary state.

## 10. What is not claimed

KCL-6.5.9.4 does not establish:

- a qualified mechanism predictor;
- a qualified controller;
- that every `A_ONLY` event belongs to one of the two stable modes;
- that `MECH{P,P}` is stable;
- that LRBS-v1 or another representation is sufficient;
- that the protected confirmatory cohort should be opened;
- that KCL-7 should start.

## 11. Integrity and provenance

Protocol commit:

```
92f0a22a3b2f6198d47c7232998f68d880c278dc
```

Protocol SHA-256:

```
12d89ace37d6d95129fa559b492c2005ab6884e75d4b93ac6142c981787f5578
```

Implementation commit:

```
da4fd62f5608601f71572b0e7e2b0e5588062530
```

Contract tests commit:

```
2914cace36b9c18cfcaa2bad116460d02f8942bb
```

Pre-science technical repairs:

- missing NumPy workflow dependency: `305852d692b2690871c681bf9dc24cd6641d6dfd`;
- malformed cause-code test assertion: `78230c7b9117583b6d261a5bad09d9860ed00be6`.

Both failures occurred before scientific execution and did not change the
protocol, taxonomy, cohorts, thresholds, or adjudication.

Canonical discovery source:

```
4451f86dd1966af062c02c3630d187335d7d47b8
```

Canonical replication raw JSON SHA-256:

```
01af50dcea2a55beb2c61e5bc8207db922239d7f24bf218fa3e90d3405b5ca20
```

Replication artifact:

```
ID 10587572307
ZIP SHA-256
ed08fb0672aeff79927809d1637ccf5c03d99d913206b9483fc53be4369f4f76
```

Replication evidence commit:

```
f84009b533dd84b574bd1d5f129f828bd33cbbc6
```

All phase integrity checks passed.

Protected confirmatory cohort:

```
UNTOUCHED
```

Controller:

```
NOT IMPLEMENTED
```

KCL-7:

```
NOT STARTED
```

## 12. STOP / PIVOT

### STOP

Do not return to the monolithic `A_ONLY` target and simply escalate classifier
complexity.

Do not promote `MECH{P,P}` to a stable target.

### PIVOT

The next admissible question is whether the two stably replicated,
causally-specific targets:

```
MECH{P,R}
MECH{P+R,R}
```

are more identifiable/predictable from pre-boundary information than the
original `A_ONLY` target under a prospectively frozen, apples-to-apples
predictor comparison.

Candidate next milestone:

```
KCL-6.5.9.5 — Mechanism-Specific Target Identifiability
```

It requires an entirely fresh non-confirmatory cohort and a preregistered target,
representation, model and comparison contract before execution.

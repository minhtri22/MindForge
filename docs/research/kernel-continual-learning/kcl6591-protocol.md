# MindForge Kernel Continual Learning — KCL-6.5.9.1 Boundary Regime Replication Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.9.1 SCIENTIFIC EXECUTION**

## 1. Trigger

KCL-6.5.9 closed:

```
NEGATIVE
NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY
```

It observed two rare preregistered regimes:

```
B_AND_C_SAFE                  2 / 20 discovery seeds
CARRY_CATASTROPHIC_FAILURE   3 / 20 discovery seeds
```

but neither met the frozen KCL-6.5.9 support gate.

KCL-6.5.9 explicitly permits only one next step before any regime-first
classifier/controller work:

> replicate the same frozen taxonomy on a fresh non-confirmatory cohort.

## 2. Scientific question

### H-REP

At least one of the two rare KCL-6.5.9 regimes reproduces with preregistered
support on fresh seeds while its dominant within-binary companion remains
supported.

The two exact replication routes are:

### H-REP-ACTION

```
B_AND_C_SAFE is SUPPORTED
AND
C_SAFE_ONLY is SUPPORTED
```

### H-REP-NEGATIVE

```
CARRY_CATASTROPHIC_FAILURE is SUPPORTED
AND
A_SUFFICIENT is SUPPORTED
```

Primary replication PASS iff either route passes.

`B_SAFE_ONLY` remains part of the frozen taxonomy, but because it was absent
in KCL-6.5.9 it is an unexpected/new regime and cannot by itself satisfy the
primary replication hypothesis.

## 3. Frozen taxonomy and thresholds

Reuse KCL-6.5.9 exactly.

Policies:

```
A = A_CARRY_ALL
B = B_RESET_ALL
C = C_CARRY_STEP_RESET_MOMENTS
```

Action criteria:

```
STRICT_CURRENT_MIN      = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN       = 1/24
```

Primary regimes:

```
B_AND_C_SAFE
B_SAFE_ONLY
C_SAFE_ONLY
CARRY_CATASTROPHIC_FAILURE
A_SUFFICIENT
```

Support rule:

```
instance_count >= 5
AND
unique_seed_count >= 3
```

No threshold/taxonomy/support change is permitted after replication outcome.

## 4. Fresh replication cohort

Use exactly 66 new seeds:

```
200001
200998
201995
202992
203989
204986
205983
206980
207977
208974
209971
210968
211965
212962
213959
214956
215953
216950
217947
218944
219941
220938
221935
222932
223929
224926
225923
226920
227917
228914
229911
230908
231905
232902
233899
234896
235893
236890
237887
238884
239881
240878
241875
242872
243869
244866
245863
246860
247857
248854
249851
250848
251845
252842
253839
254836
255833
256830
257827
258824
259821
260818
261815
262812
263809
264806
```

Each seed contributes boundaries after T1, T2 and T3:

```
N = 66 seeds × 3 boundaries = 198 boundary instances
```

These seeds are intentionally far outside the prior KCL-6.5.6 discovery and
protected confirmatory ranges.

Required pre-execution disjointness:

- no overlap with KCL-6.5.6 / KCL-6.5.7 / KCL-6.5.8 / KCL-6.5.9 discovery
  seeds;
- no overlap with the untouched confirmatory cohort.

Any overlap is:

```
REVISE
REPLICATION_COHORT_NOT_FRESH
```

## 5. Sample-size rationale

KCL-6.5.9 observed:

```
B_AND_C_SAFE                 in 2/20 seeds  ~= 0.10 per seed
CARRY_CATASTROPHIC_FAILURE  in 3/20 seeds  ~= 0.15 per seed
```

Both rare regimes occurred only at boundary 3 in the original discovery
cohort, so seed-level occurrence is the conservative planning unit.

For the unchanged support requirement of at least 5 observed instances:

```
P[X >= 5 | n=66, p=0.10] ~= 0.8019
P[X >= 5 | n=66, p=0.15] ~= 0.9774
```

These probabilities are planning calculations only. They do not alter the
replication decision rule and are not evidence for either hypothesis.

## 6. Execution harness

Reuse the frozen KCL-6.5.6 boundary counterfactual harness.

For each fresh seed:

1. build the same KCL substrate;
2. follow the same A reference trajectory;
3. at each boundary fork A/B/C under the same optimizer-boundary policies;
4. train/evaluate the next task under the same fixed budgets;
5. preserve A/B/C AUC, final accuracy and retention;
6. assign the primary regime with the unchanged KCL-6.5.9 truth table.

No feature fitting or action selection occurs.

## 7. Anti-leakage and protected cohort

The protected confirmatory seeds remain:

```
13635
13837
14039
14241
14443
14645
14847
15049
15251
15453
15655
15857
16059
16261
16463
16665
16867
17069
17271
17473
```

They may not be:

- executed;
- inspected for replication;
- used for sample-size adjustment;
- used for threshold/taxonomy/support changes;
- used for classifier/controller fitting.

KCL-6.5.9.1 is a fresh **non-confirmatory replication cohort**.

## 8. Primary replication adjudication

For each regime compute:

- instance count;
- prevalence across 198 boundaries;
- unique seed count;
- support status under the unchanged KCL-6.5.9 rule;
- boundary-index counts.

Define:

```
ACTION_REPLICATION =
  supported(B_AND_C_SAFE)
  AND supported(C_SAFE_ONLY)

NEGATIVE_REPLICATION =
  supported(CARRY_CATASTROPHIC_FAILURE)
  AND supported(A_SUFFICIENT)

PRIMARY_REPLICATION =
  ACTION_REPLICATION
  OR NEGATIVE_REPLICATION
```

### PASS

```
PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

iff `PRIMARY_REPLICATION = true`.

### NEGATIVE

```
NEGATIVE
RARE_BOUNDARY_REGIMES_NOT_SUPPORT_REPLICATED
```

iff execution/integrity is valid but `PRIMARY_REPLICATION = false`.

### REVISE

```
REVISE
BOUNDARY_REGIME_REPLICATION_INVALID
```

for technical/provenance/integrity failure only.

## 9. Secondary unexpected-regime rule

If `B_SAFE_ONLY` becomes SUPPORTED:

```
UNEXPECTED_SUPPORTED_B_SAFE_ONLY = true
```

Report it prominently, but do not convert it into primary replication PASS.

It may motivate a new separately preregistered question after KCL-6.5.9.1
closure.

## 10. Replication prevalence uncertainty

Use seed-cluster bootstrap:

```
20,000 resamples
RNG seed = 6591
95% percentile interval
```

Resample seeds with replacement and retain all three boundaries from each
sampled seed.

Intervals are descriptive only and cannot rescue a failed support gate.

## 11. Discovery-to-replication comparison

Report, descriptively:

- KCL-6.5.9 discovery prevalence;
- KCL-6.5.9.1 replication prevalence;
- absolute prevalence difference;
- regime boundary-index distribution.

No equivalence/non-inferiority margin is introduced post hoc.

## 12. Integrity requirements

Before scientific adjudication require:

1. exactly 66 frozen replication seeds;
2. exactly 198 records;
3. each seed contributes boundaries 1/2/3 exactly once;
4. all fresh seeds are unique;
5. no discovery-seed overlap;
6. no confirmatory-seed overlap;
7. all A/B/C counterfactual integrity checks pass;
8. regime assignment is exactly-one and collectively exhaustive;
9. assignment is invariant to A/B/C dictionary presentation order;
10. all frozen KCL-6.5.9 constants/taxonomy/support rules match;
11. no classifier is trained;
12. no controller is implemented;
13. no KCL-7 work is opened.

Any failed item prevents scientific adjudication.

## 13. Scope exclusions

KCL-6.5.9.1 does not:

- change KCL-6.5.9;
- tune H4;
- fit any boundary-state predictor;
- fit a regime classifier;
- implement an adaptive controller;
- alter replay/memory mechanisms;
- touch confirmatory seeds;
- open KCL-7;
- open reasoning, agents, RAG, OIR-PPV or Local2API.

## 14. STOP / PIVOT rules

### If PASS

STOP treating the rare regimes as unsupported noise.

The next admissible milestone is a separately preregistered **regime
predictability qualification** using new non-confirmatory train/validation data.

KCL-6.5.9.1 PASS still does **not** authorize a controller and still does not
consume the protected confirmatory cohort.

### If NEGATIVE

STOP the current regime-first controller hypothesis.

Do not add more seeds to KCL-6.5.9.1 after inspecting the outcome.

Return to the boundary target/representation question and formulate a new
hypothesis rather than increasing taxonomy/classifier complexity.

### If REVISE

Fix only implementation/provenance defects and rerun the exact frozen protocol.
No sample-size, taxonomy, threshold or support changes are allowed.

## 15. Required artifacts

```
docs/research/kernel-continual-learning/kcl6591-protocol.md
experiments/kernel_cl/kcl6591_boundary_regime_replication.py
tests/test_kernel_cl_kcl6591.py
.github/workflows/kernel-cl-kcl6591.yml
experiments/kernel_cl/results/kcl6591_replication.json
docs/research/kernel-continual-learning/kcl6591-paper.md
Lineage.md
```

No rule artifact and no confirmatory workflow are authorized.

## 16. Closure

A complete closure requires:

1. protocol freeze commit before scientific execution;
2. implementation + focused tests;
3. one official GitHub Actions replication run;
4. canonical raw evidence preserved;
5. paper written from canonical evidence;
6. append-only Lineage update;
7. README state reviewed if the scientific status materially changes;
8. confirmatory cohort remains untouched;
9. KCL-7 remains NOT STARTED.

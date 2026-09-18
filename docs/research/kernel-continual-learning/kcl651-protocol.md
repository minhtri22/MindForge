# MindForge Kernel Continual Learning — KCL-6.5.1 Stability–Plasticity Tradeoff Confirmation Protocol

Status: **FROZEN BEFORE KCL-6.5.1 SCIENTIFIC EXECUTION**

## 1. Prerequisite chain

KCL-6.5.1 is opened only because KCL-6.5 produced the following mixed result:

- KCL-6.5 overall = `FAIL`
- verdict = `TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS`
- H-S1 target specificity = PASS
- H-S2 matched-query null/integrity = PASS
- H-S3 targeted information improves prior retention = PASS
- H-S4 paired current-task non-degradation = FAIL
- H-S5 query/storage integrity = PASS

KCL-6.5 observed:

```
mean(E prior - F prior) = +0.25556
mean(E T4 - F T4)       = -0.00833
```

with the T4 decrement localized to seed 4949.

KCL-6.5.1 does **not** alter the KCL-6.5 FAIL verdict.

## 2. Research question

Is the small KCL-6.5 E-vs-F T4 decrement:

1. a reproducible stability–plasticity tradeoff;
2. a small directional effect that remains within one benchmark item;
3. finite-seed variation with no reproducible directional cost;
4. statistically/practically inconclusive?

The experiment also verifies that the large targeted-clarification prior-retention benefit replicates on an independent cohort.

## 3. Policies are frozen

Use the exact KCL-6.5 E/F policies without modification.

### E — TARGETED_CLARIFICATION

- same fuzzy representation;
- same decay schedule;
- same width-4 bucket;
- same query trigger;
- same same-task key_min cue;
- uncertainty `4 -> 1`;
- exact reactivation;
- exact replay.

### F — MATCHED_PLACEBO_QUERY

- same fuzzy representation;
- same decay schedule;
- same width-4 bucket;
- same query opportunities;
- current-task key_min placebo cue;
- queried prior uncertainty remains `4 -> 4`;
- no prior-memory update;
- frozen fuzzy-guess replay continues.

No policy parameter may change.

## 4. Fresh independent confirmation cohort

Primary KCL-6.5.1 seeds:

```
5555
5757
5959
6161
6363
6565
6767
6969
7171
7373
7575
7777
7979
8181
8383
8585
8787
8989
9191
9393
```

N = 20.

These seeds are disjoint from:

- all KCL-1 through KCL-6.4 seeds;
- KCL-6.5-Q seed 5151;
- KCL-6.5 main seeds 4343/4545/4747/4949/5353.

No seed replacement, dropping, selective rerun, or outcome-conditioned extension is permitted.

## 5. Historical cohort use

KCL-6.5 seeds are **not** pooled into the primary endpoint.

They may be shown only as secondary historical context after the independent N=20 result is classified.

Primary inference is based solely on the 20 fresh KCL-6.5.1 seeds.

## 6. Frozen model / optimizer / task stream

Identical to KCL-6.5:

- TransformerLM diagnostic kernel;
- 4,880 parameters;
- vocab 96;
- d_model 16;
- heads 2;
- layers 1;
- context 2;
- FF multiplier 4;
- dropout 0;
- AdamW;
- lr 3e-3;
- weight decay 0;
- 250 steps/task;
- batch size 16;
- deterministic CPU execution.

Task stream:

```
T1_U1_A
→ T2_U1_B
→ T3_U3_A
→ T4_U3_B
```

## 7. Frozen replay/query budgets

Both E and F:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

Query schedule:

```
T2 = 0
T3 = 1
T4 = 2
total = 3 / seed
```

Final persistent memory:

```
143 bytes
```

No cue enters gradient or persistent raw replay storage.

## 8. Primary paired endpoints

For each seed:

```
DeltaR =
E_final_mean_prior_accuracy
-
F_final_mean_prior_accuracy
```

and:

```
DeltaP =
E_final_T4_accuracy
-
F_final_T4_accuracy
```

The hypothesis under examination is the joint pattern:

```
DeltaR >> 0
while DeltaP may be < 0
```

## 9. Benchmark-resolution margin

Each task has 24 evaluation items.

One item corresponds to:

```
M = 1/24 = 0.0416666667
```

This is frozen as the practical non-inferiority margin for mean paired T4 accuracy.

No smaller post-hoc margin may be substituted.

## 10. Bootstrap inference

Use paired nonparametric bootstrap over the 20 seed-level paired deltas.

Frozen settings:

```
resamples = 20000
bootstrap RNG seed = 651651
confidence interval = two-sided 95% percentile CI
```

For each resample:

- draw 20 seed indices with replacement;
- compute mean paired delta.

Report 2.5th and 97.5th percentiles.

No alternative CI is selected after outcome inspection.

## 11. Retention-specificity replication gate

Targeted clarification retention effect is considered independently replicated iff all are true:

1. `mean(DeltaR) >= 0.10`
2. bootstrap 95% CI lower bound for `mean(DeltaR)` is `> 0`
3. at least `16/20` seeds have `DeltaR > 0`

If this fails, the KCL-6.5 retention-specificity effect is not independently replicated.

## 12. Absolute E plasticity gate

The original strict absolute gate remains:

```
E_final_T4_accuracy >= 0.95
```

for all 20 seeds.

No relaxation is allowed.

## 13. Plasticity classification

Let:

```
CI_P = bootstrap 95% CI for mean(DeltaP)
M = 1/24
```

### Class A — MATERIAL_TRADEOFF_CONFIRMED

```
CI_P.upper <= -M
```

Interpretation: mean E current-task cost is reproducibly at least one benchmark item.

### Class B — SMALL_SYSTEMATIC_TRADEOFF_WITHIN_MARGIN

```
CI_P.upper < 0
and
CI_P.lower > -M
```

Interpretation: a directional E cost is reproducible, but it remains within the one-item practical margin.

### Class C — NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN

```
CI_P.lower > -M
and
CI_P.lower <= 0 <= CI_P.upper
```

Interpretation: no directional cost is confirmed and E is practically non-inferior within one item.

### Class D — TRADEOFF_CONFIRMATION_INCONCLUSIVE

All other valid cases.

Examples include an interval spanning both a material decrement below `-M` and zero.

## 14. Directional diagnostics

Also report:

- count of `DeltaP < 0`
- count of `DeltaP = 0`
- count of `DeltaP > 0`
- mean/median/min/max `DeltaP`
- count of `DeltaR > 0`
- Spearman-like descriptive rank association is **not** required; no correlation claim is pre-registered.

The sign counts are descriptive only and do not override bootstrap classification.

## 15. Integrity gates

Every seed must preserve KCL-6.5 contract:

- E candidate set `4 -> 1`;
- F candidate set `4 -> 4`;
- E/F query schedule equal;
- query envelope equal;
- query does not enter gradient/storage;
- E exact replay rate = 1.0;
- final E/F storage = 143 bytes;
- final age state = `[fuzzy, fuzzy, fuzzy, exact]`;
- replay budget unchanged;
- architecture unchanged.

Any integrity failure => REVISE.

## 16. Milestone verdict

### Integrity valid + retention specificity replicated + E absolute gate PASS

KCL-6.5.1 closes **PASS** with one of the four plasticity classifications:

- `MATERIAL_TRADEOFF_CONFIRMED`
- `SMALL_SYSTEMATIC_TRADEOFF_WITHIN_MARGIN`
- `NO_REPRODUCIBLE_PLASTICITY_TRADEOFF_WITHIN_MARGIN`
- `TRADEOFF_CONFIRMATION_INCONCLUSIVE`

The classification is the scientific result; PASS means the confirmation experiment executed validly and the original E mechanism remained viable.

### Retention specificity not replicated

```
KCL-6.5.1 = NEGATIVE
RETENTION_SPECIFICITY_NOT_REPLICATED
```

### E violates strict 95% gate on any seed

```
KCL-6.5.1 = FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

### Integrity invalid

```
KCL-6.5.1 = REVISE
TRADEOFF_CONFIRMATION_INVALID
```

## 17. No tuning rule

After freeze do not change:

- E/F policy;
- seeds;
- N;
- bootstrap seed;
- bootstrap resamples;
- confidence level;
- practical margin;
- replay/query budgets;
- task stream;
- strict 95% gate;
- retention replication threshold.

No additional seeds are added after seeing results.

## 18. Scope exclusions

KCL-6.5.1 does not establish:

- model-scale transfer;
- autonomous question generation;
- arbitrary uncertainty discovery;
- natural-language clarification;
- optimal query selection;
- general semantic memory.

KCL-7 remains unopened until KCL-6.5.1 closes.

## 19. Required artifacts

```
experiments/kernel_cl/kcl651_tradeoff_confirmation.py
experiments/kernel_cl/results/kcl651_summary.json
tests/test_kernel_cl_kcl651.py
docs/research/kernel-continual-learning/kcl651-paper.md
.github/workflows/kernel-cl-kcl651.yml
```

## 20. Closure requirement

KCL-6.5.1 closes only after:

- this protocol is committed before execution;
- focused tests PASS;
- one official N=20 execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

# MindForge Kernel Continual Learning — KCL-6.5.9.2 Boundary Regime Predictability Qualification

Status: **FROZEN BEFORE ANY KCL-6.5.9.2 TRAIN OR VALIDATION OUTCOME**

## 1. Trigger

KCL-6.5.9.1 closed:

```
PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

Fresh replication established supported positive-class action heterogeneity:

- `C_SAFE_ONLY` — supported;
- `B_AND_C_SAFE` — supported;
- `B_SAFE_ONLY` — supported as an unexpected replicated-cohort finding;
- `CARRY_CATASTROPHIC_FAILURE` — not support-replicated.

No boundary classifier/controller is qualified. The next admissible question is whether the action regime can be predicted using information available **at the boundary before the future task counterfactual is observed**.

## 2. Scientific hypothesis

### H-RPQ

A fixed, low-capacity multiclass predictor using only preregistered boundary-time state can predict the safe-action regime on unseen whole seeds better than stage/H4 baselines and with non-trivial recall for every action class.

KCL-6.5.9.2 is a **predictability qualification**, not a controller test.

## 3. Frozen target: SAFE_ACTION_SET-v1

Do not use the five KCL-6.5.9 descriptive regimes directly.

The target is the exhaustive safe-action set induced by the unchanged A/B/C counterfactual safety predicates:

```
A_ONLY       := safe_B = false AND safe_C = false
C_ONLY       := safe_B = false AND safe_C = true
B_AND_C_SAFE := safe_B = true  AND safe_C = true
B_ONLY       := safe_B = true  AND safe_C = false
```

Frozen class order:

```
A_ONLY
C_ONLY
B_AND_C_SAFE
B_ONLY
```

Rationale:

- the unsupported `CARRY_CATASTROPHIC_FAILURE` and supported `A_SUFFICIENT` both imply the same safe action set `{A}`;
- the three supported positive action regimes remain distinct;
- the target is mutually exclusive and collectively exhaustive;
- no future "best AUC action" is used as the label.

## 4. Frozen fresh cohort

Exactly 360 fresh non-confirmatory seeds are used.

Generation provenance:

```
Python 3.12
random.Random(6592).sample(range(300001, 900000), 360)
```

The explicit frozen lists below are authoritative.

### Training — 240 whole seeds

```
857358,348434,468582,461139,473479,327035,376368,705271,378009,762246,530553,653483,799618,671805,556535,659145,373486,801628,834743,665330,830692,383139,448112,324812,448781,888462,883531,711545,875550,465689,856408,697066,614578,735005,529287,646853,528638,871673,822516,701571,457351,528572,783495,419315,845774,877397,851929,492207,826924,672086,498167,645017,310029,427666,718671,352185,414107,541624,390348,633150,345751,577928,511849,772521,789592,451590,363425,894707,423888,574921,851601,632470,302881,634338,557864,467365,342140,795434,379754,453294,603564,622086,326515,568333,817464,601779,795496,463602,614571,518648,655754,486850,798851,648142,638696,512088,717672,349969,519679,655889,765254,875709,531987,685908,701296,504219,334514,410848,528357,669199,554446,497698,419027,494564,544410,709276,795282,689126,872997,336152,814395,761781,737231,651805,677211,301391,345926,441301,332714,632994,472554,339215,641864,536651,579223,702505,843624,748965,730314,594138,621698,737680,676216,645867,718426,365404,617147,732718,869341,822746,825339,618354,699284,520741,748531,615493,304544,704801,502068,443342,394247,362756,666212,676263,775696,610769,705295,409438,346707,795604,367193,567522,463611,781026,573729,714292,447472,767857,798337,713339,570695,400614,584796,866480,529565,802765,656999,776014,409735,565714,533747,560722,435207,846906,890786,821404,317775,330665,738279,479078,514252,773216,655469,801139,850287,582985,865828,808042,511264,698003,521999,528443,834157,669881,350931,456619,368498,615812,433078,774212,736883,866007,821000,887108,813458,896365,509196,895686,426598,540180,749014,406612,562615,718200,311196,617622,811197,514044,869931,374540
```

### Validation — 120 whole seeds

```
384891,314256,314740,727553,506172,608741,843687,486364,425737,330214,775722,325734,460280,480300,439813,726715,356352,499291,370753,647972,808425,575331,538327,506660,765810,620872,897523,517764,578334,425323,506256,442330,309925,628393,714826,639547,872908,451207,697314,811852,330684,469692,308074,561294,408157,534162,423691,814699,870274,559113,494592,488533,836183,706092,624263,346755,643663,438370,724657,350340,784596,629041,347772,713121,618230,858299,579744,838079,790316,472521,388908,591976,553827,769806,879361,746756,645486,838695,432484,533728,472072,603113,597733,322891,877808,577990,763710,680552,355772,392840,398325,882431,495882,873447,779476,396884,807818,782730,367545,728868,710558,564601,402575,612256,763601,570016,704251,523135,770290,783234,570147,397731,612432,597905,709599,503627,741049,779883,328666,318719
```

Required disjointness:

- train ∩ validation = empty;
- no overlap with KCL-6.5.6 discovery seeds;
- no overlap with protected KCL confirmatory seeds;
- no overlap with KCL-6.5.9.1 replication seeds.

Each seed contributes exactly three boundaries, so:

```
training   = 240 × 3 = 720 boundary instances
validation = 120 × 3 = 360 boundary instances
total      = 1080 boundary instances
```

Splits may not be changed after any KCL-6.5.9.2 outcome is inspected.

## 5. Sample-size planning

KCL-6.5.9.1 observed seed-level boundary-3 occurrence rates:

```
B_ONLY       = 5/66 ~= 0.07576
B_AND_C_SAFE = 9/66 ~= 0.13636
```

Frozen minimum support for model fitting/evaluation:

```
TRAIN_MIN_PER_CLASS = 10 instances from >= 10 unique seeds
VAL_MIN_PER_CLASS   = 5 instances from >= 5 unique seeds
```

For the rarer `B_ONLY` planning rate only:

```
P[train >= 10 | n=240, p=5/66] ~= 0.9886
P[val   >=  5 | n=120, p=5/66] ~= 0.9542
```

For `B_AND_C_SAFE`:

```
P[train >= 10 | n=240, p=9/66] > 0.999999
P[val   >=  5 | n=120, p=9/66] ~= 0.99985
```

These are design calculations only. They do not enter the qualification score.

No extra seeds may be appended after outcomes are inspected.

## 6. Boundary-time feature contract

Only the frozen global KCL-6.5.6 features available before future-task execution are allowed.

Primary RPQ-v1 features:

```
STAGE_2
STAGE_3
H1_M1_RMS
H2_SQRT_M2_RMS
H3_BIAS_CORRECTED_ADAM_PRESSURE_RMS
H4_TASK_DRIFT_RELATIVE_L2
H5_PRESSURE_TO_DRIFT_RATIO
H6_DRIFT_PRESSURE_COSINE
H7_PRIOR_MEAN_ACCURACY
H8_PRIOR_WORST_ACCURACY
H9_CURRENT_TASK_LOSS
```

`STAGE_2` and `STAGE_3` are one-hot indicators for boundary indices 2 and 3; boundary 1 is the reference level.

Forbidden features include:

- next-task identity/family/tensors;
- any A/B/C counterfactual outcome;
- `SAFE_RESET_OPPORTUNITY`;
- safe_B/safe_C;
- `BEST_SAFE_ACTION`;
- future-task loss/gradient;
- validation-label statistics during fitting;
- KCL-6.5.8 localized F1–F13 features.

The last exclusion is deliberate: KCL-6.5.9.2 first asks whether the already-frozen global boundary state is sufficient for regime identity before adding representation complexity.

## 7. Frozen model: RPQ-v1

Use one model family only:

```
class-balanced L2-regularized multinomial logistic regression
```

Frozen solver:

- float64;
- softmax cross-entropy;
- train-only standardization;
- class weights computed from training only:
  `w_c = N / (K * n_c)`;
- L2 penalty on weight matrix only;
- intercept unregularized;
- `lambda = 1.0`;
- deterministic PyTorch LBFGS;
- `lr = 1.0`;
- `max_iter = 200`;
- `history_size = 20`;
- `tolerance_grad = 1e-9`;
- `tolerance_change = 1e-12`;
- `line_search_fn = strong_wolfe`.

No lambda search, architecture search, threshold search, feature selection, oversampling or validation tuning is allowed.

Prediction is `argmax softmax probability` in frozen class order.

## 8. Frozen baselines

Fit the same multinomial-logistic procedure on training data with these feature subsets:

### B-STAGE

```
STAGE_2
STAGE_3
```

### B-H4

```
H4_TASK_DRIFT_RELATIVE_L2
```

### B-STAGE-H4

```
STAGE_2
STAGE_3
H4_TASK_DRIFT_RELATIVE_L2
```

Also report the deterministic training-majority baseline descriptively.

The strongest of B-STAGE, B-H4 and B-STAGE-H4 is the qualification baseline.

## 9. Two-stage anti-leakage execution

KCL-6.5.9.2 must be executed in two separate phases.

### Phase A — TRAIN/FREEZE

1. generate only the 240 training seeds;
2. derive labels from A/B/C outcomes;
3. verify class support;
4. fit RPQ-v1 and all baselines;
5. freeze scaler, class weights, coefficients, intercepts and feature order;
6. preserve a machine-readable rule artifact in git.

No validation seed may be executed before the rule artifact is frozen.

### Phase B — VALIDATE

Only after the rule artifact is committed:

1. generate the 120 frozen validation seeds;
2. apply the frozen RPQ-v1 and baseline models with no refit;
3. compute validation metrics and bootstrap intervals;
4. adjudicate the frozen qualification gates.

If a validation seed is executed before the rule artifact commit, KCL-6.5.9.2 is invalid.

## 10. Training support gate

Before fitting, each SAFE_ACTION_SET-v1 class must have:

```
count >= 10
unique_seed_count >= 10
```

If any class fails:

```
NEGATIVE
REGIME_PREDICTABILITY_TRAIN_SUPPORT_INSUFFICIENT
```

Validation is not authorized.

This is a scientific negative, not a technical REVISE, because the fresh cohort failed to sustain adequate target support.

## 11. Validation support gate

For scientific qualification, every class must have:

```
count >= 5
unique_seed_count >= 5
```

If not:

```
NEGATIVE
REGIME_PREDICTABILITY_VALIDATION_SUPPORT_INSUFFICIENT
```

No extra validation seeds may be added.

## 12. Frozen metrics

On validation report:

- 4×4 confusion matrix;
- exact accuracy;
- per-class precision;
- per-class recall;
- per-class F1;
- macro precision;
- macro recall;
- macro F1;
- multiclass log loss.

Primary discrimination metric:

```
MACRO_RECALL
```

because each action regime must matter despite imbalance.

## 13. Seed-cluster bootstrap

Validation uncertainty uses whole-seed resampling:

```
20,000 resamples
RNG seed = 6592
95% percentile interval
```

For each resample carry all three boundary predictions from each sampled seed.

Report bootstrap intervals for:

- macro recall;
- macro F1;
- exact accuracy.

No model refit occurs inside bootstrap.

## 14. Frozen qualification gates

RPQ-v1 qualifies iff all are true:

```
validation class support gate passes

macro_recall >= 0.60
macro_F1     >= 0.50

recall(A_ONLY)       >= 0.50
recall(C_ONLY)       >= 0.50
recall(B_AND_C_SAFE) >= 0.50
recall(B_ONLY)       >= 0.50

F1(A_ONLY)       >= 0.35
F1(C_ONLY)       >= 0.35
F1(B_AND_C_SAFE) >= 0.35
F1(B_ONLY)       >= 0.35

macro_recall >= max(
    macro_recall(B-STAGE),
    macro_recall(B-H4),
    macro_recall(B-STAGE-H4)
) + 0.05

bootstrap_95pct_macro_recall_lower > 0.45
```

These thresholds are frozen before training/validation outcomes.

### PASS

```
PASS
BOUNDARY_REGIME_PREDICTOR_QUALIFIED
```

### NEGATIVE

If integrity/support is valid but any qualification gate fails:

```
NEGATIVE
BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED
```

with explicit failed-gate list.

### REVISE

Reserved only for implementation/provenance/integrity defects:

```
REVISE
BOUNDARY_REGIME_PREDICTABILITY_INVALID
```

No scientific threshold may change on REVISE.

## 15. Rule artifact

After Phase A succeeds, freeze:

```
experiments/kernel_cl/results/kcl6592_rule.json
```

It must contain:

- protocol SHA-256;
- training evidence SHA-256;
- exact train/validation seed lists;
- class order;
- target truth table;
- primary feature order;
- scaler;
- train-only class weights;
- RPQ-v1 weights/intercepts;
- baseline weights/intercepts;
- training class counts/support;
- solver contract;
- git commit/source provenance.

The rule artifact must be committed before any validation workflow is created/executed.

## 16. Integrity

Training integrity requires:

1. exactly 240 train seeds / 720 records;
2. three boundaries per seed;
3. no overlap with previous discovery/replication/protected-confirmatory cohorts;
4. all KCL-6.5.6 A/B/C counterfactual integrity checks pass;
5. all features finite;
6. target exactly reconstructs safe_B/safe_C truth table;
7. no validation seed executed;
8. solver converges for primary and baselines;
9. no classifier/model selection beyond frozen RPQ-v1/baselines;
10. KCL-7 remains closed.

Validation integrity additionally requires:

1. exact frozen rule artifact SHA;
2. exactly 120 validation seeds / 360 records;
3. no train overlap;
4. no refit/scaler/class-weight change;
5. all counterfactual integrity checks pass;
6. all features finite;
7. whole-seed bootstrap only;
8. protected confirmatory cohort untouched.

## 17. Protected confirmatory cohort

The legacy protected seeds remain untouched:

```
13635,13837,14039,14241,14443,14645,14847,15049,15251,15453,15655,15857,16059,16261,16463,16665,16867,17069,17271,17473
```

They are not used for train, validation, threshold tuning or class-support rescue.

KCL-6.5.9.2 does not consume them even if RPQ-v1 PASSes.

## 18. Scope exclusions

KCL-6.5.9.2 does not:

- implement an online controller;
- choose A/B/C actions during training;
- use KCL-6.5.8 localized features;
- tune model family/hyperparameters;
- alter A/B/C safety definitions;
- add validation seeds post hoc;
- use the protected confirmatory cohort;
- open KCL-7;
- mix OIR-PPV, agents, RAG or Local2API.

## 19. STOP / PIVOT

### If PASS

Freeze the qualified predictor exactly as validated.

The next admissible scientific step is a separately preregistered **prospective policy-value test** on a new adequately powered cohort:

- predictor sees boundary-time state;
- predictor selects from A/B/C only through a frozen mapping;
- compare against fixed A/B/C policies and oracle upper bound;
- no online retraining of predictor.

Do not open KCL-7 solely from this PASS.

### If NEGATIVE because class support fails

STOP this cohort-based qualification without adding seeds.

Treat instability of a rare action class as evidence that the current four-class target is not sufficiently stable at the planned prevalence.

### If NEGATIVE because predictability gates fail

STOP RPQ-v1.

Do not add nonlinear models or localized features post hoc. Return to the representation/target hypothesis and preregister a new question if justified.

### If REVISE

Fix implementation/provenance only and rerun the exact frozen protocol.

## 20. Required artifacts

```
docs/research/kernel-continual-learning/kcl6592-protocol.md
experiments/kernel_cl/kcl6592_regime_predictability.py
tests/test_kernel_cl_kcl6592.py
.github/workflows/kernel-cl-kcl6592-train.yml
experiments/kernel_cl/results/kcl6592_train.json
experiments/kernel_cl/results/kcl6592_rule.json
.github/workflows/kernel-cl-kcl6592-validate.yml
experiments/kernel_cl/results/kcl6592_validation.json
docs/research/kernel-continual-learning/kcl6592-paper.md
Lineage.md
```

No controller artifact and no KCL-7 workflow are authorized.

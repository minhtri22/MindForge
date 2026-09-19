# MindForge Kernel Continual Learning — KCL-6.5.9.3 Boundary Action Identifiability Decomposition

Status: **FROZEN BEFORE ANY KCL-6.5.9.3 TRAIN OR VALIDATION OUTCOME**

## 1. Trigger

KCL-6.5.9.2 closed:

```
NEGATIVE
BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED
```

The four SAFE_ACTION_SET-v1 classes were adequately supported in both fresh
train and validation cohorts, but RPQ-v1 using stage + global H1–H9 boundary
state failed qualification and did not outperform the frozen stage-only
baseline.

Two explanations remain live:

1. **representation insufficiency** — pre-boundary state may contain
   discriminative information not captured by H1–H9;
2. **pre-boundary target non-identifiability** — action-regime identity may
   depend materially on interaction with the future task and therefore may not
   be recoverable from state before that interaction.

KCL-6.5.9.3 decomposes these explanations. It is not a controller test and not
a post-hoc stronger-classifier rescue.

## 2. Scientific question

Using the same low-capacity classifier family and the same fresh examples,
where does action-regime identifiability appear as information is added?

Frozen information sets:

```
S0 = stage only
S1 = stage + frozen global H1–H9 state
S2 = S1 + frozen LRBS-v1 F1–F13 localized pre-boundary state
O  = S2 + FUTURE-PROBE-v1 zero-step future-task interaction state
```

The comparison is paired by seed/boundary.

## 3. Frozen target

Reuse KCL-6.5.9.2 SAFE_ACTION_SET-v1 exactly:

```
A_ONLY
C_ONLY
B_AND_C_SAFE
B_ONLY
```

Truth table:

```
safe_B=false, safe_C=false -> A_ONLY
safe_B=false, safe_C=true  -> C_ONLY
safe_B=true,  safe_C=true  -> B_AND_C_SAFE
safe_B=true,  safe_C=false -> B_ONLY
```

No "best observed action" target is introduced.

## 4. Fresh cohort

Exactly 450 fresh non-confirmatory seeds are frozen.

Generation:

```
Python 3.12
random.Random(6593).sample(range(1000001, 2000000), 450)
```

The explicit lists below are authoritative.

### Training — 300 whole seeds

```
1987237,1619978,1292425,1065865,1467009,1404245,1122419,1596677,1657930,1703877,1874678,1896633,1715930,1653353,1182145,1011759,1523944,1718329,1401218,1740501,1322529,1574451,1625871,1578559,1231649,1316846,1090438,1160645,1666965,1995349,1038845,1967227,1316543,1602863,1914159,1092387,1914788,1211242,1214462,1683279,1434677,1427855,1940122,1044444,1738380,1594935,1060035,1424735,1828197,1451762,1520567,1314946,1152121,1367389,1671261,1363551,1407245,1576517,1138057,1214225,1605547,1194036,1773725,1686034,1258367,1164211,1309058,1745896,1048190,1572512,1061773,1517149,1562938,1579974,1940769,1405682,1238539,1252431,1930916,1919738,1787335,1475682,1313561,1181778,1844192,1860110,1707692,1739989,1354075,1353306,1652074,1292662,1803423,1560816,1178808,1838488,1249012,1815972,1772503,1555919,1229438,1289553,1588617,1728652,1721454,1063889,1621239,1341885,1140723,1242762,1799562,1011326,1212801,1800663,1019666,1642513,1023869,1865905,1052899,1438406,1885693,1790514,1075176,1178213,1302633,1117148,1134216,1574221,1760175,1057954,1548509,1615994,1409472,1619953,1919469,1448279,1026535,1482784,1173122,1619569,1733991,1529312,1477091,1390133,1933347,1151850,1224090,1964727,1110312,1990511,1088482,1387158,1620702,1645849,1966812,1822992,1233598,1177787,1623607,1591065,1467017,1491244,1546842,1923903,1318638,1373213,1672782,1435565,1557368,1429978,1400438,1116402,1728880,1101018,1339158,1653104,1225211,1077503,1363436,1652610,1383419,1496548,1818920,1747173,1134996,1773999,1700833,1935466,1999880,1403828,1688476,1765481,1094267,1623232,1241535,1258056,1307007,1578252,1551770,1171238,1942056,1241975,1838896,1535104,1563072,1585186,1315138,1362598,1290116,1927512,1663775,1922200,1001603,1393321,1404257,1228785,1611666,1383775,1264693,1948879,1189323,1066803,1620739,1344583,1568008,1232469,1298394,1594380,1471430,1040791,1090169,1962465,1766041,1208300,1074317,1049165,1769239,1242218,1763732,1544928,1898013,1575562,1312369,1244909,1227549,1833284,1885250,1759747,1069785,1802027,1146219,1089137,1112870,1624265,1862781,1291024,1909436,1254514,1947140,1655161,1014141,1354529,1033812,1738871,1146210,1803816,1571660,1318685,1930792,1050713,1739643,1388359,1661364,1656611,1353707,1931002,1222918,1731033,1910641,1736461,1601691,1972730,1589955,1467361,1004400,1966316,1841046,1039786,1461609,1870988,1821804,1141556,1984968,1708148,1624275,1531015,1791093,1694424,1748185,1097458
```

### Validation — 150 whole seeds

```
1948788,1545332,1865052,1261110,1385037,1614442,1652687,1002290,1201311,1143934,1902970,1469992,1481029,1687443,1694186,1312898,1852277,1531242,1245111,1586708,1601767,1629770,1238933,1272708,1712920,1779271,1420318,1087536,1199180,1927477,1391851,1668436,1649769,1199747,1684055,1529442,1559572,1425987,1308172,1964166,1031381,1811533,1607736,1136834,1912574,1623454,1770446,1609102,1822654,1443657,1676850,1619336,1155582,1771706,1472666,1354307,1224781,1144320,1319198,1067061,1966597,1447277,1080703,1353673,1210738,1164882,1585586,1798548,1172396,1883890,1017037,1901122,1942564,1060265,1394265,1564920,1703431,1859078,1800638,1710590,1791238,1523873,1853833,1522414,1442772,1301773,1590554,1873538,1047164,1074993,1555532,1811873,1003444,1358706,1169280,1973722,1188600,1581433,1557976,1294003,1174526,1029591,1986589,1691275,1538186,1822200,1920601,1558125,1170663,1361365,1067700,1414270,1008004,1970501,1837945,1780963,1737219,1383785,1498241,1156838,1659443,1335252,1249840,1776826,1423780,1777136,1764635,1279849,1823405,1429062,1708551,1574299,1857439,1779302,1220514,1746881,1695324,1839589,1916959,1119950,1794760,1338808,1713524,1699560,1035542,1494791,1063845,1567004,1020875,1774151
```

Each seed contributes boundaries 1/2/3:

```
training   = 300 × 3 = 900 boundary instances
validation = 150 × 3 = 450 boundary instances
total      = 1350 boundary instances
```

Required disjointness:

- train ∩ validation = empty;
- no KCL-6.5.6 discovery/protected-confirmatory overlap;
- no KCL-6.5.9.1 replication overlap;
- no KCL-6.5.9.2 train/validation overlap.

The protected legacy confirmatory cohort remains untouched.

## 5. Sample-size support planning

KCL-6.5.9.2 validation observed seed-level boundary-3 rates:

```
B_ONLY       = 15/120 = 0.125
B_AND_C_SAFE = 18/120 = 0.150
```

Frozen minimum support:

```
TRAIN: count >= 20 and unique_seed_count >= 20
VAL:   count >= 10 and unique_seed_count >= 10
```

Planning probabilities:

```
B_ONLY:
P[train >=20 | n=300,p=.125] ~= 0.99966
P[val   >=10 | n=150,p=.125] ~= 0.99301

B_AND_C_SAFE:
P[train >=20 | n=300,p=.150] ~= 0.999997
P[val   >=10 | n=150,p=.150] ~= 0.99946
```

Planning only; these values do not enter adjudication.

No seeds may be appended after outcomes are observed.

## 6. Same classifier family for all information sets

To isolate **information**, not model capacity, every arm uses the exact
KCL-6.5.9.2 fitting contract:

```
class-balanced L2 multinomial logistic regression
lambda = 1.0
float64
train-only standardization
train-only class weights
deterministic PyTorch LBFGS
lr = 1.0
max_iter = 200
history_size = 20
tolerance_grad = 1e-9
tolerance_change = 1e-12
line_search_fn = strong_wolfe
```

No hyperparameter search, nonlinear model, feature selection, threshold search,
oversampling or validation tuning.

## 7. S0 — stage only

```
STAGE_2
STAGE_3
```

Boundary 1 is the reference level.

## 8. S1 — frozen global pre-boundary state

Reuse KCL-6.5.9.2 exactly:

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

All are extracted before the future task is bound.

## 9. S2 — richer pre-boundary representation

S2 appends the exact frozen KCL-6.5.8 LRBS-v1 representation to S1:

```
F1..F13
```

The LRBS-v1 features retain their original definitions:

- F1–F4: drift × pressure × retention-attribution overlaps;
- F5–F7: total-variation mismatch;
- F8: retention reserve;
- F9–F12: fixed parameter-group identity triple attribution;
- F13: retention-weighted drift/pressure directional compatibility.

This representation predates KCL-6.5.9.2 and is not selected from its
validation errors.

S2 remains strictly pre-boundary and may use only already-observed tasks.

## 10. O — FUTURE-PROBE-v1 oracle-information arm

O is diagnostic only. It may never become an operational controller input
without a new protocol.

After S0/S1/S2 extraction, bind the future task but perform **no optimizer
update**.

Compute the full-dataset next-task zero-step loss and gradient:

```
g_next = grad_theta CE(model(next_task))
```

Using frozen KCL-6.5.8 drift, Adam-pressure and retention-gradient vectors,
define exactly eight oracle features:

```
P1_NEXT_TASK_LOSS
P2_NEXT_GRAD_NORM
P3_NEXT_GRAD_DRIFT_COSINE
P4_NEXT_GRAD_PRESSURE_COSINE
P5_NEXT_GRAD_RETENTION_COSINE
P6_NEXT_GRAD_DRIFT_SHARE_OVERLAP
P7_NEXT_GRAD_PRESSURE_SHARE_OVERLAP
P8_NEXT_GRAD_RETENTION_SHARE_OVERLAP
```

Directions:

```
next-task descent      = -g_next
recent drift direction = theta_post - theta_pre
Adam descent proxy     = -pressure
retention descent      = -grad_ret
```

For each frozen parameter group g, let q_g be the share of next-task gradient
norm. Then:

```
P6 = sum_g q_g d_g
P7 = sum_g q_g p_g
P8 = sum_g q_g k_g
```

No A/B/C counterfactual outcome, safe_B/safe_C value, post-training metric or
label is an oracle feature.

The probe must leave model parameters and optimizer state bitwise unchanged and
clear all gradients before counterfactual execution.

## 11. Anti-leakage hierarchy

Information availability:

```
S0 ⊂ S1 ⊂ S2 < O
```

S0/S1/S2 are legal pre-boundary representations.

O explicitly violates deployment-time pre-future-task availability and is
therefore an oracle/diagnostic information arm only.

The target is derived only after the frozen features/probe have been extracted
and the A/B/C counterfactuals are executed.

## 12. Two-stage execution

### Phase A — TRAIN/FREEZE

On the 300 training seeds only:

1. construct all four information sets;
2. derive SAFE_ACTION_SET-v1 labels after feature/probe extraction;
3. verify class support;
4. fit S0/S1/S2/O with the same frozen logistic contract;
5. freeze all scalers, class weights, coefficients/intercepts and feature order;
6. preserve train evidence and a machine-readable rule artifact in git.

No validation seed may be executed before the rule artifact is committed.

### Phase B — VALIDATE

Only after rule freeze:

1. execute exactly the 150 validation seeds;
2. load all four frozen models without refit;
3. compute paired validation metrics;
4. compute paired whole-seed bootstrap contrasts;
5. adjudicate the frozen decomposition rules.

## 13. Metrics

For every arm report:

- 4×4 confusion matrix;
- exact accuracy;
- per-class precision/recall/F1;
- macro precision;
- macro recall;
- macro F1;
- multiclass log loss.

Primary discrimination metric:

```
macro recall
```

## 14. Whole-seed paired bootstrap

Frozen:

```
20,000 resamples
RNG seed = 6593
95% percentile intervals
```

Each resample draws validation seeds with replacement and carries all three
boundaries from each selected seed.

No model refit inside bootstrap.

Report intervals for each arm's macro recall and macro F1, plus paired
differences:

```
D10 = macro_recall(S1) - macro_recall(S0)
D21 = macro_recall(S2) - macro_recall(S1)
DO2 = macro_recall(O)  - macro_recall(S2)
```

## 15. Frozen base qualification predicate

An arm is QUALIFIED iff all are true:

```
macro_recall >= 0.60
macro_F1     >= 0.50

recall(each class) >= 0.50
F1(each class)     >= 0.35

bootstrap_95pct_macro_recall_lower > 0.45
```

This reuses the substantive KCL-6.5.9.2 performance floors while removing its
separate baseline-superiority clause because S0/S1/S2/O are themselves the
ordered decomposition.

## 16. Frozen decomposition decisions

### Route R — PREBOUNDARY_REPRESENTATION_GAP_IDENTIFIED

PASS iff:

```
S1 is NOT QUALIFIED
S2 is QUALIFIED
D21 >= 0.10
bootstrap_95pct_lower(D21) > 0.03
```

Verdict:

```
PASS
PREBOUNDARY_REPRESENTATION_GAP_IDENTIFIED
```

Interpretation: richer pre-boundary representation materially closes the
KCL-6.5.9.2 gap.

### Route I — FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED

PASS iff:

```
S2 is NOT QUALIFIED
O is QUALIFIED
DO2 >= 0.15
bootstrap_95pct_lower(DO2) > 0.05
```

Verdict:

```
PASS
FUTURE_INTERACTION_IDENTIFIABILITY_GAP_IDENTIFIED
```

Interpretation: substantial discriminative information appears only after
zero-step interaction with the future task under the tested representations.

### Route M — MIXED_INFORMATION_GAIN

PASS iff S2 is QUALIFIED and O additionally has:

```
DO2 >= 0.10
bootstrap_95pct_lower(DO2) > 0.03
```

Verdict:

```
PASS
MIXED_PREBOUNDARY_AND_INTERACTION_INFORMATION_GAIN
```

The operational conclusion remains that S2 already makes the target
pre-boundary identifiable enough to qualify.

### Otherwise

If integrity/support are valid but none of R/I/M passes:

```
NEGATIVE
BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE
```

This does not authorize model-complexity escalation.

## 17. Secondary descriptive findings

Report but do not alter verdict:

- S0→S1 paired uplift D10;
- class-wise recall changes across S0/S1/S2/O;
- boundary-index distribution by class;
- training metrics;
- oracle probe feature distributions.

No post-outcome subgroup becomes a primary gate.

## 18. Integrity requirements

Training requires:

1. exactly 300 train seeds / 900 records;
2. three boundaries per seed;
3. no prior/protected cohort overlap;
4. all counterfactual integrity valid;
5. all S0/S1/S2/O features finite;
6. LRBS share sums valid;
7. zero-step probe leaves model and optimizer unchanged;
8. gradients cleared before counterfactual execution;
9. target truth table exact;
10. all four solvers converge;
11. no validation seed executed;
12. no controller;
13. KCL-7 closed.

Validation additionally requires:

1. exact frozen rule SHA;
2. exactly 150 validation seeds / 450 records;
3. no train overlap;
4. no refit/scaler/class-weight change;
5. same feature extraction contracts;
6. whole-seed paired bootstrap only;
7. protected confirmatory cohort untouched.

## 19. Scope exclusions

KCL-6.5.9.3 does not:

- tune or replace multinomial logistic regression;
- introduce neural/tree/kernel classifiers;
- use A/B/C outcomes as model inputs;
- use oracle features operationally;
- implement an adaptive policy controller;
- tune replay/memory;
- touch protected confirmatory seeds;
- open KCL-7;
- mix unrelated MindForge research tracks.

## 20. STOP / PIVOT

### If Route R passes

Freeze the S2 representation result. Next question may test a separately
preregistered S2 predictor/control mapping prospectively on a new cohort.
Do not use O operationally.

### If Route I passes

STOP pure pre-boundary action prediction under the tested state families.
The next admissible architecture question is a preregistered
**probe/observe/decide** mechanism, because future-task interaction carries
material identifying information.

### If Route M passes

Treat S2 as sufficient for pre-boundary qualification; oracle gain is
descriptive for later efficiency questions.

### If INCONCLUSIVE

Do not try stronger classifiers post hoc. Reassess target formulation or define
a new mechanistically justified representation/probe in a separate protocol.

### If REVISE

Fix implementation/provenance only. Cohort, feature sets, model family and
decision thresholds remain frozen.

## 21. Required artifacts

```
docs/research/kernel-continual-learning/kcl6593-protocol.md
experiments/kernel_cl/kcl6593_action_identifiability.py
tests/test_kernel_cl_kcl6593.py
.github/workflows/kernel-cl-kcl6593-train.yml
experiments/kernel_cl/results/kcl6593_train.json
experiments/kernel_cl/results/kcl6593_rule.json
.github/workflows/kernel-cl-kcl6593-validate.yml
experiments/kernel_cl/results/kcl6593_validation.json
docs/research/kernel-continual-learning/kcl6593-paper.md
Lineage.md
README.md
```

No controller artifact/workflow is authorized.

## 22. Closure

Complete closure requires protocol freeze before science, successful Phase A
rule freeze before any validation execution, one canonical Phase B validation,
exact evidence preservation, paper, append-only Lineage update, README review,
protected confirmatory cohort untouched and KCL-7 NOT STARTED.

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
1987237,1619978,1292425,1065865,1467009,1898914,1285590,1615852,1668147,1667061,1205181,1478254,1673760,1418965,1392645,1677150,1369695,1523682,1282342,1601881,1855934,1153656,1417227,1457119,1164679,1011373,1600717,1785790,1241954,1664863,1142272,1881318,1619391,1817376,1849790,1751875,1425393,1374970,1385338,1837082,1473648,1974531,1880044,1392998,1988878,1582390,1941967,1362179,1573122,1201017,1681174,1012325,1854785,1090435,1161701,1419436,1942730,1591671,1764216,1738921,1952507,1259512,1517067,1596887,1029680,1975465,1027566,1423478,1085476,1977390,1084350,1260795,1088032,1598807,1301618,1752040,1820319,1828749,1333410,1658768,1088161,1367676,1930480,1280029,1120992,1778873,1773670,1935028,1937082,1131061,1711629,1176504,1706161,1928117,1535963,1778066,1905343,1446796,1501613,1347298,1671600,1478457,1488718,1850960,1633613,1813512,1975190,1062192,1116661,1950865,1716981,1035282,1812181,1940411,1528277,1931123,1537767,1775686,1180298,1419729,1689867,1201974,1683380,1369526,1849630,1896407,1751056,1093929,1636836,1628282,1775937,1159068,1319480,1615988,1688394,1344012,1015458,1737134,1207118,1841349,1893796,1937712,1902513,1487170,1320577,1925966,1982154,1827637,1285156,1892031,1288256,1879623,1557081,1467674,1261192,1579688,1592890,1635338,1489265,1781522,1818681,1284846,1011304,1494058,1228669,1957128,1887986,1945352,1807934,1400034,1276019,1148283,1378318,1952260,1122607,1606213,1059900,1718055,1790230,1692613,1145938,1787706,1496292,1194030,1036511,1292701,1719375,1846881,1564287,1944016,1549417,1219793,1533132,1372255,1467651,1136693,1976074,1563109,1824383,1256968,1337358,1822673,1589511,1644195,1594866,1536334,1167211,1561908,1540556,1352621,1135525,1482165,1567756,1840919,1765560,1691710,1142645,1802722,1706156,1165604,1734553,1324821,1527738,1810419,1653427,1882014,1414141,1795539,1595547,1802887,1366512,1508255,1013983,1333016,1204268,1521642,1844284,1533136,1692174,1092962,1741909,1909407,1541007,1889589,1854056,1109924,1279775,1591654,1221325,1520201,1770314,1679595,1378667,1650077,1427293,1349524,1318622,1227364,1765808,1124073,1529954,1024321,1098346,1648487,1642891,1593167,1869010,1237272,1443235,1739418,1656142,1823958,1930398,1037836,1235579,1970222,1024686,1670037,1797483,1823658,1973835,1106796,1064692,1181542,1247578,1091924,1639170,1908784,1941232,1061896,1336212,1771794,1322889,1531545,1652365,1694424,1748185,1097458,1948788,1545332
```

### Validation — 150 whole seeds

```
1865052,1261110,1385037,1908320,1318010,1874206,1205762,1349539,1474108,1141292,1810095,1320740,1152672,1939916,1499174,1753111,1741574,1960492,1129521,1954768,1216011,1565731,1170545,1236539,1127378,1440191,1147849,1808531,1633284,1699472,1178128,1857722,1761617,1970395,1399877,1075629,1674185,1538330,1883444,1328233,1747384,1102547,1498610,1049124,1911722,1117902,1921647,1338954,1792352,1775538,1361526,1476342,1555364,1591698,1460584,1323120,1855596,1159348,1172036,1203446,1348528,1873954,1395826,1150052,1140165,1838953,1594741,1328030,1605741,1551702,1520370,1762741,1199611,1025650,1112285,1437471,1193732,1343379,1283445,1684370,1630375,1418099,1605500,1625319,1548934,1392313,1163918,1879951,1128023,1971365,1795729,1874994,1323846,1685272,1855909,1249715,1611628,1192297,1721246,1984710,1320395,1225554,1100528,1822944,1158542,1306628,1853504,1202430,1930558,1214027,1463697,1638361,1139768,1627835,1443864,1495018,1668326,1913538,1608961,1311342,1832353,1676461,1881421,1022995,1989464,1471496,1640348,1677168,1955460,1259169,1020994,1841113,1395718,1252429,1878173,1440575,1179110,1567004,1020875,1774151
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

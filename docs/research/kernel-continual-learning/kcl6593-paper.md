# KCL-6.5.9.3 — Boundary Action Identifiability Decomposition

## Status

```
NEGATIVE
BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE
```

KCL-6.5.9.3 prospectively tested whether the KCL-6.5.9.2 prediction failure
is better explained by:

1. **pre-boundary representation insufficiency**, or
2. **information that only appears after interaction with the future task**.

The experiment used the same low-capacity multiclass logistic model family for
four nested information sets:

```
S0 = stage only
S1 = stage + frozen global H1–H9 state
S2 = S1 + frozen LRBS-v1 F1–F13 pre-boundary state
O  = S2 + FUTURE-PROBE-v1 zero-step future-task interaction state
```

No arm qualified under the frozen absolute gates.

S2 did not improve S1:

```
D21 = macro_recall(S2) - macro_recall(S1)
    = -0.00993
95% paired whole-seed CI:
[-0.07989, 0.06036]
```

The oracle-information arm improved S2 numerically:

```
DO2 = macro_recall(O) - macro_recall(S2)
    = +0.08347
95% paired whole-seed CI:
[-0.01100, 0.17835]
```

but this failed both preregistered Route-I requirements:

```
DO2 >= 0.15
bootstrap lower(DO2) > 0.05
```

Therefore the current experiment identifies neither a sufficient richer
pre-boundary representation nor a qualified future-interaction identifiability
gap.

## 1. Trigger

KCL-6.5.9.2 closed:

```
NEGATIVE
BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED
```

Its four action classes remained adequately supported, but the frozen global
boundary representation failed to qualify and did not outperform stage-only by
the preregistered margin.

The unresolved scientific alternatives were:

```
representation insufficiency
vs
pre-boundary target/action non-identifiability
```

KCL-6.5.9.3 was designed to distinguish those alternatives without increasing
classifier capacity.

## 2. Frozen protocol and pre-science QA

Protocol:

```
docs/research/kernel-continual-learning/kcl6593-protocol.md
```

Initial protocol freeze commit:

```
c59a54c959407b4857900728eac8a4e6333b02a8
```

A pre-science QA check detected that the explicit validation seed list had only
140 entries because of a transcription defect. No scientific execution had
occurred.

The seed lists were repaired using the already-frozen deterministic generator:

```
random.Random(6593).sample(range(1000001, 2000000), 450)
```

Final cohort remained exactly the originally specified:

```
300 train seeds
150 validation seeds
```

Repair commit:

```
ee2bf486dbdeed20d934d63d410176e5a7a593eb
```

Final protocol SHA-256 used by science:

```
0878993d53afbdbebad365a2ff8af2790904e7277502dcb8536ea455ccdde0d3
```

No outcome was observed before this repair.

## 3. Frozen target

Reuse SAFE_ACTION_SET-v1 exactly:

```
A_ONLY
C_ONLY
B_AND_C_SAFE
B_ONLY
```

The target is determined from frozen A/B/C safety predicates after all
information-set features have been extracted.

No future best-action optimization target was introduced.

## 4. Fresh cohorts

Training:

```
300 fresh whole seeds
900 boundaries
```

Validation:

```
150 fresh whole seeds
450 boundaries
```

All KCL-6.5.9.3 seeds are disjoint from:

- KCL-6.5.6 discovery seeds;
- the protected confirmatory cohort;
- KCL-6.5.9.1 replication seeds;
- KCL-6.5.9.2 train/validation seeds;
- each other across KCL-6.5.9.3 train and validation.

## 5. Frozen information sets

### S0 — stage only

```
STAGE_2
STAGE_3
```

### S1 — current global boundary state

Exactly the KCL-6.5.9.2 state:

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

### S2 — richer pre-boundary state

S2 appends the exact pre-existing KCL-6.5.8 LRBS-v1 features:

```
F1..F13
```

This choice predates KCL-6.5.9.2 and was therefore not selected from the
KCL-6.5.9.2 validation errors.

### O — FUTURE-PROBE-v1 diagnostic oracle arm

O appends eight zero-step future-task interaction features:

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

The future task is exposed only to compute its zero-step loss/gradient.

No optimizer update is allowed.

The probe does **not** include:

- A/B/C counterfactual outcomes;
- safe_B or safe_C;
- final next-task accuracy;
- retention outcomes;
- SAFE_ACTION_SET-v1 label.

The model and optimizer are verified unchanged and gradients are cleared before
counterfactual execution.

O is diagnostic only and is not an operational controller input.

## 6. Frozen classifier contract

All four arms use exactly the same model family:

```
class-balanced L2 multinomial logistic regression
lambda = 1.0
float64
train-only standardization
train-only class weights
deterministic PyTorch LBFGS
```

No:

- nonlinear classifier;
- model search;
- feature selection;
- lambda tuning;
- oversampling;
- validation tuning;
- post-outcome threshold change.

Thus S0/S1/S2/O primarily differ in available information, not classifier
capacity.

## 7. Training support

Canonical Phase-A support:

| Class | Count | Unique seeds |
|---|---:|---:|
| `A_ONLY` | 281 | 209 |
| `C_ONLY` | 540 | 289 |
| `B_AND_C_SAFE` | 49 | 49 |
| `B_ONLY` | 30 | 30 |

All train support requirements passed:

```
count >= 20
unique_seed_count >= 20
```

## 8. Phase-A QA and provenance

The first train workflow run:

```
35444505255
```

stopped before scientific execution because a focused test incorrectly treated
the word `RETENTION` in the legitimate already-observed retention-gradient
probe feature name as future-outcome leakage.

No science ran in that attempt.

The test predicate was corrected without changing:

- protocol;
- feature sets;
- cohorts;
- model family;
- thresholds.

The next train run:

```
35444584655
```

completed the full scientific train/freeze step successfully.

Scientific source commit:

```
04cb560a9532e173892fa2e22c7cd3c4612ae2f7
```

However the post-science git preservation step failed with a non-fast-forward
push because the branch had advanced with the QA commit. This was a provenance
failure after the scientific result, not a scientific failure.

Canonical first-run hashes were already emitted:

```
train JSON:
d97b8ae97fedfbc31fe5d04772134dcc41dc02b3d26938bb6b8576f6a5ec3aa5

rule JSON:
ef8ba7bd06c3d749926c671a92d99a875e2fe243787e3b80cf44f2ba411768ac
```

A recovery workflow replayed the exact scientific source commit and was allowed
to preserve evidence only if both files reproduced those SHA-256 values
byte-for-byte.

Recovery run:

```
35445995924
SUCCESS
```

Recovered evidence commit:

```
885b229de1259f5425d0a4ac08bdeb1a91e78750
```

Recovery artifact:

```
Artifact ID: 10586095267
ZIP SHA-256:
ba5d15890aa9997ecbe5a43b64f6385904ea4ec02a0b2b7bd313f370eddd20b6
```

Validation was not opened until this rule was committed.

## 9. Training diagnostics

Training macro recall:

```
S0 = 0.45556
S1 = 0.52682
S2 = 0.51236
O  = 0.56359
```

Training macro F1:

```
S0 = 0.24019
S1 = 0.34059
S2 = 0.33603
O  = 0.36459
```

These values were descriptive only.

They did not modify any validation rule.

## 10. Canonical validation

Validation workflow source commit:

```
25ca7a2ee03b4519e99407a07814411ff62a0f6a
```

Official validation run:

```
35447023652
```

Workflow conclusion:

```
SUCCESS
```

Focused tests:

```
7 passed — KCL-6.5.9.3
10 passed — KCL-6.5.9.2
```

Canonical artifact:

```
Artifact ID: 10585625788
ZIP SHA-256:
23d1e73ae6a0505d2f120c51942631787cedf322d528c76841af00471992cffa
```

Raw validation JSON SHA-256:

```
c9e577658f75100240a1ed2a514b64993914604b6eb15e4b3c7b68ef7cdf6a1b
```

Exact validation evidence was preserved into the repository without rerunning
science.

Preservation workflow commit:

```
d558861bbca16a99f58eecc90dd2d771388d210a
```

Preserved validation evidence commit:

```
46c9e44e62cc1da59358218281b4e41827452fd0
```

## 11. Validation support

| Class | Count | Unique seeds | Boundary 1/2/3 |
|---|---:|---:|---|
| `A_ONLY` | 138 | 102 | 34 / 39 / 65 |
| `C_ONLY` | 277 | 143 | 116 / 111 / 50 |
| `B_AND_C_SAFE` | 19 | 19 | 0 / 0 / 19 |
| `B_ONLY` | 16 | 16 | 0 / 0 / 16 |

All classes passed:

```
count >= 10
unique_seed_count >= 10
```

Therefore the identifiability result is not invalidated by insufficient class
support.

## 12. Validation performance

### S0

```
accuracy     = 0.54000
macro recall = 0.45487
macro F1     = 0.24490
log loss     = 1.24936
```

### S1

```
accuracy     = 0.54444
macro recall = 0.43993
macro F1     = 0.30459
log loss     = 1.14297
```

### S2

```
accuracy     = 0.52000
macro recall = 0.43000
macro F1     = 0.29604
log loss     = 1.13178
```

### O

```
accuracy     = 0.54222
macro recall = 0.51347
macro F1     = 0.33120
log loss     = 1.11421
```

No arm reaches the frozen base qualification floors:

```
macro recall >= 0.60
macro F1 >= 0.50
per-class recall >= 0.50
per-class F1 >= 0.35
bootstrap macro-recall lower > 0.45
```

## 13. Persistent A_ONLY failure

Validation `A_ONLY` support:

```
138 instances
102 unique seeds
```

Per-arm A_ONLY recall:

```
S0 = 0.0000
S1 = 0.04348
S2 = 0.04348
O  = 0.05072
```

Per-arm A_ONLY F1:

```
S0 = 0.0000
S1 = 0.08054
S2 = 0.07595
O  = 0.08861
```

Thus the dominant failure persists even after:

- global optimizer/retention state;
- localized LRBS-v1 state;
- zero-step future-task loss/gradient interaction.

This makes a simple rare-class scarcity explanation untenable for the tested
information sets.

## 14. Whole-seed bootstrap

Frozen:

```
20,000 paired whole-seed resamples
RNG seed = 6593
no model refit
```

Macro-recall 95% intervals:

```
S0: [0.44643, 0.46362]
S1: [0.35344, 0.52552]
S2: [0.34359, 0.51641]
O : [0.43304, 0.59009]
```

Only S0 has a lower bound close to the absolute 0.45 threshold, but S0 still
fails the remaining base gates and is not qualified.

## 15. Paired information gains

### S1 vs S0

```
D10 = -0.01494
95% CI:
[-0.10018, 0.07065]
```

Global H1–H9 state does not show reliable uplift over stage.

### S2 vs S1

```
D21 = -0.00993
95% CI:
[-0.07989, 0.06036]
```

LRBS-v1 does not close the pre-boundary identifiability gap.

Route R required:

```
S1 NOT QUALIFIED
S2 QUALIFIED
D21 >= 0.10
CI lower(D21) > 0.03
```

Observed:

```
S2 NOT QUALIFIED
D21 < 0
CI spans 0
```

Therefore:

```
Route R = FALSE
```

### O vs S2

```
DO2 = +0.08347
95% CI:
[-0.01100, 0.17835]
```

The zero-step future interaction probe shows a numerical uplift but it is not
statistically stable under the frozen paired bootstrap and does not meet the
preregistered magnitude requirement.

Route I required:

```
S2 NOT QUALIFIED
O QUALIFIED
DO2 >= 0.15
CI lower(DO2) > 0.05
```

Observed:

```
O NOT QUALIFIED
DO2 = 0.08347
CI lower(DO2) = -0.01100
```

Therefore:

```
Route I = FALSE
```

Route M also requires S2 and O qualification and therefore fails.

## 16. Frozen adjudication

```
qualified(S0) = false
qualified(S1) = false
qualified(S2) = false
qualified(O)  = false

Route R = false
Route I = false
Route M = false
```

Therefore:

```
KCL-6.5.9.3 = NEGATIVE
BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE
```

## 17. Scientific interpretation

### What is supported

The experiment supports the narrower findings:

1. **LRBS-v1 does not rescue pre-boundary action identifiability.**
   S2 is not better than S1 under the frozen paired analysis.

2. **FUTURE-PROBE-v1 contains some numerical incremental signal**, because O
   has higher point macro recall than S2.

3. That oracle uplift is **not large or stable enough** to identify a
   future-interaction dependence under the frozen Route-I gate.

4. The failure is concentrated strongly in `A_ONLY`, despite abundant
   support.

### What is not supported

KCL-6.5.9.3 does **not** support either conclusion:

```
"the problem is representation insufficiency"
```

or:

```
"the action target is non-identifiable before future-task interaction"
```

Neither route passed prospectively.

The correct result is therefore genuinely inconclusive between the broad
remaining explanations.

## 18. What this rules out

Do not use this result to justify:

- a controller;
- a nonlinear classifier rescue;
- retuning logistic regression;
- adding more validation seeds;
- operational use of FUTURE-PROBE-v1;
- claiming LRBS-v1 is sufficient;
- claiming zero-step future gradient interaction solves identifiability;
- consuming the protected confirmatory cohort;
- opening KCL-7.

## 19. Stronger structural clue

The persistent `A_ONLY` failure is now more informative than before.

`A_ONLY` means neither B nor C meets the frozen safe-policy contract relative
to A.

Across KCL-6.5.9.2 and KCL-6.5.9.3, the class has substantial support but very
low recall under:

- stage-only;
- global pre-boundary state;
- localized pre-boundary attribution;
- zero-step future-task interaction.

This suggests the next question should not merely add another broad state
representation.

The unresolved variable may lie in the **structure of the target itself**:
`A_ONLY` collapses multiple ways in which B/C can fail the joint
plasticity-retention contract.

## 20. STOP / PIVOT

Per frozen protocol:

### STOP

Stop the current S0/S1/S2/O identifiability decomposition.

Do not tune the same arms post hoc.

### PIVOT

The next experiment should examine whether the four-class SAFE_ACTION_SET-v1
target is itself internally heterogeneous, especially the `A_ONLY` class,
before another representation or controller is proposed.

A scientifically defensible next milestone is:

```
KCL-6.5.9.4 — Action-Target Failure-Mode Decomposition
```

The purpose should be to prospectively decompose, on fresh non-confirmatory
data, why B and C are unsafe in A_ONLY cases:

- insufficient plasticity gain;
- retention-margin violation;
- current-task strict-accuracy failure;
- combinations of these causes;
- whether B and C fail for the same or different causes.

This should initially be an **outcome/target decomposition**, not a predictor.

Only after stable failure modes are demonstrated should a new representation
or probe be designed against a more causally specific target.

Protected confirmatory seeds remain untouched.

KCL-7 remains **NOT STARTED**.

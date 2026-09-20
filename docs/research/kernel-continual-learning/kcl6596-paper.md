# KCL-6.5.9.6 — Mechanistic Representation Qualification

## 1. Result

**Status: NEGATIVE**

```
MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION
```

KCL-6.5.9.6 prospectively tested whether a new mechanistically motivated
pre-boundary representation, MRIG-v1, could make the previously unresolved
`MECH{P+R,R}` target materially more identifiable than frozen S2.

It did not.

No validation refit, classifier-capacity escalation, target redefinition,
future-task leakage, controller implementation, or protected-confirmatory
execution occurred.

## 2. Trigger

KCL-6.5.9.5 closed:

```
NEGATIVE
NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN
```

That result established that target refinement alone did not solve the
identifiability problem under S2, motivating a representation-level hypothesis.

## 3. MRIG-v1 hypothesis

MRIG-v1 represented the exact one-step optimizer response induced by frozen
boundary policies A/B/C using only already-observed tasks.

At each boundary it measured:

- adaptation response under virtual one-step AdamW updates;
- retention cost under the observed-task retention gradient;
- reset asymmetry and step-scale divergence;
- B/C-exchange-symmetric summary features.

Primary comparison:

```
S2 = frozen KCL-6.5.9.5 representation
S3 = S2 + MRIG-v1
```

Primary target:

```
Y_PRR = MECH{P+R,R} vs rest
```

## 4. Prospective cohorts

Frozen fresh non-confirmatory cohort:

```
TRAIN      = 480 seeds = 1440 boundaries
VALIDATION = 240 seeds =  720 boundaries
```

Frozen seed SHA-256:

```
ALL:
f96a7f4c5c8f45234c9108a6eb184b941bcd464398f34e2d5798fe722a24aade

TRAIN:
3c2b02dccac5f7344daf2ffdb22b2dd7f581af5bbdd92c5c8481c001e0ed19d6

VALIDATION:
f036e088b316f8988df27bbb088f87d50ac52efa062ad5058ccf8a35b0151051
```

All prior/protected overlap checks passed.

## 5. Train/freeze phase

Canonical run:

```
35478292166
SUCCESS
```

Scientific source:

```
2bda6e3ac56fbc18340c9db43c9220fde6227748
```

Primary Y_PRR train support:

```
NEG = 1350 boundaries / 480 unique seeds
POS =   90 boundaries /  85 unique seeds
```

All frozen support and integrity gates passed.

All six target × representation solvers converged.

Frozen rule:

```
MRIG-Q-v1
SHA-256:
ebd6d2d02b7263fd4a58bf52507a50f639b3211c4a3e133fa798b57c9e8ba296
```

Train evidence:

```
raw JSON SHA-256:
f4f3805072ebe67c71076741df9f79e525537c2d6855353a204b1d5f99f352f0

artifact ID:
10595821309

artifact ZIP SHA-256:
0547055137015d8839259cbef634898f3b48ea30e17b4ea0370638ec5235a643

evidence commit:
74c606154bf3681c1a9d34ee7156ca5940bb08db
```

## 6. Validation phase

Canonical run:

```
35483474452
SUCCESS
```

Validation workflow source:

```
5bbbd28aea651c0a76520f321273773f00c8146e
```

Primary Y_PRR validation support:

```
NEG = 684 boundaries / 240 unique seeds
POS =  36 boundaries /  32 unique seeds
```

The frozen validation support gate passed.

All validation integrity checks passed.

## 7. Primary result

### S2 baseline

```
macro recall = 0.584064
macro F1     = 0.436747
accuracy     = 0.609722

NEG recall   = 0.612573
NEG F1       = 0.748883

POS recall   = 0.555556
POS F1       = 0.124611
```

Qualification:

```
S2_QUALIFIED = false
```

### S3 = S2 + MRIG-v1

```
macro recall = 0.557749
macro F1     = 0.431671
accuracy     = 0.609722

NEG recall   = 0.615497
NEG F1       = 0.749777

POS recall   = 0.500000
POS F1       = 0.113565
```

Qualification:

```
S3_QUALIFIED = false
```

## 8. Frozen gain test

Primary delta:

```
D_MRIG
= macro_recall(Y_PRR,S3) - macro_recall(Y_PRR,S2)
= -0.026316
```

20,000 paired whole-seed bootstrap 95% CI:

```
[-0.068479, +0.004373]
```

Frozen PASS required:

```
S3 qualified
AND D_MRIG >= +0.10
AND bootstrap CI lower > +0.03
```

Observed:

```
S3 qualified = false
D_MRIG       = -0.026316
CI lower     = -0.068479
```

Therefore:

```
KCL-6.5.9.6 = NEGATIVE
MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION
```

## 9. Secondary diagnostics

Representation gain on diagnostic targets:

```
Y_A:
S3 - S2 macro recall = +0.003358

Y_PR:
S3 - S2 macro recall = +0.018333

Y_PRR:
S3 - S2 macro recall = -0.026316
```

MRIG-v1 therefore produced no material representation uplift on any tested
target.

A notable frozen-feature diagnostic was:

```
M9_MAX_JOINT_BADNESS = 0
```

for every train record and every validation record.

Because M9 was frozen before outcomes, it was retained unchanged. Its observed
degeneracy is evidence against the specific static one-step joint-badness
construction, not a reason for post-hoc redesign inside KCL-6.5.9.6.

## 10. Scientific interpretation

The chain now distinguishes three claims:

1. `A_ONLY` target heterogeneity is real — supported by KCL-6.5.9.4.
2. Mechanism-specific target refinement alone resolves identifiability —
   rejected by KCL-6.5.9.5.
3. Static observed-task reset-response geometry resolves the remaining
   `MECH{P+R,R}` gap — rejected by KCL-6.5.9.6.

MRIG-v1 directly simulated the frozen optimizer interventions but used only a
static boundary snapshot and gradients from already-observed tasks.

Its failure therefore motivates a different hypothesis class rather than more
MRIG feature engineering: the missing signal may lie in **temporal transition
geometry across boundaries**, not in a single static snapshot.

## 11. Integrity

All canonical validation integrity checks passed:

- exact frozen seed checksum;
- exact record count;
- exactly three boundaries per seed;
- prior/protected overlap absent;
- all S2/MRIG features finite;
- exact mechanism taxonomy;
- mechanism targets remain subsets of A_ONLY;
- virtual probe used no future task;
- original model unchanged;
- original optimizer unchanged;
- gradients cleared;
- virtual updates finite;
- B/C-visible predictor features exchange-symmetric;
- counterfactual harness valid;
- LRBS share sums valid;
- frozen validation rule valid;
- no validation refit;
- controller not implemented;
- protected confirmatory cohort untouched;
- KCL-7 not started.

## 12. Provenance

Protocol commit:

```
8d725d398944b8fd84a708f1129c18e4101766c7
```

Protocol SHA-256:

```
e6acbb980f8d8bbc8fac222e15fdda933f1b50a539f03695b387dcdafdc8abda
```

Implementation commit:

```
5e8a2689c65b77d5a8467ac416326873241dab2c
```

Contract-test commit:

```
7cb61e9442a78977f8794c552bd54e5f00636cb8
```

Train workflow source:

```
2bda6e3ac56fbc18340c9db43c9220fde6227748
```

Validation workflow source:

```
5bbbd28aea651c0a76520f321273773f00c8146e
```

Validation raw JSON SHA-256:

```
6bf4b59281f78cbea6244b36a493b182a3fcbeb2ed2428842a93eb4952123183
```

Validation artifact:

```
ID 10597037043
ZIP SHA-256
fda04308beb0e04d7a70abe0ed2934b03aa0876d806b56463a8a8c20ca9b8744
```

Validation evidence commit:

```
cb2e0cf7e8969d998f4bcd1393e74a721a579f58
```

## 13. STOP / PIVOT

### STOP

Do not:

- add more static MRIG-v1 features post hoc;
- increase classifier capacity;
- reuse the validation cohort for feature design;
- open a controller;
- open KCL-7.

### PIVOT

The next admissible hypothesis class is temporal:

> Does the trajectory of observable reset/interference geometry across already
> completed task transitions carry predictive signal that is absent from a
> single static boundary snapshot?

Candidate next milestone:

```
KCL-6.5.9.7 — Temporal Mechanistic Representation Qualification
```

It must use a fresh cohort and only information that is historically available
at the prediction boundary.

# KCL-6.5.9.5 — Mechanism-Specific Target Identifiability

## 1. Result

**Status: NEGATIVE**

```
NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN
```

KCL-6.5.9.5 prospectively tested whether the two KCL-6.5.9.4
stably-replicated failure mechanisms:

```
MECH{P,R}
MECH{P+R,R}
```

are more identifiable from frozen pre-boundary state than the monolithic
`A_ONLY` target.

Neither preregistered mechanism-specific route passed.

No classifier-capacity escalation, target redefinition, validation refit,
controller implementation, or protected-confirmatory execution occurred.

## 2. Trigger

KCL-6.5.9.4 established:

```
PASS
A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY
```

with two stable mechanism signatures:

```
M_PR  = MECH{P,R}
M_PRR = MECH{P+R,R}
```

This motivated a direct target-specific identifiability test while holding the
representation and model family fixed.

## 3. Frozen target family

All three binary targets were defined over the same full boundary population.

```
Y_A:
  POS = A_ONLY
  NEG = otherwise

Y_PR:
  POS = A_ONLY AND mechanism == MECH{P,R}
  NEG = otherwise

Y_PRR:
  POS = A_ONLY AND mechanism == MECH{P+R,R}
  NEG = otherwise
```

The two mechanism targets were strict subsets of `Y_A`.

## 4. Frozen information/model contract

Primary representation:

```
S2 = stage + global H1..H9 + frozen LRBS-v1 F1..F13
```

Diagnostic representations:

```
S0 = stage only
S1 = stage + global H1..H9
```

No FUTURE-PROBE features were used.

Every target × representation arm used the same model family:

```
class-balanced L2 binary logistic regression
ridge lambda = 1.0
float64
train-only standardization
deterministic PyTorch LBFGS
```

No nonlinear model, feature search, threshold tuning, oversampling, or
validation refit was allowed.

## 5. Fresh prospective cohort

The protocol froze 720 fresh non-confirmatory seeds:

```
TRAIN      = 480 seeds = 1440 boundaries
VALIDATION = 240 seeds =  720 boundaries
```

The cohorts were mutually disjoint and disjoint from prior KCL cohorts and the
protected confirmatory seeds.

Frozen seed checksums:

```
ALL:
5463cd9804c8f4e857a5e5a32a85119f0ab459e5857dcc6a5123123c28b22318

TRAIN:
9ed96c29e86613ac10572f4079b080c5ae70638aa70c3080b4d1773e1736e2d7

VALIDATION:
c4f5b8d112cc8fbe7235a22e32ccfe33dcca0c265baca496c440a1517c67df0d
```

## 6. Train/freeze phase

Canonical train run:

```
35457510797
SUCCESS
```

Scientific source:

```
a7a1386602705687626c13fc7a0cab131c08d085
```

Training support:

| Target | NEG count / seeds | POS count / seeds |
|---|---:|---:|
| `Y_A` | 1028 / 464 | 412 / 291 |
| `Y_PR` | 1167 / 478 | 273 / 227 |
| `Y_PRR` | 1356 / 480 | 84 / 80 |

All frozen training support gates passed.

All nine target × representation solvers converged.

Frozen rule:

```
MSTI-v1
SHA-256:
2e6649a6f32040e56c0ecaac365ee28f593516dd24cff9f2bf3ddd7c87ce0c7b
```

Train evidence raw SHA-256:

```
ef72f9f78aa544fda5aae6220fca9ed7b40438e8e908270587b91298f3b78853
```

Train/freeze artifact:

```
ID 10589766677
ZIP SHA-256
d61f6afc02bc9b4461ef3163ecd7dccfe4dd1a24c33d630b62feb54e9c104f8f
```

Train evidence commit:

```
e103802b7126fb306882123ba57cef1c9fde7a76
```

## 7. Validation phase

Validation opened only after the frozen rule was committed.

Canonical validation run:

```
35461892375
SUCCESS
```

Validation workflow source:

```
e1e6f55191f81c5d01fc0db2c914dc414846a8c8
```

Validation support:

| Target | NEG count / seeds | POS count / seeds |
|---|---:|---:|
| `Y_A` | 527 / 238 | 193 / 151 |
| `Y_PR` | 610 / 240 | 110 / 98 |
| `Y_PRR` | 676 / 240 | 44 / 42 |

All frozen validation support gates passed.

All validation integrity checks passed.

## 8. Primary S2 validation metrics

### 8.1 Y_A — monolithic A_ONLY

```
macro recall = 0.615474
macro F1     = 0.597304
accuracy     = 0.648611
log loss     = 0.668429
```

Per class:

```
NEG recall = 0.686907
NEG F1     = 0.741044
POS recall = 0.544041
POS F1     = 0.453564
```

Frozen qualification:

```
QUALIFIED = true
```

### 8.2 Y_PR — MECH{P,R}

```
macro recall = 0.686289
macro F1     = 0.566631
accuracy     = 0.638889
log loss     = 0.613953
```

Per class:

```
NEG recall = 0.618033
NEG F1     = 0.743590
POS recall = 0.754545
POS F1     = 0.389671
```

Frozen qualification:

```
QUALIFIED = true
```

### 8.3 Y_PRR — MECH{P+R,R}

```
macro recall = 0.576520
macro F1     = 0.424856
accuracy     = 0.563889
log loss     = 0.679587
```

Per class:

```
NEG recall = 0.562130
NEG F1     = 0.707635
POS recall = 0.590909
POS F1     = 0.142077
```

Frozen qualification:

```
QUALIFIED = false
```

The main qualification failures are the low macro F1 and very low positive
class F1.

## 9. Primary mechanism-specific gain test

The preregistered point deltas were:

```
D_PR  = macro_recall(Y_PR,  S2) - macro_recall(Y_A, S2)
      = +0.0708149

D_PRR = macro_recall(Y_PRR, S2) - macro_recall(Y_A, S2)
      = -0.0389546
```

Frozen target-specific gain required:

```
mechanism S2 model is QUALIFIED
AND point delta >= +0.10
AND paired whole-seed bootstrap 95% CI lower > +0.03
```

### 9.1 H-PR

20,000 paired whole-seed bootstrap 95% CI:

```
D_PR CI = [0.0334223, 0.1090740]
```

Although the CI lower bound exceeds +0.03 and `Y_PR` itself qualifies, the
point gain is only:

```
+0.0708149 < +0.10
```

Therefore:

```
H_PR = false
```

### 9.2 H-PRR

20,000 paired whole-seed bootstrap 95% CI:

```
D_PRR CI = [-0.1328015, 0.0517780]
```

The point estimate is negative and the `Y_PRR` S2 model is not qualified.

Therefore:

```
H_PRR = false
```

## 10. Primary adjudication

Observed:

```
H_PR  = false
H_PRR = false
```

Therefore:

```
KCL-6.5.9.5 = NEGATIVE
NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN
```

This is a scientific negative, not a technical REVISE.

## 11. Secondary representation diagnostics

The richer S2 representation barely improved macro recall over the lower
information sets:

```
Y_A:
  S2 - S0 = +0.003392
  S2 - S1 = +0.003903

Y_PR:
  S2 - S0 = +0.002086
  S2 - S1 = +0.009762

Y_PRR:
  S2 - S0 = +0.007934
  S2 - S1 = +0.004034
```

Thus the observed target-specific differences are not evidence that LRBS-v1
itself supplies a large new identifiability signal.

For `Y_PR`, even stage-only already achieved validation macro recall
`0.684203`, close to S2 `0.686289`.

## 12. Scientific interpretation

KCL-6.5.9.4 established that `A_ONLY` is structurally heterogeneous.

KCL-6.5.9.5 shows that this structural decomposition does **not** by itself
produce the preregistered identifiability gain under the existing pre-boundary
S2 representation and low-capacity model family.

The result separates two claims:

1. **Target heterogeneity is real** — supported by KCL-6.5.9.4.
2. **Mechanism-specific target decomposition resolves predictability** — not
   supported by KCL-6.5.9.5.

The two stable mechanisms also behave differently:

- `MECH{P,R}` is individually qualified and shows a positive paired gain over
  `A_ONLY`, but the gain is smaller than the frozen +0.10 effect threshold.
- `MECH{P+R,R}` is not qualified and shows no positive gain.

This argues against a generic claim that causal target refinement alone fixes
the earlier `A_ONLY` identifiability problem.

## 13. What is not claimed

KCL-6.5.9.5 does not establish:

- that `MECH{P,R}` has no useful signal at all;
- that a different prospectively justified representation could not help;
- that `MECH{P+R,R}` is fundamentally unidentifiable;
- that a nonlinear model should now be tried;
- that a controller is qualified;
- that the protected confirmatory cohort should be opened;
- that KCL-7 should start.

## 14. Integrity and provenance

Protocol commit:

```
27866c98043f9cf8a3d275fe3c4f93156132445c
```

Protocol SHA-256:

```
c1d5a9b4ba26ea1574902ad024c636ed79965f8c98a5711b187b07cac31be326
```

Initial implementation commit:

```
683230a1c48b8ff8b3e52243c77e4c843577cfd4
```

Contract-test commit:

```
b987e93385218e87c73ad84d38f0d24697c1a5f5
```

Pre-science technical repair:

```
3b3d12faf59ed8cb66ca5395ffeeb5754aaba3d6
```

The repair changed only the canonical KCL-6.5.8 module import and occurred
before any KCL-6.5.9.5 scientific execution.

Canonical train workflow source:

```
a7a1386602705687626c13fc7a0cab131c08d085
```

Canonical validation workflow source:

```
e1e6f55191f81c5d01fc0db2c914dc414846a8c8
```

Validation raw JSON SHA-256:

```
482e1cdab8c17dccc4385a2feab982af2d6bca1074d4eea68b9430903ddf325d
```

Validation artifact:

```
ID 10590011691
ZIP SHA-256
4a7ce2ad3d0c2e0ae32a8b271a56728abcedacf5a74e224bbecfc10fc2b8c996
```

Validation evidence commit:

```
c8d7aaa3a48aa5922bb0fa2aa907d726d8256e14
```

Guardrails:

```
validation refit = NO
future-probe features = ABSENT
controller = NOT IMPLEMENTED
protected confirmatory = UNTOUCHED
KCL-7 = NOT STARTED
```

## 15. STOP / PIVOT

### STOP

Do not:

- relax the +0.10 gain threshold after seeing `Y_PR = +0.0708`;
- promote `Y_PR` to a PASS based only on its positive bootstrap CI;
- increase classifier capacity post hoc;
- add features or validation seeds after outcome inspection;
- implement a controller from these models.

### PIVOT

The next scientific study should test a new **mechanistic representation
hypothesis**, not another target-only decomposition or a stronger classifier.

The current evidence suggests:

- target heterogeneity exists;
- target refinement alone is insufficient;
- S2 adds almost no macro-recall gain over S0/S1;
- `MECH{P+R,R}` remains the harder unresolved mechanism.

A future milestone should therefore preregister a representation designed to
measure the missing causal interaction that distinguishes the stable mechanisms,
then compare it against the frozen S2 baseline on a fresh cohort.

Until such a hypothesis is explicitly specified and frozen, the KCL chain
should stop here.

Protected confirmatory seeds remain untouched and KCL-7 remains closed.

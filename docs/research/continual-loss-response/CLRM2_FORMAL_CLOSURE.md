# CLRM-2 Formal Closure

Status: **NEGATIVE / CLOSED**

Date: 2026-09-29

## Scientific question

CLRM-2 asked exactly:

> Can the frozen observable pre-boundary state representation predict the six
> policy-specific CE-loss response channels materially better than the frozen
> strongest simple baseline on a sealed seed-grouped validation cohort, while
> satisfying the frozen point-calibration gate?

The answer under the exact frozen CLRM-2 contract is:

```text
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

This is a negative predictive-qualification result, not an integrity stop.

## Frozen upstream state

Parent scientific chain:

```text
MSA
  terminal accuracy = coarse under the frozen substrate
  terminal CE loss  = informative
        ↓
CLRM-1
  six direct CE-loss response channels = support-qualified
        ↓
CLRM2-A
  D-train discovery = PASS / CLOSED
  RBF-KRR-v1 candidate frozen
  strongest baseline frozen = B2
        ↓
CLRM2-B
  Validation Lock independently verified PASS
        ↓
sealed D-val + one-shot Gate-2
```

Exact Validation Lock SHA-256:

```text
bd5845eb350bc5bbe889d0d1e2570d9a97b51c8bc683585c6d344f53ee15abde
```

Frozen candidate package SHA-256:

```text
310bd9805cb028691826722c8cf5ee365e85d549872f2f3e898d8e348cef2a83
```

Frozen D-train SHA-256:

```text
8e7e38357f2117e76337b454f40debeb7741f1a8f3993a61add9f50c490d1b28
```

Candidate:

```text
family = RBF-KRR-v1
gamma  = 0.02
lambda = 1.0
```

Frozen strongest baseline:

```text
B2 = linear ridge state-response on exact OBS11-v1
```

## Sealed validation execution history

Attempt 1:

```text
workflow = 36256306507
classification = TECHNICAL_PRE_SCIENCE_LITERAL_GUARD_FAILURE
```

The failure occurred inside the pre-science retired-workflow literal guard.
No D-val seed executed and Gate-2 was not called.

Recovery changed only that workflow guard. Scientific source, frozen candidate,
D-val manifest, features, targets, baseline, runtime and Gate-2 remained
unchanged.

Canonical sealed validation:

```text
workflow = 36256426311
head = 659b834b95723b8ca11b9bfac55e078710c6c8a2
status = completed / success
```

D-val integrity:

```text
seed count      = 80
boundary count  = 240
integrity       = PASS
D-val seed SHA-256 =
a2287c490acf6c8a94cff56be1a5eb4aaa0115fce26675312ac590d5bfe6ee96

D-val collection SHA-256 =
a5fbf4bc170112929536a056fcb0001245dbae42daaf89160d63c66a816d767a

D-val git blob =
7fe091331b3eedd61233d8e60b07edc26091f3b3
```

Evidence preservation:

```text
raw pre-integrity artifact
  ID = 10910702079
  ZIP SHA-256 =
  dcb9592639a3ac8b8ea31d9abaaaa5e8c6527a1bcc68bdb0f02b70497d29bff0

complete D-val before adjudication
  ID = 10911211564
  ZIP SHA-256 =
  fd2a3215e09293abe7ef18615b9b7f6f67176b8cdd08f4a97c5a5c766a1e9b22

complete sealed validation evidence
  ID = 10910737184
  ZIP SHA-256 =
  85c5364275fd54892814cc7a1ae3002ea5f401f08b1aae3c07044a0270a7b1af
```

D-val preservation commit:

```text
cac54ba32fcada0eda0827c1419fb83f82727aad
```

## One-shot Gate-2 result

Gate-2 was called exactly once after valid D-val preservation.

Formal result SHA-256:

```text
03f66e5851f2d7ef61d2db1a59a6a4ce6c3249f8920e3830b2ce7cfe7721fc79
```

Formal result git blob:

```text
4a1150dc7f8a2b5a297ec5973a54dd413068a63c
```

Formal result preservation commit:

```text
44ebebc65a76a8233c5323a2a56a0222d3813bf8
```

Observed status:

```text
NEGATIVE
```

Observed verdict:

```text
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

### Baseline-superiority gate

```text
macro_ratio   = 1.0020429145900482
relative_gain = -0.0020429145900482393

95% whole-seed bootstrap macro-ratio interval =
[0.9887160134229875, 1.0157851023851696]

required:
relative_gain >= 0.10
AND upper_97p5 < 1.0
AND every channel ratio <= 1.05
```

Result:

```text
baseline_superiority_pass = false
```

Per-channel candidate / B2 MAE ratios:

```text
A.current_loss       1.0166136685174996
A.prior_mean_loss    0.9903468510616578
B.current_loss       0.9863983121201932
B.prior_mean_loss    1.006825091657637
C.current_loss       1.001120156245776
C.prior_mean_loss    1.0109534079375257
```

All six ratios remained below the frozen per-channel degradation ceiling 1.05,
but the candidate did not achieve the required material aggregate improvement
and the bootstrap interval crossed 1.0.

### Calibration gate

Only:

```text
B.prior_mean_loss
```

passed the complete frozen alpha/beta calibration criterion.

The other five direct channels failed at least one frozen calibration
requirement. Therefore:

```text
calibration.all_pass = false
```

Notable assessment values include:

```text
A.current_loss
  beta = 1.1383988752122176
  |alpha| / baseline_MAE = 0.1921905309966203

A.prior_mean_loss
  beta = 1.058007180019129
  |alpha| / baseline_MAE = 0.10717306464675622

B.current_loss
  beta = 0.4687479617378252
  |alpha| / baseline_MAE = 1.2173483588350438

C.current_loss
  beta = 2.7042719398211656
  |alpha| / baseline_MAE = 2.616121162641837

C.prior_mean_loss
  beta = 1.0873659151068702
  |alpha| / baseline_MAE = 0.29983432626719797
```

## What this result establishes

Within the exact frozen substrate, cohort, OBS11-v1 representation, six
continuous CE-loss targets, RBF-KRR-v1 candidate family and B0/B1/B2 comparator
contract:

1. The six response channels were measurable and non-degenerate; CLRM-1 remains
   valid.
2. A nonlinear RBF-KRR predictor selected on D-train did **not** provide a
   material sealed-validation advantage over the strongest simple baseline.
3. The strongest baseline was B2, a linear ridge state-response model using the
   same OBS11-v1 observables.
4. Point calibration of the frozen candidate was not qualified across all six
   direct channels.
5. Therefore the CLRM-2 predictor contract is not qualified for downstream use.

## What this result does not establish

This result does **not** show that:

- CE-loss response is uninformative;
- OBS11-v1 contains no predictive information;
- every possible predictor family must fail;
- accuracy should replace loss;
- a controller should be introduced;
- B2 itself is a production-qualified predictor.

The result is narrower:

> The preregistered RBF-KRR-v1 candidate did not materially outperform the
> frozen strongest B2 baseline and did not satisfy all-channel calibration on
> the sealed D-val cohort.

No post-outcome feature selection, model-family rescue, threshold relaxation,
recalibration, seed substitution or extra D-val seed is permitted.

## Governance closure

```text
CLRM-0                               PASS / CLOSED
CLRM-1                               PASS / CLOSED
CLRM2-A                              PASS / CLOSED
CLRM2-B Validation Lock              PASS / CLOSED
sealed D-val                         SPENT
Gate-2                               ONE-SHOT / SPENT
CLRM-2 predictor qualification       NEGATIVE / CLOSED

verdict =
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED

CLRM-3                               NOT AUTHORIZED
CLRM-2.1 / CLRM-2.2 rescue           NOT AUTHORIZED
controller                           CLOSED
KCL-7                                CLOSED
```

The sealed-validation workflow was retired/hard-disabled after the canonical
result at commit:

```text
535078620359d2fac2369b521373222c28cc0771
```

The only scientifically valid next action is the mandatory formal convergence
review. No further CLRM science is authorized by this closure.

# CLRM Mandatory Formal Convergence Review

Status: **CLOSED / CONVERGED AFTER NEGATIVE CLRM-2 QUALIFICATION**

Date: 2026-09-29

Parent formal result:

```text
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

Parent formal result SHA-256:

```text
03f66e5851f2d7ef61d2db1a59a6a4ce6c3249f8920e3830b2ce7cfe7721fc79
```

This review is required by the frozen CLRM-2 governance after a negative sealed
validation result. It does not authorize a rescue experiment.

## 1. WHAT DID THE PROGRAM PROVE?

### Measurement result

MSA established, within the frozen continual-learning substrate:

```text
terminal accuracy = coarse / ceiling-compressed
terminal CE loss  = informative
```

This justified moving the response-modeling question from terminal accuracy to
continuous terminal CE loss without mutating the substrate difficulty.

### Response-support result

CLRM-1 established:

```text
PASS_LOSS_RESPONSE_SUPPORT
ALL_SIX_DIRECT_LOSS_CHANNELS_NONDEGENERATE
```

Therefore the policy-conditioned response surface itself had enough direct
within-stage support to justify a predictive study.

### Predictive-discovery result

CLRM2-A successfully froze:

- exact OBS11-v1 pre-boundary observables;
- exact six direct CE-loss response targets;
- one RBF-KRR-v1 candidate;
- mandatory B0/B1/B2 baselines;
- one strongest baseline selected from D-train only;
- a complete candidate package capable of sealed prediction without refitting.

The strongest D-train baseline was B2, the linear ridge state-response model.

### Sealed-validation result

CLRM2-B established:

```text
LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED
```

The candidate did not meet baseline superiority:

```text
macro_ratio   = 1.0020429145900482
relative_gain = -0.0020429145900482393
bootstrap 95% upper macro-ratio = 1.0157851023851696
```

and did not meet all-channel calibration.

Thus the evidence does not support the claim that the frozen nonlinear
RBF-KRR-v1 predictor adds material predictive capability beyond the strongest
simple linear baseline on fresh seeds.

## 2. WHAT CAPABILITY DID THE PROGRAM CREATE?

CLRM created a **measurement and evaluation capability**, not a qualified
predictive/controller capability.

The reusable assets are:

```text
pre-boundary observable state extraction
        ↓
same-state A/B/C policy counterfactual response extraction
        ↓
six continuous CE-loss response channels
        ↓
seed-grouped discovery / sealed validation separation
        ↓
frozen candidate + frozen strongest baseline
        ↓
all-channel superiority + calibration adjudication
```

Concrete reusable research capabilities:

1. high-resolution continuous response measurement based on CE loss;
2. exact same-terminal-state current/prior loss extraction;
3. explicit separation of support qualification from predictability
   qualification;
4. two-lock anti-leakage discovery/validation architecture;
5. deterministic seed-grouped model comparison;
6. evidence preservation before scientific reveal;
7. one-shot adjudication with no post-outcome rescue.

These capabilities are valid even though the specific predictor failed
qualification.

## 3. SHOULD THE CAPABILITY ENTER MINDFORGE CORE?

### Retain as research/core instrumentation

The following are eligible to be retained as scientific infrastructure:

```text
CE-loss response measurement contract
same-state response extractor
accuracy-as-sentinel rule
support-qualification methodology
two-lock discovery/validation governance
seed-grouped validation/evidence preservation machinery
```

They have already produced reproducible evidence and are not dependent on the
failed predictive claim.

### Do not promote as MindForge decision capability

The following must **not** enter MindForge core as an active decision or
control mechanism:

```text
CLRM-2 RBF-KRR predictor
automatic policy selection from CLRM-2 predictions
controller derived from CLRM-2
KCL-7 reopening
```

Reason:

```text
predictive qualification = NEGATIVE
baseline superiority     = FAIL
all-channel calibration  = FAIL
```

### B2 status

B2 should remain a **scientific comparator**, not silently become the new
predictor.

The sealed result shows that RBF-KRR did not materially beat B2. It does not
establish that B2 itself satisfies an independently preregistered production or
controller qualification gate.

## 4. SCIENTIFIC INTERPRETATION

The strongest supported interpretation is:

> The current observable state contains enough structure for a simple linear
> ridge comparator to be competitive, but the preregistered nonlinear RBF-KRR
> formulation did not extract additional stable, calibrated response information
> on fresh seeds.

This narrows the search space.

It argues against spending more evidence on a same-question ladder of:

```text
more RBF tuning
more kernels
more features chosen after seeing D-val
more validation seeds
threshold relaxation
recalibration rescue
```

Those would answer a post-hoc rescue question rather than the preregistered
CLRM-2 question.

## 5. CONVERGENCE DECISION

```text
CLRM scientific question                    CLOSED
CLRM-2 specific predictor                   ARCHIVE AS NEGATIVE EVIDENCE
continuous CE response measurement          RETAIN
response-support methodology                RETAIN
two-lock predictive governance              RETAIN
B2                                          RETAIN AS COMPARATOR ONLY
predictor promotion                         NO
controller promotion                        NO
CLRM-3                                      NOT AUTHORIZED
same-question rescue ladder                 CLOSED
```

The CLRM branch has reached a legitimate scientific stopping point.

## 6. NEXT SCIENTIFIC TRANSITION

No immediate successor experiment is authorized by CLRM itself.

A future research program may be opened only if it asks a materially different
question that is independently justified before using any new evidence. It
must not be framed as a rescue of the spent CLRM-2 D-val result.

Examples of genuinely different question classes could include:

- whether a different *causal process* representation is required rather than a
  static observable state representation;
- whether the useful object is a lower-dimensional sufficient statistic rather
  than direct six-channel prediction;
- whether prediction should target a different prospectively defined quantity
  with independent evidence.

Those are research directions only, not authorized experiments.

Current canonical action:

```text
preserve CLRM as closed negative predictive evidence
retain its measurement/governance assets
return to the MindForge research portfolio
choose the next independent scientific question there
```

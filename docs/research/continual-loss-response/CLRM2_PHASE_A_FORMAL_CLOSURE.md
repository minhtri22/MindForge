# CLRM2-A Phase-A Formal Closure

Status: **PASS / CLOSED**

Date: 2026-09-26

## Scientific scope

CLRM2-A Phase A was authorized only to:

- collect the frozen 160-seed D-train cohort;
- preserve 480 pre-boundary OBS11-v1 / six-response records;
- fit/tune the preregistered RBF-KRR-v1 candidate on D-train only;
- fit/tune mandatory B0/B1/B2 baselines on D-train only;
- select exactly one strongest baseline from D-train OOF evidence;
- refit and freeze the candidate/baseline package;
- preserve exact evidence without executing or inspecting D-val.

D-val and Gate-2 remained prohibited throughout Phase A.

## Frozen parent lock

Training Lock SHA-256:

```text
e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5
```

Independent Training Lock verification:

```text
CLRM2_TRAINING_LOCK_VERIFICATION_PASS
workflow = 36100335778
```

## Technical execution history

Attempt 1:

```text
workflow = 36107392997
classification = TECHNICAL_QA_SELF_MATCH / ZERO-SCIENCE
```

Failure occurred in the pre-science workflow self-audit. No D-train seed executed.

Attempt 2:

```text
workflow = 36107534594
classification = TECHNICAL_INTEGRITY_HARNESS_KEY_ORDER_MISMATCH
```

The exact 160-seed collection process completed, but the post-collection integrity
harness incorrectly required JSON dictionary key iteration order to equal OBS11
semantic feature order. The scientific runner serializes JSON with
`sort_keys=True`, so the assertion was invalid. Candidate fitting did not run,
D-val did not run, and no response geometry or validation outcome was inspected.
No artifact had been uploaded, so the ephemeral collection was not recoverable.

Recovery changed only the QA assertion from dictionary iteration-order equality
to exact feature-key set equality and added immediate raw-collection
preservation before integrity validation. Scientific source, seed manifest,
representation, targets, model family, hyperparameter grids, CV, baselines,
runtime and gates were unchanged.

Canonical same-lock technical recovery:

```text
workflow = 36254847891
head = b67a374eb1a5f04672d1bf3afdce3c7af8e1f21e
status = completed / success
```

## Canonical D-train collection

```text
seed count      = 160
boundary count  = 480
D-train seed manifest SHA-256 =
bc7f7dd941a5ec280156e9cbfc3f1501565213db7efa3b940dd4d189891b93e8

D-train collection SHA-256 =
8e7e38357f2117e76337b454f40debeb7741f1a8f3993a61add9f50c490d1b28

D-train git blob =
46731fbbf621829d55234c0ad670482c7a09bd51
```

Integrity:

```text
CLRM2_DTRAIN_INTEGRITY=PASS
D-val seeds executed = 0
Gate-2 called        = false
```

Raw pre-integrity artifact:

```text
artifact ID = 10910576776
artifact ZIP SHA-256 =
0efa68a8ceea97b0810f4509f51724fb46d2bfbb207b0149ee539418ba5e3dd7
```

## Frozen candidate package

Candidate family:

```text
RBF-KRR-v1
```

Selected shared candidate hyperparameters:

```text
gamma  = 0.02
lambda = 1.0
```

D-train OOF candidate score:

```text
0.418296023976582
```

Mandatory baseline D-train OOF family scores:

```text
B0 = 0.46650102517933295
B1 = 0.4376053822804449
B2 = 0.4155581142489717
```

Frozen strongest baseline:

```text
B2
```

Frozen per-channel B2 lambdas in exact target order:

```text
[100.0, 0.01, 100.0, 1.0, 100.0, 1.0]
```

Candidate package SHA-256:

```text
310bd9805cb028691826722c8cf5ee365e85d549872f2f3e898d8e348cef2a83
```

Candidate package git blob:

```text
7bf84b2c4c4ddbc84131aaab807d9620a317d40c
```

Evidence commit:

```text
29ff470e4c392b76795b6546d0d331553368de88
```

Complete Phase-A artifact:

```text
artifact ID = 10911205821
artifact ZIP SHA-256 =
9a1d1fc6b3d1f64817a685f8d6e9c1737d87aa1a57a6318d4b15bc43c0123325
```

## Interpretation boundary

The candidate having been selected on D-train does **not** establish that the
observable state representation predicts policy-conditioned CE-loss response
better than the strongest baseline.

The following scientific question remains sealed:

> On fresh D-val, does the frozen RBF-KRR-v1 candidate beat the frozen strongest
> B2 baseline under the preregistered six-channel superiority and calibration
> Gate-2?

No D-val result exists at this closure.

## Governance closure

```text
CLRM2-A Phase A                         PASS / CLOSED
D-train                                SPENT
Phase-A collection workflow            RETIRED / HARD-DISABLED
candidate package                      FROZEN
strongest baseline                     FROZEN = B2
D-val                                  SEALED / NOT EXECUTED
Gate-2                                 NOT CALLED
controller                             CLOSED
```

The only authorized transition is:

```text
CLRM2-B Validation Lock
  -> independent Validation Lock verification
  -> only then one-shot sealed D-val execution
```

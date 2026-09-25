# CLRM-1 Formal Closure

Status: **PASS / CLOSED**

Date: 2026-09-25

## Canonical scientific execution

Workflow:

```text
36092039012
```

Exact verified execution lock:

```text
39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e
```

Role-S manifest SHA-256:

```text
3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6
```

Protocol SHA-256:

```text
1841fb6ce65eb9d1f4ce93771797819fa68bc9216f5714322de645a874f59411
```

## Collection

```text
72/72 frozen Role-S seeds
3/3 boundaries per seed
216/216 complete matched boundaries
72 boundaries at each stage
648/648 A/B/C response vectors
1296/1296 primary loss scalars
6/6 deterministic reliability repeats exact
```

Integrity/support/reliability:

```text
PASS
```

Collection SHA-256:

```text
adc69007e98f036785427617b7109f0a93cc236e4ef605bfbdfcdf727748c7b4
```

Collection evidence commit:

```text
ff3d4d6b5c386c036e5e0de3286ff53f19cb18c4
```

Collection-before-adjudication artifact:

```text
ID = 10845952892
ZIP SHA-256 = b7530afd0e3ad748777518fad46d45311116da6fd881c46ac1dacbc7d4537155
```

The complete collection was preserved before the support adjudicator was
called.

Before preservation/adjudication:

```text
six-channel geometry inspected = NO
contrast geometry inspected    = NO
accuracy distributions read    = NO
```

The complete valid collection is canonical and must never be rerun.

## One-shot adjudication

Exactly one valid CLRM-1 support adjudicator call was executed.

Observed result:

```text
status  = PASS
verdict = PASS_LOSS_RESPONSE_SUPPORT
reason  = ALL_SIX_DIRECT_LOSS_CHANNELS_NONDEGENERATE
```

Formal-result SHA-256:

```text
1ed1ce672454c845445c0f87efb27df75cdc4842dea01c8a22b825a5ed76ff20
```

Formal-result evidence commit:

```text
aa35ad61f032b35303958edafd7b2c8e3ce7010d
```

Complete evidence artifact:

```text
ID = 10845703212
ZIP SHA-256 = 6cf2ff1afde9f2b41d540362720c8d9c4c481cfbf8212bd27e19dc8e1f3b70c8
```

## Frozen Gate-1 result

Direct-channel qualified-stage counts:

```text
A.current_loss       3 / 3
A.prior_mean_loss    3 / 3

B.current_loss       2 / 3
B.prior_mean_loss    3 / 3

C.current_loss       2 / 3
C.prior_mean_loss    3 / 3
```

Every direct channel therefore satisfies the preregistered requirement:

```text
qualified stage cells >= 2 / 3
```

and the global Gate-1 requirement:

```text
ALL 6 DIRECT CHANNELS QUALIFIED
```

The result does not rely on pooled-across-stage variation.

## Diagnostic-only outputs

A-relative B-A/C-A contrast geometry was computed only after the complete
collection was preserved and did not enter the verdict.

Accuracy sentinels were also revealed only after adjudication and did not enter
eligibility, support, geometry qualification or the PASS decision.

No correctness threshold was imported.

## What CLRM-1 establishes

Within the frozen current substrate and the prospectively defined all-boundary
Role-S population:

1. the exact two-axis CE-loss response can be extracted reproducibly from the
   same terminal state;
2. all six A/B/C direct response channels possess preregistered within-stage
   non-degenerate support;
3. the response-support prerequisite for a predictive study is satisfied.

## What CLRM-1 does not establish

CLRM-1 does not establish:

- that observable pre-boundary state predicts these responses;
- that any candidate model beats B0/B1/B2;
- that predictions are calibrated;
- that action contrasts are predictable;
- that any A/B/C decision rule is useful;
- that a controller is justified.

No predictor was fitted.

## Role-S data disposition

The full CLRM-1 Role-S cohort is now:

```text
HISTORICAL / SPENT SUPPORT EVIDENCE
```

It may be retained for provenance and exact reproduction only.

It may not be used in CLRM-2 for:

- predictor fitting;
- feature selection;
- representation selection;
- hyperparameter selection;
- baseline selection;
- sealed validation;
- replication qualification.

The exact spent Role-S manifest is:

```text
3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6
```

## Governance transition

Frozen downstream rule:

```text
PASS_LOSS_RESPONSE_SUPPORT
→ authorize CLRM-2 DESIGN ONLY
```

Therefore:

```text
CLRM-1                        PASS / CLOSED
CLRM-2 protocol design        AUTHORIZED
CLRM-2 fresh science          NOT AUTHORIZED
predictor training            NOT AUTHORIZED
controller                    CLOSED
KCL-7                         CLOSED
```

A separate CLRM-2 preregistration must freeze the observable representation,
candidate model family, D-train/D-val manifests and split, preprocessing,
hyperparameter-selection procedure, B0/B1/B2 implementation, sealed-validation
procedure, bootstrap/calibration adjudicator, execution lock and zero-science
qualification before any predictor can be fitted.

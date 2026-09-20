# CPRM-0 — Primary Target Contract

Status: **FROZEN PROGRAM-LEVEL TARGET CONTRACT**

## 1. Primary scientific object

For every prospectively eligible pre-boundary state `X` and canonical policy
`a ∈ {A,B,C}`, the primary response vector is:

```text
Y(X,a) = [
  plasticity_auc,
  final_current_accuracy,
  prior_task_retention,
  worst_prior_accuracy
]
```

The exact operational extraction of each quantity must reuse canonical KCL
semantics or explicitly document a new measurement contract before CPRM-1
execution.

## 2. Primary policy contrasts

A-relative continuous contrasts are part of the primary response object:

```text
C_B(X) = Y(X,B) - Y(X,A)
C_C(X) = Y(X,C) - Y(X,A)
```

Each component retains its original scale and meaning.

## 3. Hard labels are downstream only

Historical labels such as:

```text
A_ONLY
B_SAFE_ONLY
C_SAFE_ONLY
B_AND_C_SAFE
MECH{P,R}
MECH{P+R,R}
Y_PRR
```

are not CPRM primary targets.

They may be computed only in a later, separately authorized diagnostic if
required for interpretation. They may not define eligibility, training support
or success in the first predictive program.

## 4. No target cherry-picking

The first predictive protocol may not inspect fresh outcomes and then promote
the easiest component to "primary".

Before fresh execution it must predeclare:

- which response components are primary qualification targets;
- whether qualification is joint or componentwise;
- how missing/degenerate components are handled;
- the exact strongest-baseline comparison;
- the material superiority margin.

The program-level vector above cannot be redefined after outcome inspection.

## 5. No threshold inheritance as a target

KCL thresholds:

```text
STRICT_CURRENT_MIN     = 0.95
PLASTICITY_BENEFIT_MIN = 0.01
RETENTION_MARGIN       = 1/24
```

remain historical definitions only.

CPRM does not optimize toward reproducing the labels produced by those
thresholds.

## 6. Controller prohibition

A response predictor is not a controller.

No action-selection rule may be derived, tuned or evaluated until the response
model has passed discovery and independent fresh replication under the frozen
CPRM roadmap.

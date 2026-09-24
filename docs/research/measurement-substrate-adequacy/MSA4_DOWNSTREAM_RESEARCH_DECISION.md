# MSA-4 — Downstream Research Decision

Status: **FORMAL GOVERNANCE REVIEW — CLOSED**

Date: 2026-09-25

Trigger:

```text
MSA-3
REPLICATION_CONFIRMED
ACCURACY_COARSE_LOSS_INFORMATIVE
```

MSA-4 is governance-only.

No scientific execution is performed.
No predictor is fitted.
No task difficulty is changed.
No spent MSA-1/MSA-3 data are used to tune a downstream target.

## 1. Evidence entering MSA-4

The current substrate now has two independent fresh cohorts supporting the same
frozen classification:

```text
MSA-1 discovery:
  ACCURACY_COARSE_LOSS_INFORMATIVE

MSA-3 replication:
  ACCURACY_COARSE_LOSS_INFORMATIVE
  REPLICATION_CONFIRMED
```

Thus the measurement question that motivated MSA is resolved inside this
substrate:

```text
terminal accuracy = reproducibly coarse / ceiling-compressed
terminal CE loss  = reproducibly informative
```

The correct response is not to manufacture more difficulty merely to rescue
accuracy.

## 2. Candidate downstream paths

### Path A — Open MSA-2 and vary task/substrate difficulty

Decision:

```text
NOT SELECTED / CLOSED
```

Reason:

MSA-2 was conditional on a concrete need to distinguish measurement coarseness
from substrate saturation. Replicated informative loss shows that the current
substrate already contains usable endpoint information.

Opening MSA-2 now solely to make accuracy vary would be outcome-seeking
difficulty search.

If a future architecture question independently requires structure dependence,
that question must be opened under a new preregistered program rather than
retroactively reviving MSA-2.

### Path B — Stop all endpoint-response modeling in this synthetic family

Decision:

```text
NOT SELECTED
```

Reason:

The measurement prerequisite is not absent: terminal cross-entropy loss is
reproducibly informative. Therefore measurement inadequacy alone does not
justify terminating every downstream response-modeling question.

This does not imply that a predictor will work.

### Path C — Authorize a separately named new response-modeling program

Decision:

```text
SELECTED
```

The new program may test whether observable pre-boundary state predicts
policy-specific continuous responses under a measurement contract informed by
the replicated MSA result.

This is not CPRM-2.

It must start from a new program/branch and specification foundation.

It receives no authorization to train a predictor yet.

## 3. Measurement inheritance allowed downstream

A future program may inherit the following replicated measurement fact:

> terminal cross-entropy loss is an informative endpoint co-measurement under
> the current frozen substrate, while terminal accuracy is reproducibly coarse
> under the preregistered MSA rule.

Accordingly, terminal cross-entropy loss may be proposed as a primary
continuous endpoint candidate in the new program.

Terminal accuracy may remain a correctness sentinel / descriptive diagnostic,
but it must not be treated as a high-resolution continuous target without a new
independent justification.

MSA-4 does **not** freeze the future program's complete target vector.

That must be specified prospectively in the new program before fresh science.

## 4. Anti-rescue boundary

The downstream program may not:

- call itself CPRM-2;
- reuse CPRM-1, MSA-1 or MSA-3 scientific values for fitting/tuning;
- simply drop failed CPRM dimensions and train;
- choose features from spent cohorts;
- tune gates against the replicated MSA result;
- assume predictor success because measurement support exists;
- open a controller.

Historical CPRM evidence may be used only for provenance and to state which
questions were previously attempted/closed.

## 5. Required new-program specification foundation

Before any downstream fresh science, the new program must freeze:

1. origin and explicit non-CPRM-rescue rationale;
2. exact prediction question;
3. exact continuous response vector;
4. role of terminal CE loss versus terminal accuracy sentinel;
5. prospectively eligible all-boundary population;
6. frozen simple baselines;
7. seed-grouped development / validation / independent replication separation;
8. calibration and baseline-superiority gates;
9. fresh cohort exclusions covering KCL, ACO-1, CPRM-1, MSA-1 and MSA-3;
10. finite STOP roadmap;
11. controller prohibition;
12. zero-science specification QA.

No model fitting is authorized by MSA-4.

## 6. Final MSA decision

```text
MSA-0                         PASS / CLOSED
MSA-1                         PASS / CLOSED
MSA-2                         CLOSED / NOT SELECTED
MSA-3                         REPLICATION_CONFIRMED / CLOSED
MSA-4                         CLOSED

MEASUREMENT QUESTION          RESOLVED FOR CURRENT SUBSTRATE

REPLICATED FINDING:
  ACCURACY_COARSE_LOSS_INFORMATIVE

CURRENT SUBSTRATE             RETAIN
DIFFICULTY MUTATION           NOT JUSTIFIED
MSA PROGRAM                   FORMALLY CONVERGED / CLOSED

NEXT DIRECTION                NEW RESPONSE-MODELING PROGRAM
NEXT WORK                      SPECIFICATION FOUNDATION ONLY
FRESH SCIENCE                 NOT AUTHORIZED
PREDICTOR TRAINING            NOT AUTHORIZED
CONTROLLER                    CLOSED
KCL-7                         CLOSED
```

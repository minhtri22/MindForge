# CPRM Formal Convergence Review

Status: **FORMAL REVIEW — CLOSED**

Date: 2026-09-20

Trigger:

```text
CPRM-1
NEGATIVE
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
```

This review is evidence/governance synthesis only.

No new seed is executed.
No predictor is fitted.
No target/gate is recomputed.
No CPRM-1 outcome is used to tune a replacement model.
No controller is opened.

## 1. Evidence that must be held simultaneously

The canonical CPRM-1 result contains two facts.

First, meaningful continuous geometry exists:

```text
plasticity_auc          qualified
prior_task_retention    qualified
worst_prior_accuracy    qualified

B-A contrast family     qualified
C-A contrast family     qualified
```

Second, the preregistered joint object fails because:

```text
final_current_accuracy qualified = false
qualified cells = 0/9
all-four-component contract = false
```

The second fact controls the CPRM-1 verdict.

## 2. Candidate continuation paths

### Path A — open CPRM-2 using only the three qualified components

Decision:

```text
REJECTED
```

Reason:

The all-four-component requirement was frozen before fresh outcomes.
Dropping the failed component after observation is direct target rescue.

### Path B — keep CPRM but weaken the final_current_accuracy geometry gate

Decision:

```text
REJECTED
```

Reason:

Changing unique-count, robust-span or resolution requirements after seeing
ceiling saturation is threshold rescue.

### Path C — use the same 60-seed cohort to design a new endpoint metric

Decision:

```text
REJECTED
```

Reason:

The cohort is now spent confirmatory evidence. Reusing it for target design
would leak outcomes into the next formulation.

### Path D — terminate CPRM as formulated and return upstream to
measurement/substrate adequacy

Decision:

```text
SELECTED
```

This path preserves the scientific distinction between:

- a potentially informative continuous plasticity/retention response structure;
- an endpoint current-task metric that is saturated under the current
  substrate.

The next uncertainty is therefore no longer "can CPRM-2 predict the frozen
four-component target?" That question is closed NEGATIVE.

The upstream question is:

> Does the current continual-learning substrate provide a scientifically useful
> endpoint-performance measurement regime, or is final current-task accuracy
> too ceiling-saturated to serve as a response dimension for future
> state-conditioned modeling?

This is a substrate/measurement adequacy question, not a predictor question.

## 3. Why this is not a rescue of CPRM

A future adequacy study may not be called CPRM-1.1 or CPRM-2.

It must not:

- reuse the CPRM-1 cohort for metric selection;
- drop endpoint accuracy merely because it failed;
- tune task difficulty until a desired geometry appears;
- preserve CPRM-2 as an assumed downstream destination.

It must instead begin from a separately preregistered upstream question and a
fresh evidence contract.

Possible outcomes must include the possibility that endpoint accuracy is
correctly saturated because the substrate is already solved, in which case
future response modeling should be reconsidered rather than forced.

## 4. Program decision

```text
CPRM_FORMAL_CONVERGENCE_REVIEW = CLOSED

CPRM_PROGRAM                    = TERMINATED AS FORMULATED
CPRM-1                          = NEGATIVE / CLOSED
CPRM-2                          = FORBIDDEN
THREE-COMPONENT RESCUE          = FORBIDDEN
GEOMETRY-GATE RELAXATION        = FORBIDDEN
SAME-COHORT TARGET REDESIGN     = FORBIDDEN

NEXT_DIRECTION                  = RETURN UPSTREAM
NEXT QUESTION                   = MEASUREMENT / SUBSTRATE ADEQUACY
NEW RESEARCH PROGRAM REQUIRED   = YES

PREDICTOR TRAINING              = CLOSED
CONTROLLER                      = CLOSED
KCL-7                           = CLOSED
PROTECTED KCL COHORT            = UNTOUCHED
```

## 5. Data disposition

The 60 CPRM-1 seeds / 180 boundaries / 540 policy-response vectors are now:

```text
HISTORICAL / SPENT CPRM EVIDENCE
```

They may be retained for provenance and exact reproduction of the CPRM-1
negative verdict.

They may not be used in a future program for:

- target selection;
- task-difficulty selection;
- metric selection;
- model fitting;
- hyperparameter tuning;
- validation;
- replication qualification.

## 6. Next scientifically valid step

The next admissible work is **new-program specification only** for an upstream
measurement/substrate adequacy study.

Before any fresh execution it must freeze:

1. the exact scientific question;
2. why the study is upstream rather than CPRM rescue;
3. endpoint-performance measurement candidates justified independently of the
   CPRM-1 cohort;
4. task/substrate difficulty controls;
5. fresh cohorts disjoint from KCL protected, ACO spent and CPRM-1 spent seeds;
6. falsification gates including the possibility that the current substrate is
   simply endpoint-saturated;
7. a finite STOP roadmap;
8. zero-science QA.

No new scientific execution is authorized by this convergence review.

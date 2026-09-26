# Continual Loss Response Modeling (CLRM)

Status: **CLRM-0 PASS / CLOSED — CLRM-1 DESIGN ONLY AUTHORIZED**

Branch: `research/continual-loss-response`

Parent closure:

```text
research/measurement-substrate-adequacy
64138ab9cb09dcb56a387d3b1f500063eff8302d

MSA PROGRAM = FORMALLY CONVERGED / CLOSED
MSA-3 = REPLICATION_CONFIRMED
replicated finding = ACCURACY_COARSE_LOSS_INFORMATIVE
```

CLRM is a new response-modeling program opened after MSA convergence.

It is **not CPRM-2** and does not rescue the CPRM-1 frozen target.

CLRM-0 contains specification/governance only.

No fresh seed cohort, scientific collection, predictor fitting, feature
selection, hyperparameter tuning, controller, or KCL-7 execution is authorized.

Canonical CLRM-0 documents:

- `ORIGIN.md`
- `EVIDENCE_INHERITANCE.md`
- `RESEARCH_QUESTION.md`
- `RESPONSE_VECTOR_CONTRACT.md`
- `ACCURACY_SENTINEL_CONTRACT.md`
- `ELIGIBLE_POPULATION_CONTRACT.md`
- `BASELINE_CONTRACT.md`
- `PARTITION_CONTRACT.md`
- `QUALIFICATION_GATES.md`
- `FRESHNESS_EXCLUSIONS.md`
- `ROADMAP.md`
- `LINEAGE.md`

The next admissible transition after CLRM-0 PASS is design/preregistration of
CLRM-1 measurement-support qualification. CLRM-1 is still a no-predictor
milestone.


## CLRM-0 formal closure

Independent static zero-science specification QA is **PASS / CLOSED**.

Canonical closure: `CLRM0_SPEC_QA.md`.

```text
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS

CLRM-1 protocol design          AUTHORIZED
CLRM-1 fresh execution         NOT AUTHORIZED
predictor fitting              NOT AUTHORIZED
controller                     CLOSED
KCL-7                          CLOSED
```


Canonical zero-science Actions confirmation:

```text
workflow = 36057035870
4/4 tests PASS
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS
```


## CLRM-1 preregistration status

CLRM-1 Loss Response Support Qualification is preregistered and its
zero-science preflight is **PASS / CLOSED**.

```text
Role-S seeds                   72 FROZEN
boundaries                     216 expected
policy response vectors        648 expected
direct loss channels           6 FROZEN
reliability repeats            6 FROZEN
Execution Lock SHA-256
39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e

CLRM1_ZERO_SCIENCE_PREFLIGHT_PASS
```

Fresh CLRM-1 science remains blocked pending independent exact-lock
verification. CLRM-2 design and predictor fitting remain closed.


## CLRM-1 independent lock verification

Independent exact-lock verification is **PASS / CLOSED**.

Canonical closure: `CLRM1_EXECUTION_LOCK_VERIFICATION.md`.

```text
CLRM1_EXECUTION_LOCK_VERIFICATION_PASS

lock =
39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e

72-seed Role-S collection      ELIGIBLE TO OPEN
fresh Role-S science           NOT STARTED

CLRM-2 design                  CLOSED UNTIL CLRM-1 PASS
predictor training             CLOSED
controller                     CLOSED
```


## CLRM-1 formal result

CLRM-1 is **PASS / CLOSED**.

```text
PASS_LOSS_RESPONSE_SUPPORT
ALL_SIX_DIRECT_LOSS_CHANNELS_NONDEGENERATE
```

Canonical closure: `CLRM1_FORMAL_CLOSURE.md`.

```text
72/72 Role-S seeds
216/216 boundaries
648/648 A/B/C response vectors
6/6 deterministic repeats exact

A.current_loss       3/3 stages
A.prior_mean_loss    3/3 stages
B.current_loss       2/3 stages
B.prior_mean_loss    3/3 stages
C.current_loss       2/3 stages
C.prior_mean_loss    3/3 stages
```

Role-S is now spent support evidence.

CLRM-2 **design only** is authorized. No CLRM-2 fresh execution or predictor
training is authorized yet.


## CLRM-2 zero-science training preflight

CLRM2-A Training Lock preflight is **PASS / CLOSED**.

```text
CLRM2_ZERO_SCIENCE_PREFLIGHT_PASS
Training Lock =
e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5

D-train      NOT AUTHORIZED
predictor    NOT AUTHORIZED
D-val        SEALED / PROHIBITED
```

Next: independent static verification of the exact Training Lock.


## CLRM2-A Training Lock verification

Independent Training Lock verification is **PASS / CLOSED**.

```text
CLRM2_TRAINING_LOCK_VERIFICATION_PASS

Training Lock =
e29873b3fd384f95c1d65490e259055b8c03545ea6a99a8b839f0d51f13619b5

Phase A D-train collection/fitting  ELIGIBLE TO OPEN
D-val                               SEALED / PROHIBITED
Gate-2 adjudication                 PROHIBITED
```

Canonical closure:
`CLRM2_TRAINING_LOCK_VERIFICATION.md`.

No fresh CLRM-2 seed has been executed and no predictor has been fitted yet.


## CLRM2-A Phase A formal closure

CLRM2-A D-train discovery is **PASS / CLOSED**.

```text
canonical workflow = 36254847891
D-train            = 160 seeds / 480 boundaries / integrity PASS
candidate           = RBF-KRR-v1
gamma               = 0.02
lambda              = 1.0
strongest baseline  = B2

D-train SHA-256 =
8e7e38357f2117e76337b454f40debeb7741f1a8f3993a61add9f50c490d1b28

candidate SHA-256 =
310bd9805cb028691826722c8cf5ee365e85d549872f2f3e898d8e348cef2a83
```

Canonical closure: `CLRM2_PHASE_A_FORMAL_CLOSURE.md`.

```text
D-train workflow       RETIRED / HARD-DISABLED
D-train                SPENT
candidate package      FROZEN
strongest baseline     FROZEN = B2
D-val                  SEALED / NOT EXECUTED
Gate-2                 NOT CALLED
```

The candidate's D-train selection is not a Gate-2 result and does not establish
predictive qualification.

Next authorized transition: create and independently verify the exact
`CLRM2-B Validation Lock`. Only after that verification may the sealed
80-seed D-val cohort execute once.

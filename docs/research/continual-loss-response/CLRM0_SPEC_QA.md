# CLRM-0 Zero-Science Specification QA

Status: **PASS / CLOSED**

Date: 2026-09-25

## Canonical program identity

```text
Program: CLRM — Continual Loss Response Modeling
Branch: research/continual-loss-response
Parent MSA closure:
64138ab9cb09dcb56a387d3b1f500063eff8302d
```

Independent GitHub compare confirms:

```text
merge base = 64138ab9cb09dcb56a387d3b1f500063eff8302d
ahead      = 3
behind     = 0
changed files = 17
```

All 17 changed files are newly added CLRM specification/QA files. No inherited
MSA/CPRM/KCL scientific implementation was modified.

## QA method

The canonical closure uses an independent static audit of the exact GitHub
branch tree and frozen documents.

No scientific runner is invoked.
No model is trained.
No fresh seed manifest is created or consumed.
No scientific outcome is generated.

GitHub Actions attempt `36056186547` failed before tests because `pytest`
was absent.

Recovery attempt `36056366585` experienced a checkout stall and is
non-canonical.

The bounded-depth recovery run `36057035870` completed successfully and is
the canonical Actions confirmation of this static audit:

```text
4/4 tests PASS
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS

QA JSON SHA-256:
74710fb9c8fe5422f33749664996ecc47f5e32c0a4f11d01c087f2e0e6d4d257

artifact ID:
10832548397

artifact ZIP SHA-256:
59776fe2373ead0fb9d3d1f790ec86643879fb7252cd38dd0f65b8f0e9af4659
```

Every zero-science flag in the canonical run is false.

## Frozen research object

Primary response vector for each policy `a ∈ {A,B,C}`:

```text
R(X,a) = [
  L_current_end(X,a),
  L_prior_mean_end(X,a)
]
```

Direct channels:

```text
A.current_loss
A.prior_mean_loss
B.current_loss
B.prior_mean_loss
C.current_loss
C.prior_mean_loss
```

Derived contrasts:

```text
D_B(X) = R(X,B) - R(X,A)
D_C(X) = R(X,C) - R(X,A)
```

This is prospectively redefined in CE-loss space and is not the CPRM vector
with `final_current_accuracy` removed.

The primary vector does not inherit the CPRM target variables
`plasticity_auc`, `prior_task_retention`, or `worst_prior_accuracy`.

## Accuracy role

Frozen sentinel only:

```text
S_acc(X,a) = [
  current_terminal_accuracy,
  min_prior_terminal_accuracy
]
```

Accuracy is not a predictor target and does not enter baseline superiority or
point-calibration qualification.

No 0.95 correctness threshold is imported into CLRM-0.

## Population

Frozen primary population:

```text
ALL prospectively eligible matched boundaries

T1 → T2
T2 → T3
T3 → T4
```

Seed is the grouping unit. All boundaries from one seed remain in one data
role.

Difficulty mutation is not authorized.

## Baselines

Frozen minimum family:

```text
B0 = policy-global mean
B1 = policy-by-stage mean
B2 = ridge state-response baseline
```

B2 regularization grid:

```text
{1e-6, 1e-4, 1e-2, 1, 100}
```

All baseline selection/tuning is training-only.

## Data roles

Frozen separation:

```text
Role S       = support qualification only
Role D-train = predictive development
Role D-val   = sealed validation
Role R       = independent replication
```

Role S becomes spent before any predictor study.

No seed may cross roles.

## Predictive qualification contract

Baseline superiority requires:

```text
relative_gain >= 0.10

whole-seed paired bootstrap
95% upper CI(macro_ratio) < 1.0

every direct channel:
ratio_j <= 1.05
```

Point calibration requires every direct channel:

```text
0.80 <= beta_j <= 1.20
abs(alpha_j) / MAE_baseline_j <= 0.10
```

These are program-level frozen Gate-2 contracts; they do not authorize
predictor fitting yet.

## Freshness exclusions

Frozen exclusions include:

- all historical KCL scientific seeds;
- protected KCL confirmatory cohort;
- ACO-1 manifest
  `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`;
- CPRM-1 manifest
  `d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3`;
- MSA-1 manifest
  `e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347`;
- MSA-3 manifest
  `5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8`.

CLRM-0 itself has no fresh seed manifest.

## Finite roadmap

```text
CLRM-0  Specification Foundation
        ↓
CLRM-1  Loss Response Support Qualification
        no predictor
        ↓ only on PASS_LOSS_RESPONSE_SUPPORT
CLRM-2  Predictive Discovery
        ↓ only on qualified prediction
CLRM-3  Independent Fresh Replication
        ↓ only on replication PASS
CLRM-4  Downstream Decision Governance
```

Mandatory convergence review follows CLRM-1 NEGATIVE/STOP, CLRM-2 failure, or
CLRM-3 replication failure.

No CLRM-2.1/2.2 rescue ladder is authorized.

## Zero-science assertions

```text
experiments/clrm              ABSENT
CLRM fresh seed manifest      ABSENT
CLRM scientific result        ABSENT
predictor implementation      ABSENT

fresh_seed_execution_attempted = false
scientific_outcome_generated   = false
predictor_fitting_performed    = false
controller_execution_performed = false
```

## Formal decision

```text
CLRM-0                         PASS / CLOSED
CLRM PROGRAM                   OPEN
TARGET CONTRACT                FROZEN
ACCURACY ROLE                  SENTINEL ONLY
POPULATION CONTRACT            FROZEN
BASELINE CONTRACT              FROZEN
PARTITION CONTRACT             FROZEN
PREDICTIVE GATES               FROZEN
FRESHNESS EXCLUSIONS           FROZEN
FINITE ROADMAP                 FROZEN

CLRM-1 DESIGN                  AUTHORIZED
CLRM-1 FRESH EXECUTION         NOT AUTHORIZED
PREDICTOR TRAINING             NOT AUTHORIZED
CONTROLLER                     CLOSED
KCL-7                          CLOSED
```

The next admissible action is design/preregistration of CLRM-1 loss-response
support qualification. It must still be a no-predictor study.

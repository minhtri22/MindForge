# CPRM-1 — Fresh Response Support & Geometry Qualification Protocol

Status: **PREREGISTERED / SCIENTIFIC EXECUTION LOCKED**

Program: Continual Policy Response Modeling (CPRM)

Milestone: CPRM-1

CPRM-0 prerequisite:

```text
CPRM0_ZERO_SCIENCE_SPEC_QA_PASS
research/continual-policy-response@43ddcd12b679024d771abeb61d321fb7c731a9f4
```

## 1. Scientific question

CPRM-1 asks:

> On a fresh, prospectively defined all-boundary cohort, do the frozen
> policy-specific continuous response vector and A-relative policy contrasts
> have sufficient measurement integrity, support, reproducibility and
> non-degenerate geometry to justify a later predictive study?

CPRM-1 does **not** fit or qualify a predictor.

It does not select an online action and does not implement a controller.

## 2. Canonical policies

The exact inherited policies are:

```text
A = A_CARRY_ALL
B = B_RESET_ALL
C = C_CARRY_STEP_RESET_MOMENTS
```

Policy semantics are inherited from
`experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py`.

No policy mutation is allowed in CPRM-1.

## 3. Exact measurement / extraction contract

For each eligible boundary `X` and policy `a ∈ {A,B,C}`:

```text
Y(X,a) = [
  plasticity_auc,
  final_current_accuracy,
  prior_task_retention,
  worst_prior_accuracy
]
```

### 3.1 plasticity_auc

Use the canonical KCL stage learning curve at checkpoints:

```text
0,25,50,75,100,125,150,175,200,225,250
```

Accuracy is evaluated on the next/current task at each checkpoint.

Use the existing normalized trapezoidal AUC:

```text
AUC = trapezoid_area(accuracy vs step) / 250
```

This reuses `kcl655.normalized_auc` semantics.

Natural measurement resolution:

```text
r_auc = 1/480
```

because benchmark accuracy is quantized in units of `1/24` and an endpoint
checkpoint has normalized trapezoid weight `0.05`.

### 3.2 final_current_accuracy

Use the canonical current-task accuracy at step `250`.

Natural resolution:

```text
r_final = 1/24
```

### 3.3 prior_task_retention

After the next-task counterfactual training finishes, evaluate the resulting
policy model on every task observed before the boundary action.

Let those accuracies be:

```text
R_prior = [acc(T1), ..., acc(Tk)]
```

where `k = boundary_index ∈ {1,2,3}`.

Define:

```text
prior_task_retention = mean(R_prior)
```

This is exactly the historical KCL retention definition.

Stage-specific natural resolution:

```text
r_retention(k) = 1 / (24*k)
```

### 3.4 worst_prior_accuracy

Using the **same** post-counterfactual prior-task accuracy vector:

```text
worst_prior_accuracy = min(R_prior)
```

Natural resolution:

```text
r_worst = 1/24
```

No additional training, replay or intervention is introduced to obtain this
quantity.

### 3.5 A-relative contrasts

For every component `j`:

```text
C_B,j(X) = Y_j(X,B) - Y_j(X,A)
C_C,j(X) = Y_j(X,C) - Y_j(X,A)
```

Contrasts retain the natural resolution of their component.

## 4. Fresh cohort

CPRM-1 uses exactly 60 fresh scientific seeds:

```text
814887,863137,944290,493874,333929,674723,
629896,563470,452971,659444,563718,222175,
332624,957861,506630,735777,693319,612663,
330455,271971,396729,463395,650240,394015,
596743,717212,700981,787278,430901,538687,
927431,885588,748598,724163,573227,689490,
439438,774009,639141,850216,427422,235913,
355296,574310,665271,791304,909129,757353,
834226,280648,906973,523942,480884,388898,
404202,430651,508646,398464,915507,458769
```

Canonical SHA-256 over the exact comma-joined decimal sequence:

```text
d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3
```

The committed list is the canonical provenance.

No replacement seed may be introduced after scientific outcome generation.

## 5. Freshness / collision exclusion

Before execution, the 60-seed manifest must be disjoint from:

1. historical KCL scientific seeds;
2. the protected KCL confirmatory cohort;
3. the 40 spent ACO-1 seeds;
4. any previous CPRM scientific cohort.

The preflight collision auditor must scan historical KCL source/docs and the
root lineage in addition to explicit protected/spent lists.

Any collision before scientific execution requires a new preregistered cohort
and a new lock.

## 6. Exact population

For every fresh seed, the primary population is all three canonical boundaries:

```text
boundary 1: after T1, before T2
boundary 2: after T2, before T3
boundary 3: after T3, before T4
```

Expected primary population:

```text
60 seeds × 3 boundaries = 180 matched boundaries
180 boundaries × 3 policies = 540 response vectors
```

Eligibility is determined before post-action outcomes.

No boundary may be excluded because of hard label, policy benefit/harm,
threshold proximity, response magnitude or contrast sign.

## 7. Support gate

Scientific adjudication requires:

```text
unique fresh seeds             = 60
eligible boundaries per seed   = 3
eligible boundaries total      = 180
boundaries at stage 1          = 60
boundaries at stage 2          = 60
boundaries at stage 3          = 60
policy responses per boundary  = exactly A,B,C
response vectors total         = 540
```

No partial-complete scientific inference is allowed.

Persistent failure of one frozen seed is a support/integrity STOP, not
authorization to substitute a seed.

## 8. Measurement integrity gates

Every boundary must satisfy:

1. all policy forks begin from identical model state;
2. boundary policy application does not mutate model parameters;
3. exact replay match rate is `1.0`;
4. all four response values are finite;
5. every response lies in `[0,1]`;
6. `worst_prior_accuracy <= prior_task_retention`;
7. at boundary 1, `worst_prior_accuracy == prior_task_retention`;
8. policy set is exactly A/B/C.

Any violation yields `STOP_INTEGRITY_OR_SUPPORT`.

## 9. Measurement reliability gate

The first six frozen fresh seeds are preregistered reliability repeats:

```text
814887,863137,944290,493874,333929,674723
```

For these seeds, the complete CPRM response extraction is run a second time
under the same locked source/runtime.

Required:

```text
numeric response max_abs_diff = 0
boundary/policy/integrity structure identical
```

The repeat is an exact deterministic reliability check, not a second
independent sample.

Failure yields `STOP_INTEGRITY_OR_SUPPORT`.

## 10. Response non-degeneracy gate

For each response component, policy and stage cell (60 observations):

```text
unique_count >= 4
p90 - p10 >= 2 × natural_resolution(component, stage)
```

A response component qualifies iff:

```text
qualified policy×stage cells >= 6 of 9
qualified stages             >= 2 of 3
qualified policies           >= 2 of 3
```

All four primary response components must qualify.

This is a **joint component contract**. CPRM-1 may not promote only the easiest
component after seeing outcomes.

## 11. Contrast-support gate

For each `B-A` and `C-A` contrast component within each stage, magnitude
geometry qualifies iff:

```text
unique_count >= 4
p90 - p10 >= 2 × natural_resolution
fraction(|contrast| >= natural_resolution) >= 0.20
```

A contrast component has magnitude support iff at least `2 of 3` stage cells
qualify.

Directional support for a contrast component requires, pooled over all 180
boundaries:

```text
fraction(contrast >= +resolution) >= 0.10
fraction(contrast <= -resolution) >= 0.10
```

and each sign must appear in at least two stages with at least three seeds in
each represented stage.

Each contrast family (`B-A`, `C-A`) qualifies iff:

```text
magnitude-supported components >= 2 of 4
direction-supported components >= 1 of 4
```

Contrast qualification is a geometry prerequisite only. It does not select a
CPRM-2 target or controller.

## 12. One-shot adjudication

The one-shot adjudicator receives only the complete frozen collection.

If support, integrity or reliability fails:

```text
CPRM-1 = STOP
STOP_INTEGRITY_OR_SUPPORT
```

If those pass but any primary response component or either contrast family
fails its frozen geometry contract:

```text
CPRM-1 = NEGATIVE
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
```

Only if every gate passes:

```text
CPRM-1 = PASS
PASS_RESPONSE_SUPPORT
```

No threshold or gate may be relaxed after outcome inspection.

## 13. Scientific interpretation

PASS means only that the frozen continuous response object has enough support,
reliability and geometry to justify designing CPRM-2 prospective
predictability. It does not mean responses are predictable.

NEGATIVE means the frozen response/contrast geometry does not support the
planned predictive program under this design.

STOP means integrity/support/reliability prerequisites failed, so geometry
inference is not admissible.

## 14. Technical retry policy

Collection retry is allowed only for a technical failure before a complete,
valid 180-boundary collection exists.

Rules:

- retry exact same seed under exact same lock;
- do not replace a seed;
- do not inspect scientific geometry before retry;
- do not change source/protocol/dependencies/gates;
- once a complete valid collection exists, collection must not be rerun.

Adjudication:

- exactly one valid one-shot adjudication;
- technical retry only if no valid formal result exists;
- same complete input and same lock;
- once a valid formal result exists, adjudication must not be rerun.

Any scientific-source, protocol, seed, dependency or gate change invalidates the
execution lock and requires a new zero-science preflight.

## 15. Execution lock / authorization

Fresh execution is prohibited until:

1. CPRM-1 implementation and synthetic tests exist;
2. `CPRM1_EXECUTION_LOCK.json` binds exact protocol/source/runtime/seed manifest;
3. zero-science preflight PASSes under that lock;
4. an independent execution-lock verification is later completed.

The current protocol does not authorize fresh execution merely by being
committed.

## 16. CPRM-2 transition

CPRM-2 protocol design is authorized only if the canonical CPRM-1 one-shot
result is:

```text
PASS
PASS_RESPONSE_SUPPORT
```

Otherwise a formal convergence review is required before further predictive
work.

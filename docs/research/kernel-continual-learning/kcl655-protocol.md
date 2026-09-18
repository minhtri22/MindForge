# MindForge Kernel Continual Learning — KCL-6.5.5 AdamW Boundary Policy A/B/C Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.5 SCIENTIFIC EXECUTION**

## 1. Trigger and upstream evidence

KCL-6.5.4 closed:

```
PASS
MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT
```

with the POST-T1 model held fixed.

Frozen findings:

- carrying AdamW `step` alone preserved T4 acquisition;
- carrying `exp_avg` alone was sufficient for failure;
- carrying `exp_avg_sq` alone was sufficient for failure;
- full reset `O000` reached T4 = 1.0;
- carry-step/reset-both-moments `O100` reached T4 = 1.0;
- carry-all `O111` reproduced T4 = 0.91667.

KCL-6.5.5 now tests actual task-boundary policies on the full continual-learning trajectory rather than one isolated transition.

## 2. Scientific question

Can task-boundary treatment of AdamW state improve future-task plasticity **without sacrificing prior-task retention** when the previously validated targeted-clarification reconstructive memory mechanism is active?

Compare three policies:

### A — CARRY_ALL

Carry the full AdamW state across every task boundary.

### B — RESET_ALL

At every boundary, create a fresh AdamW optimizer on the unchanged model:

- step resets;
- exp_avg resets;
- exp_avg_sq resets.

### C — CARRY_STEP_RESET_MOMENTS

At every boundary:

- preserve exact optimizer `step`;
- zero `exp_avg`;
- zero `exp_avg_sq`.

No model parameters are reset in any arm.

## 3. Memory/replay policy is fixed

All A/B/C arms use exactly the KCL-6.4/KCL-6.5 E policy:

```
fuzzy memory
→ targeted same-task clarification when selected
→ exact schema reactivation
→ exact replay
```

Frozen memory details:

- width-4 offset bucket;
- one-subsequent-task decay;
- 15 current + 1 replay;
- batch 16;
- replay fraction 6.25%;
- no clarification cue enters gradient;
- no clarification cue is retained as raw episodic replay.

The memory policy is **not** an experimental variable in KCL-6.5.5.

## 4. Task stream

Exactly:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

## 5. Boundary timing

T1 is trained once.

After completing T1, the common post-T1 model/optimizer state is cloned into A/B/C, then each boundary policy is applied before T2.

After T2 and T3, each arm applies its own policy before the next task.

There is no post-T4 optimizer intervention because no T5 is trained.

Boundary policy therefore executes exactly three times per arm:

```
after T1
after T2
after T3
```

## 6. Frozen model / optimizer hyperparameters

Exactly prior diagnostic kernel:

- vocab 96
- d_model 16
- heads 2
- layers 1
- context 2
- FF multiplier 4
- dropout 0
- AdamW
- learning rate 3e-3
- weight decay 0
- 250 steps/task
- deterministic CPU execution.

Optimizer hyperparameters may not change between policies.

## 7. Matched training data

Within each seed, A/B/C must receive exactly the same:

- current-task minibatch indices;
- replay source sequence;
- replay rank sequence;
- targeted clarification events;
- exact replay observations.

The three arms are trained lockstep from shared sampled current/replay observations.

Only optimizer boundary state differs.

Any training-data divergence => REVISE.

## 8. Independent primary cohort

Use exactly 20 fresh seeds:

```
9595
9797
9999
10201
10403
10605
10807
11009
11211
11413
11615
11817
12019
12221
12423
12625
12827
13029
13231
13433
```

These seeds are disjoint from all earlier KCL scientific cohorts.

No seed replacement, dropping, selective rerun, or outcome-conditioned extension.

## 9. Diagnostic sentinel

Seed:

```
9393
```

is run separately from the fresh cohort.

It is **not** used in bootstrap population inference.

Sentinel A must reproduce canonical KCL-6.5.1 E:

```
A T4 = 0.75
A final mean prior = 0.5000000049670538
```

within tolerance `1e-9`.

Failure => REVISE.

The sentinel asks whether B/C repair the known acquisition anomaly under the full CL trajectory.

## 10. Current-task acquisition curves

For T2, T3 and T4, record current-task accuracy/loss at:

```
0,25,50,75,100,125,150,175,200,225,250
```

All 250 updates execute.

For each stage report:

- final current-task accuracy;
- maximum accuracy;
- first checkpoint reaching >=0.95;
- normalized accuracy AUC.

Normalized AUC is trapezoidal area over steps 0..250 divided by 250.

For each seed/policy:

```
plasticity_AUC =
mean(AUC_T2, AUC_T3, AUC_T4)
```

This is the primary plasticity endpoint.

## 11. Absolute current-task gate

For a candidate policy to qualify:

```
final current-task accuracy >= 0.95
```

for T2, T3 and T4 on every one of the 20 fresh seeds.

The sentinel is evaluated separately.

## 12. Retention endpoint

After T4, define:

```
retention =
mean(final T1, final T2, final T3 accuracy)
```

Also report:

- worst prior-task accuracy;
- all-task mean accuracy.

Retention is the primary stability endpoint.

## 13. Bootstrap inference

Use paired nonparametric bootstrap over the 20 fresh seeds.

Frozen settings:

```
resamples = 20000
bootstrap RNG seed = 655655
95% two-sided percentile CI
```

Primary paired contrasts:

```
DeltaPlasticity_BA = AUC_B - AUC_A
DeltaPlasticity_CA = AUC_C - AUC_A
DeltaPlasticity_CB = AUC_C - AUC_B

DeltaRetention_BA = R_B - R_A
DeltaRetention_CA = R_C - R_A
DeltaRetention_CB = R_C - R_B
```

No alternative CI method may be selected after outcome inspection.

## 14. Practical margins

Retention non-inferiority margin:

```
M_R = 1/24 = 0.0416666667
```

Plasticity equivalence margin for B-vs-C:

```
M_P = 0.01
```

The AUC margin corresponds to one percentage point of average normalized acquisition accuracy.

## 15. Policy qualification against carry-all A

For policy `P ∈ {B,C}`, define:

### Plasticity improvement

```
CI_lower(DeltaPlasticity_PA) > 0
```

### Retention non-inferiority

```
CI_lower(DeltaRetention_PA) > -M_R
```

### Absolute acquisition

Policy P passes the final current-task >=0.95 gate at T2/T3/T4 for all 20 fresh seeds.

### Sentinel repair

```
sentinel P T4 >= 0.95
```

Policy P is **QUALIFIED** iff all four conditions pass.

## 16. B-vs-C interpretation

If both B and C qualify:

### C_STEP_CARRY_ADDS_VALUE

If:

```
CI_lower(DeltaPlasticity_CB) > 0
and
CI_lower(DeltaRetention_CB) > -M_R
```

### B_RESET_ALL_ADDS_VALUE

If:

```
CI_upper(DeltaPlasticity_CB) < 0
and
CI_upper(DeltaRetention_CB) < M_R
```

### B_C_PRACTICALLY_EQUIVALENT

If both:

```
CI(DeltaPlasticity_CB) lies within [-M_P, +M_P]
CI(DeltaRetention_CB) lies within [-M_R, +M_R]
```

### B_C_NO_CLEAR_WINNER

Any other case where both qualify.

## 17. Primary milestone classification

### Only C qualifies

```
PASS
C_STEP_CARRY_RESET_MOMENTS_POLICY_VALIDATED
```

### Only B qualifies

```
PASS
B_RESET_ALL_POLICY_VALIDATED
```

### Both qualify

```
PASS
B_AND_C_BOUNDARY_POLICIES_VALIDATED
```

with the B-vs-C secondary classification.

### Neither qualifies because retention non-inferiority fails

```
FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

when at least one intervention improves plasticity but neither preserves retention.

### Neither qualifies because no reproducible plasticity improvement

```
NEGATIVE
NO_BOUNDARY_POLICY_PLASTICITY_ADVANTAGE
```

### Any integrity failure

```
REVISE
BOUNDARY_POLICY_ABC_INVALID
```

## 18. Memory/query integrity

Every arm/seed must preserve:

- exact replay match rate = 1.0 at T2/T3/T4;
- query schedule:
  - T2 = 0
  - T3 = 1
  - T4 = 2
  - total = 3;
- final memory state:
  - fuzzy, fuzzy, fuzzy, exact;
- final logical replay storage = 143 bytes.

Because the memory representation is shared/matched, all policies must have identical query/replay accounting.

## 19. Optimizer-policy integrity

### A

Boundary optimizer state is unchanged.

### B

Immediately after each boundary:

```
optimizer per-parameter state count = 0
```

### C

Immediately after each boundary:

- optimizer state remains allocated for every trained parameter;
- all `exp_avg = 0`;
- all `exp_avg_sq = 0`;
- step values equal the pre-boundary step values.

No policy may alter model parameters at the boundary.

## 20. No tuning rule

After protocol freeze do not change:

- policies A/B/C;
- seed cohort;
- sentinel;
- task order;
- replay/query mechanism;
- optimizer hyperparameters;
- stage steps;
- AUC definition;
- bootstrap seed/resamples;
- retention/plasticity margins;
- qualification rules.

No fourth policy may be added after observing outcome.

## 21. Scope exclusions

KCL-6.5.5 does not yet:

- implement an adaptive coordinator;
- choose task-specific moment decay values;
- test model scale;
- open KCL-7;
- open reasoning.

It only validates fixed boundary policies.

## 22. Required artifacts

```
experiments/kernel_cl/kcl655_adamw_boundary_policy_abc.py
experiments/kernel_cl/results/kcl655_summary.json
tests/test_kernel_cl_kcl655.py
docs/research/kernel-continual-learning/kcl655-paper.md
.github/workflows/kernel-cl-kcl655.yml
```

## 23. Closure

KCL-6.5.5 closes only after:

- protocol commit before execution;
- focused tests PASS;
- one official sentinel + N=20 A/B/C run;
- raw evidence preserved;
- paper written;
- append-only Lineage update.

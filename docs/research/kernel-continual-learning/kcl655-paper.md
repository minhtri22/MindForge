# KCL-6.5.5 — AdamW Boundary Policy A/B/C

## Abstract

KCL-6.5.4 showed that both AdamW first-moment and second-moment history can independently contribute to poor future plasticity when paired with a learned model state, while optimizer step/age alone did not reproduce the isolated T4 failure. KCL-6.5.5 therefore tests three fixed task-boundary policies on the full four-task continual-learning stream while holding the targeted-clarification reconstructive memory mechanism constant.

The policies are:

- A — carry all AdamW state;
- B — reset all AdamW state at every task boundary;
- C — carry optimizer step while resetting both `exp_avg` and `exp_avg_sq`.

A diagnostic seed 9393 is kept separate from population inference, while the primary cohort contains 20 fresh paired seeds.

The result does not validate either boundary intervention as a fixed kernel policy.

C produces a large and statistically clear plasticity improvement over A:

```
mean Delta AUC(C-A) = +0.06094
95% paired bootstrap CI = [+0.03111, +0.09774]
```

but final prior-task retention decreases:

```
mean Delta retention(C-A) = -0.04514
95% CI = [-0.07708, -0.01319]
```

The lower confidence bound crosses the frozen non-inferiority margin `-1/24 = -0.04167`. C also fails the all-seed absolute current-task gate on 2/20 fresh seeds and does not repair the known seed-9393 anomaly: sentinel T4 remains 91.67%.

B preserves retention relative to A:

```
mean Delta retention(B-A) = +0.01111
95% CI = [-0.02014, +0.03889]
```

and repairs sentinel 9393 to T4 = 100%, but plasticity AUC is reproducibly worse than A:

```
mean Delta AUC(B-A) = -0.03396
95% CI = [-0.05993, -0.00333]
```

and B passes the strict fresh-seed acquisition gate on only 16/20 seeds.

Thus no fixed boundary policy satisfies the joint plasticity-plus-retention contract.

The canonical script emitted `NEGATIVE / NO_BOUNDARY_POLICY_PLASTICITY_ADVANTAGE` because of an implementation error in the final decision predicate. The frozen protocol requires the only plasticity-improving intervention to preserve retention; C does not. B's retention preservation cannot compensate for the fact that B does not improve plasticity. No scientific rerun was performed. The protocol-adjudicated verdict is therefore:

```
KCL-6.5.5 = FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

The experiment changes the architectural conclusion: the kernel should not adopt a fixed global optimizer reset rule. The evidence now supports a genuinely adaptive task-boundary coordinator that decides when and how optimizer moment state should be carried based on plasticity/stability state.

## 1. Upstream chain

KCL-6.5.3:

```
MODEL_OPTIMIZER_INTERACTION_ONLY
```

showed that future plasticity failure can emerge from the paired model/optimizer state even when either state alone remains compatible with learning.

KCL-6.5.4:

```
MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT
```

showed that:

- `exp_avg` history can independently induce failure;
- `exp_avg_sq` history can independently induce failure;
- optimizer step alone does not.

The strongest isolated candidate was:

```
carry step
reset exp_avg
reset exp_avg_sq
```

KCL-6.5.5 asks whether that isolated candidate remains useful when applied repeatedly over an actual continual-learning trajectory.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl655-protocol.md`

Protocol commit:

`ce17e0bef0932a78d7d38c42f7ad4f153750c5d5`

Protocol SHA-256:

`5eff537df64f9d2cbce849a2340904027dd192742d2574dc39b6fb9e8adf581a`

Scientific source:

`b5edc36d30202ee9b19e9634e328e6eda109f32d`

No policy, seed, margin, replay rule, or statistical threshold changed after outcome inspection.

## 3. Controlled variable

All three arms use the same model architecture, task order, replay budget, current-task samples, replay source/rank schedule, and targeted-clarification memory mechanism.

Every training step uses the same:

```
15 current samples
+
1 exact replay sample
```

for A/B/C.

The only experimental variable is optimizer treatment at task boundaries.

## 4. Boundary policies

### A — CARRY_ALL

Carry:

```
step
exp_avg
exp_avg_sq
```

unchanged.

### B — RESET_ALL

At each boundary construct fresh AdamW state:

```
state = empty
```

which initializes on the next update.

### C — CARRY_STEP_RESET_MOMENTS

At each boundary:

```
step preserved
exp_avg = 0
exp_avg_sq = 0
```

Observed carried step values behave as intended:

- after T1: 250;
- after T2: 500;
- after T3: 750.

All boundary operations leave model parameters unchanged.

## 5. Memory/query mechanism remains valid

All arms share the frozen E memory lifecycle:

```
exact
→ decay to fuzzy
→ targeted clarification
→ exact reactivation
→ exact replay
```

Per trajectory:

```
T2 queries = 0
T3 queries = 1
T4 queries = 2
total = 3
```

Exact replay match rate remains 1.0.

Final memory state remains:

```
[fuzzy, fuzzy, fuzzy, exact]
```

with final logical storage:

```
143 bytes
```

Thus KCL-6.5.5 does not trade optimizer-policy effects against a different memory system.

## 6. Diagnostic sentinel 9393

A must reproduce the canonical KCL-6.5.1 E failure.

Observed A:

```
T4 = 0.7500
mean prior = 0.50000000497
```

Exact reproduction passes.

### Sentinel B

```
T4 = 1.0000
mean prior = 0.55556
```

B repairs the known T4 anomaly.

### Sentinel C

```
T4 = 0.91667
mean prior = 0.43056
```

C does **not** repair the known anomaly.

This is a critical generalization failure of the isolated KCL-6.5.4 O100 result.

O100 was successful for one POST-T1→T4 boundary. Reapplying carry-step/reset-moments across the entire T1→T2→T3 trajectory produces a different joint state and does not preserve the isolated repair.

## 7. Fresh independent cohort

Primary seeds:

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

N = 20.

Seed 9393 is excluded from primary bootstrap inference.

## 8. Plasticity endpoint

Primary plasticity metric:

```
plasticity AUC =
mean(normalized current-task acquisition AUC over T2,T3,T4)
```

Aggregate:

```
A carry-all                    = 0.81594
B reset-all                    = 0.78198
C carry-step/reset-moments     = 0.87688
```

### B versus A

```
mean Delta = -0.03396
95% CI = [-0.05993, -0.00333]
```

B is reproducibly slower/worse in acquisition AUC than A.

### C versus A

```
mean Delta = +0.06094
95% CI = [+0.03111, +0.09774]
```

C provides a clear plasticity improvement.

### C versus B

```
mean Delta = +0.09490
95% CI = [+0.07222, +0.12128]
```

C has substantially better acquisition dynamics than reset-all.

## 9. Final current-task robustness

Fresh-cohort T4 mean:

```
A = 0.87292
B = 0.92292
C = 0.98333
```

Strict all-stage gate pass counts:

```
A = 17/20
B = 16/20
C = 18/20
```

C is clearly the most robust of the three on final T4 average, but the pre-registered contract requires every fresh seed to pass T2/T3/T4 final >=0.95.

### A failing fresh seeds

```
9797:  T4 = 0.04167
9999:  T4 = 0.04167
12019: T4 = 0.37500
```

### B failing fresh seeds

```
9797:  T4 = 0.62500
11009: T4 = 0.91667
11615: T4 = 0.87500
12019: T4 = 0.08333
```

### C failing fresh seeds

```
9797:  T4 = 0.79167
11615: T4 = 0.91667
```

All T2/T3 endpoints in these listed failures are 1.0; the failures are concentrated at T4.

Therefore C reduces but does not eliminate the long-horizon acquisition instability.

## 10. Retention endpoint

Final mean prior-task accuracy:

```
A = 0.65000
B = 0.66111
C = 0.60486
```

### B versus A

```
mean Delta = +0.01111
95% CI = [-0.02014, +0.03889]
```

The lower bound is safely above the frozen non-inferiority limit:

```
-1/24 = -0.04167
```

So B preserves retention relative to A.

### C versus A

```
mean Delta = -0.04514
95% CI = [-0.07708, -0.01319]
```

The CI lower bound crosses below -0.04167.

Therefore C fails retention non-inferiority.

### C versus B

```
mean Delta = -0.05625
95% CI = [-0.09097, -0.02292]
```

C retains prior tasks significantly worse than B.

## 11. Policy qualification

### B RESET_ALL

Required:

- plasticity improvement vs A: FAIL;
- retention non-inferior vs A: PASS;
- strict all-fresh acquisition: FAIL;
- sentinel repair: PASS.

Therefore:

```
B qualified = false
```

B is not a valid policy because preserving retention is not enough; its acquisition dynamics are reproducibly worse than carry-all and its absolute robustness is also insufficient.

### C CARRY_STEP_RESET_MOMENTS

Required:

- plasticity improvement vs A: PASS;
- retention non-inferior vs A: FAIL;
- strict all-fresh acquisition: FAIL;
- sentinel repair: FAIL.

Therefore:

```
C qualified = false
```

C moves the system toward plasticity but shifts too far away from stability.

## 12. Main scientific result

The fixed policies expose a genuine stability/plasticity policy tradeoff:

### Carry-all A

Better retention than C, but poor long-horizon plasticity robustness.

### Reset-all B

Preserves retention and repairs sentinel 9393, but degrades mean acquisition AUC and still has four fresh-seed current-task failures.

### Carry-step/reset-moments C

Produces the best acquisition AUC and best mean T4, but sacrifices retention beyond the frozen non-inferiority margin and still fails two fresh seeds plus the 9393 sentinel.

No fixed policy simultaneously satisfies:

```
plasticity improvement
+
retention preservation
+
absolute robustness
```

## 13. Canonical classifier issue

The canonical script emitted:

```
NEGATIVE
NO_BOUNDARY_POLICY_PLASTICITY_ADVANTAGE
```

The raw metrics are valid, but this label is inconsistent with the frozen protocol because:

```
C plasticity improvement vs A = PASS
```

The implementation used:

> retention non-inferiority from any intervention

to avoid the FAIL branch.

That allows B's retention result to mask C's retention cost even though B itself does not improve plasticity.

The protocol's intended joint-policy rule is:

> a plasticity-improving policy must itself preserve retention.

Under the observed data:

- C is the only intervention with reproducible plasticity improvement;
- C fails retention non-inferiority.

Therefore the protocol-adjudicated status is:

```
FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

No scientific rerun was performed and no metric was altered.

The canonical raw script label is retained in machine-readable evidence for provenance.

## 14. What KCL-6.5.5 falsifies

The experiment falsifies the simple architecture hypothesis:

> "Once the bad AdamW component is identified, apply one fixed reset policy at every task boundary."

That is too simple.

A policy that works at one isolated boundary can fail when applied recursively across a multi-task trajectory.

The state is path-dependent.

## 15. Architectural consequence

The evidence now supports **adaptive**, not fixed, boundary control.

The future coordinator cannot just encode one global rule such as:

```
always carry
always reset
always keep step/reset moments
```

It must decide based on the current joint learning state.

A plausible architectural responsibility is now:

> **Task-Boundary Plasticity/Retention Controller**

Inputs should eventually include measurable boundary-state signals describing:

- model transition;
- optimizer moment state;
- plasticity health;
- retention risk.

Output should choose among boundary actions rather than hard-code one action globally.

## 16. Why adaptation is now necessary

KCL-6.5.3 already showed non-monotonic plasticity:

```
PASS → FAIL → PASS → FAIL
```

KCL-6.5.5 now shows non-universal policy effects:

- B repairs 9393 but worsens cohort acquisition AUC;
- C improves cohort acquisition AUC but harms retention and does not repair 9393;
- A preserves more retention than C but contains catastrophic T4 failures.

This is exactly the pattern expected when the correct boundary action depends on state.

## 17. Integrity

All scientific data integrity checks pass:

- upstream anchor valid;
- sentinel A reproduced exactly;
- model architecture unchanged;
- memory mechanism unchanged;
- optimizer hyperparameters unchanged;
- A/B/C training data matched;
- replay/query mechanism identical;
- boundary operations leave model parameters unchanged;
- KCL-7 not started.

The only issue is the final script decision predicate, not the experiment itself.

## 18. Verdict

Protocol-adjudicated official scientific verdict:

```
KCL-6.5.5 = FAIL
BOUNDARY_RESET_PLASTICITY_GAIN_COSTS_RETENTION
```

Canonical script output preserved for provenance:

```
NEGATIVE
NO_BOUNDARY_POLICY_PLASTICITY_ADVANTAGE
```

No A/B/C policy is validated as a fixed kernel boundary policy.

## 19. Provenance

Protocol:

`ce17e0bef0932a78d7d38c42f7ad4f153750c5d5`

Implementation:

`72299a5cf06f699390abb96f3d088d3b5c65d516`

Contract tests:

`bf04cd00824d8437fbd7128ab79a89430ba591f0`

Canonical scientific source:

`b5edc36d30202ee9b19e9634e328e6eda109f32d`

Canonical workflow:

`35374304856`

Focused tests:

`20 passed (10 KCL-6.5.5 + 10 KCL-6.5.4)`

Artifact:

`10559323752`

Artifact ZIP SHA-256:

`a14c7762f562f518fec3eb119c2ed2cc1a9bd5f2500c3b9dc3dd221331ea5395`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl655_summary.json`

## 20. Next scientific requirement

Do not implement an adaptive coordinator yet.

The missing piece is now a **boundary health signal** that can predict which policy is appropriate before observing future-task outcome.

The next milestone should qualify candidate signals using only state available at the boundary, then test whether those signals distinguish:

- boundaries where carry-all preserves useful stability;
- boundaries where moment reset is needed for plasticity;
- boundaries where reset creates retention risk.

Only after a predictive, non-oracular boundary signal exists should adaptive policy selection be implemented.

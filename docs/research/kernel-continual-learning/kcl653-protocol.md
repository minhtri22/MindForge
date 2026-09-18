# MindForge Kernel Continual Learning — KCL-6.5.3 Sequential Trajectory Mechanism Isolation Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.3 SCIENTIFIC EXECUTION**

## 1. Trigger and fixed upstream evidence

KCL-6.5.2 closed:

```
PASS
SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE
```

for seed `9393`.

Frozen evidence:

```
G0 fresh T4 only                 = 1.0000
G1 T1→T2→T3→T4 current-only     = 0.8750
```

Therefore T4 is independently learnable, while the ordinary sequential trajectory is sufficient to make T4 miss the unchanged `0.95` acquisition floor.

KCL-6.5.3 must answer two narrower questions:

1. Which prefix transition first creates the acquisition failure?
2. Is the failure carried primarily by model parameters, AdamW optimizer state, their interaction, or a localized parameter group?

No upstream verdict is modified.

## 2. Scientific objective

Locate the first transition:

```
P0: fresh
P1: T1
P2: T1→T2
P3: T1→T2→T3
```

such that a frozen current-only T4 probe changes from PASS to FAIL.

Then factor the transition state into:

```
MODEL state
×
OPTIMIZER state
```

using a pre-registered 2×2 counterfactual cross.

If model state is implicated, localize the responsible parameter group by matched state swaps.

The goal is diagnosis, not rescue.

## 3. Diagnostic seed and gate

Use exactly:

```
seed = 9393
```

T4 acquisition floor remains:

```
final T4 accuracy >= 0.95
```

No replacement seed, threshold change, or additional outcome-conditioned seed is allowed.

## 4. Frozen model/task/optimizer

Exactly the current diagnostic kernel:

- vocab 96
- d_model 16
- 2 heads
- 1 transformer layer
- context 2
- FF multiplier 4
- dropout 0
- tied token embedding / LM head
- AdamW
- lr 3e-3
- weight decay 0
- 250 steps/task
- deterministic CPU execution

Task stream:

```
T1_U1_A
T2_U1_B
T3_U3_A
T4_U3_B
```

## 5. Frozen sequential prefix construction

Create one canonical current-only trajectory and snapshot after each prefix.

### S0

Fresh model and fresh AdamW initialized from seed 9393.

### S1

Train T1 from S0:

```
steps = 250
batch = 16 current
stream seed = 9393 + 101 = 9494
```

### S2

Continue S1 with T2:

```
steps = 250
batch = 16 current
stream seed = 9393 + 2000 + 307 = 11700
```

### S3

Continue S2 with T3:

```
steps = 250
batch = 16 current
stream seed = 9393 + 3000 + 307 = 12700
```

No replay and no query are used in prefix construction.

Each snapshot contains:

- exact model state;
- exact AdamW state.

## 6. Prefix T4 probes P0–P3

From each snapshot `Sj`, clone both model and optimizer and train T4 current-only:

```
steps = 250
batch = 16 current
T4 stream seed = 9393 + 4000 + 307 = 13700
```

All P0–P3 therefore see the exact same T4 data stream.

Record T4 accuracy/loss at:

```
0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250
```

All 250 updates execute; no early stopping.

## 7. Canonical reproduction gate

KCL-6.5.3 must reproduce KCL-6.5.2:

```
P0 final T4 = 1.0000
P3 final T4 = 0.8750
```

Required tolerance:

```
1e-9
```

Failure =>

```
REVISE / PREFIX_REPRODUCTION_INVALID
```

## 8. First failing prefix transition

Define:

```
j* = minimum j in {1,2,3}
     such that
     P(j-1) >= 0.95
     and
     Pj < 0.95
```

The trigger task is:

- j*=1 → T1
- j*=2 → T2
- j*=3 → T3

If no such j exists while canonical P0/P3 are reproduced, verdict is REVISE because the prefix chain is internally inconsistent.

The primary prefix result is the first transition only; later failures are descriptive.

## 9. Transition state notation

At `j*` define:

```
Mpre  = model state at S(j*-1)
Opre  = AdamW state at S(j*-1)

Mpost = model state at Sj*
Opost = AdamW state at Sj*
```

The transition itself is exactly the frozen training of task `Tj*`.

## 10. Frozen 2×2 model/optimizer state cross

Run four T4 probes, all with the same T4 stream seed `13700`, 250 steps, batch 16.

### X00 — PRE_MODEL + PRE_OPT

```
Mpre + Opre
```

This must equal prefix probe P(j*-1).

### X10 — POST_MODEL + PRE_OPT

```
Mpost + Opre
```

Counterfactual model-state-only transition.

### X01 — PRE_MODEL + POST_OPT

```
Mpre + Opost
```

Counterfactual optimizer-state-only transition.

### X11 — POST_MODEL + POST_OPT

```
Mpost + Opost
```

This must equal prefix probe Pj*.

AdamW states are loaded by the frozen parameter order of the identical architecture.

## 11. 2×2 integrity

Required:

```
X00 final == P(j*-1) final
X11 final == Pj* final
```

within `1e-9`.

All optimizer tensors must load without shape/key mismatch.

Any violation => REVISE.

## 12. State-factor classification

Use T4 final gate `0.95`.

Given by definition:

```
X00 PASS
X11 FAIL
```

Classify:

### O — OPTIMIZER_STATE_DOMINANT

```
X10 PASS
X01 FAIL
```

Post-transition optimizer state is sufficient to induce failure while post-transition model state alone is not.

Architectural requirement candidate:

> task-boundary optimizer-state lifecycle / decay / reset / partitioning.

### M — MODEL_STATE_DOMINANT

```
X10 FAIL
X01 PASS
```

Post-transition model parameters are sufficient while optimizer state alone is not.

Proceed to parameter-group localization.

Architectural requirement candidate:

> parameter/representation plasticity protection or state partitioning.

### B — BOTH_STATES_INDEPENDENTLY_SUFFICIENT

```
X10 FAIL
X01 FAIL
```

Both model and optimizer transition states independently make T4 miss the floor.

Proceed to parameter-group localization for the model-state branch.

Architectural requirement candidate:

> coordinated parameter plasticity + optimizer-state governance.

### I — MODEL_OPTIMIZER_INTERACTION_ONLY

```
X10 PASS
X01 PASS
X11 FAIL
```

Neither state alone is sufficient; their post-transition combination is.

Architectural requirement candidate:

> joint task-boundary state coordination.

Any other valid pattern => `STATE_FACTOR_UNRESOLVED`.

## 13. Parameter groups

Group localization runs only when model state is implicated:

- classification M or B; or
- X10 FAIL under any unresolved valid state pattern.

Frozen groups must cover every named parameter exactly once.

### G_TOKEN_SHARED

```
token_embedding.weight
```

The LM head is tied to this same tensor.

### G_POSITION

```
position_embedding.weight
```

### G_TRANSFORMER

All names beginning:

```
layers.
```

### G_FINAL_NORM

All names beginning:

```
norm.
```

Coverage integrity:

```
union(groups) == set(model.named_parameters())
intersections(groups) == empty
```

Any violation => REVISE.

## 14. Parameter-group causal swaps

Hold optimizer state fixed to `Opre` in every group-localization arm.

All arms use the exact same T4 stream `13700`.

For each group `g`:

### ONLY_g

Start from `Mpre`, replace only group `g` with its `Mpost` parameter values.

```
Mpre + POST(g) + Opre
```

If T4 FAILs, transition changes in group `g` are sufficient to induce failure under the PRE context.

### WITHOUT_g

Start from `Mpost`, revert only group `g` to `Mpre`.

```
Mpost - POST(g) + PRE(g) + Opre
```

If T4 PASSes, transition changes in group `g` are necessary for failure under the POST context.

## 15. Group localization classification

For each group report:

- `sufficient = ONLY_g < 0.95`
- `necessary = WITHOUT_g >= 0.95`

Classification:

### STRONG_LOCALIZATION_<GROUP>

Exactly one group is both sufficient and necessary.

### MULTI_GROUP_REDUNDANT

Two or more groups are individually sufficient; no unique necessary group.

### MULTI_GROUP_INTERACTION

No group alone is sufficient, but at least one group is necessary.

### DISTRIBUTED_PARAMETER_INTERFERENCE

No single group is sufficient or necessary while X10 remains FAIL.

### MIXED_PARAMETER_LOCALIZATION

Any other valid pattern.

No group is chosen after outcome inspection.

## 16. Parameter drift diagnostics

For the trigger transition, report per group:

```
L2(Mpost - Mpre)
relative_L2 = L2(delta) / max(L2(Mpre), 1e-12)
max_abs_delta
parameter_count
```

These metrics are descriptive and do not override causal swap results.

## 17. Architecture-gap mapping

KCL-6.5.3 may identify a **candidate missing architectural requirement**, not implement a fix.

Frozen mapping:

- `OPTIMIZER_STATE_DOMINANT`:
  - optimizer-state lifecycle at task boundaries.
- `MODEL_OPTIMIZER_INTERACTION_ONLY`:
  - coordinated task-boundary model/optimizer state management.
- strong `G_TOKEN_SHARED` localization:
  - protection/partitioning of shared token-output representation.
- strong `G_POSITION` localization:
  - position/context representation isolation.
- strong `G_TRANSFORMER` localization:
  - backbone representation plasticity control / subspace allocation.
- strong `G_FINAL_NORM` localization:
  - normalization-affine adaptation isolation.
- distributed/multi-group parameter interference:
  - global plasticity governor or task-conditioned parameter subspace separation.
- both model and optimizer independently sufficient:
  - combined plasticity governor + optimizer lifecycle.

These are architecture **requirements suggested by causal evidence**, not validated implementations.

## 18. Secondary trajectory diagnostics

Report:

- P0–P3 T4 curves;
- first checkpoint reaching 95%;
- final/max T4 accuracy;
- trigger task at j*;
- T1/T2/T3 own-task accuracy immediately after each prefix task;
- zero-step T4 accuracy/loss from S0–S3;
- 2×2 T4 curves;
- group-swap T4 endpoints when applicable.

## 19. Milestone verdict

### Valid prefix reproduction + valid j* + valid 2×2 decomposition

```
KCL-6.5.3 = PASS
<STATE_FACTOR_CLASS>
[+ optional GROUP_LOCALIZATION_CLASS]
```

PASS means mechanism isolation succeeded; it does not mean the kernel CL gate is repaired.

### Any frozen integrity failure

```
KCL-6.5.3 = REVISE
SEQUENTIAL_MECHANISM_ISOLATION_INVALID
```

### Valid but state factor remains unresolved

```
KCL-6.5.3 = INCONCLUSIVE
SEQUENTIAL_STATE_FACTOR_UNRESOLVED
```

## 20. No tuning rule

After protocol freeze do not change:

- seed;
- prefix streams;
- T4 stream;
- step count;
- gate;
- 2×2 construction;
- parameter groups;
- group swap definitions;
- classification rules.

No rescue arm or new parameter grouping may be added after observing results.

## 21. Scope exclusions

KCL-6.5.3 does not:

- alter E/F;
- tune replay;
- repair the kernel;
- open KCL-7;
- open reasoning;
- introduce adapters/gates/reset policies as implementations.

Those become separate hypotheses only after KCL-6.5.3 closes.

## 22. Required artifacts

```
experiments/kernel_cl/kcl653_sequential_trajectory_isolation.py
experiments/kernel_cl/results/kcl653_summary.json
tests/test_kernel_cl_kcl653.py
docs/research/kernel-continual-learning/kcl653-paper.md
.github/workflows/kernel-cl-kcl653.yml
```

## 23. Closure

KCL-6.5.3 closes only after:

- protocol commit before execution;
- focused tests PASS;
- one official seed-9393 run;
- raw evidence preserved;
- paper written;
- append-only Lineage update.

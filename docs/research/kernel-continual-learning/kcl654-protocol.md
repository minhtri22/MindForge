# MindForge Kernel Continual Learning — KCL-6.5.4 AdamW Boundary-State Decomposition Protocol

Status: **FROZEN BEFORE ANY KCL-6.5.4 SCIENTIFIC EXECUTION**

## 1. Trigger and fixed upstream evidence

KCL-6.5.3 closed:

```
PASS
MODEL_OPTIMIZER_INTERACTION_ONLY
```

at seed `9393`, first failing transition `fresh → T1`.

Frozen 2×2 evidence:

```
PRE model  + PRE optimizer   = 1.0000
POST model + PRE optimizer   = 1.0000
PRE model  + POST optimizer  = 1.0000
POST model + POST optimizer  = 0.9167
```

Therefore neither POST-T1 model parameters nor POST-T1 AdamW state is sufficient alone. Their combination is sufficient to make future T4 acquisition miss the unchanged `0.95` floor.

KCL-6.5.4 holds the POST-T1 model fixed and decomposes the AdamW state into:

- optimizer step / age;
- first moment `exp_avg`;
- second moment `exp_avg_sq`.

No upstream verdict is modified.

## 2. Scientific question

Which AdamW state component, or interaction among components, is required for the bad POST-model/POST-optimizer joint state?

The experiment is diagnostic, not a rescue.

## 3. Frozen seed, model and target task

Use exactly:

```
seed = 9393
```

Construct the exact deterministic POST-T1 model/optimizer state using:

```
T1 stream seed = 9494
250 steps
batch = 16
```

Then every KCL-6.5.4 arm trains T4 current-only using:

```
T4 stream seed = 13700
250 steps
batch = 16
```

T4 final acquisition gate remains:

```
>= 0.95
```

No replay, no query, no memory mechanism.

## 4. AdamW state components

For every model parameter, frozen AdamW state is expected to contain:

```
step
exp_avg
exp_avg_sq
```

AMSGrad is disabled.

KCL-6.5.4 treats these as three global component classes:

```
S = step
M = exp_avg
V = exp_avg_sq
```

A component is either:

- `1`: carry exact POST-T1 value;
- `0`: reset to fresh-zero baseline.

## 5. Reset semantics

Reset values:

```
step       -> 0
exp_avg    -> zeros_like(post exp_avg)
exp_avg_sq -> zeros_like(post exp_avg_sq)
```

All other optimizer hyperparameters remain exactly unchanged.

The zero-state representation is pre-populated for every parameter so that all 2^3 arms share identical state-key structure.

## 6. Fresh-equivalence control

Because a truly fresh AdamW optimizer has an empty per-parameter state dictionary before its first update, KCL-6.5.4 must validate reset semantics.

### FRESH_EMPTY

POST-T1 model + newly constructed AdamW with empty state.

### O000

POST-T1 model + pre-populated zero state:

```
S=0, M=0, V=0
```

Required:

```
T4 curve FRESH_EMPTY == T4 curve O000
final model state equal
final optimizer state equal
```

If this fails:

```
KCL-6.5.4 = REVISE
ADAMW_RESET_BASELINE_INVALID
```

No factorial interpretation is allowed.

## 7. Full 2^3 factorial

Run all eight optimizer states on the exact same POST-T1 model and T4 stream.

Bit order is:

```
SMV
```

### O000

Reset step, first moment, second moment.

### O100

Carry step only.

### O010

Carry first moment only.

### O001

Carry second moment only.

### O110

Carry step + first moment.

### O101

Carry step + second moment.

### O011

Carry first moment + second moment.

### O111

Carry all POST-T1 AdamW state.

## 8. Canonical reproduction gates

Required:

### Reset endpoint

KCL-6.5.3 X10:

```
POST model + PRE/fresh optimizer = 1.0000
```

Therefore:

```
O000 final T4 = 1.0000
```

within tolerance `1e-9`.

### Carry-all endpoint

KCL-6.5.3 X11:

```
POST model + POST optimizer = 0.9166666865348816
```

Therefore:

```
O111 final T4 = 0.9166666865348816
```

within tolerance `1e-9`.

Any failure:

```
REVISE / ADAMW_BOUNDARY_REPRODUCTION_INVALID
```

## 9. Acquisition curves

For FRESH_EMPTY and every Oxyz arm, evaluate T4 at:

```
0,25,50,75,100,125,150,175,200,225,250
```

All 250 updates execute.

Report:

- final accuracy;
- maximum accuracy;
- first checkpoint reaching `>=0.95`;
- loss curve.

No early stopping.

## 10. Minimal sufficient failing sets

Define a factorial cell as FAIL iff:

```
final T4 < 0.95
```

A carried component set `C` is **minimal sufficient for failure** iff:

1. arm `C` FAILs;
2. every strict subset of `C` PASSes.

Examples:

- O100 FAIL => `{S}` minimal sufficient.
- O110 FAIL while O100/O010 PASS => `{S,M}` minimal sufficient.
- O111 FAIL while all six non-empty proper subsets PASS => `{S,M,V}` is a three-way interaction.

Report all minimal sufficient failing sets.

## 11. Component necessity under carry-all context

A component is **necessary in the O111 context** iff resetting only that component rescues T4:

### S necessary

```
O011 PASS
```

### M necessary

```
O101 PASS
```

### V necessary

```
O110 PASS
```

Report necessity independently from minimal sufficiency.

## 12. Primary optimizer-state classification

After integrity passes:

### STEP_ONLY_SUFFICIENT

Exactly `{S}` is the unique minimal sufficient set.

### FIRST_MOMENT_ONLY_SUFFICIENT

Exactly `{M}` is the unique minimal sufficient set.

### SECOND_MOMENT_ONLY_SUFFICIENT

Exactly `{V}` is the unique minimal sufficient set.

### MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT

Two or more singleton sets are minimal sufficient.

### STEP_FIRST_MOMENT_INTERACTION

Unique minimal sufficient set is `{S,M}`.

### STEP_SECOND_MOMENT_INTERACTION

Unique minimal sufficient set is `{S,V}`.

### FIRST_SECOND_MOMENT_INTERACTION

Unique minimal sufficient set is `{M,V}`.

### MULTIPLE_PAIR_INTERACTIONS

Two or more pair sets are minimal sufficient and no singleton is sufficient.

### THREE_WAY_ADAMW_INTERACTION_REQUIRED

The unique minimal sufficient set is:

```
{S,M,V}
```

### ADAMW_COMPONENT_PATTERN_MIXED

Any other valid minimal-sufficient-set pattern.

## 13. Architectural requirement mapping

Frozen mapping:

- `STEP_ONLY_SUFFICIENT`
  - `OPTIMIZER_AGE_BIAS_CORRECTION_GOVERNANCE`.
- `FIRST_MOMENT_ONLY_SUFFICIENT`
  - `FIRST_MOMENT_BOUNDARY_GOVERNANCE`.
- `SECOND_MOMENT_ONLY_SUFFICIENT`
  - `SECOND_MOMENT_PRECONDITIONER_GOVERNANCE`.
- `STEP_FIRST_MOMENT_INTERACTION`
  - `AGE_MOMENTUM_BOUNDARY_COORDINATION`.
- `STEP_SECOND_MOMENT_INTERACTION`
  - `AGE_VARIANCE_BOUNDARY_COORDINATION`.
- `FIRST_SECOND_MOMENT_INTERACTION`
  - `MOMENT_PAIR_BOUNDARY_COORDINATION`.
- `THREE_WAY_ADAMW_INTERACTION_REQUIRED`
  - `FULL_ADAMW_BOUNDARY_STATE_COORDINATION`.
- multiple/mixed patterns
  - `ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION`.

These are architectural requirements suggested by evidence, not implemented fixes.

## 14. Step semantics diagnostics

Report POST-T1 optimizer step values:

- minimum across parameters;
- maximum;
- unique values.

Required for deterministic T1 training:

```
all parameter step values = 250
```

If parameter step values are inconsistent unexpectedly, classify REVISE.

## 15. Moment diagnostics

For POST-T1 `exp_avg` and `exp_avg_sq`, report aggregate:

- total element count;
- L2 norm;
- max absolute value;
- finite check.

Also report these statistics by KCL-6.5.3 parameter group:

- shared token/output;
- position embedding;
- transformer block;
- final norm.

These are descriptive and do not override factorial causality.

## 16. Update-scale diagnostics

For each Oxyz arm, report the T4 step-1 parameter-update L2 norm:

```
||theta_after_step1 - theta_before_T4||
```

and first-step loss.

This can reveal how carried optimizer components alter effective update scale/direction.

It is descriptive only.

## 17. Verdicts

### Valid factorial and classification obtained

```
KCL-6.5.4 = PASS
<OPTIMIZER_STATE_CLASS>
```

### Reset baseline or canonical endpoint invalid

```
KCL-6.5.4 = REVISE
ADAMW_BOUNDARY_DECOMPOSITION_INVALID
```

### Valid factorial but no class matches due unexpected pattern

```
KCL-6.5.4 = INCONCLUSIVE
ADAMW_COMPONENT_PATTERN_UNRESOLVED
```

## 18. No tuning rule

After freeze do not change:

- seed;
- POST-T1 model;
- T4 stream;
- gate;
- component definitions;
- zero baseline;
- factorial arms;
- classification rules;
- architecture mapping.

No extra reset policy may be added after outcome inspection.

## 19. Scope exclusions

KCL-6.5.4 does not:

- implement a coordinator;
- choose a production reset schedule;
- tune Adam betas/epsilon/lr;
- modify E/F memory mechanisms;
- open KCL-7;
- open reasoning.

A concrete task-boundary policy becomes a separate hypothesis only after this milestone closes.

## 20. Required artifacts

```
experiments/kernel_cl/kcl654_adamw_boundary_state.py
experiments/kernel_cl/results/kcl654_summary.json
tests/test_kernel_cl_kcl654.py
docs/research/kernel-continual-learning/kcl654-paper.md
.github/workflows/kernel-cl-kcl654.yml
```

## 21. Closure

KCL-6.5.4 closes only after:

- this protocol is committed before execution;
- focused tests PASS;
- one official seed-9393 factorial run;
- raw evidence preserved;
- paper written;
- append-only Lineage update.

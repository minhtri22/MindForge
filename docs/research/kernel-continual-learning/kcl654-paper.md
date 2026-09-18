# KCL-6.5.4 — AdamW Boundary-State Decomposition

## Abstract

KCL-6.5.3 identified a joint model–optimizer interaction at the first failing sequential transition. With the POST-T1 model fixed, a fresh AdamW state preserved T4 acquisition at 100%, while the full POST-T1 AdamW state reduced T4 to 91.67%. KCL-6.5.4 decomposes that optimizer state exhaustively into three global AdamW component classes: optimizer step/age `S`, first moment `M = exp_avg`, and second moment `V = exp_avg_sq`.

All eight `2^3` carry/reset combinations were run on the exact same POST-T1 model and identical T4 stream. Reset semantics were independently validated: a pre-populated zero state `O000` is bit-equivalent to a genuinely fresh AdamW optimizer in T4 learning curve, final model state, and final optimizer state.

The factorial result is:

| Arm | Carried AdamW state | T4 final |
|---|---|---:|
| O000 | none | **1.0000** |
| O100 | step only | **1.0000** |
| O010 | first moment only | **0.0833** |
| O001 | second moment only | **0.9167** |
| O110 | step + first moment | **0.2917** |
| O101 | step + second moment | **0.9167** |
| O011 | first + second moments | **0.9167** |
| O111 | step + first + second moments | **0.9167** |

The minimal sufficient failing sets are independently:

```
{exp_avg}
{exp_avg_sq}
```

while `step` alone is harmless under the frozen T4 gate.

Therefore:

```
KCL-6.5.4 = PASS
MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT
```

and the pre-registered architecture-gap mapping is:

```
ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION
```

The key implication is not "reset one AdamW field." Both first- and second-moment histories can independently produce poor future plasticity when paired with the learned POST-T1 model, and resetting only one moment from the full state does not rescue because the other remains sufficient. The evidence points toward coordinated boundary treatment of AdamW moment state.

## 1. Upstream trigger

KCL-6.5.3 closed:

```
PASS
MODEL_OPTIMIZER_INTERACTION_ONLY
```

At the first failing transition:

```
POST model + fresh optimizer = 1.0000
POST model + POST optimizer  = 0.9167
```

This ruled out model parameters alone and optimizer state alone as universal causes, but left the internal AdamW component responsible unresolved.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl654-protocol.md`

Protocol commit:

`dea6fbf0fedaaf0679a4aed7e61b51048c8b224b`

Protocol SHA-256:

`b42347460823f38ea250022489d34ecbd5b94ea9513feb194d336949acbd9e25`

Scientific source:

`990c000a7ca723bb469dbcc058c4d6c269e7bd82`

No post-outcome changes were made to:

- seed;
- POST-T1 model;
- T4 stream;
- 0.95 gate;
- state components;
- reset semantics;
- factorial arms;
- classification rules.

## 3. State contract

Seed:

`9393`

POST-T1 AdamW state is present for all 16 optimizer parameter states.

Every parameter has:

```
step = 250
exp_avg
exp_avg_sq
```

Step consistency:

```
min = 250
max = 250
unique = [250]
```

AMSGrad is not used.

## 4. Reset-baseline validation

A concern in optimizer-state counterfactuals is that a manually zeroed state may not behave like a genuinely fresh optimizer.

KCL-6.5.4 explicitly compares:

### FRESH_EMPTY

POST-T1 model plus newly created AdamW whose per-parameter state dictionary is initially empty.

### O000

POST-T1 model plus state explicitly pre-populated with:

```
step = 0
exp_avg = 0
exp_avg_sq = 0
```

Required equivalence:

- T4 curve equal;
- final model state equal;
- final optimizer state equal.

All checks pass.

Both reach:

```
T4 final = 1.0000
```

First-step parameter update L2:

```
0.2035969
```

for both.

Therefore the factorial zero baseline is a valid representation of fresh AdamW behavior.

## 5. Canonical endpoint reproduction

### O000

Required from KCL-6.5.3 fresh optimizer result:

```
1.0000
```

Observed:

```
1.0000
```

### O111

Required from KCL-6.5.3 carry-all optimizer result:

```
0.9166666865
```

Observed:

```
0.9166666865
```

The factorial therefore reproduces both upstream causal endpoints exactly.

## 6. Full factorial result

Bit order:

```
SMV
S = step
M = exp_avg
V = exp_avg_sq
```

### O000 — reset all

```
final T4 = 1.0000
first >=95% checkpoint = 200
first-step update L2 = 0.2036
```

### O100 — carry step only

```
final T4 = 1.0000
first >=95% checkpoint = 175
first-step update L2 = 0.2948
```

Step/age alone is not harmful under this benchmark.

### O010 — carry first moment only

```
final T4 = 0.0833
max T4   = 0.2083
first-step update L2 = 8657.89
```

This is a catastrophic mismatch.

A retained nonzero first moment combined with a reset second moment produces an extremely large effective first update.

This establishes `exp_avg` as sufficient for failure under the reset-baseline context.

### O001 — carry second moment only

```
final T4 = 0.9167
max T4   = 0.9167
first-step update L2 = 0.0982
```

A retained second moment with reset first moment and step is also independently sufficient to miss the 95% acquisition floor.

Unlike O010, the effect is not explosive. The first update is approximately half the fresh-state update norm.

### O110 — carry step + first moment

```
final T4 = 0.2917
max T4   = 0.3333
first-step update L2 = 1599.52
```

Keeping the old step counter moderates but does not remove the first-moment/reset-variance mismatch.

### O101 — carry step + second moment

```
final T4 = 0.9167
first-step update L2 = 0.1463
```

Still fails.

### O011 — carry both moments, reset step

```
final T4 = 0.9167
first-step update L2 = 0.0985
```

Still fails.

### O111 — carry all

```
final T4 = 0.9167
first-step update L2 = 0.1467
```

Canonical POST-T1 failure reproduced.

## 7. Minimal sufficient failing sets

The pre-registered criterion asks for a FAIL arm whose every strict carried-state subset PASSes.

Observed minimal sets:

```
{M}
{V}
```

or:

```
{exp_avg}
{exp_avg_sq}
```

Each moment history is independently sufficient to produce a failed T4 acquisition trajectory in its respective counterfactual context.

Step is not a minimal sufficient component.

## 8. Necessity under full O111 context

A component is necessary in O111 only if resetting that one component rescues the full carry state.

### Reset step only → O011

```
0.9167 FAIL
```

So step is not necessary.

### Reset first moment only → O101

```
0.9167 FAIL
```

So first moment is not individually necessary in O111, because second moment remains sufficient.

### Reset second moment only → O110

```
0.2917 FAIL
```

So second moment is not individually necessary in O111, because first moment remains sufficient.

This is exactly the pattern expected from redundant causal routes:

> neither moment is necessary because either moment history can independently generate failure.

## 9. Official classification

The frozen classification returns:

```
MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT
```

because two singleton carried-state sets are minimal sufficient:

```
{M}
{V}
```

The architecture mapping returns:

```
ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION
```

## 10. Why "reset only exp_avg" is not enough

A tempting interpretation after seeing O010 would be:

> first moment is the problem; reset exp_avg.

But the factorial explicitly rejects that conclusion.

Resetting only `exp_avg` from O111 yields O101:

```
step + exp_avg_sq
→ T4 = 0.9167
→ FAIL
```

Likewise, resetting only `exp_avg_sq` yields O110:

```
step + exp_avg
→ T4 = 0.2917
→ FAIL
```

Therefore a boundary policy must at minimum reason about the two moment states together.

## 11. Step/age is not the observed root component

Step alone:

```
O100 = 1.0000
```

and reaches the 95% checkpoint at step 175, earlier than O000 at step 200.

Thus retaining optimizer age without old moments does not reproduce the failure in this experiment.

This makes a strong candidate policy visible for future validation:

```
carry step
reset both moments
```

but KCL-6.5.4 does not yet claim this policy generalizes or preserves continual-learning retention.

It is only a hypothesis generated by the factorial.

## 12. First-step update diagnostics

All arms use the same T4 minibatch at the first update, so first-train loss is identical:

```
11.8714
```

Yet effective update magnitude differs dramatically.

Approximate first-step parameter-update L2:

```
O000  0.2036
O100  0.2948
O001  0.0982
O101  0.1463
O011  0.0985
O111  0.1467

O010  8657.89
O110  1599.52
```

This demonstrates two qualitatively different optimizer-history hazards:

1. **retained first moment without matching variance state** can cause explosive updates;
2. **retained second moment** can strongly shrink future updates and is independently associated with insufficient acquisition.

The balanced carried pair avoids explosion but still does not restore the fresh optimizer's future plasticity.

## 13. POST-T1 moment diagnostics

All moment tensors are finite.

By parameter group:

### Shared token/output representation

```
exp_avg L2    = 0.02944
exp_avg_sq L2 = 0.00659
```

### Position embedding

```
exp_avg L2    = 0.00220
exp_avg_sq L2 = 0.00502
```

### Transformer block

```
exp_avg L2    = 0.03300
exp_avg_sq L2 = 0.02111
```

### Final norm

```
exp_avg L2    = 0.05033
exp_avg_sq L2 = 0.07639
```

These values are descriptive only. KCL-6.5.4 does not localize moment causality by parameter group.

## 14. Architectural consequence

KCL-6.5.3 suggested a generic:

> Task-Boundary Joint Plasticity Coordinator.

KCL-6.5.4 makes its optimizer-side contract substantially more concrete.

The coordinator cannot merely track:

- optimizer step;
- total optimizer reset yes/no.

It must treat optimizer moment state as a first-class boundary object.

The evidence supports the requirement:

> **Adaptive Componentwise Optimizer Boundary Coordination**

At minimum the architecture must know that:

- `exp_avg` carries directional momentum from the previous task;
- `exp_avg_sq` carries a learned coordinate-wise preconditioner from the previous task;
- either may become incompatible with the newly learned model state and future task;
- partial resets can be worse than either full carry or full reset if they destroy the internal coupling between moments.

## 15. Candidate architecture contract

A future Task-Boundary Joint Plasticity Coordinator should expose separate controls for:

```
step / age
first moment
second moment
```

rather than a single binary "reset optimizer" operation.

Candidate actions may eventually include:

- carry;
- reset;
- decay;
- rebase;
- partition;
- task-local moment banks;
- validated consolidation.

But KCL-6.5.4 does not choose among them yet.

## 16. Important caution about hybrid counterfactuals

O010 and O110 intentionally create states that ordinary AdamW training would not naturally generate: old first moment paired with a reset second moment.

Their extreme update norms are scientifically useful because the factorial asks about component sufficiency.

They should not be interpreted as recommended operational policies.

The production-policy question is separate.

## 17. Integrity

All required integrity checks pass:

- KCL-6.5.3 anchor valid;
- all POST-T1 parameter step values = 250;
- fresh-empty optimizer exactly equals O000;
- O000 reproduces 100%;
- O111 reproduces 91.67%;
- model fixed across all arms;
- T4 stream fixed across all arms;
- all metrics finite;
- optimizer hyperparameters unchanged;
- architecture unchanged;
- KCL-7 not started.

## 18. Verdict

```
KCL-6.5.4 = PASS
MULTIPLE_SINGLE_COMPONENTS_SUFFICIENT
```

Architecture-gap candidate:

```
ADAPTIVE_COMPONENTWISE_OPTIMIZER_BOUNDARY_COORDINATION
```

## 19. Provenance

Protocol:

`dea6fbf0fedaaf0679a4aed7e61b51048c8b224b`

Implementation:

`52e01c88c624601a97f414f86fc4c16f73d16737`

Contract tests:

`4364ddb63fb09619e0f1d9ca24be4e1e7d519768`

Canonical scientific source:

`990c000a7ca723bb469dbcc058c4d6c269e7bd82`

Official workflow:

`35373053828`

Focused tests:

`20 passed (10 KCL-6.5.4 + 10 KCL-6.5.3)`

Artifact:

`10558109849`

Artifact ZIP SHA-256:

`d316c5a9a6cc7ab660a45a126028f981d302f1d85d1a4f06256911cb6c622e03`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl654_summary.json`

## 20. Next scientific question

The diagnostic problem is now sufficiently narrow to test actual boundary policies.

The strongest candidate generated by KCL-6.5.4 is:

```
carry step
reset exp_avg
reset exp_avg_sq
```

because O100 reaches 100% T4 while preserving optimizer age.

It must now be tested against at least:

- carry-all AdamW state;
- reset-all AdamW state;
- carry-step/reset-both-moments;

on a sequential multi-task continual-learning workload, with both future-task plasticity and prior-task retention measured.

Only if a boundary policy improves plasticity without destroying retention should the Task-Boundary Joint Plasticity Coordinator become an implemented kernel component.

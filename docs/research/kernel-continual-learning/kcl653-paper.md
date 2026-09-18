# KCL-6.5.3 — Sequential Trajectory Mechanism Isolation

## Abstract

KCL-6.5.2 established that seed 9393's T4 failure is already present under ordinary current-only sequential training, before replay or clarification is required. KCL-6.5.3 localizes the first trajectory transition that changes T4 learnability and then factorizes that transition into model parameters versus AdamW optimizer state.

The prefix result is non-monotonic:

```
P0 fresh             → T4 = 1.0000
P1 T1                → T4 = 0.9167
P2 T1→T2             → T4 = 1.0000
P3 T1→T2→T3          → T4 = 0.8750
```

Thus the first failing transition is already T1, but T2 subsequently restores T4 acquisition before T3 destroys it again. This rules out a simple monotonic capacity-exhaustion interpretation.

The pre-registered 2×2 state cross at the first transition gives:

```
X00 PRE model + PRE optimizer   = 1.0000
X10 POST model + PRE optimizer  = 1.0000
X01 PRE model + POST optimizer  = 1.0000
X11 POST model + POST optimizer = 0.9167
```

Neither the post-T1 model state nor the post-T1 AdamW state is sufficient by itself to make T4 fail. The failure appears only when the two post-transition states are paired. Therefore:

```
KCL-6.5.3 = PASS
MODEL_OPTIMIZER_INTERACTION_ONLY
```

The pre-registered architecture-gap mapping identifies:

```
JOINT_MODEL_OPTIMIZER_TASK_BOUNDARY_COORDINATION
```

as the missing architectural requirement suggested by the current evidence.

This does not yet validate a concrete solution such as optimizer reset. It establishes that continual learning currently lacks a mechanism governing how learned model state and accumulated optimizer state are carried together across task boundaries.

## 1. Upstream evidence

KCL-6.5.2 closed:

```
PASS
SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE
```

with:

```
fresh T4 only                 = 1.0000
T1→T2→T3→T4 current-only     = 0.8750
```

Therefore KCL-6.5.3 does not test replay or clarification. It asks where in the sequential trajectory future plasticity is first damaged.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl653-protocol.md`

Protocol commit:

`491540e5201b245f63f6d4763a086ca75711be0f`

Protocol SHA-256:

`9719a64876602455b873b9e68cf33be5dc9a441ba49359b247a7461fa75abdb6`

Scientific source:

`7ef57cb38059d084fe05a6604a8b00c67c9dadb5`

No outcome-conditioned change was made to:

- seed;
- prefix streams;
- T4 stream;
- 0.95 gate;
- factorial state construction;
- parameter groups;
- classification rules.

## 3. Prefix construction

Seed:

`9393`

Snapshots:

```
S0 = fresh
S1 = after T1
S2 = after T1→T2
S3 = after T1→T2→T3
```

Each snapshot stores both:

- exact model parameters;
- exact AdamW state.

Every T4 probe uses the identical current-only T4 stream:

`13700`

for 250 steps with batch size 16.

## 4. Prefix localization

### P0 — fresh

```
T4 final = 1.0000
T4 max   = 1.0000
first >=95% checkpoint = 200
zero-step T4 loss = 13.7647
```

### P1 — after T1

```
T4 final = 0.9167
T4 max   = 0.9167
never reaches 95%
zero-step T4 loss = 11.3559
```

### P2 — after T1→T2

```
T4 final = 1.0000
T4 max   = 1.0000
first >=95% checkpoint = 200
zero-step T4 loss = 8.6948
```

### P3 — after T1→T2→T3

```
T4 final = 0.8750
T4 max   = 0.8750
never reaches 95%
zero-step T4 loss = 9.7110
```

Canonical KCL-6.5.2 endpoints P0/P3 reproduce exactly.

## 5. First failing transition

The protocol defines:

```
j* = first j where P(j-1) PASS and Pj FAIL
```

Observed:

```
j* = 1
trigger task = T1_U1_A
```

So the first sequential task is already sufficient to create a model/optimizer state from which T4 no longer meets the acquisition floor.

However the trajectory is not monotonic:

```
FAIL after T1
→ RECOVER after T2
→ FAIL after T3
```

This is a major mechanistic result.

The phenomenon is not consistent with a simple explanation such as:

> each task consumes irreversible capacity until plasticity eventually collapses.

The system can regain future-task plasticity after an additional task.

## 6. Current tasks themselves are learned correctly

Immediate own-task accuracy after each prefix task:

```
T1 = 1.0000
T2 = 1.0000
T3 = 1.0000
```

Therefore the problematic state is not visible by asking only whether the current task was learned.

A kernel can have:

```
current task accuracy = 100%
```

while already being in a state with degraded ability to acquire a future task.

This exposes a missing dimension in the current architecture/evaluation:

> plasticity state is latent and is not represented or controlled explicitly.

## 7. Zero-step T4 quality does not explain plasticity

Zero-step T4 loss:

```
P0 = 13.7647 → PASS after training
P1 = 11.3559 → FAIL
P2 =  8.6948 → PASS
P3 =  9.7110 → FAIL
```

Thus a better initial T4 loss does not guarantee future T4 learnability.

The failure is about optimization trajectory/plasticity, not merely bad zero-shot predictions.

## 8. Factorial model × optimizer decomposition

At transition T1:

```
Mpre/Opre   = fresh model + fresh AdamW
Mpost/Opost = post-T1 model + post-T1 AdamW
```

Four pre-registered counterfactual T4 probes:

| Cell | Model | Optimizer | T4 final |
|---|---|---|---:|
| X00 | PRE | PRE | **1.0000** |
| X10 | POST | PRE | **1.0000** |
| X01 | PRE | POST | **1.0000** |
| X11 | POST | POST | **0.9167** |

X00 reproduces P0 exactly.

X11 reproduces P1 exactly.

## 9. State-factor result

The frozen classification rule yields:

```
MODEL_OPTIMIZER_INTERACTION_ONLY
```

because:

```
POST model + PRE optimizer  PASS
PRE model  + POST optimizer PASS
POST model + POST optimizer FAIL
```

Therefore:

- learned model parameters alone are not sufficient for failure;
- accumulated AdamW state alone is not sufficient for failure;
- the paired post-task state is sufficient.

This is stronger than saying "optimizer state is stale" or "the model forgot how to learn."

The evidence points to a **joint state compatibility problem**.

## 10. Why parameter-group localization did not run

The protocol allowed parameter-group causal swaps only if:

```
POST model + PRE optimizer
```

failed.

It passed at 100%.

Therefore model parameter state alone is not sufficient and group-level parameter localization is not scientifically warranted in this milestone.

The pre-registered parameter groups remain:

- shared token embedding / LM head;
- position embedding;
- transformer block;
- final norm.

But none may be labeled causal from KCL-6.5.3.

## 11. Parameter drift is descriptive only

T1 changes all model groups.

Relative L2 drift:

```
transformer block      ≈ 0.6411
shared token/LM head   ≈ 0.2167
final norm             ≈ 0.1369
position embedding     ≈ 0.0715
```

Absolute L2 drift is largest in:

```
shared token/LM head = 8.5228
transformer          = 6.0248
```

However:

```
POST model + PRE optimizer = PASS
```

so large parameter drift by itself is not a causal explanation.

## 12. Architectural implication

The pre-registered architecture-gap mapping returns:

```
JOINT_MODEL_OPTIMIZER_TASK_BOUNDARY_COORDINATION
```

The current kernel has:

```
model parameters
+
AdamW state
```

but treats them as passive state carried continuously from one task to the next.

KCL-6.5.3 shows that this is insufficient.

A task can be learned perfectly while leaving a paired model/optimizer state that has degraded future plasticity.

The missing architectural requirement is therefore a mechanism that explicitly governs the **joint learning state at task transitions**.

This mechanism must reason about both:

- what the parameters have become;
- what optimizer history is being carried with those parameters.

## 13. What the evidence suggests — and does not yet prove

The result suggests testing mechanisms such as:

- task-local optimizer moments;
- optimizer moment decay at task boundaries;
- selective moment reset;
- optimizer-state rollback/consolidation;
- plasticity-health gates before committing a task transition.

But KCL-6.5.3 does **not** prove which of these is correct.

In particular it does not yet prove:

```
"reset AdamW after every task"
```

is the solution.

That must be separately pre-registered and A/B tested.

## 14. Non-monotonic plasticity is an architectural clue

The most informative sequence is:

```
P0 PASS
P1 FAIL
P2 PASS
P3 FAIL
```

Future plasticity behaves as a hidden dynamical state, not a monotonic resource counter.

This suggests that a production continual-learning kernel should not merely track:

- loss;
- current-task accuracy;
- retention.

It likely needs an explicit **plasticity health/state signal** at transitions.

Without such a signal, the kernel can commit a task update that looks successful locally but leaves the next learning step in a bad state.

## 15. Candidate missing component

The present evidence supports the following requirement:

> **Task-Boundary Joint Plasticity Coordinator**

Its responsibility would not yet be to choose a particular optimizer reset rule.

Its contract would be:

1. observe the model-state transition;
2. observe optimizer-state transition;
3. estimate whether their combination preserves future plasticity;
4. decide how optimizer/model learning state should be carried, decayed, reset, partitioned, or consolidated;
5. refuse or revise a transition when plasticity health violates a frozen criterion.

This is an architectural hypothesis generated from KCL-6.5.3, not an implemented component.

## 16. Integrity

All required integrity gates pass:

- KCL-6.5.2 anchor valid;
- P0/P3 canonical reproduction exact;
- first failing transition identified;
- X00/X11 reproduce corresponding prefix probes;
- parameter groups cover all named parameters exactly;
- all metrics finite;
- architecture unchanged;
- AdamW hyperparameters unchanged;
- KCL-7 not started.

## 17. Verdict

```
KCL-6.5.3 = PASS
MODEL_OPTIMIZER_INTERACTION_ONLY
```

Architecture-gap candidate:

```
JOINT_MODEL_OPTIMIZER_TASK_BOUNDARY_COORDINATION
```

Parameter-group localization:

```
NOT EXECUTED
```

because model state alone is not sufficient for failure.

## 18. Provenance

Protocol:

`491540e5201b245f63f6d4763a086ca75711be0f`

Implementation:

`e83e5fd04fcdaab9c8f2b591de78c5b1e49e8b59`

Contract tests:

`96f85e8bbb6c1ff95c06dc36a9d94f03a3ec0f99`

Canonical scientific source:

`7ef57cb38059d084fe05a6604a8b00c67c9dadb5`

Official workflow:

`35367367265`

Focused tests:

`20 passed (10 KCL-6.5.3 + 10 KCL-6.5.2)`

Artifact:

`10557106353`

Artifact ZIP SHA-256:

`1e112e6feadc4884f4e26a7096f2783ee70dd9e11d7a9401ab39a7229c4ddc5a`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl653_summary.json`

## 19. Next scientific question

The remaining question is no longer "which parameter group is damaged?"

It is:

> Which part of AdamW state, and what task-boundary treatment of that state, is sufficient to preserve the learned model while avoiding the bad joint state?

The next experiment should decompose:

- AdamW step counter;
- first moment `exp_avg`;
- second moment `exp_avg_sq`;

and compare frozen boundary policies such as:

- carry all state;
- reset all state;
- reset first moment only;
- reset second moment only;
- restore pre-task moments while keeping post-task model parameters.

Only after that mechanism is established should an actual Task-Boundary Joint Plasticity Coordinator be implemented and tested.

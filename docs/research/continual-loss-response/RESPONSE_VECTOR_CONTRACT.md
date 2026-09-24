# CLRM-0 — Exact Continuous Response Vector

Status: **FROZEN PROGRAM-LEVEL TARGET CONTRACT**

## 1. Primary response vector

For every prospectively eligible pre-boundary state `X` and canonical policy
`a ∈ {A,B,C}`, define:

```text
R(X,a) = [
  L_current_end(X,a),
  L_prior_mean_end(X,a)
]
```

Both components are cross-entropy losses evaluated from the same post-policy,
post-training terminal state at the frozen endpoint.

Lower is better for both components.

## 2. Exact component semantics

### L_current_end

At a boundary preceding task `T_next`:

```text
L_current_end(X,a)
= terminal cross-entropy loss on T_next
  after exactly 250 next-stage training steps
  under boundary policy a
```

This is the measurement family independently qualified by MSA-1 and MSA-3.

### L_prior_mean_end

Let `P(X)` be the set of all tasks completed before the boundary.

At the exact same terminal model state used for `L_current_end`:

```text
L_prior_mean_end(X,a)
= (1 / |P(X)|) * Σ_{t in P(X)} CE_loss(t; terminal_state(X,a))
```

Every prior task contributes with equal weight.

No thresholded retention label enters this definition.

This component is justified independently of CPRM-1 outcomes by the continual
learning objective: acquisition must be studied jointly with retention.

## 3. Policy-specific surface

The direct prediction object has six channels:

```text
A.current_loss
A.prior_mean_loss

B.current_loss
B.prior_mean_loss

C.current_loss
C.prior_mean_loss
```

No channel may be removed after fresh outcome inspection.

## 4. A-relative contrasts

Contrasts are deterministic derived quantities:

```text
D_B(X) = R(X,B) - R(X,A)
D_C(X) = R(X,C) - R(X,A)
```

Each contrast has two components:

```text
[current-loss contrast, prior-mean-loss contrast]
```

Negative means the compared policy has lower loss than A on that component.

Contrasts are required diagnostics in discovery and replication, but CLRM-0
does not convert them into a controller.

## 5. Explicit discontinuity from CPRM

The CLRM primary vector is **not**:

```text
CPRM vector minus final_current_accuracy
```

and it does not contain the historical CPRM variables
`plasticity_auc`, `prior_task_retention`, or `worst_prior_accuracy`.

The vector is defined afresh in probability-sensitive CE-loss space.

## 6. No post-outcome target edits

After any CLRM fresh scientific outcome is generated, the response vector may
not be changed inside the active program.

A materially different target requires formal convergence review and a new
program.

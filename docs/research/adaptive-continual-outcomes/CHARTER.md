# ACO Charter

Status: **FROZEN PROGRAM CHARTER v0.1**

Program: **Adaptive Continual Outcome Modeling (ACO)**

Branch: `research/adaptive-continual-outcomes`

## Why ACO exists

KCL established a real structural fact inside the tested continual-learning substrate:

```text
one fixed optimizer-boundary policy
≠
uniformly good plasticity + retention + robustness
```

KCL also established that action suitability is heterogeneous, while repeated attempts to predict the derived hard mechanism `MECH{P+R,R}` from increasingly rich representations did not qualify.

ACO exists because the unresolved scientific question is no longer:

> which extra feature makes the hard classifier pass?

It is:

> can the continuous action-specific consequences that generate the hard labels be modeled prospectively and reliably enough to support adaptive continual learning later?

## Research object

At boundary state `X` and action `a ∈ {A,B,C}`, model continuous outcome vector:

```text
Y(X,a) = [
  next_task_plasticity_auc,
  next_task_final_accuracy,
  prior_task_retention,
  worst_prior_accuracy
]
```

and derived contrasts such as:

```text
ΔP_B = P_B - P_A
ΔR_B = R_B - R_A
ΔP_C = P_C - P_A
ΔR_C = R_C - R_A
```

Hard safe-action labels may be derived only **after** outcome prediction is independently evaluated.

## Capability alignment

ACO serves the original MindForge path:

```text
continual learning
→ measurable memory
→ adaptive learning
```

It is not an optimizer project in isolation.

## In scope

- target-margin / label-stability qualification;
- policy-specific continuous outcome prediction;
- action-contrast prediction;
- calibration and uncertainty;
- policy-conditioned B/C factorization if prerequisite evidence supports it;
- fresh prospective replication;
- later decision-rule qualification only after upstream PASSes.

## Out of scope now

- controller implementation;
- KCL-7;
- threshold relaxation;
- post-hoc feature rescue;
- consuming protected KCL confirmatory seeds;
- changing the KCL historical verdict;
- claiming real-language or scale generalization;
- importing a large causal-inference framework as architecture.

## Governance

Every scientific milestone must follow:

```text
hypothesis
→ preregistration
→ freeze
→ implementation
→ tests / zero-science preflight
→ fresh execution
→ one-shot adjudication
→ evidence
→ paper
→ append-only lineage
```

Technical defects may yield `REVISE`.

Scientific gate failure yields `NEGATIVE` or `STOP`.

No post-outcome threshold relaxation is permitted.

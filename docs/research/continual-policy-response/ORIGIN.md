# CPRM-0 — Origin / WHY_CPRM_EXISTS

Status: **FROZEN SPECIFICATION**

Base commit:

```text
0700601f9196d3c5989fa8eb5169f28b1bb01799
```

## 1. Why CPRM exists

CPRM exists because two evidence statements must be held simultaneously.

First, the KCL program established within its tested synthetic operating envelope:

1. controlled sequential forgetting can be reproduced;
2. bounded replay causally reduces forgetting;
3. fixed global optimizer-boundary policies do not jointly satisfy the full
   plasticity/retention/robustness contract;
4. boundary action suitability is heterogeneous and replicated;
5. B and C have qualitatively different plasticity/retention effects;
6. no hard-target boundary controller was qualified.

Second, ACO-1 terminated because its frozen hard-target prerequisite lacked
enough canonical `Y_PRR` support:

```text
required >= 30 Y_PRR boundaries
observed = 12 across stages [1,2,3]
verdict = TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

ACO-1 therefore did not test whether continuous policy responses themselves are
predictable.

## 2. Why CPRM is not ACO-2

ACO encoded this dependency:

```text
ACO-1 hard-target stability/support
        ↓ prerequisite
ACO-2 continuous outcome prediction
```

The prerequisite STOPPED by contract and the ACO convergence review terminated
the program.

CPRM instead derives its justification directly from upstream KCL structural
evidence:

```text
policy-specific effects are heterogeneous
        ↓
fixed global action is insufficient
        ↓
continuous policy responses remain an unresolved generating quantity
```

Therefore CPRM changes the population/evidence contract and cannot inherit ACO
phase numbering.

## 3. Original capability alignment

CPRM remains subordinate to the original MindForge capability path:

```text
continual learning
→ measurable memory
→ adaptive learning
```

It is not an optimizer project for its own sake.

The immediate scientific question is narrower:

> Can observable pre-boundary state predict policy-specific continuous learning
> responses and A-relative contrasts over a prospectively defined eligible
> boundary population, materially better than frozen simple baselines?

## 4. Why this question remains independently justified

The question remains justified without using ACO-1 outcome values for design
because KCL had already established before ACO:

- fixed-policy insufficiency;
- replicated action-suitability heterogeneity;
- distinct B/C plasticity-retention behavior.

Those findings imply a scientifically meaningful response surface may exist.
They do not imply that it is predictable.

## 5. Non-goals

CPRM-0 does not claim:

- continuous responses are predictable;
- a nonlinear model is needed;
- a controller is justified;
- historical hard thresholds are correct or incorrect;
- the synthetic findings transfer to real language;
- the ACO-1 data may be recycled for discovery.

No scientific execution occurs in CPRM-0.

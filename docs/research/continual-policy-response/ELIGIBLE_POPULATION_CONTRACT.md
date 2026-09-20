# CPRM-0 — Eligible Population Contract

Status: **FROZEN PROGRAM-LEVEL POPULATION CONTRACT**

## 1. Population unit

The scientific unit is a canonical continual-learning boundary from a fresh
seed trajectory.

For the current KCL-compatible four-task substrate, eligible canonical
boundaries are the transitions after:

```text
T1 → next task
T2 → next task
T3 → next task
```

A future CPRM-1 protocol may narrow the substrate only for a new independent
scientific reason committed before fresh execution. It may not select a subset
because observed responses are favorable.

## 2. Eligibility is pre-outcome

A boundary is eligible iff, before inspecting post-action scientific outcomes:

1. its seed belongs to the preregistered CPRM cohort;
2. the canonical pre-boundary trajectory/state was constructed successfully;
3. the exact A/B/C fork starts from matched model/optimizer/data state;
4. policy-identity and fork-integrity checks pass;
5. the boundary stage is part of the preregistered design.

Eligibility must not depend on:

- Y_PRR;
- A_ONLY or any other hard action label;
- whether an intervention is beneficial;
- whether a margin is near a threshold;
- the magnitude/sign of any post-action outcome.

## 3. Primary population principle

The default primary population is:

```text
ALL prospectively eligible matched boundaries
```

not a rare threshold-defined subpopulation.

This is the key population-level discontinuity from ACO-1.

## 4. Grouping / independence

Seed is the grouping unit.

All boundaries from one seed must remain in the same train/validation or
replication partition.

Boundary rows from the same seed may not be split across partitions as if they
were independent observations.

## 5. Freshness exclusions

A CPRM scientific cohort must be disjoint from:

- all historical KCL scientific seeds;
- protected KCL confirmatory seeds;
- 40 spent ACO-1 seeds;
- all previously consumed CPRM seeds outside the role explicitly allowed by a
  frozen protocol.

## 6. Support failure definition

CPRM support failure must be defined on the prospectively eligible population
and measurement availability, not on prevalence of a derived hard label.

A future protocol must freeze minimum counts by seed and stage before
execution.

It may not add seeds after outcome inspection to meet a failed support gate.

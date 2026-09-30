# Continual-Learning Portfolio Closure — 2026-10-01

Status: **FORMALLY ARCHIVED AS HISTORICAL SCIENTIFIC EVIDENCE**

This document closes the active continual-learning research chain as a portfolio program. It does not rewrite any branch-local result.

## Canonical chain

~~~text
research/kernel-cl
  ↓
research/adaptive-continual-outcomes
  ↓
research/continual-policy-response
  ↓
research/measurement-substrate-adequacy
  ↓
research/continual-loss-response
~~~

Related design-only pivot retained for provenance:

~~~text
research/cl-potential-outcomes
~~~

## What the program proved

### KCL
- reproducible forgetting substrate established;
- bounded replay causally reduced forgetting;
- 6.25% replay was effective on the frozen substrate;
- frozen replay generalized across two qualified unseen synthetic task pairs;
- policy/action effects were heterogeneous;
- the tested controller-identifiability sequence did not qualify a reliable boundary controller.

### ACO
- the frozen hard-target formulation had insufficient prospective support and was correctly stopped.

### CPRM
- continuous response geometry was partially informative;
- terminal current-task accuracy was ceiling-saturated under the frozen formulation;
- the four-component frozen target did not qualify.

### MSA
- discovery and independent replication established:
  - terminal accuracy = coarse / saturated;
  - terminal cross-entropy loss = informative.
- MSA formally converged/closed.

### CLRM
- six direct CE-loss response channels were support-qualified;
- the frozen RBF-KRR-v1 candidate was selected only on D-train;
- sealed D-val one-shot validation returned:
  `LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED`;
- baseline superiority failed;
- all-channel calibration failed;
- CLRM formal convergence closed the same-question rescue ladder.

## What capability was created

The program created **measurement and research-method capability**, not a qualified continual-learning controller.

Retained:
- bounded replay as positive synthetic research evidence;
- CE-loss response measurement on the tested substrate;
- accuracy-as-sentinel guidance;
- same-state A/B/C response extraction;
- support qualification before predictability qualification;
- seed-grouped discovery / sealed-validation separation;
- evidence preservation before reveal;
- one-shot anti-rescue adjudication.

Not retained as capability:
- CLRM-2 RBF-KRR predictor;
- B2 as production predictor;
- automatic policy selection;
- controller;
- KCL-7;
- any claim that replay or response modeling is proven on real user workloads.

## Core admission decision

No continual-learning mechanism from this chain enters MindForge core.

Only the replicated MSA measurement lesson is admitted to canonical research methodology.

## Archive state

~~~text
research/kernel-cl                    ARCHIVED / HISTORICAL
research/cl-potential-outcomes        ARCHIVED / DESIGN REFERENCE
research/adaptive-continual-outcomes  ARCHIVED / STOP
research/continual-policy-response    ARCHIVED / NEGATIVE FORMULATION
research/measurement-substrate-adequacy ARCHIVED / CONVERGED
research/continual-loss-response      ARCHIVED / CONVERGED NEGATIVE PREDICTOR
~~~

Physical branches are intentionally preserved. "Archived" means governance read-only evidence: no branch-local successor is authorized.

## Reopen rule

A future continual-learning study may open only if it asks a materially different question justified at the MindForge portfolio level.

It may not be framed as:
- KCL-7 continuation;
- CLRM-3;
- CLRM-2.x rescue;
- more RBF tuning;
- post-hoc feature selection;
- threshold relaxation;
- extra D-val seeds;
- controller rescue.

A valid reopen requires a fresh preregistered question with an independently justified capability decision.

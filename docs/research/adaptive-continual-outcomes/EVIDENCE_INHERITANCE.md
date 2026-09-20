# ACO Evidence Inheritance

Status: **FROZEN BEFORE ACO SCIENTIFIC EXECUTION**

Parent closure: `research/kernel-cl@a9159ae8f17693453e7b6378c92deb5effc4a56f`

## 1. Evidence inherited as established input

ACO may treat the following as inherited findings **within the tested KCL operating envelope**:

1. KCL-1/2 established a controlled reproducible untreated forgetting substrate.
2. KCL-3 established a causal bounded-replay anti-forgetting effect.
3. KCL-4 established 6.25% as the minimum positive replay dose representable under batch size 16 that passed the frozen contract.
4. KCL-5.2 established replay generalization across two independently qualified unseen task-pair families.
5. KCL-6 established useful four-task retention under fixed replay compute, while replay storage grew with history.
6. KCL-6.2 established exact reconstructive compression on the frozen synthetic workload.
7. KCL-6.3 established that unresolved fuzzy reconstructions used as supervised replay can fail the frozen continual-learning/plasticity contract.
8. KCL-6.4→6.5.2 established that targeted clarification can recover exact replay semantics, while later absolute acquisition failures can arise from the sequential trajectory itself.
9. KCL-6.5.3/4 established a model–optimizer interaction and AdamW moment-state contribution in the tested transition.
10. KCL-6.5.5 established that fixed A/B/C optimizer-boundary policies do not jointly satisfy plasticity + retention + robustness.
11. KCL-6.5.9.1 replicated positive action-regime heterogeneity.
12. KCL-6.5.9.4 replicated failure-mode heterogeneity including `MECH{P,R}` and `MECH{P+R,R}`.
13. KCL-6.5.9.2→.8 failed to qualify the hard `Y_PRR` target under the tested representation/information families.
14. Formal convergence closed KCL-6.5.9.x and forbade another in-family feature rescue.

## 2. Evidence inherited only as constraints, not as success claims

- Existing hard thresholds remain frozen historical definitions.
- Existing protected confirmatory seeds remain protected and untouched.
- Existing A/B/C action definitions remain canonical reference policies for ACO-1.
- Existing KCL results can define baselines and sanity checks but cannot be reused as fresh ACO validation outcomes.

## 3. Claims ACO may NOT inherit

ACO may not claim:

- `MECH{P+R,R}` is fundamentally unlearnable;
- potential outcomes are predictable;
- policy-conditioned factorization will work;
- a nonlinear model will solve the problem;
- a controller is justified;
- KCL mechanisms generalize to real language or larger models;
- exact reconstructive compression is a general memory solution;
- protected KCL confirmatory data are available for exploration.

## 4. Protected assets

The KCL protected cohort remains:

```text
13635,13837,14039,14241,14443,
14645,14847,15049,15251,15453,
15655,15857,16059,16261,16463,
16665,16867,17069,17271,17473
```

ACO must not use these seeds for discovery, protocol tuning, target-stability analysis, outcome modeling, or ablation.

## 5. Evidence provenance rule

Every ACO artifact must record:

- parent Git SHA;
- current Git SHA;
- protocol hash;
- source evidence hash;
- exact seed manifest;
- model/task/policy identity;
- result artifact SHA-256;
- whether data are inherited, development, validation, replication, or protected.

Inherited evidence is context, never a substitute for fresh prospective validation.

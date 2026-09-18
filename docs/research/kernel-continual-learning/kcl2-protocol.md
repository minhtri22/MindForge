# MindForge Kernel Continual Learning — KCL-2 Untreated Baseline Protocol

Status: **FROZEN BEFORE EXECUTION**

Prerequisite: KCL-1 PASS with `C1_TASK_PREFIX_CYCLIC`.

## Research question

Does the KCL-1 forgetting substrate remain reproducible on a disjoint final seed set, without any continual-learning treatment?

KCL-2 characterizes the untreated sequential baseline. It does not test replay or any other mitigation.

## Frozen substrate

- candidate: `C1_TASK_PREFIX_CYCLIC`
- task construction: unchanged from KCL-1
- model class: existing `mindforge.model.TransformerLM`
- model architecture change: none
- config: identical to KCL-1
- optimizer/schedule: identical to KCL-1
- matched A→A control: required

## Final seeds

```
101
202
303
707
909
```

These seeds are disjoint from KCL-1 qualification seeds `404` and `505`.

No additional seed may be added after outcome inspection.

## Per-seed branches

Each final seed must run:

1. independent A;
2. independent B;
3. A→B sequential training;
4. A→A matched-duration control from the exact post-A model and optimizer state.

## Per-seed metrics

- independent A accuracy/loss;
- independent B accuracy/loss;
- A-after-A accuracy/loss;
- A-after-B accuracy/loss;
- B-after-B accuracy/loss;
- A-after-A2 control accuracy/loss;
- absolute forgetting;
- control drift.

## Aggregate metrics

For all scalar metrics report:

- mean;
- population standard deviation;
- minimum;
- maximum.

No significance claim is made from five seeds.

## Frozen reproducibility gates

Every one of the five final seeds must satisfy:

- independent A accuracy >= 0.95;
- independent B accuracy >= 0.95;
- A-after-A accuracy >= 0.95;
- B-after-B accuracy >= 0.95;
- forgetting >= 0.50;
- absolute control drift <= 0.10.

Additional aggregate integrity gates:

- all expected five seeds present exactly once;
- all metrics finite;
- mean forgetting >= 0.50;
- maximum absolute control drift <= 0.10;
- no treatment mechanism present;
- model architecture unchanged.

## Verdicts

If all gates pass:

```
KCL-2 = PASS
UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE
```

Otherwise:

```
KCL-2 = STOP
UNTREATED_FORGETTING_BASELINE_NOT_REPRODUCIBLE
```

A PASS authorizes KCL-3 causal treatment research. A STOP blocks KCL-3 on this substrate.

## Integrity rules

- This protocol must be committed before final execution.
- No replay, rehearsal, regularization, parameter isolation, gradient constraint, memory or treatment of any kind.
- No changes to thresholds, model, task mapping, steps, batch, optimizer, or seeds after seeing final outcomes.
- Raw evidence must be preserved even on STOP.
- Workflow implementation failures that occur before scientific execution may be corrected if task/model/gates/seeds remain unchanged.
- Scientific execution must not be repeated merely to obtain a preferred result.

## Scope exclusions

PIT, OIR-PPV, PPF, RAG, agents, application memory, teachers, external APIs, distillation, reasoning, SFT and RL remain out of scope.

## Expected artifacts

```
experiments/kernel_cl/kcl2_baseline.py
experiments/kernel_cl/results/kcl2_summary.json
docs/research/kernel-continual-learning/kcl2-paper.md
.github/workflows/kernel-cl-kcl2.yml
```

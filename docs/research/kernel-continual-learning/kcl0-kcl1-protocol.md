# MindForge Kernel Continual Learning — KCL-0 / KCL-1 Protocol

Status: **FROZEN BEFORE EXECUTION**

Branch: `research/kernel-cl`

Base: `main@924654c81c08832c23ff192fdcbf63d3f2680d3a`

## Research question

Can the existing compact MindForge decoder-only kernel exhibit a reproducible continual-learning failure mode on a controlled sequential task without changing `TransformerLM`, and can that failure mode be made scientifically usable for later causal treatment experiments?

This protocol tests the substrate only. It does **not** test replay or any anti-forgetting treatment.

## Scope

In scope:

- existing `mindforge.model.TransformerLM`;
- sequential optimization;
- controlled token-level tasks;
- checkpointable/reproducible CPU experiment harness;
- acquisition, retention, forgetting and A→A control metrics.

Out of scope:

- PIT;
- OIR-PPV;
- PPF;
- RAG;
- agents/tools;
- application memory;
- teacher models or external APIs;
- distillation;
- SFT/chat alignment;
- reasoning;
- RL;
- architecture changes to `TransformerLM`.

## KCL-0 kernel audit decision

No model architecture change is authorized for KCL-1.

KCL-1 must reuse the current `TransformerLM`. The experiment may own its task generator, optimizer schedule and evaluator because the research question is sequential interference, not ordinary corpus pretraining.

## KCL-1 bounded candidate search

Candidate order is frozen:

1. `C1_TASK_PREFIX_CYCLIC`
2. `C2_TASK_PREFIX_REVERSE`
3. `C3_TASK_PREFIX_BLOCKSWAP`

The first candidate satisfying every qualification gate is selected. Search stops immediately after the first PASS.

No fourth candidate is permitted in KCL-1.

### Shared task construction

Each domain contains 24 deterministic key→value relations.

Input to the LM is two tokens:

```
[TASK_ID, KEY]
```

The supervised target is the next token:

```
VALUE
```

Domain A and B use distinct task IDs, so the two functions are jointly representable. They share the same keys and output vocabulary but use different mappings.

Therefore, inability to preserve A after learning B cannot be justified as a logically impossible requirement caused by identical unconditioned inputs.

### Candidate mappings

- C1: B is a one-position cyclic permutation of A values.
- C2: B reverses the A value mapping.
- C3: B swaps the first and second halves of the A value mapping.

## Model / optimization freeze

- vocab size: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- feed-forward multiplier: 4
- dropout: 0
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- stage steps: 250
- batch size: 16
- qualification seeds: 404, 505
- device: CPU
- loss: cross entropy on the final position only

CPU is intentional: KCL-1 qualifies the benchmark substrate, not target-machine performance.

## Required branches per candidate / seed

1. Independent A training.
2. Independent B training.
3. Sequential A→B training.
4. A→A matched-duration control from the exact post-A model/optimizer state.

## Metrics

- independent A final accuracy;
- independent B final accuracy;
- A accuracy immediately after A;
- B accuracy immediately after B in A→B;
- A accuracy after B;
- A accuracy after matched A→A control;
- forgetting = A_after_A - A_after_B;
- control drift = A_after_A - A_after_A2.

## Qualification gates

A candidate PASSes only if **both qualification seeds** satisfy all gates:

- independent A accuracy >= 0.95;
- independent B accuracy >= 0.95;
- A_after_A >= 0.95;
- B_after_B >= 0.95;
- forgetting >= 0.50 absolute accuracy;
- |control drift| <= 0.10.

Aggregate gate:

- all required metrics finite;
- candidate outcome identical in interpretation across both seeds;
- no post-outcome hyperparameter change;
- no model architecture change.

## Selection rule

Evaluate candidates in frozen order. Select the first PASS candidate.

If none PASS:

```
KCL-1 = STOP
VALID_FORGETTING_SUBSTRATE_NOT_ESTABLISHED
```

If one PASSes:

```
KCL-1 = PASS
VALID_FORGETTING_SUBSTRATE_ESTABLISHED
```

The selected candidate becomes immutable input to KCL-2.

## Integrity rules

- Protocol/gates must exist in git before result generation.
- Raw per-step or per-run evidence is machine-readable JSON.
- Results are not edited manually.
- No rerun with changed thresholds.
- Failed candidates remain preserved.
- A PASS substrate is not evidence that MindForge has continual-learning capability; it establishes only a measurable untreated forgetting problem.

## Expected artifacts

```
experiments/kernel_cl/kcl1_substrate.py
experiments/kernel_cl/results/kcl1_summary.json
docs/research/kernel-continual-learning/kcl1-paper.md
.github/workflows/kernel-cl-kcl1.yml
```

## Next gate

KCL-2 may start only if KCL-1 PASSes. KCL-2 freezes and characterizes the untreated baseline using final seeds distinct from 404/505.

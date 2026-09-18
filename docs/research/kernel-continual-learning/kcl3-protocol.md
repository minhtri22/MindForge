# MindForge Kernel Continual Learning — KCL-3 Causal Replay Treatment Protocol

Status: **FROZEN BEFORE REPLAY EXECUTION**

Prerequisites:

- KCL-1: `VALID_FORGETTING_SUBSTRATE_ESTABLISHED`
- KCL-2: `UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE`

## 1. Research question

Can a single minimal continual-learning treatment — bounded replay — causally reduce first-task forgetting on the frozen KCL substrate while preserving second-task acquisition under an equal optimizer-step and equal batch-token budget?

KCL-3 tests one treatment only. It does not compare multiple continual-learning mechanisms and does not search replay ratios.

## 2. Frozen causal contrast

For every seed, start from the same initialized MindForge `TransformerLM` and train A identically.

From the exact post-A model and optimizer state, fork two arms:

### CONTROL

Continue training on B only.

### TREATMENT

Continue training for the same number of optimizer steps and the same batch size, but each B-stage batch contains:

- 14 current-task B examples;
- 2 replayed A examples.

Total batch size remains 16.

Replay fraction:

```
2 / 16 = 12.5%
```

No replay-ratio search is authorized in KCL-3.

## 3. Why this treatment is kernel-scope

Replay is used only as a bounded training-time mechanism:

```
previous-task examples
+ current-task examples
→ mixed training batch
→ unchanged TransformerLM
```

It is not application memory, RAG, retrieval, user memory, or a persistent inference-time subsystem.

`TransformerLM` architecture remains unchanged.

## 4. Frozen substrate and model

Candidate:

`C1_TASK_PREFIX_CYCLIC`

Model/configuration must remain identical to KCL-2:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- context: 2
- FF multiplier: 4
- dropout: 0
- relations/task: 24
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- A-stage steps: 250
- B-stage steps: 250
- batch size: 16
- device: CPU
- deterministic algorithms: enabled

## 5. Frozen seeds

Use exactly the KCL-2 final seeds:

```
101
202
303
707
909
```

These seeds are used for paired causal comparison because the untreated baseline has already been characterized on them.

No extra seed may be added after outcome inspection.

## 6. Randomness contract

For each seed:

1. initialize one model;
2. train A once;
3. deep-copy the exact post-A model and optimizer state into CONTROL and TREATMENT;
4. CONTROL and TREATMENT use separate deterministic generators derived from the same seed;
5. the replay sampler must not alter model architecture or optimizer hyperparameters.

The purpose of the fork is to isolate the B-stage treatment.

## 7. Equal-budget rule

Both arms execute:

- 250 B-stage optimizer updates;
- 16 examples/update;
- 4,000 examples processed during the B stage.

CONTROL allocation:

```
4000 B
0 A replay
```

TREATMENT allocation:

```
3500 B
500 A replay
```

Therefore the treatment does not receive additional optimizer steps or additional total examples.

KCL-3 does not claim compute equality at the microsecond level; it claims equal update and example-count budget.

## 8. Primary outcomes

Per seed measure for both arms:

- A accuracy immediately after A;
- A accuracy after B-stage;
- B accuracy after B-stage;
- A loss after B-stage;
- B loss after B-stage.

Derived metrics:

```
control_forgetting
= A_after_A - CONTROL_A_after_B

treatment_forgetting
= A_after_A - TREATMENT_A_after_B

retention_gain
= TREATMENT_A_after_B - CONTROL_A_after_B

forgetting_reduction
= control_forgetting - treatment_forgetting

B_delta
= TREATMENT_B_after_B - CONTROL_B_after_B
```

## 9. Frozen causal success gates

KCL-3 PASSes only if all conditions below hold.

### Integrity gates

- exactly five frozen seeds appear once;
- all scalar metrics finite;
- post-A fork uses identical model/optimizer state;
- CONTROL receives no A replay;
- TREATMENT replay fraction is exactly 12.5%;
- same optimizer-step count and batch size in both arms;
- model architecture unchanged.

### Plasticity gate

For every seed:

```
TREATMENT_B_after_B >= 0.95
```

Replay is not allowed to "solve" forgetting by preventing B acquisition.

### Retention gate

For every seed:

```
retention_gain >= 0.30
```

### Aggregate effect gate

Across the five seeds:

```
mean(retention_gain) >= 0.50
mean(treatment_forgetting) <= 0.50
```

### Directional consistency gate

Every seed must show:

```
TREATMENT_A_after_B > CONTROL_A_after_B
```

No significance test is claimed from five seeds.

## 10. Verdicts

If every gate passes:

```
KCL-3 = PASS
BOUNDED_REPLAY_CAUSALLY_REDUCES_FORGETTING
```

If B acquisition collapses:

```
KCL-3 = FAIL
REPLAY_IMPAIRS_PLASTICITY
```

If retention improvement is insufficient:

```
KCL-3 = FAIL
REPLAY_EFFECT_INSUFFICIENT
```

If implementation/integrity prevents valid interpretation:

```
KCL-3 = REVISE
CAUSAL_CONTRAST_INVALID
```

A PASS demonstrates a causal effect on this frozen substrate only. It does not yet establish generalized continual-learning capability.

## 11. No tuning rule

After scientific execution starts, KCL-3 may not change:

- replay fraction;
- seeds;
- steps;
- batch size;
- learning rate;
- model;
- task mapping;
- gates.

A scientific FAIL is preserved.

Replay-dose exploration, if authorized later, belongs to KCL-4.

## 12. Scope exclusions

Still excluded:

- PIT
- OIR-PPV
- PPF
- RAG
- application memory
- agents
- external teacher/model APIs
- distillation
- SFT/chat alignment
- reasoning
- RL
- EWC
- DER/DER++
- parameter isolation
- gradient projection
- alternative CL mechanisms

## 13. Required artifacts

```
experiments/kernel_cl/kcl3_replay.py
experiments/kernel_cl/results/kcl3_summary.json
tests/test_kernel_cl_kcl3.py
docs/research/kernel-continual-learning/kcl3-paper.md
.github/workflows/kernel-cl-kcl3.yml
```

## 14. Authorization boundary

Only after this protocol is committed may replay treatment code be executed.

KCL-4 is not authorized by this protocol.

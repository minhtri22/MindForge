# KCL-1 — Establishing a Controlled Forgetting Substrate for the MindForge Kernel

## Abstract

MindForge previously closed Phase-0 continual-learning work with a STOP result because its bounded real-language search did not establish a scientifically usable forgetting substrate. KCL-1 reopens the question at a narrower kernel-research layer without changing the Transformer architecture. We pre-registered three controlled sequential mapping families, fixed two qualification seeds, froze model and optimizer settings, required independent learnability of both domains, successful acquisition of the second domain, measurable degradation of the first domain, and a matched A→A control. The first candidate, `C1_TASK_PREFIX_CYCLIC`, satisfied every frozen gate for both seeds. Independent A and B accuracies were 1.0, A accuracy immediately after A was 1.0, B accuracy after sequential A→B was 1.0, A accuracy after B fell to 0.0, and the matched A→A control retained A at 1.0. The resulting absolute forgetting was 1.0 for both seeds with zero control drift. This result establishes a controlled untreated-forgetting substrate for subsequent causal continual-learning experiments. It does not establish a continual-learning capability.

## 1. Introduction

The current MindForge core is a compact decoder-only language-model kernel with reproducible training, checkpointing, evaluation and experiment provenance. Historical P0.9 work attempted to identify a real-language catastrophic-forgetting benchmark but failed its pre-registered bounded search. That STOP remains valid.

The next scientific requirement is not to add a continual-learning mechanism immediately. A treatment can only be interpreted if an untreated baseline exhibits a reproducible failure that the treatment could causally improve. KCL-1 therefore asks only whether the existing kernel can exhibit controlled, reproducible forgetting on a jointly representable sequential task.

## 2. Historical Lineage

KCL-1 does not revise or relabel P0.9. The historical result remains:

```
P0.9 = STOP
real-language forgetting substrate not established under the bounded protocol
```

KCL-1 changes the experimental substrate, not the historical conclusion. It uses a controlled token-level conditional mapping so that learnability, second-task acquisition and first-task degradation can be separated cleanly.

## 3. Research Question

Can the unchanged MindForge `TransformerLM` exhibit reproducible first-task forgetting after learning a second task while:

1. each task is independently learnable;
2. the second task is successfully acquired in sequence;
3. the two tasks are jointly representable because the task identity is part of the input; and
4. a matched A→A continuation does not produce comparable degradation?

A PASS is evidence for a benchmark substrate only.

## 4. Methods

### 4.1 Model

KCL-1 reused the existing `mindforge.model.TransformerLM` without architectural modification.

Frozen model configuration:

| Field | Value |
|---|---:|
| vocabulary | 96 |
| d_model | 16 |
| heads | 2 |
| layers | 1 |
| context | 2 |
| FF multiplier | 4 |
| dropout | 0 |
| parameters | 4,880 |

### 4.2 Optimization

| Field | Value |
|---|---:|
| optimizer | AdamW |
| learning rate | 3e-3 |
| weight decay | 0 |
| steps per stage | 250 |
| batch size | 16 |
| loss | final-position cross entropy |
| device | CPU |
| qualification seeds | 404, 505 |

CPU was deliberately used because KCL-1 qualifies a benchmark substrate rather than target-machine throughput.

## 5. Frozen Protocol

The protocol was committed before successful execution at:

`docs/research/kernel-continual-learning/kcl0-kcl1-protocol.md`

Protocol SHA-256:

`3a4151f2c18a2f7f19f5396a07a61be49e9f5f84f0d2a76cc3484ba68be8087f`

Frozen candidate order:

1. `C1_TASK_PREFIX_CYCLIC`
2. `C2_TASK_PREFIX_REVERSE`
3. `C3_TASK_PREFIX_BLOCKSWAP`

The first candidate passing all gates must be selected and search must stop. No fourth candidate was authorized.

## 6. Task Construction

Each domain contains 24 deterministic key/value relations.

Input:

```
[TASK_ID, KEY]
```

Target:

```
VALUE
```

A and B use different task IDs, so the mappings are jointly representable. They share the same key set and output vocabulary but differ in the mapping from keys to values.

For C1, B is a one-position cyclic permutation of A values.

This design is important: complete A degradation after B cannot be dismissed as a logically unavoidable conflict caused by identical unconditioned inputs.

## 7. Experimental Branches

For each candidate and seed the harness runs:

1. independent A training;
2. independent B training;
3. sequential A→B training;
4. matched A→A continuation from an exact post-A copy of model and optimizer state.

Metrics include independent accuracies, A-after-A, B-after-B, A-after-B, A-after-A2 control, absolute forgetting and control drift.

## 8. Pre-registered Qualification Gates

Each of the two qualification seeds had to satisfy:

| Gate | Threshold |
|---|---:|
| independent A accuracy | >= 0.95 |
| independent B accuracy | >= 0.95 |
| A-after-A accuracy | >= 0.95 |
| B-after-B accuracy | >= 0.95 |
| absolute A forgetting | >= 0.50 |
| absolute A→A control drift | <= 0.10 |

All required metrics also had to be finite, and no post-outcome model or hyperparameter change was allowed.

## 9. Results

C1 passed all gates for both seeds, so C2 and C3 were not evaluated, exactly as required by the frozen first-PASS selection rule.

| Seed | Indep. A | Indep. B | A after A | A after B | B after B | A after A2 control | Forgetting | Control drift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 404 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 505 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Loss evidence is consistent with the accuracy result. For seed 404, A loss rose from 0.01629 after A to 9.05526 after B while B loss after B was 0.01257. For seed 505, A loss rose from 0.01745 to 8.00831 while B loss after B was 0.01592.

Final machine verdict:

```
KCL-1 = PASS
VALID_FORGETTING_SUBSTRATE_ESTABLISHED
```

## 10. Matched Control Interpretation

The A→A continuation is the critical negative control.

For both seeds:

```
A after A  = 1.0
A after A2 = 1.0
control drift = 0.0
```

Therefore the complete A collapse in A→B is not reproduced by simply extending training for the same duration from the same post-A state. Under this controlled setup, the degradation is attributable to sequential B training rather than generic continuation time alone.

## 11. CI and Integrity Audit

Official successful workflow:

- workflow: `Kernel CL — KCL-1 substrate qualification`
- run ID: `35317924719`
- source commit: `3e8deabf9cb4e0b77db42817978a553baa7a796b`
- focused tests: 4/4 PASS
- experiment step: PASS
- artifact: `kcl1-evidence`
- artifact ID: `10536050915`
- artifact ZIP SHA-256: `23a78cc640928758539e1858f39cfde1af597edf8e5bdfaab08ff54c18ce3c9d`

Four earlier workflow attempts are retained as implementation history and are not counted as scientific qualification runs:

1. run 35317190484: dynamic-import/dataclass test-loader failure; experiment skipped;
2. run 35317414382: malformed dependency command; experiment skipped;
3. run 35317551678: loader fix had not actually changed the test file; experiment skipped;
4. run 35317736356: tests passed but runner failed before training because the repository root was absent from `sys.path`.

None of these attempts reached scientific training. The first run to execute the qualifier through training was run 35317924719.

No candidate order, model configuration, seed, task mapping, scientific threshold or qualification rule was changed while fixing those CI defects.

## 12. Scope Audit

KCL-1 used:

- existing MindForge Transformer;
- optimizer/training operations;
- deterministic generated task data;
- local CPU execution;
- deterministic evaluation.

It used no:

- PIT;
- OIR-PPV;
- PPF;
- RAG;
- application memory;
- agents;
- external teacher;
- external API;
- reasoning intervention;
- distillation;
- RL.

## 13. Limitations

The result is intentionally narrow.

First, the substrate is synthetic and controlled rather than natural-language continual learning. Second, only two qualification seeds were used; they are qualification seeds, not final characterization seeds. Third, the model is a 4,880-parameter diagnostic instance of the same Transformer class, not the canonical 10.3M model. Fourth, complete forgetting on this substrate demonstrates a measurable problem but says nothing yet about whether a bounded treatment can solve it without impairing B acquisition.

Consequently, the experiment must not be interpreted as proof that MindForge already has continual-learning capability.

## 14. Conclusion

KCL-1 establishes the prerequisite that historical P0.9 did not: a controlled, reproducible untreated-forgetting substrate with successful independent learning, successful sequential B acquisition, severe A degradation and a clean matched A→A control.

The next scientific step is KCL-2: freeze and characterize the untreated baseline using previously unused final seeds. Only after that characterization may a continual-learning treatment be tested.

## Reproducibility

Focused test:

```bash
python -m pytest tests/test_kernel_cl_kcl1.py -q
```

Qualification:

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl1_substrate.py \
  --output experiments/kernel_cl/results/kcl1_summary.json
```

Canonical machine-readable evidence:

`experiments/kernel_cl/results/kcl1_summary.json`

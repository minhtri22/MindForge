# KCL-2 — Reproducibility of the Untreated Continual-Learning Failure Baseline

## Abstract

KCL-1 established a controlled sequential task on which the unchanged MindForge Transformer could learn domains A and B independently, acquire B after A, and then lose A almost completely. KCL-2 tests whether that failure substrate reproduces outside the two KCL-1 qualification seeds. The candidate, model, optimizer, task mapping, schedule and gates were frozen unchanged, and five disjoint final seeds (101, 202, 303, 707, 909) were evaluated. All five independently learned both tasks at 100% accuracy, acquired B at 100%, and retained A perfectly under a matched A→A continuation. After A→B, A accuracy ranged from 0% to 8.33%, yielding mean absolute forgetting of 97.5% (population SD 3.33 percentage points; minimum 91.67%). Every pre-registered seed-level and aggregate gate passed. KCL-2 therefore establishes a reproducible untreated forgetting baseline suitable for causal mitigation experiments.

## 1. Introduction

A continual-learning treatment is only interpretable if the untreated failure it targets is stable. KCL-1 qualified the first pre-registered task family using seeds 404 and 505. KCL-2 freezes that family and tests a new five-seed set without changing the scientific setup.

The purpose is characterization, not mitigation.

## 2. Prerequisite

KCL-1 verdict:

```
VALID_FORGETTING_SUBSTRATE_ESTABLISHED
```

Frozen candidate:

`C1_TASK_PREFIX_CYCLIC`

KCL-2 does not re-select among candidate tasks.

## 3. Research Question

Does the KCL-1 substrate continue to satisfy independent learnability, sequential B acquisition, large A forgetting, and a stable A→A negative control on five previously unused seeds?

## 4. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl2-protocol.md`

SHA-256:

`e9fc806a5921757e0d0d6ceb2ccfe1703fc05e20f9f6b36330540f0600573d57`

Final seeds:

`101, 202, 303, 707, 909`

Qualification seeds 404/505 were not reused.

## 5. Model and Optimization

KCL-2 retains the KCL-1 diagnostic instance of the actual MindForge `TransformerLM`:

- 4,880 parameters;
- vocabulary 96;
- d_model 16;
- 2 heads;
- 1 layer;
- context 2;
- dropout 0;
- AdamW;
- LR 3e-3;
- 250 steps per stage;
- batch 16;
- CPU;
- deterministic algorithms.

No model architecture change or treatment mechanism is present.

## 6. Task and Controls

Each seed executes:

1. independent A;
2. independent B;
3. sequential A→B;
4. matched A→A continuation from an exact post-A model/optimizer copy.

The A→A branch controls for degradation caused merely by continued optimization time.

## 7. Pre-registered Gates

Every final seed must satisfy:

- independent A >= 0.95;
- independent B >= 0.95;
- A-after-A >= 0.95;
- B-after-B >= 0.95;
- absolute forgetting >= 0.50;
- absolute A→A control drift <= 0.10.

All five expected seeds must be present exactly once, metrics must be finite, mean forgetting must be >= 0.50, and maximum absolute control drift must be <= 0.10.

## 8. Results

| Seed | Indep. A | Indep. B | A after A | A after B | B after B | A→A control | Forgetting |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| 202 | 1.0000 | 1.0000 | 1.0000 | 0.0417 | 1.0000 | 1.0000 | 0.9583 |
| 303 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| 707 | 1.0000 | 1.0000 | 1.0000 | 0.0833 | 1.0000 | 1.0000 | 0.9167 |
| 909 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |

Aggregate A-after-B accuracy:

- mean: 0.0250;
- population SD: 0.03333;
- min: 0;
- max: 0.08333.

Aggregate forgetting:

- mean: 0.9750;
- population SD: 0.03333;
- min: 0.91667;
- max: 1.0.

A→A control drift was exactly zero for every seed.

## 9. Gate Outcome

All seed gates passed.

All aggregate integrity checks passed:

- all metrics finite;
- final seeds present exactly once;
- all seed gates pass;
- mean-forgetting gate pass;
- max-control-drift gate pass.

Final verdict:

```
KCL-2 = PASS
UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE
```

## 10. Interpretation

The KCL-1 observation generalizes across the frozen final seed set. Learning B is consistently successful, but it nearly eliminates A performance, while continued A training does not degrade A.

This provides the controlled untreated baseline required for a causal continual-learning treatment experiment.

It does not show that any mitigation works.

## 11. Workflow and Provenance

Canonical workflow:

- run ID: `35318411840`;
- source commit: `878b4d79a9084d88f0d3c6077fa440d0f9a519b4`;
- focused unit tests: PASS;
- scientific verdict enforcement: PASS;
- artifact ID: `10535203983`;
- artifact ZIP SHA-256: `ea4da768c6a5642d26107e215c8e11940e9c1bc768eaf6082fbbaf9d7d2ac963`.

Machine-readable evidence:

`experiments/kernel_cl/results/kcl2_summary.json`

## 12. CI Integrity Note

After KCL-1 had already been closed, its original broad path trigger caused two unintended identical post-closure reruns when files under `experiments/kernel_cl/` were committed (workflow runs 35318159665 and 35318403532). They both completed successfully but are not used as KCL-1 selection evidence. The KCL-1 workflow was subsequently changed to manual dispatch only at commit `5dba6aec0a7ebf3d7a88048f281ea6406f3cfc32`.

This CI side effect does not change the KCL-1 scientific verdict, but it is recorded to avoid falsely claiming that no later identical rerun occurred.

## 13. Limitations

KCL-2 still uses a small synthetic diagnostic model and one controlled mapping family. It proves reproducibility of the failure substrate, not ecological generality. No natural-language claim, scale-transfer claim, or continual-learning treatment claim is supported yet.

## 14. Conclusion

The untreated forgetting baseline is reproducible across five final seeds and is now sufficiently stable for a controlled treatment experiment.

KCL-3 is authorized to test one minimal continual-learning treatment against this frozen baseline.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl2_baseline.py \
  --output experiments/kernel_cl/results/kcl2_summary.json
```

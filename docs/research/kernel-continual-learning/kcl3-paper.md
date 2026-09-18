# KCL-3 — Causal Effect of Bounded Replay on Catastrophic Forgetting in the MindForge Kernel

## Abstract

KCL-1 established a controlled catastrophic-forgetting substrate and KCL-2 showed that the untreated failure reproduces across five disjoint final seeds. KCL-3 tests one pre-registered continual-learning treatment only: bounded replay at 12.5% of each current-task batch. The existing MindForge `TransformerLM` was unchanged. For each seed, CONTROL and TREATMENT were forked from the exact same post-A model and optimizer state. Both arms used 250 B-stage optimizer updates, batch size 16, and 4,000 total examples. CONTROL used 16 B examples per batch; TREATMENT used 14 B plus 2 replayed A examples. Across seeds 101, 202, 303, 707, and 909, mean A accuracy after the B stage increased from 2.5% under CONTROL to 87.5% under replay, a mean retention gain of 85 percentage points. Mean forgetting fell from 97.5% to 12.5%. B accuracy remained 100% in both arms for every seed. All frozen causal, plasticity, retention, and integrity gates passed. KCL-3 therefore provides causal evidence that a small bounded replay treatment reduces forgetting on the frozen substrate without impairing acquisition of B. It does not yet establish generalized continual-learning capability.

## 1. Background

Historical MindForge continual-learning work stopped because it lacked a scientifically usable forgetting substrate. KCL-1 solved that prerequisite on a controlled task; KCL-2 demonstrated that the untreated failure was reproducible across five final seeds.

KCL-3 is the first treatment experiment in the reopened kernel-only continual-learning track.

## 2. Research Question

Can a fixed, minimal replay intervention causally improve retention of A while preserving learning of B under an equal optimizer-step and equal batch-example budget?

## 3. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl3-protocol.md`

Protocol SHA-256:

`21b489dfdeb0914bd190c85a5489aa38d2a0e00026ef09ff180e78df6b9fca40`

Protocol commit:

`088102bb1080f550b3f3bb296abb214d00ef412d`

The protocol was committed before any official replay execution.

## 4. Treatment

Frozen replay ratio:

`12.5%`

Per B-stage batch:

- CONTROL: 16 B, 0 A replay;
- TREATMENT: 14 B, 2 A replay.

Both arms:

- 250 optimizer updates;
- batch size 16;
- 4,000 total processed examples;
- same optimizer hyperparameters;
- same unchanged Transformer architecture.

KCL-3 performed no replay-ratio search.

## 5. Paired Causal Design

For each seed:

1. initialize one model;
2. train A once;
3. copy exact post-A model state into CONTROL and TREATMENT;
4. copy exact post-A optimizer state into both arms;
5. train CONTROL on B only;
6. train TREATMENT on B plus bounded replay;
7. evaluate both on A and B.

The implementation verified model-state and optimizer-state equality after the fork.

## 6. Seeds

Frozen paired seeds:

`101, 202, 303, 707, 909`

These are the same final seeds used to characterize the untreated baseline in KCL-2.

## 7. Frozen Gates

KCL-3 required:

- TREATMENT B accuracy >= 0.95 for every seed;
- retention gain >= 0.30 for every seed;
- mean retention gain >= 0.50;
- mean treatment forgetting <= 0.50;
- TREATMENT A-after-B > CONTROL A-after-B for every seed;
- all pair-integrity checks PASS;
- no architecture change;
- no replay-ratio search.

## 8. Results

| Seed | Control A after B | Replay A after B | Retention gain | Control B | Replay B | Control forgetting | Replay forgetting |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 0.0000 | 0.9583 | 0.9583 | 1.0000 | 1.0000 | 1.0000 | 0.0417 |
| 202 | 0.0417 | 0.9167 | 0.8750 | 1.0000 | 1.0000 | 0.9583 | 0.0833 |
| 303 | 0.0000 | 0.8333 | 0.8333 | 1.0000 | 1.0000 | 1.0000 | 0.1667 |
| 707 | 0.0833 | 1.0000 | 0.9167 | 1.0000 | 1.0000 | 0.9167 | 0.0000 |
| 909 | 0.0000 | 0.6667 | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 0.3333 |

Aggregate results:

| Metric | CONTROL | TREATMENT / effect |
|---|---:|---:|
| A-after-B mean | 0.0250 | 0.8750 |
| A-after-B population SD | 0.03333 | 0.11785 |
| B-after-B mean | 1.0000 | 1.0000 |
| forgetting mean | 0.9750 | 0.1250 |
| retention gain mean | — | 0.8500 |
| retention gain minimum | — | 0.6667 |
| B accuracy delta mean | — | 0.0000 |

Every seed improved directionally and every treatment seed retained perfect B accuracy.

## 9. Causal Interpretation

The paired post-A fork removes initialization and A-stage differences between arms. The B-stage total example count and update count are equal. The only planned scientific difference is that 2 of 16 treatment examples are replayed A items rather than B items.

Under this contrast, bounded replay increased mean A retention by 85 percentage points with no measured loss in B accuracy.

This supports a causal treatment effect on the frozen substrate.

## 10. Plasticity

Replay did not preserve A by refusing to learn B.

For every seed:

`TREATMENT_B_after_B = 1.0`

The frozen plasticity gate therefore passed for all five seeds.

## 11. Integrity

Canonical workflow:

- workflow: `Kernel CL — KCL-3 causal replay`
- run ID: `35330552367`
- source commit: `1f8ddc606895e4401d818dfb1ef2932f62438453`
- focused tests: `13 passed`
- scientific step: PASS
- artifact ID: `10541022481`
- artifact ZIP SHA-256: `b2e557583e67745f2b40cd766d4850bb7fcb4eb6812bd86c1c4926fff2bdf7c5`

All pair-integrity checks passed, replay-ratio search was not performed, and `TransformerLM` was unchanged.

## 12. Verdict

```
KCL-3 = PASS
BOUNDED_REPLAY_CAUSALLY_REDUCES_FORGETTING
```

## 13. What This Proves

KCL-3 proves, on the frozen KCL substrate, that a bounded replay mechanism can substantially reduce catastrophic forgetting without preventing second-task acquisition under the pre-registered budget and gates.

## 14. What This Does Not Prove

KCL-3 does not yet establish:

- the minimum effective replay dose;
- transfer to a different task family;
- performance over long task sequences;
- transfer across model scales;
- natural-language continual learning;
- a frozen general continual-learning kernel capability.

Those questions remain downstream milestones.

## 15. Scope

No PIT, OIR-PPV, PPF, RAG, agent, teacher API, distillation, reasoning, SFT, RL, EWC, DER/DER++, parameter isolation, or alternate CL mechanism was used.

Replay exists only as a training-time kernel research mechanism.

## 16. Next Scientific Step

KCL-4 may investigate the minimal effective replay boundary under a newly frozen protocol.

KCL-4 must not be interpreted as authorization to add new architectures or alternate mechanisms.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl3_replay.py \
  --output experiments/kernel_cl/results/kcl3_summary.json
```

Canonical machine-readable evidence:

`experiments/kernel_cl/results/kcl3_summary.json`

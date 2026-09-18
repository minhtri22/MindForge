# KCL-4 — Minimum Effective Replay Boundary Under Fixed Batch Granularity

## Abstract

KCL-3 established that 12.5% bounded replay strongly reduced catastrophic forgetting on the frozen MindForge continual-learning substrate. KCL-4 asks a narrower question: under the already-frozen batch size of 16, can the replay dose be reduced to the smallest representable non-zero value, 1/16 = 6.25%, while still satisfying the exact KCL-3 effectiveness contract? KCL-4 pre-registered a single new dose, 15 B + 1 replayed A sample per batch, and retained the same five paired seeds, model, optimizer, training budget, task, and gates. The low-dose treatment increased mean A-after-B accuracy from 2.5% under CONTROL to 57.5%, yielding a mean retention gain of 55 percentage points. Mean forgetting fell from 97.5% to 42.5%. B accuracy remained above the 95% plasticity gate for every seed, with mean 99.17% and minimum 95.83%. All frozen effectiveness and integrity gates passed. Because no smaller positive replay count is representable at batch size 16, KCL-4 establishes 6.25% as the minimum effective replay boundary under the current discrete batch granularity. This does not claim that 6.25% is globally optimal or that the result generalizes beyond the frozen substrate.

## 1. Background

KCL-2 established a reproducible untreated forgetting baseline. KCL-3 then showed that 12.5% replay causally increased retention without measurable loss of B acquisition.

KCL-4 does not open a new mechanism. It only asks whether the proven replay dose can be reduced to the smallest positive dose representable by the frozen batch structure.

## 2. Research Question

With batch size fixed at 16, does replaying exactly one A example per B-stage batch satisfy the same effectiveness contract used in KCL-3?

## 3. Discrete Boundary Logic

The batch size is 16.

Therefore possible integer replay fractions are:

```
0/16, 1/16, 2/16, ...
```

Relevant frozen anchors are:

- 0/16 = 0%: untreated KCL-2 baseline;
- 1/16 = 6.25%: KCL-4 test;
- 2/16 = 12.5%: KCL-3 proven treatment.

There is no representable integer replay dose strictly between 0% and 6.25%, nor between 6.25% and 12.5%, without changing batch granularity.

## 4. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl4-protocol.md`

Protocol commit:

`be71a53dfe521729de76ddab83dfc416b8b426f4`

Protocol SHA-256:

`c186bd6e3b47b1c02f0b8b6ecbd7f5d96efb71605c5b55dfaba8fe8709740fb0`

The protocol was committed before the official KCL-4 execution.

## 5. Treatment

CONTROL:

```
16 B
0 A replay
```

LOW-DOSE:

```
15 B
1 A replay
```

Replay fraction:

```
1/16 = 6.25%
```

Both arms used:

- 250 B-stage optimizer updates;
- batch size 16;
- 4,000 total processed examples;
- identical model architecture;
- identical optimizer hyperparameters;
- the same exact post-A state fork.

## 6. Seeds

Frozen seeds:

`101, 202, 303, 707, 909`

No seed was added or removed after execution.

## 7. Effectiveness Contract

The new dose had to satisfy the exact KCL-3 thresholds:

- LOW-DOSE B accuracy >= 0.95 for every seed;
- retention gain >= 0.30 for every seed;
- mean retention gain >= 0.50;
- mean low-dose forgetting <= 0.50;
- LOW-DOSE A-after-B > CONTROL A-after-B for every seed;
- full paired-state and budget integrity.

## 8. Results

| Seed | Control A after B | 6.25% A after B | Retention gain | Control B | 6.25% B | Control forgetting | 6.25% forgetting |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 0.0000 | 0.5000 | 0.5000 | 1.0000 | 0.9583 | 1.0000 | 0.5000 |
| 202 | 0.0417 | 0.6250 | 0.5833 | 1.0000 | 1.0000 | 0.9583 | 0.3750 |
| 303 | 0.0000 | 0.7083 | 0.7083 | 1.0000 | 1.0000 | 1.0000 | 0.2917 |
| 707 | 0.0833 | 0.5833 | 0.5000 | 1.0000 | 1.0000 | 0.9167 | 0.4167 |
| 909 | 0.0000 | 0.4583 | 0.4583 | 1.0000 | 1.0000 | 1.0000 | 0.5417 |

Aggregate metrics:

| Metric | CONTROL | 6.25% replay |
|---|---:|---:|
| A-after-B mean | 0.0250 | 0.5750 |
| A-after-B population SD | 0.03333 | 0.08898 |
| B-after-B mean | 1.0000 | 0.99167 |
| B-after-B minimum | 1.0000 | 0.95833 |
| forgetting mean | 0.9750 | 0.4250 |
| retention gain mean | — | 0.5500 |
| retention gain minimum | — | 0.45833 |
| B accuracy delta mean | — | -0.00833 |

## 9. Plasticity Trade-off

Unlike KCL-3 at 12.5%, the 6.25% dose produced a small measurable B-acquisition cost in one seed.

Seed 101:

```
CONTROL B = 1.0000
6.25% B  = 0.9583
delta    = -0.0417
```

This remains above the pre-registered 0.95 plasticity threshold.

Therefore KCL-4 passes the frozen contract, but the lower replay dose is closer to the stability/plasticity boundary than the 12.5% treatment.

## 10. Retention Effect

Mean A retention increased:

```
2.5% → 57.5%
```

Mean retention gain:

```
+55 percentage points
```

Mean forgetting decreased:

```
97.5% → 42.5%
```

Every seed improved A retention relative to CONTROL.

## 11. Boundary Determination

The 6.25% dose passes every frozen KCL-3 effectiveness gate.

Since batch size remains fixed at 16, one replay item is the minimum possible positive integer replay count.

Therefore:

```
MINIMUM_EFFECTIVE_REPLAY_BOUNDARY_6_25_PERCENT
```

This boundary is specific to the current frozen batch granularity and substrate.

## 12. Historical Anchors

KCL-4 validated the committed KCL-2 and KCL-3 evidence before interpretation.

KCL-2 committed evidence SHA-256:

`d93bf257f5fb052b457473a16430c222e43bdc64bb7fb72a9298d8ef8bf34038`

KCL-3 committed evidence SHA-256:

`61d3d8cb7dd3b7402a8984d4958977340370bcc72842f54dbdd8aea5078a7c0d`

Both anchor verdicts matched the expected frozen lineage.

## 13. Integrity and Provenance

Canonical workflow:

- workflow: `Kernel CL — KCL-4 minimum replay boundary`;
- run ID: `35332116173`;
- source commit: `fb3a7466909f108f49d29a0bacf3fc9fbfa55fd4`;
- focused tests: `19 passed`;
- scientific step: PASS;
- artifact ID: `10542015732`;
- artifact ZIP SHA-256: `d41c7e58c48db87a3a8dc8484b45d4eab3a2159c4ab831c3601285b4ffba3ff3`.

Integrity checks:

- exact seed set: PASS;
- post-A model-state equality: PASS;
- post-A optimizer-state equality: PASS;
- equal update budget: PASS;
- equal batch size: PASS;
- historical anchors valid: PASS;
- model architecture changed: NO;
- replay-ratio search: NO.

## 14. Verdict

```
KCL-4 = PASS
MINIMUM_EFFECTIVE_REPLAY_BOUNDARY_6_25_PERCENT
```

## 15. What This Proves

Within the frozen KCL substrate and batch size 16, one replayed prior-task example per current-task batch is sufficient to satisfy the KCL-3 anti-forgetting contract.

This is the smallest positive replay amount representable without changing batch granularity.

## 16. What This Does Not Prove

KCL-4 does not prove:

- that 6.25% is optimal for other batch sizes;
- that 6.25% generalizes to unseen task pairs;
- that replay dominates other CL mechanisms;
- that the effect persists over long task sequences;
- that the effect transfers to larger model scales;
- that MindForge has a fully qualified continual-learning capability.

Those belong to later unopened milestones.

## 17. Scope

KCL-4 introduced no:

- alternate CL mechanism;
- architecture change;
- reasoning work;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external model/API;
- distillation;
- SFT;
- RL.

## 18. Next Boundary

KCL-5 remains unopened.

No challenger mechanism is authorized by the KCL-4 experiment itself.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl4_boundary.py \
  --output experiments/kernel_cl/results/kcl4_summary.json
```

Canonical machine-readable evidence:

`experiments/kernel_cl/results/kcl4_summary.json`

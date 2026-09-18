# KCL-5.1 — Reconstructing a Second Unseen Continual-Learning Substrate

## Abstract

KCL-5 attempted to test replay generalization across two unseen task-pair families but stopped before treatment because only U1_AFFINE_PREFIX qualified as a clean untreated continual-learning substrate. KCL-5.1 therefore isolates benchmark reconstruction from mechanism evaluation. Three new unseen candidate families were pre-registered in a diversity-first order and evaluated under the original untreated qualification contract using two new seeds. Replay was prohibited. The first candidate, U3_MIXED_POSITION, qualified on both seeds and the bounded search stopped immediately as pre-registered. Independent A and B learning were 100% on both seeds; sequential B acquisition was also 100%; A forgetting was 79.17% and 66.67%; matched A→A control drift was 0% on both seeds. KCL-5.1 therefore establishes a second qualified unseen substrate without changing model architecture, optimizer, gates, or replay. Together with the previously qualified U1_AFFINE_PREFIX substrate, this restores the benchmark basis required for a clean replay-generalization experiment.

## 1. Background

KCL-5 closed with:

```
UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED
```

The failure occurred before replay execution. U1_AFFINE_PREFIX qualified, while U2_STRIDE_SUFFIX failed because one seed reached only 87.5% sequential B acquisition.

The scientific problem after KCL-5 was therefore benchmark validity, not replay effectiveness.

## 2. Research Question

Can a second unseen task-pair family satisfy the same untreated continual-learning substrate contract without consulting replay outcomes?

## 3. Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl51-protocol.md`

Protocol commit:

`af7dc5ba0c6adea1de000dabebbd00ce4068be68`

Protocol SHA-256:

`53f93f89a8a2e0c184095becf85d82cf389107a13f5d55d6afae5f5fdab9afbd`

Candidate order was frozen before execution:

1. `U3_MIXED_POSITION`
2. `U4_DISJOINT_OUTPUT_PREFIX`
3. `U5_AFFINE_PREFIX_ALT`

The first candidate passing both qualification seeds had to be selected and search had to stop.

## 4. Historical Anchor

The KCL-5 committed evidence was validated before reconstruction.

Required historical state:

- U1_AFFINE_PREFIX: qualified;
- U2_STRIDE_SUFFIX: not qualified;
- KCL-5 verdict: `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`.

Committed KCL-5 evidence SHA-256:

`32460ca4a5008004ff8ff0f8d1c3cabef4f8ebf65c52bb30db16a407bf483ac0`

Historical anchor validation passed.

## 5. Candidate U3 — MIXED_POSITION

U3 deliberately changes task-token position between A and B.

Task A input:

```
[8, KEY]
```

Task B input:

```
[KEY, 9]
```

Mappings:

```
A_index = (17*i + 4) mod 24
B_index = (19*i + 7) mod 24
```

with `i = KEY - 10`.

This family was not used in KCL-1 through KCL-5.

## 6. Frozen Qualification Contract

Qualification seeds:

```
1212
1414
```

Per-seed gates:

```
independent A >= 0.95
independent B >= 0.95
A after A >= 0.95
B after B untreated >= 0.95
forgetting >= 0.50
|A→A control drift| <= 0.10
```

The model, optimizer, step budget, batch size, and architecture remained unchanged.

## 7. Results

| Seed | Indep. A | Indep. B | A after A | A after B | B after B | Forgetting | A→A drift |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1212 | 1.0000 | 1.0000 | 1.0000 | 0.2083 | 1.0000 | 0.7917 | 0.0000 |
| 1414 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 0.6667 | 0.0000 |

Every frozen gate passed on both seeds.

## 8. Search Behavior

U3 passed immediately.

Therefore, according to the frozen first-PASS rule:

- U3 was selected;
- U4 was not executed;
- U5 was not executed;
- the pool was not extended;
- no post-outcome candidate was added.

This prevents substrate selection from becoming an unbounded benchmark search.

## 9. Replay Prohibition

KCL-5.1 executed no continual-learning treatment.

Recorded integrity values:

```
replay_calls = 0
treatment_runs = 0
```

The frozen 6.25% replay mechanism was neither changed nor executed.

## 10. Interpretation

U3 is a valid second unseen substrate under the same untreated qualification contract used throughout the KCL track.

The result is stronger than merely finding another affine mapping because U3 changes task-token position between domains:

```
A: prefix task token
B: suffix task token
```

Despite this representation shift, the kernel:

- learns A independently;
- learns B independently;
- acquires B after A;
- exhibits substantial A forgetting;
- remains stable under matched A→A continuation.

This provides a second clean environment in which replay generalization can be tested without conflating treatment effects with substrate failure.

## 11. Verdict

```
KCL-5.1 = PASS
SECOND_UNSEEN_SUBSTRATE_ESTABLISHED
```

Selected substrate:

`U3_MIXED_POSITION`

## 12. Provenance

Canonical workflow:

- workflow: `Kernel CL — KCL-5.1 unseen substrate reconstruction`;
- run ID: `35333969025`;
- source commit: `f35dfe3082b569d4d30be3b6cd0a04491861e724`;
- focused tests: `32 passed`;
- artifact ID: `10542362910`;
- artifact ZIP SHA-256: `4c61cecc02f8467d3455fed7301c3958e3efb8427ed0c57f1c1c57d11ab5257c`.

Machine-readable evidence:

`experiments/kernel_cl/results/kcl51_summary.json`

## 13. Scope

No replay, alternate CL mechanism, architecture change, long-horizon stress, scale transfer, reasoning, PIT, OIR-PPV, PPF, RAG, external API, distillation, SFT, or RL was executed.

## 14. Conclusion

KCL-5.1 repairs the benchmark layer without touching the replay mechanism.

The KCL track now has two independently qualified unseen substrates suitable for a clean generalization test:

```
U1_AFFINE_PREFIX
U3_MIXED_POSITION
```

The next experiment can therefore test the already-frozen 6.25% replay mechanism across both substrates using fresh final seeds.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl51_substrate_reconstruction.py \
  --output experiments/kernel_cl/results/kcl51_summary.json
```

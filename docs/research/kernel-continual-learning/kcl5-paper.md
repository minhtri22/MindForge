# KCL-5 — Unseen Task-Pair Generalization: Qualification Failure Before Replay Evaluation

## Abstract

KCL-1 through KCL-4 established a controlled forgetting substrate, reproducible untreated forgetting, a causal replay effect, and a minimum effective replay boundary of 6.25% under batch size 16. KCL-5 asked whether that frozen 6.25% replay mechanism generalizes to previously unseen task-pair families. Two new families were pre-registered before execution: U1_AFFINE_PREFIX and U2_STRIDE_SUFFIX. Each family first had to qualify as a valid continual-learning substrate using two fresh qualification seeds before any replay treatment could be interpreted. U1 qualified on both seeds, with independent A/B learning at 100%, sequential B acquisition at 100%, and 87.5% A forgetting. U2 qualified on seed 606 but failed on seed 808 because sequential B acquisition reached only 87.5%, below the frozen 95% gate, even though independent B learning was 100% and A forgetting remained 83.33%. According to the pre-registered protocol, final replay evaluation was therefore not executed. KCL-5 closes with `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`. This is a benchmark/substrate qualification failure, not evidence that replay itself fails to generalize.

## 1. Background

The kernel continual-learning track had accumulated the following evidence before KCL-5:

- KCL-1: valid controlled forgetting substrate established;
- KCL-2: untreated forgetting reproducible across five final seeds;
- KCL-3: 12.5% bounded replay causally reduces forgetting;
- KCL-4: 6.25% replay is the minimum effective non-zero dose under frozen batch size 16.

However, all causal treatment evidence remained tied to one task family. The next scientific threat to the claim was therefore task-pair overfitting.

KCL-5 was designed to test generalization without changing the replay mechanism.

## 2. Research Question

Does frozen 6.25% bounded replay generalize to more than one previously unseen task-pair family while preserving current-task acquisition and improving prior-task retention?

The crucial methodological requirement was that each unseen family must first exhibit a valid untreated continual-learning problem.

## 3. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl5-protocol.md`

Protocol commit:

`d318b87a066ee122ee294e6001527914c65e3eee`

Protocol SHA-256:

`6a1d4e5dbcdc0393d1a1fbf4c71d2e2088ac01a36fc10f1be0996259fcb8baf1`

The protocol was frozen before any KCL-5 qualification or treatment execution.

## 4. Frozen Replay Mechanism

Replay was inherited unchanged from KCL-4:

```
batch size = 16
15 current-task B examples
1 prior-task A replay example
replay = 6.25%
```

No replay-ratio search, family-specific tuning, optimizer modification, model change, or architecture change was authorized.

## 5. Unseen Family U1 — AFFINE_PREFIX

Input:

```
[TASK_ID, KEY]
```

Task IDs:

```
A = 4
B = 5
```

With `i = KEY - 10`:

```
A_index = (5*i + 1) mod 24
B_index = (7*i + 3) mod 24
VALUE = 40 + index
```

Both mappings are permutations of the same 24-value output set.

This mapping was not present in KCL-1 through KCL-4.

## 6. Unseen Family U2 — STRIDE_SUFFIX

Input:

```
[KEY, TASK_ID]
```

Task IDs:

```
A = 6
B = 7
```

With `i = KEY - 10`:

```
A_index = (11*i + 5) mod 24
B_index = (13*i + 2) mod 24
VALUE = 40 + index
```

Unlike prior KCL families, the task identity appears in the second input position.

## 7. Qualification Design

Qualification seeds:

```
606
808
```

For each family and each qualification seed:

1. train A independently;
2. train B independently;
3. train A then B sequentially without treatment;
4. run matched A→A continuation;
5. evaluate learnability, B acquisition, A forgetting, and control drift.

Frozen per-seed gates:

```
independent A >= 0.95
independent B >= 0.95
A after A >= 0.95
B after B untreated >= 0.95
untreated forgetting >= 0.50
|A→A control drift| <= 0.10
```

Both unseen families had to pass both qualification seeds before final replay evaluation could begin.

## 8. U1 Qualification Results

U1 passed both qualification seeds.

| Seed | Indep. A | Indep. B | A after A | A after B | B after B | Forgetting | A→A drift |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 606 | 1.0000 | 1.0000 | 1.0000 | 0.1250 | 1.0000 | 0.8750 | 0.0000 |
| 808 | 1.0000 | 1.0000 | 1.0000 | 0.1250 | 1.0000 | 0.8750 | 0.0000 |

U1 therefore constitutes a valid unseen continual-learning substrate under the frozen qualification contract.

## 9. U2 Qualification Results

U2 passed seed 606 but failed seed 808.

| Seed | Indep. A | Indep. B | A after A | A after B | B after B | Forgetting | A→A drift | Qualification |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 606 | 1.0000 | 1.0000 | 1.0000 | 0.1667 | 1.0000 | 0.8333 | 0.0000 | PASS |
| 808 | 1.0000 | 1.0000 | 1.0000 | 0.1667 | **0.8750** | 0.8333 | 0.0000 | **FAIL** |

The failing metric was:

```
B_after_B = 0.875
required >= 0.95
```

## 10. Interpretation of the U2 Failure

The failure is not caused by inability to learn B in isolation:

```
independent B accuracy = 1.0
```

Nor is it caused by absence of interference:

```
A forgetting = 0.8333
```

Instead, the sequential A→B run on seed 808 does not fully acquire B under the frozen training budget.

That makes U2 unsuitable as a clean treatment-generalization substrate under the current protocol because a replay intervention could not be interpreted cleanly against a baseline that already fails the required B-acquisition condition.

## 11. Why Final Replay Evaluation Was Not Run

The frozen protocol required:

```
both unseen families qualify
→ only then run final replay evaluation
```

Because U2 did not qualify, the harness correctly produced:

```
final_generalization = []
```

and stopped before using final seeds:

```
111, 222, 333, 777, 999
```

Those final seeds therefore remain unconsumed by KCL-5 treatment evaluation.

## 12. Verdict

Final KCL-5 verdict:

```
KCL-5 = FAIL
UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED
```

This verdict follows the pre-registered rule exactly.

## 13. What This Result Proves

KCL-5 establishes two useful facts:

1. U1_AFFINE_PREFIX is a valid unseen forgetting substrate under the frozen qualification gates.
2. U2_STRIDE_SUFFIX is not sufficiently stable as an untreated sequential substrate under the same budget, because B acquisition falls below threshold in one qualification seed.

## 14. What This Result Does Not Prove

KCL-5 does **not** show that:

- 6.25% replay fails on U1;
- 6.25% replay fails on U2;
- replay does not generalize;
- the kernel lacks continual-learning generalization;
- another replay dose is required.

The replay treatment was never executed in KCL-5 because the benchmark qualification precondition failed.

Therefore the correct interpretation is **substrate insufficiency**, not mechanism failure.

## 15. Methodological Importance

Running the replay treatment anyway would create an ambiguous result.

For U2 seed 808, untreated B acquisition was only 87.5%. If replay then changed A/B performance, it would be unclear whether the result reflected:

- anti-forgetting behavior;
- reduced or improved B acquisition;
- a budget-specific optimization issue;
- interaction with the new suffix task representation.

The qualification gate prevented that ambiguity.

## 16. Integrity

Canonical workflow:

- workflow: `Kernel CL — KCL-5 unseen task-pair generalization`;
- run ID: `35333101201`;
- source commit: `83aa689485e8cb6fcf5e3b1382af59ac3bc319ed`;
- focused tests: `25 passed`;
- scientific qualification step: completed;
- artifact ID: `10541668631`;
- artifact ZIP SHA-256: `a2f94c38caadd8e4cef489adb0086b8643478f1a9d28340e5da817ea832d8e73`.

Integrity properties:

- model architecture changed: NO;
- prior KCL seeds reused: NO;
- qualification/final seed overlap: NO;
- family selection performed: NO;
- replay-ratio search: NO;
- family-specific adaptation: NO;
- final replay execution: NO.

## 17. Scope

KCL-5 introduced no:

- challenger mechanism;
- EWC;
- DER/DER++;
- parameter isolation;
- gradient projection;
- scale experiment;
- long-horizon experiment;
- reasoning work;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external API;
- distillation;
- SFT;
- RL.

## 18. Scientific Consequence

The next scientific obstacle is no longer the replay mechanism itself.

The obstacle is obtaining at least two stable, previously unseen task-pair substrates that satisfy the same untreated acquisition/forgetting contract before replay generalization can be tested.

KCL-6 long-horizon stress should **not** start from this result because unseen-pair generalization remains untested.

## 19. Conclusion

KCL-5 produced a valid negative result at the benchmark qualification stage.

U1 generalized the forgetting substrate successfully. U2 exposed a new failure mode: the kernel can learn B independently but does not always acquire B to the required level after A under the fixed sequential budget.

The correct next scientific step is to reconstruct the unseen-generalization benchmark layer without modifying the frozen replay mechanism, and only then resume replay generalization testing.

## Reproducibility

```bash
PYTHONPATH=. python experiments/kernel_cl/kcl5_unseen_generalization.py \
  --output experiments/kernel_cl/results/kcl5_summary.json
```

Canonical evidence:

`experiments/kernel_cl/results/kcl5_summary.json`

# MindForge Kernel Continual Learning — KCL-6.4 Uncertainty-Aware Clarification & Reactivation Protocol

Status: **FROZEN BEFORE ANY KCL-6.4 SCIENTIFIC EXECUTION**

Prerequisite:

- KCL-6.3 is permanently closed as:
  - status = `FAIL`
  - verdict = `FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY`
- KCL-6.3 frozen strict gate is not amended or reinterpreted.
- Its positive sub-results remain:
  - fuzzy trace recoverability = PASS;
  - relearning advantage = PASS;
  - storage reduction = PASS;
  - active fuzzy supervised replay/plasticity = FAIL.

## 1. Research question

Does the KCL-6.3 failure arise from the fuzzy trace itself, or from using an uncertain fuzzy reconstruction as if it were a ground-truth supervised replay target?

KCL-6.4 keeps the failed D memory representation unchanged and introduces one new policy E:

> when a replay memory cannot determine a unique target, do not guess; request the minimum disambiguating cue, reactivate the exact schema, then replay.

## 2. Frozen arms

### D — FUZZY_GUESS_REPLAY

D is exactly KCL-6.3:

- exact schema decays after one subsequent completed task;
- exact offset removed;
- support count removed;
- offset retained only as width-4 bucket;
- fuzzy replay samples a candidate offset uniformly inside the bucket;
- sampled reconstruction is used as a supervised replay target.

D is rerun in KCL-6.4 as a paired failure control.

### E — FUZZY_ASK_REACTIVATE

E uses exactly the same memory representation and decay schedule as D.

The sole policy difference is:

```
if replay memory is exact:
    replay directly
else:
    ASK one minimum clarification cue
    reactivate exact schema
    replay exact target
```

E never guesses an uncertain target.

## 3. D failure remains frozen

KCL-6.4 must verify the committed KCL-6.3 evidence:

```
status = FAIL
verdict = FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY
H1 = true
H2 = false
H3 = true
H4 = true
```

KCL-6.4 does not modify the KCL-6.3 verdict even if E succeeds.

## 4. Frozen memory representation

Both D and E use:

### Exact state

The KCL-6.2 exact reconstructive schema.

### Fuzzy state

Retain:

- varying input position;
- constant context token;
- key_min;
- output_min;
- modulus;
- multiplier;
- offset_bucket_low.

Discard:

- exact offset;
- support count.

Frozen bucket width:

```
4
```

No raw episodes are retained inside fuzzy memory.

## 5. Frozen decay age schedule

Exactly KCL-6.3:

```
during T2:
T1 exact

after T2:
T1 fuzzy

during T3:
T1 fuzzy
T2 exact

after T3:
T1 fuzzy
T2 fuzzy

during T4:
T1 fuzzy
T2 fuzzy
T3 exact

after T4:
T1 fuzzy
T2 fuzzy
T3 fuzzy
T4 exact
```

Reactivation inside a stage does not disable future decay.

At the end of the current stage, any reactivated prior memory ages back to fuzzy under the same one-subsequent-task decay rule.

## 6. Frozen clarification trigger

E may ASK only when all are true:

1. the selected replay source is fuzzy;
2. more than one offset remains consistent with stored memory;
3. this replay source has not already been clarified in the current stage.

No proactive queries.

No queries for exact memories.

No repeated query for the same task within the same stage.

## 7. Minimum clarification cue

The clarification environment returns one exact observation for:

```
key = key_min
```

For the frozen affine schema class:

```
target_index(key_min) = exact offset b
```

so one cue uniquely identifies the missing offset.

The cue consists of:

```
(input_token_0, input_token_1, target)
```

for the single `key_min` observation.

## 8. Query use restriction

The clarification cue:

- may update E memory state;
- may restore the exact offset;
- may reactivate the exact schema.

The clarification cue must **not**:

- be inserted into the training batch;
- receive a gradient update by itself;
- create an episodic replay record;
- increase replay slots;
- increase optimizer steps;
- be retained as raw data after schema reactivation.

Thus E receives side information but not extra training examples.

## 9. Frozen expected query opportunities

Under the frozen task stream and decay schedule:

### T2

T1 exact:

```
queries = 0
```

### T3

T1 fuzzy, T2 exact:

```
queries = 1
```

### T4

T1 fuzzy, T2 fuzzy, T3 exact:

```
queries = 2
```

Expected total:

```
3 clarification queries / seed
```

Any deviation is an integrity failure.

## 10. Frozen task stream

Exactly:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

## 11. Frozen seeds

Exactly the KCL-6.3 paired seeds:

```
3333
3535
3737
3939
4141
```

No substitutions or selective reruns.

## 12. Frozen model / optimizer

Exactly KCL-6.3:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- FF multiplier: 4
- dropout: 0
- optimizer: AdamW
- learning rate: 3e-3
- weight decay: 0
- steps/task: 250
- batch size: 16
- CPU
- deterministic algorithms enabled.

## 13. Frozen replay compute

Both D and E use:

```
15 current examples
1 replay example
batch size = 16
replay fraction = 6.25%
```

Clarification does not change this budget.

## 14. Paired causal design

For each seed:

1. train T1 once;
2. fork exact post-T1 model + optimizer state into D and E;
3. run identical current-task batches;
4. use identical replay source-task schedule;
5. use identical logical replay ranks;
6. D applies frozen fuzzy guessing policy;
7. E applies clarification-before-replay policy.

This isolates the policy applied to uncertainty.

## 15. Frozen strict plasticity gate

The KCL-6.3 gate remains unchanged for E:

For every seed:

```
E_final_T4_accuracy >= 0.95
```

No relaxation to 0.90 or 0.9167 is allowed.

## 16. Frozen retention gate

For every seed:

```
E_final_mean_prior_accuracy >= 0.25
```

Across seeds:

```
mean(E_final_mean_prior_accuracy) >= 0.35
```

and relative to exact reconstructive C historical anchor:

```
mean(E_final_mean_prior_accuracy)
>=
0.50 * mean(C_final_mean_prior_accuracy)
```

These are the same trace-retention requirements used for D in KCL-6.3.

## 17. Paired D→E causal-improvement gates

For every seed:

```
E_final_T4_accuracy >= D_final_T4_accuracy
```

and:

```
E_final_mean_prior_accuracy > D_final_mean_prior_accuracy
```

Across seeds:

```
mean(E_prior - D_prior) >= 0.10
```

and:

```
mean(E_T4 - D_T4) > 0
```

No cross-seed compensation may reverse a seed-level prior-retention loss.

## 18. Exact replay restoration gate

For E:

After clarification, every replay observation sourced from the reactivated task must match the exact canonical replay observation.

Required:

```
E exact replay match rate = 1.0
```

for T2, T3 and T4.

This verifies that E is not still replaying uncertain pseudo-targets after asking.

## 19. Query-efficiency metrics

Report:

- total clarification queries;
- queries per stage;
- queries per fuzzy task;
- mean prior-retention improvement over D per query;
- T4 accuracy improvement over D per query;
- exact replay errors avoided relative to D.

Primary query-efficiency metric:

```
prior_gain_per_query =
(E_final_mean_prior_accuracy - D_final_mean_prior_accuracy)
/
total_queries
```

No minimum is imposed beyond the causal-improvement gates.

## 20. Storage accounting

Persistent post-stage memory remains the D fuzzy representation.

Final E storage must be:

```
143 bytes
```

matching D:

```
T1 fuzzy = 34
T2 fuzzy = 34
T3 fuzzy = 34
T4 exact = 41
total = 143
```

Reactivation may temporarily raise in-stage schema resolution.

Report peak transient schema bytes.

Frozen persistent-storage gate:

```
E_final_bytes = D_final_bytes = 143
```

## 21. Historical exact-memory reference

KCL-6.2 C remains the exact-memory reference.

KCL-6.4 must report E-C deltas but does not require exact equality as the primary gate.

If E replay observations are exact after clarification and paired training streams remain identical, equality may emerge as an empirical result.

## 22. Verdicts

### D reproduces failure + E passes strict CL gates + paired improvement + query integrity

```
KCL-6.4 = PASS
CLARIFICATION_REACTIVATION_RESCUES_FUZZY_MEMORY_POLICY
```

### E passes but D no longer reproduces the frozen failure condition

```
KCL-6.4 = REVISE
FUZZY_FAILURE_CONTROL_NOT_REPRODUCED
```

### E still violates strict plasticity/retention gates

```
KCL-6.4 = FAIL
CLARIFICATION_DOES_NOT_RESCUE_FUZZY_MEMORY
```

### Queries exceed frozen opportunities or cue enters gradient/replay storage

```
KCL-6.4 = REVISE
CLARIFICATION_CONTRAST_INVALID
```

## 23. D failure reproduction requirement

D is considered reproduced if:

1. it uses the same frozen representation/policy;
2. at least one original KCL-6.3 H2 failure condition remains:
   - any seed T4 < 0.95, or
   - H2 aggregate/retention condition fails;
3. its aggregate metrics are consistent with the committed KCL-6.3 evidence within one task-resolution tolerance:

```
1/24
```

## 24. No tuning rule

After protocol freeze do not change:

- bucket width;
- decay schedule;
- query trigger;
- cue key;
- query count;
- seeds;
- task order;
- replay budget;
- strict 0.95 T4 gate;
- retention gates;
- improvement gates.

No adaptive query strategy may be added after outcome inspection.

## 25. Scope exclusions

KCL-6.4 does not authorize:

- changing fuzzy representation D;
- semantic embeddings;
- prototype clustering;
- natural-language questioning claims;
- KCL-7 model-scale transfer;
- architecture changes;
- reasoning;
- PIT;
- OIR-PPV;
- PPF;
- RAG;
- external model APIs;
- distillation;
- SFT;
- RL.

## 26. Required artifacts

```
experiments/kernel_cl/kcl64_clarification_reactivation.py
experiments/kernel_cl/results/kcl64_summary.json
tests/test_kernel_cl_kcl64.py
docs/research/kernel-continual-learning/kcl64-paper.md
.github/workflows/kernel-cl-kcl64.yml
```

## 27. Closure requirement

KCL-6.4 closes only after:

- this protocol is committed before execution;
- focused tests PASS;
- one official paired D/E execution;
- raw evidence is preserved;
- paper is written;
- Lineage is appended.

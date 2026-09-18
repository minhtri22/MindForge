# MindForge Kernel Continual Learning — KCL-6.5 Clarification Specificity Matched-Query A/B Protocol

Status: **FROZEN BEFORE MAIN KCL-6.5 SCIENTIFIC EXECUTION**

Prerequisites:

- KCL-6.3 = FAIL / `FUZZY_DECAY_DESTROYS_USEFUL_CONTINUAL_MEMORY`.
- KCL-6.4 = PASS / `CLARIFICATION_REACTIVATION_RESCUES_FUZZY_MEMORY_POLICY`.
- KCL-6.5-Q = PASS / `MATCHED_QUERY_CONTROL_QUALIFIED`.

KCL-6.5-Q established:

- targeted cue reduces the queried fuzzy offset set `4 -> 1`;
- placebo cue leaves it `4 -> 4`;
- query timing/payload envelope can be matched;
- placebo querying is operationally null-equivalent to D;
- no cross-task resolver is used.

## 1. Research question

Does the KCL-6.4 rescue depend specifically on receiving **task-relevant disambiguating information**, rather than merely:

- issuing a query;
- receiving a ground-truth external response;
- receiving a 3-tuple payload;
- query timing;
- query count?

## 2. Main arms

### E — TARGETED_CLARIFICATION

Exactly the KCL-6.4 policy:

When selected replay memory is fuzzy:

1. query one exact `key_min` observation from the **same fuzzy prior task**;
2. reduce offset candidates from 4 to 1;
3. reactivate exact schema;
4. replay exact target.

### F — MATCHED_PLACEBO_QUERY

F uses the same fuzzy representation and the same query opportunities.

When selected replay memory is fuzzy:

1. issue one query at the same time as E;
2. receive one exact `key_min` observation from the **current task being trained**;
3. queried prior-task offset candidates remain 4;
4. prior fuzzy memory is unchanged;
5. F continues with the frozen D fuzzy-guess replay rule.

F is the qualified operational-null query control from KCL-6.5-Q.

## 3. What is matched

E and F must match:

- query opportunities;
- query count;
- response tuple arity = 3;
- ground-truth status of returned tuple;
- no-gradient rule;
- no-storage rule;
- replay source-task schedule;
- logical replay ranks;
- current-task batches;
- optimizer steps;
- processed examples;
- replay slots;
- persistent memory representation;
- decay schedule.

## 4. What is deliberately different

The sole causal variable is relevance of the response to the uncertainty being resolved.

### E

```
same-task cue
candidate offsets: 4 -> 1
```

### F

```
current-task placebo cue
candidate offsets: 4 -> 4
```

KCL-6.5 does not claim E and F responses have equal mutual information about the queried prior memory. That difference is precisely the manipulated variable.

## 5. Query restrictions

For both arms, query responses:

- do not enter the training batch;
- receive no gradient;
- do not create extra optimizer updates;
- do not create extra replay slots;
- are not retained as raw episodic memory.

E may update only the queried prior schema's missing offset.

F may not update the queried prior schema.

## 6. Frozen representation and decay

Identical to KCL-6.3/KCL-6.4:

- bucket width = 4;
- exact offset removed after one subsequent completed task;
- support count removed;
- structural schema retained;
- final persistent state after T4:
  `[fuzzy, fuzzy, fuzzy, exact]`.

Persistent final storage:

```
143 bytes
```

for both E and F.

## 7. Frozen task stream

Exactly:

```
T1 = U1_AFFINE_PREFIX / A
T2 = U1_AFFINE_PREFIX / B
T3 = U3_MIXED_POSITION / A
T4 = U3_MIXED_POSITION / B
```

## 8. Fresh confirmatory seeds

Use exactly:

```
4343
4545
4747
4949
5353
```

These were not used in KCL-1 through KCL-6.4 or KCL-6.5-Q.

No seed replacement or selective rerun.

## 9. Frozen model / optimizer

Exactly prior diagnostic kernel:

- vocabulary: 96
- d_model: 16
- heads: 2
- layers: 1
- max context: 2
- FF multiplier: 4
- dropout: 0
- AdamW
- learning rate: 3e-3
- weight decay: 0
- 250 steps/task
- batch size 16
- deterministic CPU execution.

## 10. Frozen replay compute

Both arms:

```
15 current + 1 replay
batch = 16
replay fraction = 6.25%
```

## 11. Frozen query schedule

Per seed:

```
T2: 0
T3: 1
T4: 2
total: 3
```

Any deviation is REVISE.

## 12. Candidate-set integrity

For every E query:

```
candidate count before = 4
candidate count after = 1
```

For every F query:

```
candidate count before = 4
candidate count after = 4
```

Any violation is REVISE.

## 13. Replay-target correctness

For E:

```
exact replay match rate = 1.0
```

at every stage.

For F:

- T2 exact match must equal 1.0 because no fuzzy source exists;
- at T3/T4, F must remain on fuzzy-guess policy;
- F is not required to hit a preselected exact-match percentage, but must not use targeted reactivation.

## 14. Strict current-task gate

Keep the original strict gate:

For every seed:

```
E_final_T4_accuracy >= 0.95
```

No relaxation.

F is a control and is not required to fail T4 on every fresh seed.

## 15. Prior-retention gate for E

For every seed:

```
E_final_mean_prior_accuracy >= 0.25
```

Across seeds:

```
mean(E_final_mean_prior_accuracy) >= 0.35
```

and:

```
mean(E_final_mean_prior_accuracy)
>=
0.50 * historical_C_mean_prior
```

with frozen historical:

```
historical_C_mean_prior = 0.6750000019868214
```

## 16. Specificity-effect gate

For every seed:

```
E_final_mean_prior_accuracy
>
F_final_mean_prior_accuracy
```

Across seeds:

```
mean(E_prior - F_prior) >= 0.10
```

Also:

```
E_final_T4_accuracy >= F_final_T4_accuracy
```

for every seed, and:

```
mean(E_T4 - F_T4) >= 0
```

The key confirmatory endpoint is prior retention, not requiring placebo F to fail current-task learning on every seed.

## 17. Placebo operational-null confirmation on fresh seeds

F must retain the qualified control contract:

- query does not update prior memory;
- query does not enter gradient;
- query does not enter storage;
- F replay behavior is the frozen fuzzy-guess policy.

Where a historical D comparator is available only on different seeds, no numeric equality to historical D is required.

Instead, main-run operational integrity is established by:

- candidate set remains 4;
- no prior-memory update;
- same fuzzy RNG/replay mechanism as D;
- no query-derived training data.

## 18. Query-efficiency metrics

Report:

```
specificity_gain_per_query =
(E_mean_prior - F_mean_prior) / 3
```

Also report:

- exact replay errors avoided by E relative to F;
- T4 gain/query;
- worst-prior gain;
- query count and timing.

No universal interpretation is permitted.

## 19. Storage gate

Final persistent storage:

```
E = 143 bytes
F = 143 bytes
```

Queries must not increase persistent storage.

## 20. Hypotheses

### H-S1 — Target specificity

Only E reduces uncertainty `4 -> 1`; F remains `4 -> 4`.

### H-S2 — Matched-query null

F's query mechanism does not itself alter replay memory or optimization.

### H-S3 — Targeted information improves CL

E improves final prior retention over F on every fresh seed and by >= 0.10 mean.

### H-S4 — Strict plasticity retained

E passes the unchanged 0.95 T4 gate on every seed.

### H-S5 — Query/storage integrity

Both arms use exactly 3 queries/seed and 143-byte final persistent memory; no cue enters gradient.

## 21. Verdicts

All H-S1 through H-S5 PASS:

```
KCL-6.5 = PASS
TARGETED_CLARIFICATION_SPECIFICITY_CAUSALLY_CONFIRMED
```

Matched-query integrity fails:

```
KCL-6.5 = REVISE
MATCHED_QUERY_AB_INVALID
```

E strict CL gate fails:

```
KCL-6.5 = FAIL
TARGETED_CLARIFICATION_NOT_CONFIRMATORY_ON_FRESH_SEEDS
```

E passes strict CL but specificity-effect gate fails:

```
KCL-6.5 = NEGATIVE
QUERY_OCCURRED_BUT_SPECIFICITY_EFFECT_NOT_CONFIRMED
```

## 22. No tuning rule

After freeze do not change:

- placebo source;
- query schedule;
- cue key;
- seed set;
- decay;
- bucket width;
- replay budget;
- strict gate;
- specificity-effect threshold;
- storage accounting.

No second placebo is introduced after seeing outcome.

## 23. Scope exclusions

KCL-6.5 does not establish:

- autonomous question generation;
- discovery of missing fields in arbitrary memories;
- natural-language clarification;
- optimal query selection;
- equal Shannon information between targeted/placebo replies;
- model-scale transfer.

KCL-7 remains unopened until KCL-6.5 closes.

## 24. Required artifacts

```
experiments/kernel_cl/kcl65_specificity_ab.py
experiments/kernel_cl/results/kcl65_summary.json
tests/test_kernel_cl_kcl65.py
docs/research/kernel-continual-learning/kcl65-paper.md
.github/workflows/kernel-cl-kcl65.yml
```

## 25. Closure requirement

- protocol committed before execution;
- focused tests PASS;
- one official E/F A/B execution;
- raw evidence preserved;
- paper written;
- Lineage appended.

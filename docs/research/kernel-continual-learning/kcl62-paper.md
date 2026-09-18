# KCL-6.2 — Reconstructive Memory Consolidation A/B/C

## Abstract

KCL-6.2 compares three replay-memory representations under the exact KCL-6.1 workload, seeds, replay compute, optimizer budget, and task order:

- A: raw episodic replay;
- B: weighted exact replay;
- C: reconstructive schema + exact residual exceptions.

C receives only observed `(input0,input1,target)` tuples. It infers the varying input position, searches an affine-modular schema, and stores any non-matching observations as residual exceptions. All four tasks were represented by one 41-byte schema each with zero residuals. At T4, logical memory fell from 2304 bytes in A and 2688 bytes in B to 164 bytes in C: 14.05× compression versus A and 16.39× versus B. Replay observations reconstructed by C matched A/B exactly, final continual-learning behavior was identical on every seed/task, and fresh-model learning curves from reconstructed datasets matched the original datasets exactly.

Verdict:

```
KCL-6.2 = PASS
RECONSTRUCTIVE_SCHEMA_COMPRESSES_REPLAY_WITHOUT_CL_LOSS
```

## 1. Research Question

Can full-resolution episodic replay be replaced by:

```
CoreSchema + ResidualExceptions
```

while preserving continual-learning behavior and materially reducing replay storage?

## 2. Frozen Protocol

Protocol:

`docs/research/kernel-continual-learning/kcl62-protocol.md`

Protocol commit:

`47939b37e4e86b641256cc90047426c01f978bca`

Protocol SHA-256:

`3a410c65ee4658244b8465efd712720d67b1106494a0a080adb715d926e292ef`

Frozen task sequence:

```
T1 = U1-A
T2 = U1-B
T3 = U3-A
T4 = U3-B
```

Frozen seeds:

```
3333, 3535, 3737, 3939, 4141
```

Replay remained:

```
15 current + 1 replay
batch = 16
replay = 6.25%
```

## 3. Arm Definitions

### A — RAW_EPISODIC

Store every observation:

```
(input0, input1, target)
```

Logical size:

```
24 bytes / observation
```

### B — WEIGHTED_EXACT

Store:

```
exact observation -> multiplicity
```

Logical size:

```
28 bytes / unique observation
```

### C — RECONSTRUCTIVE_SCHEMA_PLUS_RESIDUALS

C receives only observations. It does not receive family names or source mapping constants.

The fitter:

1. detects which input position varies;
2. infers constant task token, key range, output band, and modulus;
3. searches all `a,b` in `0..N-1`;
4. fits:

```
target_index = (a * key_index + b) mod N
```

5. stores every mismatch as an exact residual exception.

A C store is accepted only if schema + residuals reconstruct the complete observed task exactly.

Logical schema size:

```
41 bytes / task
```

Residual:

```
24 bytes / exception
```

## 4. Schema Discovery

All four tasks achieved:

```
coverage = 1.0
residual_count = 0
reconstruction_exact = true
```

Discovered schemas:

| Task | Varying pos | Token | a | b | N |
|---|---:|---:|---:|---:|---:|
| T1 U1-A | 1 | 4 | 5 | 1 | 24 |
| T2 U1-B | 1 | 5 | 7 | 3 | 24 |
| T3 U3-A | 1 | 8 | 17 | 4 | 24 |
| T4 U3-B | 0 | 9 | 19 | 7 | 24 |

The parameters were inferred from observations by the frozen search procedure.

## 5. Storage Results

At T4:

| Arm | Logical bytes |
|---|---:|
| A RAW | 2304 |
| B WEIGHTED_EXACT | 2688 |
| C RECONSTRUCTIVE | **164** |

Compression:

```
A / C = 14.0488×
B / C = 16.3902×
```

C residual rate:

```
0.0
```

Frozen storage gate required:

```
A/C >= 2.0
residual_rate <= 0.25
```

Both passed.

## 6. Continual-Learning Behavior

Final mean prior-task accuracy:

```
A = 0.6750
B = 0.6750
C = 0.6750
```

Across every seed and every T1-T4:

```
C accuracy - A accuracy = 0
C accuracy - B accuracy = 0
```

Per-seed final mean prior accuracy:

| Seed | A | B | C |
|---:|---:|---:|---:|
| 3333 | 0.6944 | 0.6944 | 0.6944 |
| 3535 | 0.5139 | 0.5139 | 0.5139 |
| 3737 | 0.7639 | 0.7639 | 0.7639 |
| 3939 | 0.6250 | 0.6250 | 0.6250 |
| 4141 | 0.7778 | 0.7778 | 0.7778 |

C T4 accuracy remained >= 0.95 on every seed.

Behavioral-equivalence gate: **PASS**.

## 7. Replay Equivalence

For paired replay rank `r`, A/B/C produced the same replay observation.

Thus KCL-6.2 changed memory representation, not replay evidence.

This explains the exact equality in observed CL behavior.

## 8. Relearning-Trace Probe

For every task, a fresh model was trained on:

1. the original raw task dataset;
2. the dataset reconstructed from C.

For all four tasks:

```
dataset_equal = true
learning_curves_equal = true
final_model_states_equal = true
```

Learning curves at steps 0/50/100/150/200/250 were identical.

This proves that C retains enough information to recreate the original learning problem exactly.

It does not yet prove faster relearning from a degraded or incomplete memory.

## 9. Hypothesis Outcomes

### H1 — Exact Reconstruction

**PASS**

### H2 — Continual-Learning Equivalence

**PASS**

### H3 — Meaningful Storage Reduction

**PASS**

## 10. Scientific Interpretation

KCL-6.1 showed:

```
unique observation != exact duplicate
```

so exact deduplication could not reduce the current replay store.

KCL-6.2 shows that:

```
many unique observations
can still share
one compact reconstructive pattern
```

For this workload:

```
24 unique episodes
→ 1 schema
→ 24 exactly reconstructable episodes
```

This is evidence for pattern-factorized replay memory.

## 11. Important Limitation

KCL-6.2 is not yet a fuzzy-memory result.

C loses no information:

```
episodes
→ exact schema
→ exact episodes
```

It has not yet tested:

```
episodes
→ lower-resolution gist
→ approximate reconstruction
→ faster recovery on re-exposure
```

The current synthetic tasks are also highly structured affine-modular tasks. The schema class is therefore well matched to the workload, even though the fitter was not given family labels or mapping constants.

Natural-language, noisy, exception-heavy, or non-affine knowledge is not covered by this result.

## 12. Provenance

Canonical workflow:

`35340007829`

Scientific source commit:

`f24a2b3ac6dc21714d40c6ba6f830bcae9936d0a`

Focused tests:

`24 passed`

Artifact ID:

`10545125295`

Artifact ZIP SHA-256:

`0ac50743de27b677b034478ddd2481965b5334473059c135cea4eced3ed02424`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl62_summary.json`

## 13. Conclusion

Under the frozen four-task KCL workload, reconstructive schema memory reduces replay storage by 14.05× versus raw episodic replay while preserving exactly the same replay evidence and continual-learning behavior.

The result supports the architecture:

```
raw episodes
→ consolidate into schema
→ keep residual exceptions
→ reconstruct evidence when needed
```

The remaining scientific question is whether memory can safely become lower-resolution—retaining gist while some detail decays—and still provide a measurable advantage when the old knowledge is encountered again.

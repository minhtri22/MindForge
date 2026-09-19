# KCL-6.5.9 — Boundary Regime Decomposition

## Status

```
NEGATIVE
NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY
```

KCL-6.5.9 does not support the hypothesis that the frozen binary
`SAFE_RESET_OPPORTUNITY` target hides multiple **supported** counterfactual
response regimes at the current discovery sample size.

The result is not a claim that all boundaries are mechanistically identical.
Rare alternative regimes were observed, but they failed the preregistered
minimum-support criterion and therefore cannot justify a regime-first controller.

## 1. Motivation

KCL-6.5.6, KCL-6.5.7 and KCL-6.5.8 all failed to qualify a predictor of
`SAFE_RESET_OPPORTUNITY`. H4 task-relative drift remained the strongest lead,
while increasingly rich pooled representations did not improve generalization.

KCL-6.5.9 therefore moved upstream of representation learning and asked:

> Does the binary SAFE_RESET_OPPORTUNITY target collapse multiple distinct,
> sufficiently supported A/B/C counterfactual response regimes?

This was a decomposition/characterization milestone only. No classifier,
controller, counterfactual retraining, confirmatory seed, or KCL-7 work was
authorized.

## 2. Frozen protocol

Protocol:

```
docs/research/kernel-continual-learning/kcl659-protocol.md
```

Protocol freeze commit:

```
fa1f0f0d51e62d3536a59ceafe4d52c3da60373a
```

Protocol SHA-256:

```
c4c15aaf86d470f53fb4e8e0f3474b30856fb529421fd87b23dcb9f3e8b35260
```

The taxonomy, support criteria, bootstrap design, entropy outputs and
STOP/PIVOT rules were frozen before regime frequencies were inspected.

## 3. Canonical source

KCL-6.5.9 consumed only the already-canonical KCL-6.5.8 discovery evidence:

```
experiments/kernel_cl/results/kcl658_discovery.json
```

Frozen Git blob SHA:

```
0a956a70ddb65d12a413176f84910ce889359973
```

Source SHA-256:

```
d580af009b555f774ed0478aef5adbf0c7e5bba4300b2afb3acc32e55b18374f
```

The dataset contains:

```
20 discovery seeds × 3 boundaries = 60 records
```

The untouched confirmatory cohort remained absent.

No A/B/C counterfactual was rerun in this milestone.

## 4. Frozen primary taxonomy

Every record was assigned to exactly one of:

```
B_AND_C_SAFE
B_SAFE_ONLY
C_SAFE_ONLY
CARRY_CATASTROPHIC_FAILURE
A_SUFFICIENT
```

The first three reconstruct `SAFE_RESET_OPPORTUNITY = true`; the last two
reconstruct `false`.

Minimum regime support was frozen as:

```
instance_count >= 5
AND
unique_seed_count >= 3
```

The primary hypothesis required either:

1. at least two supported positive-class regimes; or
2. both supported negative-class regimes.

## 5. QA history

### Run 35413155095 — implementation REVISE, not a scientific result

Focused contract tests:

```
12 passed
```

The decomposition code then returned:

```
REVISE
BOUNDARY_REGIME_DECOMPOSITION_INVALID
```

because the integrity dictionary stored the correct scope guards as:

```
confirmatory_workflow_created = false
rule_artifact_created = false
```

but subsequently applied `all(integrity.values())`, incorrectly treating
those correct false values as failures.

This was a predicate-polarity implementation defect. It occurred before valid
scientific adjudication and did not alter taxonomy, thresholds, source data, or
outcomes.

QA artifact:

```
10573544591
```

QA artifact ZIP SHA-256:

```
db293932f717f42b58b4323f03702cda02d3a81e400f6775f0eb5b886766bc98
```

### Patch-only fix

Commit:

```
83eb3766b7d76ce000c8d4e9d6329f4e48968f49
```

The patch changed only the boolean naming/polarity of the two scope guards to:

```
confirmatory_workflow_absent = true
rule_artifact_absent = true
```

No scientific rule changed.

## 6. Canonical workflow

Official canonical run:

```
35413205697
```

Canonical source commit:

```
83eb3766b7d76ce000c8d4e9d6329f4e48968f49
```

Workflow conclusion:

```
SUCCESS
```

Focused tests:

```
12 passed
```

Canonical artifact:

```
10573824576
```

Artifact ZIP SHA-256:

```
9d3f083916e0341f804cda22c97fbaba00e5304cd42b27cc9eb18a89ed871d72
```

Raw `kcl659_decomposition.json` SHA-256 inside the artifact:

```
4f787ea867667d968617580a9cd0ca6ed98ca24926d4b345096ac93cdc089e31
```

Machine-readable evidence preservation commit:

```
aab1d906ce82ebd20fa2042d3c40d9c0f20c80ba
```

## 7. Integrity

All frozen integrity checks passed:

- source blob SHA matched;
- KCL-6.5.8 status/verdict matched;
- 60 records present;
- exactly 20 discovery seeds × 3 boundaries;
- confirmatory seeds absent;
- all canonical record integrity checks valid;
- binary labels reproduced 60/60;
- primary regime assignment exactly-one and collectively exhaustive;
- assignment invariant to A/B/C dictionary presentation order;
- no model training invoked;
- no rule artifact created;
- no confirmatory workflow created;
- KCL-7 remained unopened.

## 8. Primary regime results

| Regime | Count | Prevalence | Unique seeds | Supported | Boundary 1/2/3 |
|---|---:|---:|---:|---|---|
| `C_SAFE_ONLY` | 39 | 65.00% | 20 | YES | 14 / 16 / 9 |
| `A_SUFFICIENT` | 16 | 26.67% | 12 | YES | 6 / 4 / 6 |
| `CARRY_CATASTROPHIC_FAILURE` | 3 | 5.00% | 3 | NO | 0 / 0 / 3 |
| `B_AND_C_SAFE` | 2 | 3.33% | 2 | NO | 0 / 0 / 2 |
| `B_SAFE_ONLY` | 0 | 0.00% | 0 | NO | 0 / 0 / 0 |

Thus:

```
SUPPORTED_ACTION_HETEROGENEITY   = false
SUPPORTED_NEGATIVE_HETEROGENEITY = false
SUPPORTED_BINARY_HETEROGENEITY   = false
```

The positive binary class is supported primarily by one regime:
`C_SAFE_ONLY`.

The negative binary class is supported primarily by one regime:
`A_SUFFICIENT`.

The observed alternatives are too sparse under the frozen support gate to
establish supported within-class regime heterogeneity.

## 9. Seed-cluster bootstrap prevalence

Frozen bootstrap:

```
20,000 seed-cluster resamples
RNG seed = 659659
95% percentile interval
```

Results:

| Regime | 95% prevalence interval |
|---|---|
| `C_SAFE_ONLY` | [0.55, 0.75] |
| `A_SUFFICIENT` | [0.1667, 0.3833] |
| `CARRY_CATASTROPHIC_FAILURE` | [0.00, 0.10] |
| `B_AND_C_SAFE` | [0.00, 0.0833] |
| `B_SAFE_ONLY` | [0.00, 0.00] |

These intervals are descriptive only and do not override the frozen support
criterion.

## 10. Binary compression information

The decomposition produced:

```
H(REGIME)                 = 1.292131 bits
H(SAFE_RESET)             = 0.900720 bits
H(REGIME | SAFE_RESET)    = 0.391411 bits
```

Therefore binary compression does discard descriptive regime information.

However, the conditional entropy is driven by rare subregimes that did not meet
the preregistered support gate. It is therefore not evidence that a
regime-predictive controller is currently justified.

## 11. H4 characterization

Median `H4_TASK_DRIFT_RELATIVE_L2` by observed regime:

```
C_SAFE_ONLY                0.183324
A_SUFFICIENT               0.170225
CARRY_CATASTROPHIC_FAILURE 0.169570
B_AND_C_SAFE               0.154570
B_SAFE_ONLY                n/a
```

IQR:

```
C_SAFE_ONLY                0.058416
A_SUFFICIENT               0.048801
CARRY_CATASTROPHIC_FAILURE 0.008803
B_AND_C_SAFE               0.002782
```

These are descriptive only. No H4 threshold was fit or selected.

## 12. Secondary mechanism

The frozen secondary flag:

```
RESET_PLASTICITY_GAIN_RETENTION_COST
```

occurred in:

```
14 / 60 boundaries
```

This supports the earlier observation that plasticity improvement can be
available while violating retention constraints, but this flag was not a
primary regime and cannot alter KCL-6.5.9 adjudication.

No `RESET_RESCUES_CARRY_FAILURE_WITH_RETENTION_COST` instances were reported
in the canonical secondary flag count.

## 13. Scientific interpretation

The motivating concern from KCL-6.5.8 was plausible but is **not supported at
the preregistered level**.

The important distinction is:

- multiple regime labels were observed;
- but only `C_SAFE_ONLY` and `A_SUFFICIENT` have adequate support;
- those two supported regimes largely align with the old positive/negative
  binary partition rather than splitting either binary class into multiple
  supported mechanisms.

Therefore the current failure of pooled boundary-health prediction should not be
explained by claiming that a hidden multi-regime target has already been
demonstrated.

This closes one tempting post-hoc escape route from the KCL-6.5.6→6.5.8
negative sequence.

## 14. What this result does not show

KCL-6.5.9 does not prove that rare regimes are nonexistent.

In particular:

- `B_AND_C_SAFE` appeared in 2 boundaries;
- `CARRY_CATASTROPHIC_FAILURE` appeared in 3 boundaries;
- both occurred only at boundary 3 in this discovery cohort.

Those observations are scientifically interesting but under-supported.
They cannot be promoted into a controller architecture from the current data.

## 15. Architectural consequence

Do **not**:

- train a regime-first controller from these 60 records;
- reopen pooled binary modeling by adding more features immediately;
- tune the taxonomy or minimum-support threshold;
- use the untouched confirmatory cohort to increase support;
- implement an adaptive boundary controller;
- open KCL-7.

The confirmatory cohort remains a protected asset.

## 16. Verdict

```
KCL-6.5.9 = NEGATIVE
NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY
```

The binary target loses some descriptive information, but the discovery cohort
does not establish enough supported within-class regime structure to justify a
regime-first architecture.

## 17. Next scientific step

Because rare preregistered regimes were observed but under-supported, the
protocol permits only a **fresh non-confirmatory replication cohort** using the
same frozen taxonomy and support rules.

A candidate next milestone is:

```
KCL-6.5.9.1 — Boundary Regime Replication
```

Its purpose should be only to test whether the rare
`B_AND_C_SAFE` and `CARRY_CATASTROPHIC_FAILURE` observations reproduce
under fresh discovery seeds.

Before execution it must freeze:

- fresh non-confirmatory seeds disjoint from all prior discovery and protected
  confirmatory seeds;
- identical KCL-6.5.9 taxonomy and thresholds;
- replication sample size / support decision;
- exact provenance and STOP/PIVOT rule.

No classifier, feature search, controller, or KCL-7 work should precede that
replication.

# CLRM-1 — Loss Response Support Qualification Protocol

Status: **PREREGISTERED / FRESH EXECUTION BLOCKED**

Program: CLRM — Continual Loss Response Modeling

Branch: `research/continual-loss-response`

Parent CLRM-0 closure:

```text
cd989bef0c314479b5be16380d024124c05d9351
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS
```

## 1. Scientific question

Before any response predictor is fit:

> Does the frozen CLRM two-axis CE-loss response object have reliable,
> all-boundary, within-stage non-degenerate support across all six canonical
> policy×response channels under the unchanged current substrate?

CLRM-1 is a measurement/support study.

It does not fit, select, tune or evaluate a predictor.

## 2. Frozen substrate

CLRM-1 retains exactly the current KCL/MSA substrate:

```text
vocab_size      = 96
d_model         = 16
n_heads         = 2
n_layers        = 1
max_context     = 2
ff_mult         = 4
dropout         = 0
relations       = 24
batch_size      = 16
stage_steps     = 250
learning_rate   = 3e-3
weight_decay    = 0

task order:
T1_U1_A
T2_U1_B
T3_U3_A
T4_U3_B

policies:
A_CARRY_ALL
B_RESET_ALL
C_CARRY_STEP_RESET_MOMENTS
```

Difficulty mutation is prohibited.

## 3. Exact same-state extraction

For a prospectively eligible boundary state `X` and policy
`a ∈ {A,B,C}`, train the next stage for exactly 250 steps under the canonical
lockstep replay stream.

At the resulting terminal model state, with no intervening training/update,
evaluate:

```text
L_current_end(X,a)
= CE loss on the current/new task

L_prior_mean_end(X,a)
= arithmetic mean CE loss across ALL tasks completed before the boundary
```

Each prior task has equal weight.

The same terminal parameter state must be used for:

- current-task loss;
- every prior-task loss;
- current terminal accuracy sentinel;
- every prior-task accuracy used to construct the minimum-prior sentinel.

The implementation must verify that evaluation does not mutate model
parameters.

The current-task loss/accuracy must exactly reproduce the terminal
step-250 curve point from the canonical lockstep stage runner.

No thresholded retention label enters the response vector.

## 4. Frozen direct response channels

Exactly six direct channels:

```text
A.current_loss
A.prior_mean_loss

B.current_loss
B.prior_mean_loss

C.current_loss
C.prior_mean_loss
```

No channel may be removed after fresh outcomes exist.

## 5. Accuracy sentinel

Record, from the same terminal model state:

```text
current_terminal_accuracy
min_prior_terminal_accuracy
```

Accuracy is diagnostic only.

It cannot affect:

- eligibility;
- support;
- reliability;
- response non-degeneracy;
- CLRM-1 verdict.

No 0.95 correctness threshold is imported.

## 6. A-relative contrasts

Compute after collection:

```text
D_B = R(B) - R(A)
D_C = R(C) - R(A)
```

for both loss components.

Contrast geometry is diagnostic only in CLRM-1.

It cannot rescue or overturn the six-direct-channel support verdict.

## 7. Fresh Role-S cohort

Cohort size:

```text
72 fresh seeds
3 boundaries / seed
216 complete matched boundaries
648 policy response vectors
1296 primary loss scalars
```

Why 72:

- each policy×stage×response cell obtains exactly 72 observations;
- p10/p90 robust-span diagnostics therefore have non-trivial tail support;
- the design matches the already-qualified measurement scale without reusing
  any MSA scientific values;
- cohort size is frozen before CLRM outcomes and is not power-tuned from CLRM
  data.

Deterministic generation phrase:

```text
MindForge|CLRM-1|role-s-loss-response-support|v1
```

Generation rule:

```text
candidate_i =
2,000,000
+ uint64_be(SHA256(phrase + "|" + decimal(i))[0:8]) mod 7,000,000

accept unique candidates in counter order until N=72
```

Manifest SHA-256 over exact comma-joined decimal sequence:

```text
3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6
```

The exact sequence is frozen in `CLRM1_ROLE_S_SEED_MANIFEST.json`.

No additional seeds may be added after outcome inspection.

## 8. Freshness / collision contract

The Role-S cohort must have zero collision with:

- all historical KCL scientific seeds;
- protected KCL confirmatory seeds;
- spent ACO-1 cohort;
- spent CPRM-1 cohort;
- spent MSA-1 cohort;
- spent MSA-3 cohort.

Exact spent manifest hashes:

```text
ACO-1:
9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91

CPRM-1:
d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3

MSA-1:
e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347

MSA-3:
5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8
```

Protected KCL cohort remains untouched.

## 9. All-boundary support gate

Required exactly:

```text
72/72 unique Role-S seeds
3/3 canonical boundaries per seed
216/216 records
72 records at boundary stage 1
72 records at boundary stage 2
72 records at boundary stage 3
A/B/C response present in every record
648/648 policy response vectors
```

Every row must pass matched-fork / boundary-policy / replay / same-state
integrity.

Failure:

```text
STOP_INTEGRITY_OR_SUPPORT
```

## 10. Deterministic reliability gate

Exactly the first six frozen Role-S seeds are repeated once.

For every repeated seed require exact equality of:

- all six direct loss channels at all three boundaries;
- all accuracy sentinel values;
- per-prior-task losses and accuracies;
- row structure and integrity metadata.

Required:

```text
6/6 exact deterministic repeats
max_abs_diff = 0
```

Failure:

```text
STOP_INTEGRITY_OR_SUPPORT
```

## 11. Frozen within-stage non-degeneracy criterion

No pooled-across-stage variation may qualify a channel.

For each policy `a`, response component `r`, and boundary stage `s`,
construct one cell of 72 values.

Cell statistics:

```text
unique_count
p10
p90
robust_span = p90 - p10
```

A cell is non-degenerate iff:

```text
unique_count >= 10
AND
robust_span >= 0.02
```

The numeric thresholds reuse the MSA CE-loss natural geometry scale, but remove
the MSA mastery/saturation condition because CLRM-1 asks whether a continuous
response can vary, not whether a task is mastered.

A direct channel is qualified iff its cell criterion passes in at least:

```text
2 of 3 boundary stages
```

This prevents a channel from qualifying only because different stages have
different means.

CLRM-1 PASS requires:

```text
all 6 direct channels qualified
```

No componentwise rescue is allowed.

## 12. One-shot adjudicator

After a complete preserved collection, run exactly one adjudication.

Allowed verdicts:

```text
PASS_LOSS_RESPONSE_SUPPORT
NEGATIVE_LOSS_RESPONSE_GEOMETRY
STOP_INTEGRITY_OR_SUPPORT
```

Decision:

```text
if integrity/support/reliability fail:
    STOP_INTEGRITY_OR_SUPPORT

else if all six direct channels qualify:
    PASS_LOSS_RESPONSE_SUPPORT

else:
    NEGATIVE_LOSS_RESPONSE_GEOMETRY
```

Accuracy sentinel and contrast diagnostics cannot alter this decision.

## 13. Blindness

Before the complete collection is preserved:

- do not inspect six-channel geometry;
- do not inspect contrast geometry;
- do not inspect accuracy-sentinel distributions;
- do not run the adjudicator.

Pre-adjudication checks are limited to integrity, cardinality, seed identity and
deterministic-repeat equality.

## 14. Technical retry policy

A technical retry is allowed only before a complete valid collection exists.

Any retry must use:

```text
same Role-S seed
same execution lock
same source blobs
same substrate
same runtime
same gates
```

Forbidden:

- seed substitution;
- extra seeds;
- difficulty change;
- source/gate change;
- outcome inspection before retry.

Once a complete valid 216-boundary collection exists:

```text
collection rerun = PROHIBITED
```

Adjudication is exactly one valid call. A technical adjudication retry is
allowed only if no valid formal result was produced.

Any source/protocol/seed/runtime/gate change invalidates the execution lock.

## 15. Execution-lock / preflight / verification order

Required order:

```text
protocol + source freeze
        ↓
execution lock
        ↓
zero-science preflight
        ↓
independent execution-lock verification
        ↓
only then:
fresh Role-S collection eligible to open
```

Zero-science preflight may use only historical seed 9595 as a deterministic
extraction probe.

It must not execute a Role-S seed.

The independent verifier must not import or call the CLRM-1 scientific runner.

## 16. Downstream rule

Only:

```text
PASS_LOSS_RESPONSE_SUPPORT
```

opens permission to **design** CLRM-2.

It does not authorize predictor training automatically.

```text
NEGATIVE_LOSS_RESPONSE_GEOMETRY
or
STOP_INTEGRITY_OR_SUPPORT
```

requires formal convergence review.

Controller and KCL-7 remain closed.

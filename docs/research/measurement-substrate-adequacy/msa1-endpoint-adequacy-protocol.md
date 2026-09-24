# MSA-1 — Current-Substrate Endpoint Adequacy Qualification

Status: **PREREGISTERED / FRESH SCIENTIFIC EXECUTION LOCKED**

Program: MSA — Measurement / Substrate Adequacy

MSA-0 prerequisite:

```text
MSA0_ZERO_SCIENCE_SPEC_QA_PASS
research/measurement-substrate-adequacy@1268a85a37bdcfa2412a48d8c2487440e787ad51
```

## 1. Scientific question

> Under the unchanged canonical KCL-compatible substrate, does the mandatory
> endpoint pair — terminal accuracy and terminal cross-entropy loss — provide a
> reliable, non-degenerate endpoint measurement regime, or is the substrate
> genuinely endpoint-saturated?

MSA-1 does not alter substrate difficulty and does not fit a predictor.

## 2. Exact unchanged substrate identity

MSA-1 freezes the inherited substrate exactly:

```text
KCL1Config:
  vocab_size   = 96
  d_model      = 16
  n_heads      = 2
  n_layers     = 1
  max_context  = 2
  ff_mult      = 4
  dropout      = 0.0
  relations    = 24
  batch_size   = 16
  stage_steps  = 250
  learning_rate = 3e-3
  weight_decay = 0.0

task order:
  T1_U1_A
  T2_U1_B
  T3_U3_A
  T4_U3_B

policies:
  A_CARRY_ALL
  B_RESET_ALL
  C_CARRY_STEP_RESET_MOMENTS

current samples per update = 15
replay samples per update  = 1
checkpoint sequence         = 0,25,...,250
device                      = CPU
```

The scientific implementation must bind the exact Git blobs of the existing
KCL substrate/model/replay/policy sources before fresh execution.

No task constructor, policy, model, optimizer, replay schedule, batch size,
training step count or task order may change.

## 3. Same-state endpoint extraction

For every fresh seed and every canonical boundary after T1/T2/T3, fork the same
pre-boundary model/optimizer/memory state into A/B/C using the canonical
KCL-6.5.5 policy machinery.

Train the next task through the existing lockstep path for exactly 250 steps.

The endpoint pair is taken from the **same canonical step-250 curve point**
already produced by `kcl655._curve_point()`:

```text
terminal_accuracy
terminal_cross_entropy_loss
```

No extra gradient update, early-stop branch or alternate evaluation set is
introduced.

Integrity requires the step-250 curve accuracy to equal the canonical
`curve_summary.final_accuracy` exactly.

## 4. Fresh cohort

Exactly 72 fresh seeds:

```text
7852877,2761307,7980060,8886053,8372679,3779647,
4340369,4656404,2606362,8420602,5624433,6963476,
7109847,4349361,4173979,3032355,8811213,4469405,
2348174,7601591,7945831,7994374,4658109,2192576,
4761197,2128138,3590175,2017834,8060511,5925203,
8484385,2496490,2757847,3322545,8487705,3599975,
3093036,2132012,4581015,6358053,8139369,8085240,
5318924,7730623,5530158,8191416,7476487,5469329,
3337298,7726785,7539302,6456627,7169558,2637791,
4500255,3710728,8425464,8494433,5135219,6119817,
4907431,8799077,8489437,5715340,2301093,2230544,
7672062,2312271,6591423,5628578,5723797,6209697
```

Canonical comma-joined SHA-256:

```text
e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347
```

Generation provenance:

```text
phrase = MindForge|MSA-1|current-substrate-endpoint-adequacy|v1
candidate_i = 2,000,000 + (
  uint64_be(SHA256(phrase + "|" + decimal(i))[0:8]) mod 7,000,000
)
accept candidates in counter order if not already accepted
stop at 72 unique seeds
```

No outcome was used in seed generation.

No seed replacement is allowed after scientific outcome generation.

## 5. Collision audit

Before fresh execution, the cohort must be disjoint from:

1. all historical KCL scientific seeds discoverable from KCL source/docs/lineage;
2. protected KCL confirmatory seeds;
3. all 40 spent ACO-1 seeds;
4. all 60 spent CPRM-1 seeds;
5. any earlier MSA scientific cohort.

Any collision found before science invalidates the cohort and requires a new
preregistered manifest + lock.

## 6. Exact population and support

Each seed contributes exactly three matched boundaries:

```text
after T1 → T2
after T2 → T3
after T3 → T4
```

At each boundary all three A/B/C endpoints are required.

Expected:

```text
72 seeds
216 matched boundaries
72 boundaries per stage
648 policy endpoint pairs
```

Support is all-or-nothing; no partial scientific adjudication.

## 7. Reliability gate

The first six frozen seeds are deterministic repeats:

```text
7852877,2761307,7980060,8886053,8372679,3779647
```

Repeat the full endpoint extraction under the same locked source/runtime.

Require:

```text
terminal_accuracy max_abs_diff = 0
terminal_cross_entropy_loss max_abs_diff = 0
boundary/policy/integrity structure identical
```

Repeat observations are reliability checks, not extra scientific samples.

## 8. Integrity gate

Every boundary must satisfy:

- A/B/C forks start from identical model state;
- boundary action does not mutate model parameters;
- exact replay match rate = 1.0;
- endpoint step = 250;
- endpoint accuracy is finite and in [0,1];
- endpoint loss is finite and >= 0;
- endpoint accuracy equals canonical curve-summary final accuracy exactly;
- policy set is exactly A/B/C.

Any violation yields `STOP_INTEGRITY_OR_SUPPORT`.

## 9. Accuracy classification contract

Natural accuracy resolution is:

```text
r_acc = 1/24
```

For each policy×stage cell (72 fresh observations), compute:

- unique count;
- p10 / p90;
- robust span = p90 - p10;
- exact ceiling fraction = fraction(accuracy == 1.0).

An accuracy cell is **SATURATED** iff:

```text
ceiling_fraction >= 0.50
AND
p10 >= 23/24
```

Interpretation: at least half of seeds are perfect and at least 90% of the cell
is within one discrete evaluation error of perfect accuracy.

An accuracy cell is **INFORMATIVE** iff:

```text
unique_count >= 4
AND
p90 - p10 >= 2/24
```

By construction these two cell states cannot both hold.

A global accuracy state qualifies iff the same cell state holds for at least
2 of 3 policies at **each** of the three stages.

Possible qualified global states:

```text
ACCURACY_SATURATED
ACCURACY_INFORMATIVE
```

Otherwise global accuracy classification support is insufficient.

## 10. Cross-entropy loss classification contract

The predeclared mastery reference is:

```text
L95 = -ln(0.95)
    = 0.05129329438755058
```

This value is defined from probability semantics, not from CPRM outcomes.

For each policy×stage cell, compute:

- unique count;
- p10 / p90;
- robust span = p90 - p10.

A loss cell is **SATURATED** iff:

```text
p90 <= L95
```

Thus at least 90% of seed-level endpoint losses in the cell are no worse than
the cross-entropy corresponding to geometric-mean true-class probability 0.95.

A loss cell is **INFORMATIVE** iff:

```text
unique_count >= 10
AND
p90 - p10 >= 0.02
AND
p90 > L95
```

The absolute 0.02 robust-span floor is frozen before MSA science and prevents
machine-level numeric differences from being called informative.

A global loss state qualifies iff the same cell state holds for at least 2 of
3 policies at each of the three stages.

Possible qualified global states:

```text
LOSS_SATURATED
LOSS_INFORMATIVE
```

Otherwise global loss classification support is insufficient.

## 11. Frozen joint classification matrix

After support/integrity/reliability PASS:

```text
ACCURACY_INFORMATIVE + LOSS_INFORMATIVE
→ ENDPOINT_MEASUREMENT_ADEQUATE

ACCURACY_SATURATED + LOSS_INFORMATIVE
→ ACCURACY_COARSE_LOSS_INFORMATIVE

ACCURACY_SATURATED + LOSS_SATURATED
→ CURRENT_SUBSTRATE_ENDPOINT_SATURATED

any other complete-data pattern
→ STOP_INTEGRITY_OR_SUPPORT
   reason = CLASSIFICATION_SUPPORT_INSUFFICIENT
```

This is exhaustive for MSA-1 governance.

No metric/gate is changed after outcomes to force a preferred class.

## 12. One-shot adjudication

The adjudicator receives only the complete frozen collection.

Exactly one valid adjudication is permitted.

It returns one of:

```text
ENDPOINT_MEASUREMENT_ADEQUATE
ACCURACY_COARSE_LOSS_INFORMATIVE
CURRENT_SUBSTRATE_ENDPOINT_SATURATED
STOP_INTEGRITY_OR_SUPPORT
```

## 13. Scientific interpretation

`ENDPOINT_MEASUREMENT_ADEQUATE` means the unchanged substrate has jointly
informative terminal accuracy and loss geometry.

`ACCURACY_COARSE_LOSS_INFORMATIVE` means discrete accuracy is broadly ceiling
compressed while the pre-existing probability-sensitive endpoint remains
informative.

`CURRENT_SUBSTRATE_ENDPOINT_SATURATED` means both mandatory endpoint measures
support a strong endpoint-mastery classification under the current substrate.

`STOP_INTEGRITY_OR_SUPPORT` means no MSA-1 scientific transition is allowed.

None of these outcomes authorizes predictor training.

## 14. Technical retry policy

Collection retry is allowed only after a technical failure and before a
complete valid 216-boundary collection exists.

Rules:

- same seed, same lock;
- no seed substitution;
- no difficulty/source/gate change;
- no endpoint-classification inspection before retry;
- once a complete valid collection exists, never rerun collection.

Adjudication:

- exactly one valid one-shot run;
- retry only if no valid formal result exists;
- same preserved input and same lock;
- once a valid formal result exists, never rerun adjudication.

Any scientific source, protocol, seed, runtime dependency or gate change
invalidates the execution lock and requires a new zero-science preflight.

## 15. Execution authorization

Fresh science remains prohibited until:

1. MSA-1 implementation + synthetic tests exist;
2. exact protocol/source/runtime/seed/substrate blobs are bound in
   `MSA1_EXECUTION_LOCK.json`;
3. zero-science preflight closes PASS;
4. a later independent execution-lock verification closes PASS.

This protocol itself does not authorize fresh execution.

## 16. MSA-2 transition

MSA-2 is not automatically opened by any MSA-1 outcome.

A formal post-MSA-1 transition review is required before MSA-2 design.

Predictor fitting remains outside MSA.

# KCL-6.5.2 — T4 Acquisition Failure Decomposition

## Abstract

KCL-6.5.1 independently replicated the retention benefit of targeted clarification, but failed its absolute current-task gate because seed 9393 produced T4 accuracy 75% for E and 87.5% for F. Both arms failed the frozen 95% current-task floor. KCL-6.5.2 decomposes this anomaly without changing the model, optimizer, task stream, replay ratio, E/F policies, or acquisition gate.

The decomposition uses a frozen hierarchy. G0 tests T4 in isolation. G1 trains the same seed through T1→T2→T3→T4 using only current-task data. G2 introduces an exact post-T3 matched fork, comparing no replay at T4 against exact replay at T4. G3 is the frozen targeted-clarification E policy; G4 is the matched-placebo fuzzy policy.

The decisive result occurs before replay is required. Fresh T4-only learning reaches 100%, but the sequential current-only arm reaches only 87.5% and never crosses the 95% gate. Therefore the first sufficient cause in the frozen hierarchy is:

```
KCL-6.5.2 = PASS
SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE
```

The experiment also establishes two important secondary facts. First, exact reconstructive replay and targeted clarification E are bit-equivalent under the current affine substrate: their post-T3 states, T4 replay streams, learning curves, final model states, and optimizer states are exactly equal. Therefore the seed-9393 E failure is not caused by the ASK/reactivation mechanism itself. Second, in the exact post-T3 matched fork, removing T4 replay improves final T4 from 75.0% to 79.17%; exact replay therefore adds a one-item acquisition cost in this state, but it is not the earliest cause because the ordinary current-only sequential trajectory already fails at 87.5%.

## 1. Trigger

KCL-6.5.1 closed:

```
FAIL
TARGETED_CLARIFICATION_ABSOLUTE_PLASTICITY_UNSTABLE
```

with the following important combination:

- targeted clarification retention benefit replicated on 20/20 fresh seeds;
- paired E-vs-F T4 tradeoff was not reproducibly confirmed within the one-item margin;
- seed 9393:
  - E T4 = 0.75;
  - F T4 = 0.875.

Because both E and F failed on the same seed, KCL-6.5.2 asks where the acquisition failure first becomes sufficient.

## 2. Frozen protocol

Protocol:

`docs/research/kernel-continual-learning/kcl652-protocol.md`

Initial protocol freeze:

`475dacdfe97f4ffa3cab04f4f0b74117effc16cb`

Final pre-execution protocol/RNG clarification:

`2827a7cba68872b9a70b974962ca9e0ccdf5221e`

Final protocol SHA-256:

`02e251bf00df6e57afdd791420153ace1388f20eef967c0b5a3d41872b0d23bd`

The final protocol state was committed before scientific execution.

## 3. Diagnostic arms

### G0 — FRESH_T4_ONLY

Fresh seed-9393 model, T4 only.

```
16 current
0 replay
```

Purpose: determine whether T4 itself is learnable for this initialization and budget.

### G1 — SEQUENTIAL_CURRENT_ONLY

```
T1 → T2 → T3 → T4
```

All stages:

```
16 current
0 replay
```

Purpose: determine whether ordinary sequential history alone is sufficient to impair T4 acquisition.

### G2-NR — EXACT_POST_T3_CURRENT_ONLY_T4

Build exact-replay history through T3, fork the exact post-T3 state, then T4 uses:

```
16 current
0 replay
```

The first 15 current samples are matched to G2-XR/G3; the 16th slot is a dedicated current example.

### G2-XR — EXACT_POST_T3_EXACT_REPLAY_T4

Same exact post-T3 fork as G2-NR.

T4:

```
15 current
1 exact replay
```

This is the clean direct T4 replay contrast against G2-NR.

### G3 — E_TARGETED_CLARIFICATION

Frozen KCL-6.5 E policy.

### G4 — F_MATCHED_PLACEBO_FUZZY

Frozen KCL-6.5 F policy.

## 4. Official results

Final T4 accuracy:

| Arm | Final T4 | 95% gate |
|---|---:|---|
| G0 fresh T4 | **1.0000** | PASS |
| G1 sequential current-only | **0.8750** | FAIL |
| G2-NR exact-history, no T4 replay | **0.7917** | FAIL |
| G2-XR exact-history + exact T4 replay | **0.7500** | FAIL |
| G3 E targeted clarification | **0.7500** | FAIL |
| G4 F fuzzy/placebo | **0.8750** | FAIL |

The frozen classification tree stops at G1 because:

```
G0 >= 0.95
G1 < 0.95
```

Therefore:

```
SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE
```

## 5. T4 learning-curve summary

### G0

```
final = 1.0000
max   = 1.0000
first >=95% checkpoint = step 200
```

T4 is independently learnable under seed 9393.

### G1

```
final = 0.8750
max   = 0.8750
first >=95% checkpoint = never
```

Thus the failure is not a late catastrophic drop after successful acquisition. The current-only sequential trajectory never reaches the historical floor during the recorded T4 checkpoints.

### G2-NR

```
final = 0.7917
max   = 0.8333
first >=95% checkpoint = never
```

### G2-XR

```
final = 0.7500
max   = 0.7917
first >=95% checkpoint = never
```

### G3 E

Identical to G2-XR:

```
final = 0.7500
max   = 0.7917
first >=95% checkpoint = never
```

### G4 F

```
final = 0.8750
max   = 0.8750
first >=95% checkpoint = never
```

## 6. Primary causal result

G0 and G1 use the same anomaly seed and the same frozen T4 current-only control stream class.

Observed:

```
fresh T4 only:
1.0000

after T1→T2→T3 current-only history:
0.8750
```

Therefore prior sequential training is already sufficient to make seed-9393 T4 fail the 95% acquisition floor.

Replay is not necessary for the failure to occur.

This rules out the interpretation that the KCL-6.5.1 anomaly is uniquely caused by fuzzy replay or clarification.

## 7. G2 matched-fork result

G2-NR and G2-XR are cloned from the exact same post-T3 model and optimizer state.

At every T4 step:

- the first 15 current examples are the same;
- batch size remains 16;
- optimizer step count remains the same.

The only deliberate difference is slot 16:

```
G2-NR: current T4 example
G2-XR: exact prior replay
```

Final:

```
G2-NR = 0.79167
G2-XR = 0.75000
delta = +0.04167 in favor of no replay
```

This is exactly one benchmark item.

Within this seed and state, exact replay during T4 therefore imposes an additional causal acquisition cost.

However this is a secondary aggravating factor, not the primary source, because G1 already fails without replay.

## 8. G2-XR / G3 exact equivalence

All equivalence gates pass:

```
post-T3 model state equal      = true
post-T3 optimizer state equal  = true
T4 replay stream equal         = true
T4 learning curve equal        = true
final model state equal        = true
final optimizer state equal    = true
```

Exact replay match rate:

```
G2-XR = 1.0
G3 E  = 1.0
```

Therefore, on the current affine workload:

> E's ASK/reactivation mechanism introduces no additional optimization distortion beyond exact reconstructive replay.

This is a strong mechanistic result.

The seed-9393 E failure cannot be attributed specifically to asking or schema reactivation.

## 9. G4 fuzzy replay

G4 final:

```
0.875
```

Exact replay-match rate during T4:

```
0.50
```

G4 therefore reproduces the historical anomaly while using substantially noisy old-task replay.

Interestingly:

```
G4 = 0.875
G3 = 0.750
```

on current-task T4 accuracy.

This is compatible with stronger exact stability pressure competing with current-task acquisition, but KCL-6.5.2 does not generalize that relationship. The N=20 KCL-6.5.1 experiment already found no reproducible population-level paired tradeoff within the one-item margin.

## 10. Canonical anomaly reproduction

Required historical endpoints:

```
G3/E = 0.750
G4/F = 0.875
```

Observed exactly:

```
G3/E = 0.750
G4/F = 0.875
```

Therefore the anomaly is deterministically reproduced.

## 11. Integrity

All frozen integrity checks pass:

- all metrics finite;
- G2 pre-T4 fork model equality;
- G2 pre-T4 fork optimizer equality;
- G2-XR/G3 post-T3 equality;
- G2-XR/G3 replay stream equality;
- G2-XR/G3 final model equality;
- G2-XR/G3 final optimizer equality;
- G2-XR/G3 T4 curve equality;
- G3/G4 historical anomaly reproduced;
- architecture unchanged;
- E/F policies unchanged;
- KCL-7 not started.

Focused tests:

```
19 passed
= 10 KCL-6.5.2
+ 9 KCL-6.5.1
```

## 12. What KCL-6.5.2 establishes

Within seed 9393 and this frozen diagnostic workload:

1. T4 is independently learnable.
2. Sequential T1→T2→T3 history alone is sufficient to make T4 fail.
3. Therefore replay is not necessary to explain the absolute seed-9393 failure.
4. Exact-replay history through T3 leaves an even more acquisition-impaired state descriptively.
5. From an identical exact post-T3 fork, exact replay during T4 causes one additional evaluation-item loss relative to replacing that replay slot with current data.
6. Targeted clarification E is exactly equivalent to exact reconstructive replay on this workload.
7. Fuzzy replay is not uniquely responsible for the seed-9393 acquisition failure.

## 13. What it does not establish

It does not prove:

- that all sequential trajectories suffer this failure;
- that replay is generally harmful;
- that exact replay always has a one-item plasticity cost;
- that the same mechanism appears at model scale;
- that the T1/T2/T3 representations responsible for the trajectory effect have been identified;
- that an optimal stability/plasticity controller has been found.

## 14. Secondary diagnostic omission

The canonical harness emitted the required T4 acquisition curves and causal endpoints but did not emit full final T1/T2/T3 per-task vectors for G1/G2.

No post-outcome scientific rerun was performed to fill this secondary reporting omission.

This omission does not affect the frozen primary classification because the causal tree depends on T4 acquisition endpoints and the exact G2/G3 equivalence checks, all of which are present.

Historical G3/G4 prior summaries remain available in the KCL-6.5.1 evidence.

## 15. Verdict

```
KCL-6.5.2 = PASS
SEQUENTIAL_TRAJECTORY_ACQUISITION_FAILURE
```

PASS means the seed-9393 anomaly was successfully decomposed.

It does **not** mean the current CL mechanism satisfies the 95% gate on seed 9393.

KCL-6.5.1 remains FAIL.

## 16. Provenance

Final pre-execution protocol commit:

`2827a7cba68872b9a70b974962ca9e0ccdf5221e`

Implementation:

`d2f4d412b9d1e167b3e037c4dcab7806f568f8ca`

Contract tests:

`197c653d51b3334d6553f5e9c1049963eb9b415a`

Canonical scientific source:

`4d2a751df195ba2ba0050b0082b486ac10c5faf4`

Canonical workflow:

`35358191886`

Artifact:

`10553270957`

Artifact ZIP SHA-256:

`a838583b89b4012052eaed86e359f75060685e187726f3d601638f2f80149018`

Machine-readable evidence:

`experiments/kernel_cl/results/kcl652_summary.json`

## 17. Scientific consequence

The next problem is no longer clarification specificity and no longer the small E-vs-F paired T4 delta.

The failure has moved one layer earlier:

> Why does a normally learnable T4 become acquisition-impaired after the seed-9393 T1→T2→T3 sequential trajectory?

That question should be isolated before KCL-7 model-scale transfer.

# KCL-6.5.9.x — Reverse-Synthesis Backlog

Status: **DEFERRED — DO NOT EXECUTE BEFORE KCL-6.5.9.8 CLOSES AND CONVERGENCE REVIEW OPENS**

Purpose: take one explicit reverse-angle slice across the already-established KCL evidence and preserve scientifically plausible alternative directions **without interrupting the active KCL-6.5.9.x sequence**.

This document is a backlog, not a protocol. Nothing below is authorized for execution yet.

## 1. Why a reverse synthesis is warranted

The active chain has repeatedly asked:

> Can a frozen representation predict a hard action/mechanism label?

That framing has produced a consistent pattern:

- fixed global boundary actions are not jointly sufficient;
- single scalar health signals do not qualify;
- broad action labels are heterogeneous;
- mechanism-specific labels remain hard to identify;
- static MRIG-v1 does not help;
- one-transition temporal TRIG-v1 does not help;
- zero-step future-task interaction previously showed the only notable positive information increment, but not enough to qualify on the broad target.

A reverse view asks instead:

> What if the hard-to-predict label is not the right primitive object to model?

The backlog below preserves directions that arise from that inversion.

## 2. Evidence anchors

### A. Action effects are policy-specific and qualitatively different

KCL-6.5.5 established:

- B RESET_ALL preserves retention better but harms acquisition AUC;
- C CARRY_STEP_RESET_MOMENTS improves plasticity AUC but harms retention;
- no fixed action jointly qualifies.

Therefore B and C are not merely interchangeable action names; their effect mechanisms differ.

### B. Broad labels collapse multiple mechanisms

KCL-6.5.9.4 replicated at least:

- MECH{P,R};
- MECH{P+R,R}.

Therefore direct classification of A_ONLY is structurally coarse.

### C. Mechanism-specific hard labels still do not become identifiable enough

KCL-6.5.9.5:

- Y_PR qualified but did not reach the frozen +0.10 gain over Y_A;
- Y_PRR remained unqualified.

### D. Richer pre-boundary representation has repeatedly failed

KCL-6.5.9.6 MRIG-v1:

- D_MRIG = -0.026316;
- S3 unqualified.

KCL-6.5.9.7 TRIG-v1:

- D_TRIG = -0.031852;
- S4 unqualified.

### E. Future interaction is the only information class with a prior positive numerical increment

KCL-6.5.9.3:

- O - S2 macro recall = +0.08347;
- 95% CI [-0.01100,+0.17835];
- not qualified, but directionally distinct from later static/temporal failures.

This is why KCL-6.5.9.8 tests FUTURE-PROBE-v1 directly on Y_PRR before any backlog item may execute.

---

# 3. Backlog candidates

## BL-1 — Continuous Potential-Outcome Modeling

### Reverse framing

Do not directly predict:

- A_ONLY;
- MECH{P,R};
- MECH{P+R,R};
- safe_B / safe_C as hard labels.

Instead predict the continuous intervention responses that generate those labels.

For each policy p in {B,C}, candidate response primitives include:

- DeltaAUC_p = AUC_p - AUC_A;
- DeltaR_p = retention_p - retention_A;
- final next-task accuracy_p;
- optionally explicit distance to each frozen safety threshold.

Only after response prediction is independently qualified may the already-frozen safety rule derive a policy label.

### Why this is scientifically grounded

KCL-6.5.5 directly demonstrated that B/C trade off different continuous endpoints.

KCL-6.5.9.4 then showed that hard labels collapse combinations of those endpoint failures.

Therefore the hard categorical target may be discarding ordered distance-to-threshold information.

### Falsifiable question

> Are the underlying policy-specific continuous counterfactual outcomes substantially more predictable/calibratable than their derived hard action/mechanism labels?

### Candidate evaluation

Priority after convergence review: **HIGH**.

Reason: this changes the modeled object, not merely the feature set or classifier capacity.

### Guardrail

Do not derive or optimize a controller in the same study. First qualify counterfactual outcome prediction itself.

---

## BL-2 — Policy-Conditioned Factorization Before Recombination

### Reverse framing

The current mechanism target intentionally removes B/C identity:

MECH{cause_1,cause_2}

This protects against spurious class multiplication, but it may also erase real policy-conditioned structure.

Instead study B and C separately:

- causes_B;
- causes_C;
- safe_B;
- safe_C;

or fit policy-conditioned risk functions with one shared representation.

Only after each policy-specific target is qualified should the results be recombined into an exchange-aware decision rule.

### Why this is scientifically grounded

KCL-6.5.5 proves B and C have qualitatively different causal effects.

Therefore B/C exchange invariance is appropriate for proving mechanism heterogeneity, but it is not automatically guaranteed to be the best representation for prediction.

### Falsifiable question

> Is the prediction problem easier when policy identity is modeled explicitly, rather than predicting the unordered joint mechanism class directly?

### Candidate evaluation

Priority after convergence review: **HIGH**.

### Required prerequisite

Before any predictor study, first establish on fresh data whether ordered/policy-conditioned failure-mode frequencies are themselves stable enough to support prospective modeling.

---

## BL-3 — Future-Task × Action-Response Interaction Geometry

### Reverse framing

KCL-6.5.9.6 asked:

> How do B/C virtual updates interact with already-observed gradients?

KCL-6.5.9.8 asks:

> Does zero-step future-task information itself materially identify Y_PRR?

A possible later combination is more direct:

> How does the **future-task gradient** align with the exact virtual update induced by each boundary action?

Candidate primitives:

- future-gradient × u_A;
- future-gradient × u_B;
- future-gradient × u_C;
- future-gradient × retention-gradient;
- B/C action-response contrasts under the future gradient.

This is not authorized now because it would be a new feature family selected after seeing earlier results.

### Why this is scientifically grounded

It combines the two strongest mechanistic facts:

1. B/C actions have distinct optimizer-state effects;
2. future-task interaction is the only information class that has shown a notable positive numerical increment.

### Trigger

Execute only if KCL-6.5.9.8 shows evidence that future interaction carries reproducible signal, even if the exact FUTURE-PROBE-v1 arm does not cross its strict qualification gate.

If KCL-6.5.9.8 is clearly null/negative with no stable positive increment, this candidate should be downgraded or dropped.

### Candidate evaluation

Priority after convergence review: **CONDITIONAL HIGH**.

---

## BL-4 — Target-Margin / Label-Stability Audit

### Reverse framing

Do not first ask why the classifier misses Y_PRR.

Ask:

> How stable is Y_PRR itself with respect to the frozen plasticity, retention and strict-accuracy thresholds?

For each B/C outcome record, compute distances to the already-frozen decision boundaries.

Possible diagnostics:

- proportion of labels lying near each safety threshold;
- mechanism transitions induced by small pre-registered perturbation bands;
- whether Y_PRR cases concentrate near intersections of P and R thresholds;
- whether the hard class is much less stable than the underlying continuous response vector.

### Why this is scientifically grounded

Y_PRR is created by conjunctions of thresholded outcomes.

Poor identifiability can arise even with informative continuous state if many cases lie near a hard boundary.

This audit does **not** relax or change any threshold.

### Falsifiable question

> Is a substantial fraction of Y_PRR classification determined by small margins around the frozen outcome thresholds?

### Candidate evaluation

Priority after convergence review: **HIGH DIAGNOSTIC**.

If labels are stable and far from thresholds, this explanation is falsified.

If labels are unstable/near-threshold, BL-1 gains stronger justification.

---

## BL-5 — Parameter-Group Interaction Representation

### Reverse framing

KCL-6.5.6 found task-relative drift H4 was the strongest single scalar but missed specificity.

KCL-6.5.8/LRBS and later S2 summarize groupwise drift/pressure/retention relationships, but mostly through aggregate shares/overlaps.

A later study could preserve explicit parameter-group interaction structure instead of compressing it into global summary features.

Candidate object:

drift_g × optimizer-pressure_g × retention-gradient_g

for frozen parameter groups, with exact group identity and no post-hoc group selection.

### Why this remains plausible

KCL-6.5.6 explicitly pointed to contextual interaction as the likely missing element after H4 nearly passed.

Later negative results reject the tested summary representations, not every possible group-structured interaction representation.

### Candidate evaluation

Priority after convergence review: **MEDIUM**.

Reason for not promoting now: S2/LRBS already explored part of this family and did not generalize strongly, so a new study would require a sharper mechanistic derivation than “more group features.”

---

## BL-6 — Stage-Conditional Mechanism Stability

### Reverse framing

Do not immediately build separate stage-specific classifiers.

First ask whether mechanism prevalence and response geometry differ reproducibly between boundary 1, 2 and 3 across independent cohorts.

KCL-6.5.9.7 already shows substantial support asymmetry for Y_PRR between boundaries 2 and 3.

That is descriptive only and cannot justify a post-hoc stage-specific model.

### Candidate evaluation

Priority after convergence review: **LOW / DIAGNOSTIC FIRST**.

A fresh replication of stage-conditional mechanism structure is required before any stage-specific modeling.

---

# 4. Directions explicitly NOT backlogged

The following are not justified by current evidence:

- more MRIG-v1 features;
- more TRIG-v1 features;
- longer history merely because one-step history failed;
- larger nonlinear classifier as a rescue;
- relaxed qualification thresholds;
- extra validation seeds after seeing outcomes;
- opening the protected confirmatory cohort;
- implementing an adaptive controller before representation/information qualification.

These remain STOPPED unless new independent evidence changes the premise.

# 5. Dependency order after KCL-6.5.9.8

Nothing in this backlog executes automatically.

After KCL-6.5.9.8:

## If KCL-6.5.9.8 PASS

1. independent replication of future-interaction gain;
2. convergence review;
3. BL-3 becomes a strong candidate only after replication;
4. BL-1 / BL-2 / BL-4 remain separate alternative formulations.

## If KCL-6.5.9.8 NEGATIVE

1. close active KCL-6.5.9.x sequence;
2. perform convergence review;
3. evaluate BL-1, BL-2 and BL-4 as **new research programs**, not continuations tuned to rescue 6.5.9.8;
4. BL-3 is retained only if KCL-6.5.9.8 still shows a stable positive information increment below the strict gate;
5. BL-5/BL-6 require stronger justification before execution.

# 6. Governance

This backlog is intentionally separated from the active proof chain.

Rules:

- no backlog experiment may be inserted before KCL-6.5.9.8 adjudication;
- no backlog item inherits authorization merely because it is listed here;
- each future item requires its own hypothesis, fresh cohort, frozen protocol and falsification gate;
- no use of KCL-6.5.9.8 validation data for feature design;
- protected confirmatory seeds remain untouched;
- controller remains closed;
- KCL-7 remains closed until convergence review explicitly authorizes a phase transition.

# 7. Current decision

Active sequence remains:

KCL-6.5.9.7 close
→ KCL-6.5.9.8 future-interaction terminal discriminator
→ convergence review

The reverse-synthesis backlog is preserved for later and does not alter this sequence.

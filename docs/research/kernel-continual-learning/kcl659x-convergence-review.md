# KCL-6.5.9.x — Formal Convergence Review

Status: **FORMAL REVIEW — CLOSED**

Date: 2026-09-20

Overall verdict:

```
DIAGNOSTIC_CONVERGENCE_ACHIEVED
NO_QUALIFIED_BOUNDARY_CONTROLLER
ACTIVE_KCL_6_5_9_X_STOP
PIVOT_ONLY_VIA_NEW_PREREGISTERED_RESEARCH_PROGRAM
```

This review closes the active KCL-6.5.9.x chain after the terminal
KCL-6.5.9.8 negative result.

It is a synthesis/adjudication step only.

No new scientific cohort is executed here.

The reverse-synthesis backlog is input to the review but remains unexecuted.

Protected confirmatory seeds remain untouched.

KCL-7 remains not started.

---

## 1. Review question

The KCL-6.5.9.x chain was opened to answer a sequence of increasingly specific
questions:

1. Are boundary-action outcomes heterogeneous?
2. If yes, are those regimes stable enough to replicate?
3. Can regime identity be predicted from observable boundary state?
4. If not, is the failure caused by representation insufficiency or target
   non-identifiability?
5. Is the hard A_ONLY target internally heterogeneous?
6. Do mechanism-specific targets become identifiable?
7. Can static mechanistic intervention geometry recover the missing signal?
8. Can temporal transition history recover it?
9. Can controlled zero-step future-task interaction recover it?

The formal convergence question is:

> Has the current hypothesis family been tested deeply enough that continuing
> with another KCL-6.5.9.x feature/representation variant would be exploratory
> rescue rather than a scientifically motivated continuation?

Answer:

```
YES
```

The active family has converged diagnostically and must stop.

---

## 2. Evidence chain

| Milestone | Primary result | Convergence contribution |
|---|---|---|
| KCL-6.5.9 | NEGATIVE — no supported within-class regime heterogeneity in the original 20-seed discovery cohort | Rare regimes observed but under-supported; authorized replication only |
| KCL-6.5.9.1 | PASS — supported positive boundary-regime heterogeneity replicated | Established that multiple positive action regimes are real |
| KCL-6.5.9.2 | NEGATIVE — RPQ-v1 not qualified | Replicated regimes are not operationally predictable from frozen global boundary state |
| KCL-6.5.9.3 | NEGATIVE / INCONCLUSIVE — S0/S1/S2/O decomposition | Richer pre-boundary S2 did not help; future probe showed only a non-qualified numerical uplift |
| KCL-6.5.9.4 | PASS — A_ONLY contains replicated failure-mode heterogeneity | Established stable causal target structure: MECH{P,R} and MECH{P+R,R} |
| KCL-6.5.9.5 | NEGATIVE — no generalized mechanism-specific identifiability gain | Target decomposition alone does not solve the prediction problem |
| KCL-6.5.9.6 | NEGATIVE — MRIG-v1 does not qualify Y_PRR | Static observed-task intervention-response geometry rejected |
| KCL-6.5.9.7 | NEGATIVE — TRIG-v1 does not qualify Y_PRR | One-transition temporal history rejected |
| KCL-6.5.9.8 | NEGATIVE — FUTURE-PROBE-v1 does not qualify Y_PRR | Terminal zero-step future-interaction hypothesis rejected for the hard mechanism |

The sequence therefore contains both positive structural discoveries and
repeated prospective falsifications. It is not an undifferentiated sequence of
negative experiments.

---

## 3. Reconciliation of KCL-6.5.9 and KCL-6.5.9.1

KCL-6.5.9 initially reported:

```
NEGATIVE
NO_SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY
```

on 20 discovery seeds / 60 boundaries.

That result did not assert homogeneous boundaries. It explicitly recorded rare
under-supported alternatives and preregistered fresh replication as the only
admissible next step.

KCL-6.5.9.1 then used 66 fresh seeds / 198 boundaries and reported:

```
PASS
SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED
```

because:

- C_SAFE_ONLY remained supported;
- B_AND_C_SAFE became supported;
- B_SAFE_ONLY unexpectedly became supported;
- the catastrophic-carry negative subregime did not replicate.

This is not a contradiction.

The correct chain-level statement is:

> the original cohort was too small to establish supported positive
> within-class heterogeneity, and fresh preregistered replication subsequently
> established it.

This is a successful example of uncertainty reduction by replication rather
than threshold relaxation.

---

## 4. Converged positive findings

### C-P1 — Fixed global boundary policies are not sufficient

Upstream KCL-6.5.5 established a real policy tradeoff:

- B RESET_ALL can preserve retention but harms acquisition dynamics;
- C CARRY_STEP_RESET_MOMENTS improves plasticity but can violate retention;
- A CARRY_ALL is not uniformly robust.

No fixed action jointly satisfies the plasticity + retention + robustness
contract.

Convergence status:

```
SUPPORTED / STABLE
```

### C-P2 — Boundary action suitability is heterogeneous

KCL-6.5.9.1 independently established multiple supported positive action
regimes.

Convergence status:

```
SUPPORTED / REPLICATED
```

### C-P3 — A_ONLY is a heterogeneous target

KCL-6.5.9.4 independently established stable failure mechanisms:

```
MECH{P,R}
MECH{P+R,R}
```

with discovery/replication stability.

Convergence status:

```
SUPPORTED / REPLICATED
```

### C-P4 — The hard unresolved mechanism is specifically MECH{P+R,R}

KCL-6.5.9.5 found:

```
Y_A  S2 macro recall = 0.615474 — qualified
Y_PR S2 macro recall = 0.686289 — qualified
Y_PRR S2 macro recall = 0.576520 — not qualified
```

Y_PR produced a real positive gain versus Y_A:

```
+0.070815
95% CI [+0.033422,+0.109074]
```

but missed the frozen +0.10 magnitude requirement.

Y_PRR remained the clear hard case.

Convergence status:

```
SUPPORTED AS THE PRIMARY UNRESOLVED HARD TARGET
```

---

## 5. Converged negative findings

### C-N1 — Global boundary state is not sufficient for action-regime prediction

KCL-6.5.9.2 validation:

```
RPQ-v1 macro recall = 0.419725
stage-only baseline = 0.458726
```

RPQ-v1 did not qualify and did not beat the strongest frozen baseline.

Convergence status:

```
FALSIFIED FOR THE TESTED GLOBAL REPRESENTATION
```

### C-N2 — Richer localized S2 does not close the broad identifiability gap

KCL-6.5.9.3:

```
S1 macro recall = 0.43993
S2 macro recall = 0.43000
D21 = -0.00993
95% CI [-0.07989,+0.06036]
```

Convergence status:

```
FALSIFIED FOR LRBS-v1 AS A BROAD RESCUE
```

### C-N3 — Target decomposition alone is insufficient

KCL-6.5.9.5 showed that stable mechanism targets do not automatically become
materially more identifiable under the same representation.

Convergence status:

```
FALSIFIED AS A SUFFICIENT SOLUTION
```

### C-N4 — Static mechanistic reset-response geometry is insufficient

KCL-6.5.9.6:

```
S2 Y_PRR macro recall = 0.584064
S3 Y_PRR macro recall = 0.557749
D_MRIG = -0.026316
95% CI [-0.068479,+0.004373]
```

Convergence status:

```
MRIG-v1 CLOSED
```

### C-N5 — One-transition temporal geometry is insufficient

KCL-6.5.9.7:

```
S3 Y_PRR macro recall = 0.545926
S4 Y_PRR macro recall = 0.514074
D_TRIG = -0.031852
95% CI [-0.094023,+0.033593]
```

Convergence status:

```
TRIG-v1 CLOSED
```

### C-N6 — Exact zero-step FUTURE-PROBE-v1 is insufficient for Y_PRR

KCL-6.5.9.8:

```
S2 Y_PRR macro recall  = 0.451525
FUT Y_PRR macro recall = 0.439006

D_FUTURE = -0.012518
95% CI [-0.021292,-0.003748]
```

The paired interval is entirely below zero.

Convergence status:

```
FUTURE-PROBE-v1 P1-P8 CLOSED FOR Y_PRR QUALIFICATION
```

This also resolves the earlier KCL-6.5.9.3 ambiguity: its broad-target
future-probe numerical uplift does not generalize into a mechanism-specific
identifiability gain for MECH{P+R,R}.

---

## 6. What has actually converged

### 6.1 Diagnostic convergence — YES

The current evidence supports a coherent structural model:

```
optimizer-boundary actions
        ↓
different plasticity / retention effects
        ↓
state-dependent action suitability
        ↓
multiple replicated action/failure regimes
        ↓
hard thresholded joint labels
        ↓
MECH{P+R,R} remains poorly identifiable
under all tested representation/information arms
```

The problem is therefore no longer well described as:

> find one better scalar or add one more state feature.

That research framing has converged and is closed.

### 6.2 Solution convergence — NO

No prospective study has established a predictor/controller that meets the
frozen operational qualification contract for the hard target.

Therefore:

```
QUALIFIED CONTROLLER = NO
```

### 6.3 Architecture convergence — PARTIAL

Evidence supports the need for state-dependent treatment in principle, but does
not support any operational state-to-action mapping yet.

Therefore architecture may record the requirement:

> fixed global boundary policy is insufficient.

It may not yet encode:

> this predictor/controller chooses A/B/C online.

---

## 7. Claims that must NOT be made

The evidence does not justify:

- all future-task interaction is useless;
- MECH{P+R,R} is fundamentally unlearnable;
- nonlinear models cannot work;
- longer temporal history cannot work;
- policy-specific modeling cannot work;
- continuous potential outcomes cannot be predicted;
- the current hard thresholds are wrong;
- an adaptive controller should now be implemented anyway;
- protected confirmatory seeds should now be consumed.

The chain has falsified specific preregistered hypotheses, not all conceivable
models.

---

## 8. Why the active KCL-6.5.9.x line must stop

A continuation such as KCL-6.5.9.9 would need to answer:

> What genuinely new scientific uncertainty does this experiment resolve?

After .8, another variant that merely:

- adds features;
- adds more temporal lags;
- combines MRIG + TRIG + FUT;
- increases classifier capacity;
- tunes thresholds;
- adds seeds;

would not isolate a new uncertainty.

It would be a rescue attempt inside a repeatedly failed formulation.

Therefore:

```
ACTIVE KCL-6.5.9.x = STOP
```

This STOP is scientific governance, not abandonment of the broader
plasticity/retention problem.

---

## 9. Reverse-synthesis backlog adjudication

The reverse-synthesis backlog was created before KCL-6.5.9.8 validation closed
and was explicitly forbidden from execution.

It is reviewed here only as a source of possible **new** research programs.

### BL-1 — Continuous Potential-Outcome Modeling

Question:

> predict DeltaAUC_B/C, DeltaRetention_B/C, final next-task accuracy and
> distance-to-safety margins before thresholding them into hard labels.

Review decision:

```
RETAIN — HIGH PRIORITY POST-CONVERGENCE PIVOT
```

Reason:

The current chain repeatedly predicts hard derived labels. KCL-6.5.5 and
KCL-6.5.9.4 show that those labels are generated from qualitatively different
continuous policy effects. Modeling the generating quantities is a genuinely
different target/objective family.

This is not authorized for execution by this review alone.

### BL-2 — Policy-Conditioned Factorization Before Recombination

Question:

> model B and C separately before recombining into a joint action decision.

Review decision:

```
RETAIN — HIGH PRIORITY POST-CONVERGENCE PIVOT
```

Reason:

B and C have empirically different plasticity/retention behavior. Exchange
invariance was appropriate for proving mechanism existence, but may erase
policy-specific predictive structure.

A fresh prospective stability study of ordered B/C failure modes should precede
any predictor.

### BL-3 — Future-Task × Action-Response Interaction Geometry

Original trigger required KCL-6.5.9.8 to show reproducible positive
future-information signal.

Observed:

```
D_FUTURE = -0.012518
95% CI entirely below 0
```

Review decision:

```
DROP / STOP UNDER CURRENT PREMISE
```

Reason:

Its preregistered motivation is not supported by the terminal discriminator.
Do not rescue FUTURE-PROBE-v1 by immediately constructing a more elaborate
future/action interaction representation.

### BL-4 — Target-Margin / Label-Stability Audit

Question:

> are Y_PRR labels concentrated near frozen plasticity/retention/accuracy
> decision margins?

Review decision:

```
RETAIN — HIGH PRIORITY DIAGNOSTIC
```

Reason:

Y_PRR is a conjunction of thresholded continuous counterfactual outcomes.
A prospective margin-stability audit can test whether hard-label instability
itself is a material source of apparent non-identifiability without changing
the thresholds.

No threshold relaxation is authorized.

### BL-5 — Parameter-Group Interaction Representation

Review decision:

```
DEFER — CONDITIONAL
```

Reason:

KCL-6.5.6 H4 and later LRBS results leave some mechanistic motivation, but the
current line has already tested multiple increasingly rich state summaries
without qualification.

Promote this only if a new target/objective study provides a specific
group-level causal quantity to predict.

### BL-6 — Stage-Conditional Mechanism Stability

Review decision:

```
DEFER — DIAGNOSTIC ONLY
```

Reason:

Stage localization repeatedly appears descriptively, especially at later
boundaries, but no fresh prospective study has established a stage-specific
prediction rule.

Do not build stage-specific classifiers from post-hoc subgroup observations.

---

## 10. Post-convergence research ordering

If research on this problem is reopened later, the scientifically preferred
order is:

```
PIVOT-0
Target-margin / label-stability qualification
        ↓
PIVOT-1
Continuous policy-specific potential-outcome predictability
        ↓
PIVOT-2
Policy-conditioned B/C factorization and recombination
        ↓
only if supported:
representation refinements tied to a demonstrated predictable quantity
        ↓
only after independent qualification:
controller study
```

Why this order:

1. first test whether the current hard label itself is a stable scientific
   object;
2. then predict the continuous quantities that generate it;
3. then preserve policy identity rather than prematurely compressing B/C;
4. only then revisit representation design.

This is a **new program structure**, not KCL-6.5.9.9.

Each stage requires its own preregistration, fresh cohort and STOP gate.

---

## 11. Protected confirmatory cohort decision

The original protected confirmatory seeds remain:

```
UNTOUCHED
```

Review decision:

```
DO NOT CONSUME
```

Reason:

There is no currently qualified predictor/rule that merits confirmatory
execution.

Using the cohort now to explore backlog hypotheses would destroy its value as a
protected asset.

---

## 12. Controller decision

Formal review:

```
BOUNDARY CONTROLLER = NOT QUALIFIED
```

Do not implement:

- A/B/C online selector;
- threshold heuristic from H4;
- MRIG-based selector;
- TRIG-based selector;
- FUTURE-PROBE-based selector;
- learned nonlinear rescue controller.

A future controller study becomes admissible only after a new target/outcome
formulation independently qualifies and replicates.

---

## 13. KCL-7 decision

Formal review:

```
KCL-7 = CLOSED / NOT AUTHORIZED
```

KCL-7 must not be opened merely because the KCL-6.5.9.x line is closed.

A transition to KCL-7 requires a separately justified scientific prerequisite,
not exhaustion of KCL-6.5.9.x numbering.

---

## 14. Convergence classification

The final review distinguishes three levels.

### Structural convergence

```
PASS
```

We know that:

- fixed policies are insufficient;
- policy effects are heterogeneous;
- action/failure regimes are real;
- A_ONLY contains replicated mechanism heterogeneity.

### Predictive convergence

```
NEGATIVE / STOP FOR CURRENT FORMULATION
```

No tested static, localized, mechanism-specific hard-target, MRIG, TRIG, or
exact P1-P8 future-interaction arm qualifies the hard Y_PRR target.

### Operational convergence

```
NOT REACHED
```

No controller is qualified.

---

## 15. Formal decision

```
FORMAL_CONVERGENCE_REVIEW = CLOSED

DIAGNOSTIC_CONVERGENCE = ACHIEVED
SOLUTION_CONVERGENCE   = NOT ACHIEVED

ACTIVE_KCL_6_5_9_X     = STOP
KCL_6_5_9_9            = FORBIDDEN_AS_RESCUE
PROTECTED_COHORT       = KEEP_CLOSED
CONTROLLER             = KEEP_CLOSED
KCL_7                  = KEEP_CLOSED

POST_CONVERGENCE:
  RETAIN BL-1 CONTINUOUS POTENTIAL OUTCOMES
  RETAIN BL-2 POLICY-CONDITIONED FACTORIZATION
  RETAIN BL-4 TARGET-MARGIN AUDIT
  DROP   BL-3 FUTURE×ACTION GEOMETRY UNDER CURRENT PREMISE
  DEFER  BL-5 PARAMETER-GROUP REPRESENTATION
  DEFER  BL-6 STAGE-CONDITIONAL MODELING
```

The next action is **not another experiment**.

The next action is governance:

1. preserve this convergence decision in Lineage/README;
2. keep all active KCL-6.5.9.x execution closed;
3. only reopen research through a separately named, preregistered
   post-convergence program if a retained pivot is explicitly authorized.

---

## 16. Evidence anchors

Key canonical evidence:

```
KCL-6.5.9.1:
PASS — SUPPORTED_BOUNDARY_REGIME_HETEROGENEITY_REPLICATED

KCL-6.5.9.2:
NEGATIVE — BOUNDARY_REGIME_PREDICTOR_NOT_QUALIFIED

KCL-6.5.9.3:
NEGATIVE — BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE

KCL-6.5.9.4:
PASS — A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY

KCL-6.5.9.5:
NEGATIVE — NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN

KCL-6.5.9.6:
NEGATIVE — MRIG_V1_DOES_NOT_QUALIFY_MECH_PRR_REPRESENTATION

KCL-6.5.9.7:
NEGATIVE — TRIG_V1_DOES_NOT_QUALIFY_TEMPORAL_MECH_PRR_REPRESENTATION

KCL-6.5.9.8:
NEGATIVE — FUTURE_INTERACTION_DOES_NOT_QUALIFY_MECH_PRR
```

Terminal KCL-6.5.9.8 evidence:

```
validation run:
35503887230

validation evidence commit:
6b1b70ed5b017cab5d3e6cda86f38379e90ddf3b

validation JSON SHA-256:
6c58b41b3a0f2ec50bf0676ba1f4f03a64a75d43aa62cb88c64faec7e23b640f

artifact ID:
10602739405

artifact ZIP SHA-256:
70a8d5dee71a368c151a1b7f20a9e6f7019810fa10a64177a5bf403827ad3573
```

Reverse-synthesis input:

```
docs/research/kernel-continual-learning/kcl659x-reverse-synthesis-backlog.md
```

No item from that backlog was executed during the active chain or this review.

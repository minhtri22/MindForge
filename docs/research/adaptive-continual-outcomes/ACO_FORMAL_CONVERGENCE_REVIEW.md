# ACO — Formal Convergence Review

Status: **FORMAL REVIEW — CLOSED**

Date: 2026-09-20

## 1. Review scope

This review is governance/evidence synthesis only.

No new seed is executed.
No outcome model is fitted.
No threshold is changed.
No ACO-1 statistic is recomputed beyond the canonical one-shot adjudication.
No protected KCL confirmatory seed is consumed.

The review is triggered by:

```text
ACO-1 = STOP
TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

Canonical ACO-1 support result:

```text
integrity_ok   = true
primary_count  = 12
primary_stages = [1,2,3]
support_ok     = false
```

Frozen support requirement:

```text
>= 30 canonical Y_PRR boundaries
across >= 2 stages
```

## 2. What ACO-1 actually falsified

ACO-1 did **not** adjudicate the near-margin instability hypothesis.

The support gate stopped the study before `near_margin_rate` or `label_flip_rate`
could become admissible primary scientific conclusions.

Therefore ACO-1 establishes only:

> the frozen 40-seed ACO-1 design does not contain enough canonical
> `Y_PRR = MECH{P+R,R}` support to test the preregistered hard-target
> stability question at its frozen minimum-support contract.

ACO-1 does **not** establish:

- that Y_PRR is stable;
- that Y_PRR is unstable;
- that continuous outcomes are unpredictable;
- that action contrasts are unpredictable;
- that policy-conditioned modeling is invalid;
- that thresholds should change;
- that adding more ACO-1 seeds is allowed.

## 3. What remains established before ACO

The parent KCL convergence review remains valid.

Within the tested KCL envelope:

1. fixed global A/B/C boundary policies are not jointly sufficient;
2. boundary action suitability is heterogeneous and replicated;
3. A_ONLY contains replicated mechanism heterogeneity;
4. B and C have qualitatively different plasticity/retention effects;
5. repeated hard-target representation families failed to qualify Y_PRR;
6. no online boundary controller is qualified.

The original MindForge capability objective remains broader than the failed
hard-label formulation:

```text
continual learning
→ measurable memory
→ adaptive learning
```

The unresolved capability question is still how state-dependent interventions
affect plasticity/retention under controlled cost.

## 4. Three-way decision review

### Option 1 — terminate ACO and terminate the continuous-response question

Decision:

```text
REJECT AS THE COMPLETE SCIENTIFIC CONCLUSION
```

ACO **must** terminate as a program because its own roadmap STOP condition was
met. However, the evidence does not justify extending that STOP to the broader
continuous-response question.

Reason:

- the ACO-1 failure is support failure for a rare thresholded hard-target
  subpopulation;
- it is not a prospective failure of continuous-response prediction;
- KCL-6.5.5 and KCL-6.5.9.1/4 independently establish heterogeneous
  action-specific consequences, which is sufficient scientific motivation to
  ask whether those continuous consequences are predictable.

Thus:

```text
ACO formulation = TERMINATE
continuous-response question = NOT FALSIFIED
```

### Option 2 — retain the continuous-response question in a new research program

Decision:

```text
SELECTED
```

This is the only direction that both respects the ACO STOP and preserves the
independently justified unresolved quantity.

The new research object must **not** be Y_PRR support or another hard-label
rescue.

Candidate object:

```text
X = observable pre-boundary state

Y(X,a) = policy-specific continuous response for a ∈ {A,B,C}

candidate quantities:
  next-task plasticity AUC
  final current-task accuracy
  prior-task retention
  worst-prior-task accuracy

contrasts:
  Y(X,B) - Y(X,A)
  Y(X,C) - Y(X,A)
```

Crucially, the primary population must be all prospectively eligible matched
boundaries defined before execution, rather than conditioning the study on a
rare post-threshold Y_PRR subset.

This changes the scientific population/target contract and therefore **cannot**
be called ACO-2.

### Option 3 — return immediately to a different upstream continual-learning question

Decision:

```text
NOT SELECTED AS THE NEXT PROGRAM
```

An upstream return remains scientifically possible later, especially for:

- real-language transfer;
- general memory-storage scaling;
- non-synthetic continual-learning value;
- external product-driven learning/memory requirements.

But it is not forced by the current evidence.

Reason:

KCL already established a valid controlled forgetting substrate, a causal
anti-forgetting treatment, replay generalization in the tested synthetic
families, and replicated state-dependent policy heterogeneity.

Those results provide an independently justified unresolved response-modeling
question. Returning upstream now would abandon that unresolved causal structure
without first testing the directly generating continuous quantities.

This decision does not claim synthetic KCL findings transfer to real language.

## 5. Formal decision

```text
ACO_FORMAL_CONVERGENCE_REVIEW = CLOSED

ACO_PROGRAM                      = TERMINATED
ACO_2                            = FORBIDDEN
EXTRA_ACO_1_SEEDS                = FORBIDDEN
ACO_THRESHOLD_RELAXATION         = FORBIDDEN
HARD_LABEL_RESCUE                = FORBIDDEN

NEXT_DIRECTION                   = OPTION_2
CONTINUOUS_RESPONSE_QUESTION     = RETAINED
NEXT_SCIENTIFIC_HOME             = NEW_RESEARCH_PROGRAM_REQUIRED

OPTION_1_AS_TOTAL_TERMINATION     = REJECTED
OPTION_3_AS_IMMEDIATE_NEXT_STEP   = NOT_SELECTED

CONTROLLER                        = CLOSED
KCL_7                             = CLOSED
PROTECTED_KCL_COHORT              = UNTOUCHED
```

## 6. Why this is a genuine new program rather than ACO continuation

ACO had the dependency:

```text
ACO-1 hard-target stability/support
        ↓ prerequisite
ACO-2 continuous outcome prediction
```

That prerequisite path has STOPPED by contract.

A new program must instead be justified directly from the upstream KCL
structural evidence and must define a new primary population/evidence contract
before seeing any new outcomes.

It may inherit only these scientific motivations:

- policy effects are heterogeneous;
- fixed policy is insufficient;
- continuous policy effects generate the historical hard labels;
- no continuous-response predictor has yet been qualified.

It may **not** inherit:

- outcome predictability;
- nonlinear-model superiority;
- a controller;
- threshold correctness;
- ACO-1 support as if it were sufficient;
- any right to reuse protected cohorts.

## 7. ACO-1 data disposition

The 40 ACO-1 seeds / 120 matched boundaries are now:

```text
HISTORICAL / SPENT ACO EVIDENCE
```

They may be retained for:

- provenance;
- reproduction of the ACO-1 STOP;
- file/schema integration tests that do not learn from scientific values.

They may not be used by the new program for:

- model fitting;
- feature selection;
- target selection;
- hyperparameter selection;
- threshold selection;
- baseline-margin tuning;
- validation;
- replication qualification.

The new program requires a fresh seed manifest disjoint from:

1. historical KCL scientific seeds;
2. the protected KCL confirmatory cohort;
3. all 40 ACO-1 seeds.

## 8. New-program design requirements

Before any new scientific execution, a separately named program must freeze:

1. an origin/lineage statement showing it is not ACO-2;
2. the exact primary continuous response vector;
3. the prospectively eligible boundary population;
4. simple frozen baselines;
5. grouped train/validation/replication separation by seed;
6. baseline-superiority and calibration gates;
7. contrast-direction metrics;
8. support rules defined on the continuous target/population, not Y_PRR
   prevalence;
9. a fresh seed manifest and protected-data exclusion;
10. a finite STOP roadmap;
11. controller prohibition until independent replication.

No scientific execution is authorized by this review itself.

## 9. Candidate new-program name

Working governance name:

```text
Continual Policy Response Modeling (CPRM)
```

The name is intentionally different from ACO and KCL.

CPRM would ask:

> Can observable pre-boundary state prospectively predict policy-specific
> continuous learning responses and A-relative action contrasts over a
> predeclared all-boundary population, materially better than frozen simple
> baselines?

This name/question is a review output only. It does not yet constitute a
preregistered experiment.

## 10. Next scientifically valid step

```text
ACO review closure
        ↓
create separate branch/program: CPRM
        ↓
CPRM-0 origin + evidence inheritance + target/population contract
        ↓
finite roadmap + falsification gates
        ↓
zero-training / zero-science specification QA
        ↓
only then design the first fresh scientific protocol
```

Do not start model fitting at CPRM-0.

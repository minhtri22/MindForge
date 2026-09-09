# OIR-PPV H1-H4 Closure Plan

## Purpose

Close H1-H4 one by one using the frozen `EXP-LRN-001` reference benchmark as the baseline layer. Each hypothesis gets its own operational metric, falsification rule, run matrix and closure artifact.

Execution order:

`H1 -> H2 -> H3 -> H4`

The order is deliberate: H1 freezes the cost/representation accounting used by later comparisons; H2 establishes transfer; H3 adds nuisance interventions; H4 adds explicit SCM counterfactual error.

## Frozen inputs

- Protocol base: `M3-Protocol-v1.0`
- Reference benchmark: `EXP-LRN-001`
- Learners: L0 PCA, L1 MLP, L2 VAE, L3 IRM-style, L4 DANN
- Seeds: `42, 123, 456, 789, 1011`
- Environments: ENV-1..ENV-4
- Reference source HEAD: `8d57175f5b5ce7195b6132fec7863331080ac1fe`

MindForge enters only as a new learner through the frozen learner boundary after the M4.1 freeze. Evaluator semantics must remain common across learners.

---

## H1 — Compression / Complexity-Utility

### Hypothesis

`C(I) < C(M)` while `Performance_I >= Performance_M` within a frozen tolerance.

### Current gap

EXP-LRN-001 contains effective rank but no complete complexity model and no raw/context-memorization baseline `M`.

### Required experiment

Create `EXP-H1-001` with three representation conditions per environment/seed:

1. `RAW` — downstream predictor receives raw observation/features.
2. `MEM` — context/raw memorization baseline with explicitly counted storage/state.
3. learner representation — L0-L4 and later MindForge.

### Frozen complexity accounting

Record at minimum:

- representation dimension;
- effective rank;
- trainable parameter count;
- serialized representation/model bytes;
- per-sample retained state bytes;
- training CPU time;
- inference CPU time.

Primary complexity metric:

`C_total = model_bytes + retained_state_bytes`

Secondary metrics: parameter count, latent dimension/effective rank, runtime.

### Utility metric

Use the same downstream task metric already frozen for each environment. Compare paired seed/environment results.

### Closure rule

- `SUPPORTED`: learner has lower `C_total` than MEM/RAW-equivalent retained state and utility is non-inferior under the pre-frozen tolerance.
- `NOT_SUPPORTED`: compression is achieved only with material utility loss, or complexity is not lower.
- `INCONCLUSIVE`: complexity accounting cannot be made comparable.

### Output

- `EXP-H1-001/matrix_manifest.json`
- per-run `complexity.json`
- `H1_CLOSURE_REPORT.md`

---

## H2 — Transfer

### Hypothesis

`Delta_new = Perf(I,new) - Perf(baseline,new) > 0`.

### Current evidence

The compact reference learners mostly lose to PCA on unseen score. This is retained as negative baseline evidence.

### Required experiment

Create `EXP-H2-001` using the frozen OOD/context holdouts already defined by ENV-1, ENV-3 and ENV-4. ENV-2 is reported separately because it has no non-empty OOD split.

Compare each learner against:

- L0 PCA as the primary frozen reference;
- RAW predictor as an additional control from H1;
- MindForge when M5 integration is available.

### Primary metric

Paired per-seed `unseen_environment_score` delta.

Secondary metrics:

- `generalization_delta`;
- accuracy/AUROC where applicable;
- failure count per seed/environment.

### Statistical rule

Freeze before execution:

- paired comparison unit = same environment + same seed;
- report mean, median, min/max and bootstrap or exact paired CI;
- no seed removal;
- no ENV-2 imputation.

### Closure rule

- `SUPPORTED`: positive paired transfer effect across the defined OOD environments with no catastrophic seed regression under the frozen rule.
- `NOT_SUPPORTED`: effect is zero/negative or materially unstable.
- `SUPPORTED_WITH_LIMITS`: uplift exists only in a documented subset of environment families.

### Output

- `H2_CLOSURE_REPORT.md`
- paired delta table and per-seed evidence.

---

## H3 — Nuisance Robustness

### Hypothesis

Representation/policy changes less under nuisance intervention than the baseline.

### Current evidence

Reference learners do not beat PCA on nuisance leakage overall. This is a valid negative baseline result.

### Required experiment

Create `EXP-H3-001` with paired factual/intervened samples under `do(N)` using identical underlying SCM state/context wherever the environment supports it.

For every learner record:

- nuisance leakage classifier performance;
- `do_N_response` / intervention invariance;
- downstream task degradation under nuisance shift;
- shortcut-learning score for ENV-4;
- per-intervention failure cases.

### Primary metric

Use task-preserving nuisance sensitivity, not representation correlation alone:

`Delta_N = Perf_factual - Perf_do(N)`

Smaller absolute degradation is better.

Leakage is a co-primary diagnostic:

`Leak_N = predictive_information(N | I)` operationalized by the frozen leakage probe.

### Falsification test

Shuffle or intervene nuisance while preserving causal task state. A claimed invariant learner should preserve task behavior while nuisance predictability from `I` falls.

### Closure rule

- `SUPPORTED`: lower task degradation and lower/equal nuisance leakage than the primary baseline under the frozen paired rule.
- `NOT_SUPPORTED`: leakage or task degradation is not improved.
- `INCONCLUSIVE`: intervention does not isolate nuisance cleanly.

### Output

- `H3_CLOSURE_REPORT.md`
- intervention-level paired evidence.

---

## H4 — Counterfactual / Causal Accuracy

### Hypothesis

`D_cf(I) < D_cf(M)` against SCM-derived counterfactual ground truth.

### Current gap

EXP-LRN-001 measures representation invariance under `do(N)`/`do(Z)` but does not expose a comparable ground-truth counterfactual outcome error.

### Required experiment

Create `EXP-H4-001` using environments with explicit SCM counterfactual support, starting with ENV-3.

For a factual unit with fixed exogenous noise/state, generate paired ground-truth outcomes under:

- `do(A=a')`;
- `do(Z=z')` where causally meaningful;
- `do(N=n')` as a negative-control intervention where nuisance should not change the causal target.

The learner/policy/generator must predict the corresponding counterfactual response without using the generated prediction as ground truth.

### Primary metric

Define and freeze:

`D_cf = mean d(Y_cf_pred, Y_cf_SCM)`

Use task-appropriate distance `d`:

- classification: counterfactual error / log loss;
- regression/dynamics: MAE or MSE;
- policy transition: state/outcome distance defined by ENV-3 SCM.

### Required controls

- RAW baseline;
- PCA baseline;
- context-only predictor;
- nuisance-only negative control where applicable;
- later MindForge under identical queries.

### Closure rule

- `SUPPORTED`: lower paired `D_cf` than the frozen primary baseline across the defined counterfactual query set.
- `NOT_SUPPORTED`: no reduction or worse error.
- `SUPPORTED_WITH_LIMITS`: improvement only for specific intervention families.

### Output

- frozen counterfactual query manifest;
- SCM ground-truth artifact separated from model predictions;
- `H4_CLOSURE_REPORT.md`.

---

## Execution gates

1. Freeze M4.1 / EXP-LRN-001.
2. Implement H1 measurement only; do not alter learner semantics.
3. QA H1 evidence and freeze the complexity baseline.
4. Run/close H2 using that baseline.
5. Run/close H3 with paired `do(N)` interventions.
6. Freeze explicit counterfactual metric/query semantics for H4.
7. Run/close H4.
8. Only after H1-H4 closure, update `PLAN.md` hypothesis states through a PM-controlled status amendment.

## Stop rules

Stop the affected hypothesis and open a protocol amendment if:

- evaluator semantics must change per learner;
- final benchmark cells have already been used to tune the tested learner;
- the intervention does not isolate the intended causal factor;
- SCM ground truth is unavailable or circularly derived from the learner/generator;
- complexity accounting changes after seeing results;
- failed seeds are removed or replaced.

Negative results are valid closure outcomes.


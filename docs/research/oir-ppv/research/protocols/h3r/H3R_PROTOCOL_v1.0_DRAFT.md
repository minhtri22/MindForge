# OIR-PPV H3R Protocol v1.0 — DRAFT

```text
status: DRAFT
execution_status: NOT_EXECUTED
freeze_status: NOT_FROZEN
scientific_evidence_status: NONE_YET
```

This document prepares the revised H3 robustness protocol under Ontology v1.0 and Formal Spec v1.0. Values marked `TBD_BEFORE_FREEZE` are mandatory freeze items and prohibit decisive execution until resolved.

## 12.1 Identity

```text
protocol_id: OIR-PPV-H3R
protocol_version: v1.0
hypothesis_id: H3R
ontology_version: v1.0
formal_spec_version: v1.0
benchmark_version: H3R-v1.0-DRAFT
status: DRAFT / NOT_EXECUTED / NOT_FROZEN
historical_parent: H3 / M3-Protocol-v1.0 / correction_v3
relation_to_historical_h3: REVISED_SUCCESSOR
```

## 12.2 Falsifiable claim

Primary question:

> Does the candidate representation preserve task and/or interventional performance under a predeclared observation-noise family better than the frozen baseline, while retaining clean utility and without suppressing causal/environment variables that legitimately affect outcomes?

H3R uses risk/loss orientation so lower is better:

```text
R_clean(X) = task risk on clean paired units
R_noisy(X) = task risk on the same units after allowed observation noise
DeltaR_noise(X) = R_noisy(X) - R_clean(X)
```

Candidate operational prediction:

```text
DeltaR_noise(I) < DeltaR_noise(B)
```

subject to a retained clean-utility guard and the frozen uncertainty/practical-equivalence rule.

For tasks historically reported as higher-is-better utility `U`, the equivalent degradation diagnostic is:

```text
D_noise(X) = U_clean(X) - U_noisy(X)
```

The protocol freeze must select one canonical orientation per metric and must not compare signs across incompatible conventions.

## 12.3 Representation lifecycle

Proposed lifecycle pending freeze:

```text
representation_scope: GLOBAL_SHARED_MECHANISM
representation_update_after_train: false
allowed_post_train_inputs: [frozen evaluation observations, declared state/context inputs permitted by model contract]
forbidden_post_train_inputs: [test labels, test outcomes, hidden mechanism parameters not exposed by the protocol, test aggregate metrics, future test cells]
adaptation_budget: 0
adaptation_steps: 0
adaptation_data_source: NONE
```

If implementation review shows the candidate architecture necessarily uses `ENVIRONMENT_CONDITIONED` or `ONLINE_INFERRED` representation, this field must be changed **before** protocol freeze and its adaptation contract must be declared. Any post-train update makes the corresponding result non-zero-shot.

## 12.4 Mechanism contract

The freeze package must declare:

```text
M_shared: TBD_BEFORE_FREEZE
G_shared: TBD_BEFORE_FREEZE
F_shared: TBD_BEFORE_FREEZE
Theta_shared: TBD_BEFORE_FREEZE
Inv(S_k): TBD_BEFORE_FREEZE
Delta_e_allowed: TBD_BEFORE_FREEZE
mechanism_ground_truth_availability: expected TRUE for current simulator candidates; verify before freeze
```

The mechanism contract must state which variables can change without changing the target mechanism and which changes constitute a different environment/mechanism family.

## 12.5 Shift contract

```text
shift_class_declared: OBSERVATION_NOISE
shift_profile_expected: task-mechanism preserving perturbation of observed variables only
realized_shift_validator: REQUIRED / TBD_BEFORE_FREEZE
```

The realized-shift validator must classify and report separately:

- surface shift;
- state-distribution shift;
- parameter shift;
- environment-condition shift;
- mechanism-component shift;
- graph shift.

An H3R observation-noise cell is invalid if the realized perturbation changes the causal target/mechanism outside the declared allowance. Historical ENV-3 is the explicit warning case and must not be repaired or silently relabeled.

## 12.6 Split contract

Formal v1.0 split-unit semantics apply.

```text
split_unit: TBD_BEFORE_FREEZE
allowed_values: [ENVIRONMENT_ID, PARAMETER_REGION, TRAJECTORY, MECHANISM_CONFIG, STATE_REGION, SEED, COMPOSITE]
split_definition: TBD_BEFORE_FREEZE
split_support_train: TBD_BEFORE_FREEZE
split_support_validation: TBD_BEFORE_FREEZE
split_support_test: TBD_BEFORE_FREEZE
```

The split must prevent candidate selection or threshold tuning on final test support. H3 historical seed/environment partitions are design inputs only.

## 12.7 Noise contract

Define a predeclared observation-noise family:

```text
N_delta: TBD_BEFORE_FREEZE
q_eta: TBD_BEFORE_FREEZE
norm: TBD_BEFORE_FREEZE
delta: TBD_BEFORE_FREEZE
variables_affected: TBD_BEFORE_FREEZE
pairing_rule: same underlying causal state/context/mechanism; perturb observation channel only
state_dependence: TBD_BEFORE_FREEZE
label_dependence: FORBIDDEN unless explicitly part of a separately identified non-H3R shift class
mechanism_preservation_assumption: REQUIRED and validated per realized pair
```

Formal separation:

```text
N_delta = allowed observation perturbations
eta ~ q_eta
supp(q_eta) subseteq N_delta
```

If changing a variable changes actual `Y`, the causal graph, or a mechanism component outside the declared allowance, that change is not H3R observation noise.

## 12.8 Metrics

Mandatory metrics:

```text
R_clean
R_noisy
DeltaR_noise = R_noisy - R_clean
```

Optional when the simulator and task support a justified intervention estimand:

```text
R_int_clean
R_int_noisy
DeltaR_int_noise = R_int_noisy - R_int_clean
```

Diagnostic only:

```text
R_repr_noise
```

Representation-distance stability must not become the primary H3R criterion. Historical scale-sensitive latent-shift behavior remains a diagnostic warning.

## 12.9 Metric registry

Every frozen metric entry must contain:

```text
metric_id
metric_version
estimand_id
orientation
requires_ground_truth_mechanism
requires_intervention
requires_counterfactual_pairing
real_data_applicable
proxy_metric_if_no_ground_truth
identification_basis_required
aggregation_rule
uncertainty_rule
acceptance_rule
```

Minimum registry entries before freeze: `R_clean`, `R_noisy`, `DeltaR_noise`, and every metric used by the retained utility guard. Optional interventional or representation diagnostics require separate entries.

## 12.10 Retained utility guard

H3R must prevent trivial robustness caused by destroying task information.

Risk-oriented candidate form:

```text
R_clean(I) <= R_clean(B) + epsilon_utility
```

`epsilon_utility` and its uncertainty rule must be selected before final test access. A candidate that is stable only because clean utility collapses cannot receive `SUPPORTED_UNDER_TESTED_CONDITIONS`.

```text
epsilon_utility: TBD_BEFORE_FREEZE
```

## 12.11 Baseline and candidate set

Historical H1/H2/H3 evidence identifies L0/PCA as the existing primary comparator. H3R therefore carries it forward as the proposed baseline rather than inventing a new comparator.

```text
baseline_id: L0/PCA (PROPOSED_FOR_FREEZE)
candidate_ids: [L1, L2, L3, L4] as historical candidate lineage; final freeze required
training_source: existing learner benchmark lineage; exact H3R training partition TBD_BEFORE_FREEZE
artifact_reuse: historical artifacts may be inspected for compatibility/design only until the H3R representation/split contract is frozen
retraining_status: TBD_BEFORE_FREEZE
model_selection_dependency: must be declared; final test data forbidden for selection
```

If Formal v1.0 lifecycle/split requirements make historical trained artifacts incompatible, H3R must retrain under the frozen H3R contract. Historical H3 values must never be copied into H3R evidence.

## 12.12 Representation equivalence / probe

Exactly one equivalence mode must be frozen if representation equivalence is used:

```text
equivalence_mode: TBD_BEFORE_FREEZE
allowed: [REPRESENTATION_WITH_SHARED_PROBE, SYSTEM_FUNCTIONAL, NOT_APPLICABLE]
```

If `REPRESENTATION_WITH_SHARED_PROBE`, freeze:

```text
probe_id
architecture
parameter_budget
training_data
training_steps
optimizer
selection_rule
seeds
```

If `SYSTEM_FUNCTIONAL`, do not restate the result as representation equivalence. If no equivalence claim is required by H3R, use `NOT_APPLICABLE`.

## 12.13 Evidence / causal identification

For current simulator configurations with verified known mechanism:

```text
evidence_level: E4
mechanism_ground_truth_available: true (VERIFY_BEFORE_FREEZE)
identification_basis: KNOWN_SCM_GROUND_TRUTH
```

For any future unknown-mechanism or real-data extension, declare one identification basis before using interventional risk:

`RANDOMIZED_INTERVENTION`, `CONTROLLED_EXPERIMENT`, `BACKDOOR_ADJUSTMENT`, `FRONTDOOR_ADJUSTMENT`, `INSTRUMENTAL_VARIABLE`, `NATURAL_EXPERIMENT`, `OTHER_DECLARED_METHOD`, or `NOT_IDENTIFIED`.

Also declare:

```text
adjustment_set
positivity_support
consistency_assumption
interference_assumption
unmeasured_confounding_assumption
```

If `NOT_IDENTIFIED`, ground-truth interventional risk must not be reported.

## 12.14 Statistical plan

Freeze before test:

```text
seeds: TBD_BEFORE_FREEZE
environment_count: TBD_BEFORE_FREEZE
state_count: TBD_BEFORE_FREEZE
intervention_count: TBD_BEFORE_FREEZE
design: PAIRED proposed; exact unit TBD_BEFORE_FREEZE
ci_method: TBD_BEFORE_FREEZE
bootstrap_resamples: TBD_BEFORE_FREEZE if bootstrap is used
alpha_or_confidence_level: TBD_BEFORE_FREEZE
multiple_comparison_rule: TBD_BEFORE_FREEZE
practical_equivalence_margin: TBD_BEFORE_FREEZE
aggregation_mode: TBD_BEFORE_FREEZE
worst_case_rule: TBD_BEFORE_FREEZE
```

No failed seed/environment may be removed because its result is unfavorable. Exclusions must be defined from protocol-validity criteria before test inspection.

## 12.15 Pareto / dominance

Pareto reporting is optional. If used, freeze:

```text
pareto_uncertainty_rule
dominance_alpha
multiple_comparison_rule
practical_equivalence_margin
```

Allowed dominance labels:

`DOMINATES`, `DOMINATED`, `NON_DOMINATED`, `STATISTICALLY_UNRESOLVED`.

Point estimates alone cannot establish dominance.

## 12.16 Cost accounting

Cost is diagnostic unless explicitly promoted before freeze. If used in interpretation, record component-wise:

```text
C_phi
C_I
C_P
C_G (if applicable)
```

Each component records:

```text
dim
params
memory_bytes
compute
latency_ms
data_examples
training_compute
```

Unlike units must not be collapsed into one scalar without a predeclared rule.

## 12.17 Test lock

Mandatory freeze fields:

```text
test_manifest: TBD_BEFORE_FREEZE
test_hash: TBD_BEFORE_FREEZE
test_generation_timestamp: TBD_BEFORE_FREEZE
protocol_freeze_timestamp: TBD_BEFORE_FREEZE
candidate_lock_timestamp: TBD_BEFORE_FREEZE
test_unlock_timestamp: null until authorized execution
test_access_log: REQUIRED
test_access_count: 0 at freeze target
```

The final test asset cannot be used for model selection, threshold tuning, candidate pruning, or retry selection.

## 12.18 Acceptance categories

Scientific result labels are restricted to:

- `SUPPORTED_UNDER_TESTED_CONDITIONS`;
- `FALSIFIED_UNDER_TESTED_CONDITIONS`;
- `INCONCLUSIVE`;
- `INVALID_PROTOCOL`;
- `PROTOCOL_DEVIATION`.

Software QA may use PASS/FAIL language separately; the scientific verdict may not.

Proposed support logic, to be fully quantified before freeze:

```text
SUPPORTED_UNDER_TESTED_CONDITIONS iff
  candidate has lower noise-induced risk increase than baseline under the frozen
  uncertainty/practical-equivalence rule
  AND retained clean utility guard passes
  AND realized-shift validation passes
  AND no protocol deviation invalidates the comparison.
```

## 12.19 Claim boundary

An H3R result is limited to the frozen candidate/baseline identities, observation-noise family, mechanism contract, split support, seeds, tasks, and statistical rule.

H3R must explicitly **not** claim:

- full causal understanding;
- transfer overall;
- H4 counterfactual success;
- H5 minimal sufficiency;
- H6 generation;
- robustness to mechanism-changing environments;
- human-like invariance.

## Freeze gate

The protocol remains `DRAFT / NOT_FROZEN / NOT_EXECUTED` until `h3r_freeze_checklist.md` is complete, a machine-readable protocol instance validates against `h3r_protocol_schema.json`, an independent review reports P0=0 and P1=0, and the final protocol hash/candidate/test lock are recorded.

H3R decisive execution is forbidden before that gate.


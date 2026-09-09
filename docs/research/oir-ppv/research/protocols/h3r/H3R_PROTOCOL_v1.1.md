# OIR-PPV H3R Protocol v1.1 — FROZEN

```text
status: FROZEN
execution_status: NOT_EXECUTED
freeze_status: FROZEN
scientific_evidence_status: NONE_YET
protocol_id: OIR-PPV-H3R
protocol_version: v1.1
benchmark_version: H3R-v1.1
ontology_version: v1.0
formal_spec_version: v1.0
freeze_timestamp_utc: 2026-09-09T10:43:48.7398025+00:00
source_anchor_head: d11dd978a19aa7ca6ac33dc7c144f8d3d1e74c2c
historical_parent: H3 / M3-Protocol-v1.0 / correction_v3
relation_to_historical_h3: REVISED_SUCCESSOR
successor_of: H3R v1.0 decisive attempt / implementation PROTOCOL_DEVIATION
scientific_semantics: UNCHANGED_FROM_H3R_v1.0
```

H3R v1.1 is the versioned successor to the consumed H3R v1.0 one-shot attempt. The v1.0 attempt produced no scientific verdict because the runner attempted to cast the full mixed ENV-1 observation table to float before the first cell completed, contradicting the already-frozen `numeric observation channels only` perturbation contract. v1.1 preserves the v1.0 estimand, candidate/baseline set, noise magnitude, metrics, statistics, margins, aggregation, and stopping rule. It changes implementation fidelity and uses a fresh test lock. Historical H3 evidence remains lineage only. H4 remains unopened.

## 1. Falsifiable claim

For each candidate representation system `I` and frozen baseline `B = L0/PCA`:

```text
R_clean(X)       = mean 0/1 task risk on frozen clean test rows
R_noisy(X)       = mean 0/1 task risk on the same rows under frozen observation noise
DeltaR_noise(X)  = R_noisy(X) - R_clean(X)
E_noise(I,B)     = DeltaR_noise(I) - DeltaR_noise(B)
```

Lower is better. H3R asks whether at least one frozen candidate achieves a practically meaningful reduction in noise-induced risk relative to L0/PCA while retaining clean utility.

Primary practical margin:

```text
m_noise = 0.01 absolute risk
epsilon_utility = 0.02 absolute clean risk
```

## 2. Representation lifecycle

```text
representation_scope: ENVIRONMENT_CONDITIONED
representation_update_after_train: false
adaptation_budget: 0
adaptation_steps: 0
adaptation_data_source: NONE
```

The extractor and shared-probe instance are trained separately for each `(environment_id, seed)` using only that cell's clean train split. The environment identity/configuration is therefore an explicit allowed condition. There is no test-time adaptation.

Allowed post-train inputs:

- frozen environment identity;
- frozen clean/noisy evaluation observations;
- frozen deterministic noise-replicate identity.

Forbidden post-train inputs:

- test labels or outcomes during representation extraction;
- aggregate or per-candidate test metrics;
- outputs from other candidates;
- hidden mechanism parameters not exposed by the environment contract;
- future test cells or any data used to retune architecture, thresholds, seeds, or noise magnitude.

## 3. Mechanism contract

H3R makes no claim that ENV-1 through ENV-4 share one identical SCM. `M_shared` is defined within each clean/noisy paired cell.

```text
M_shared:
  the environment-specific simulator mechanism and realized factual row are identical
  between the clean and noisy member of a pair

G_shared:
  the environment-specific causal/dependency structure implemented by the frozen
  generator/config is unchanged between the pair

F_shared:
  structural/outcome functions, label mapping, and factual latent/context realization
  are unchanged; noise is applied only after generate()

Theta_shared:
  effective generator configuration, generator seed, structural/context/nuisance
  realization, task label, and split identity are fixed within the pair

Inv(S_k):
  {generator code/config, causal graph/dependency structure, structural state,
   context/environment condition, nuisance realization, task label/outcome mapping,
   split row identity}

Delta_e_allowed:
  bounded observation-channel perturbation eta only

mechanism_ground_truth_availability: true
```

Any regeneration, `env.intervene(...)`, label recomputation, metadata mutation, parameter change, graph change, or state/context change is outside H3R.

## 4. Shift contract and realized-shift validator

```text
shift_class_declared: OBSERVATION_NOISE
shift_profile_expected: bounded measurement corruption of numeric observation channels only
surface_shift: EXPECTED / BOUNDED
state_distribution_shift: NONE
parameter_shift: NONE
environment_condition_shift: NONE
mechanism_component_shift: NONE
graph_shift: NONE
```

The realized-shift validator MUST verify for every clean/noisy pair:

1. identical environment, generator seed, native test row, metadata, and task label;
2. no call to `env.intervene` and no regeneration between pair members;
3. only the observation tensor changes;
4. normalized `L_inf` perturbation is at most `0.10`;
5. noise draw is produced only from the frozen noise seed derivation and never from label/state values;
6. the same noisy observation is presented to L0 and all candidates for a given row/replicate.

Any failed validator check makes that cell invalid for H3R evidence. Historical ENV-3 `do(N)` is not reused; ENV-3 is eligible here only because H3R perturbs the observation channel after factual generation.

## 5. Split contract

```text
split_unit: COMPOSITE
split_definition:
  (environment_id, generator_seed, generator-native split element)
```

Native split element means:

- ENV-1 and ENV-4: generated row identity;
- ENV-2: generated row identity under the generator's frozen train/test composition contract;
- ENV-3: episode-derived row identity under the generator's episode split.

Frozen support:

```text
train:      generator-native `train` support for the 4 environments x 5 H3R seeds
validation: generator-native `val` support for the same cells; integrity/smoke only
test:       generator-native `test` support identified and hashed in h3r_test_manifest_v1.1.json
```

Candidate identities and thresholds are frozen before any scientific test metric access. Validation cannot prune candidates or alter the primary rule.

## 6. Observation-noise contract

For each `(environment, seed)` compute candidate-independent channel scales from raw clean **train observations only**:

The perturbable-channel mask is also fit from train observations only. A channel is numeric only if all train values are finite and float-convertible. Non-numeric/categorical channels are copied unchanged into every noisy replicate. Test values never determine the numeric mask. The realized-shift validator must confirm categorical values remain unchanged for every replicate.

```text
s_j = max(std_train(X_j), 1e-6)
u_j ~ Uniform[-1, 1]
eta_j = 0.10 * s_j * u_j
X_noisy = X_clean + eta
```

Therefore:

```text
N_delta = {eta : max_j |eta_j| / s_j <= 0.10}
q_eta   = independent per-channel Uniform[-0.10*s_j, +0.10*s_j]
norm    = train-scale-normalized L_inf
delta   = 0.10
variables_affected = all numeric observation channels only
state_dependence = NONE; scale uses train-only channel statistics, draw is test-state independent
label_dependence = FORBIDDEN
mechanism_preservation_assumption = observation corruption occurs after factual generation
noise_replicates_per_test_row = 4
```

Noise seeds are deterministically derived from `(protocol_id, environment_id, generator_seed, test_row_identity, replicate_index)` by SHA-256 and reduced to an unsigned 32-bit seed. This derivation is frozen and independent of outcomes.

## 7. Baseline, candidates, retraining, shared probe

```text
baseline_id: L0/PCA
candidate_ids: [L1, L2, L3, L4]
historical_hyperparameter_source:
  experiments/OIR_PPV/Learner_Benchmark/EXP-LRN-001/matrix_manifest.json
artifact_reuse: NONE_FOR_SCIENTIFIC_EVIDENCE
retraining_status: REQUIRED_FROM_SCRATCH_FOR_H3R
model_selection_dependency: NONE_ON_H3R_TEST; candidate family and hyperparameters already locked
```

Historical trained artifacts may be used only for lineage/implementation compatibility checks. H3R retrains L0-L4 with the historical architecture/hyperparameter definitions on the new H3R seeds and clean train support.

Representation comparison mode:

```text
equivalence_mode: REPRESENTATION_WITH_SHARED_PROBE
probe_id: H3R-LR-v1
architecture: sklearn LogisticRegression
solver: lbfgs
penalty: l2
C: 1.0
max_iter: 1000
training_data: clean train representations only
selection_rule: no hyperparameter or checkpoint selection from H3R test
probe_seed: corresponding generator/model seed
```

The same probe training protocol and same factual train rows are used for baseline and candidates within a cell. H3R claims are limited to the representation-plus-frozen-probe evaluation contract.

## 8. Metrics and registry

All task risks use 0/1 classification error and lower-is-better orientation.

| Metric | Estimand | Aggregation | Uncertainty | Acceptance use |
| --- | --- | --- | --- | --- |
| `R_clean` v1 | clean task risk | mean rows within cell | paired bootstrap at comparison layer | retained utility |
| `R_noisy` v1 | expected noisy task risk | mean over 4 noise replicates then rows | paired bootstrap at comparison layer | primary component |
| `DeltaR_noise` v1 | noise-induced risk increase | `R_noisy - R_clean` | paired bootstrap | primary |
| `DeltaR_clean_vs_L0` v1 | candidate clean-risk gap vs L0 | candidate minus L0 | paired bootstrap | utility guard |

Registry properties for all four metrics:

- ground-truth mechanism required: `false` for the task-risk computation itself;
- intervention required: `false`;
- counterfactual pairing required: `true` for `DeltaR_noise`/candidate-vs-L0 contrasts, `false` for raw risks;
- real-data applicability: `true` for the risk definitions if an equivalent clean/noisy paired observation contract exists;
- proxy: `null`;
- identification basis required: `false` for these observation-noise risk estimands;
- primary comparison is `E_noise(I,B) = DeltaR_noise(I) - DeltaR_noise(B)`.

## 9. Retained clean-utility guard

```text
DeltaR_clean_vs_L0(I) = R_clean(I) - R_clean(L0)
epsilon_utility = 0.02
```

A candidate can be supported only if the multiplicity-adjusted confidence interval upper bound for `DeltaR_clean_vs_L0` is `<= 0.02`. A clearly demonstrated clean-risk loss beyond this margin falsifies the retained-utility part of the compound claim.

## 10. Evidence mode

```text
evidence_level: E4
mechanism_ground_truth_available: true
identification_basis: KNOWN_SCM_GROUND_TRUTH
adjustment_set: []
positivity_support: not required for the primary observation-noise risk estimand
consistency_assumption: paired clean/noisy observations refer to the same factual simulator row
interference_assumption: noise applied to one row does not alter any other row
unmeasured_confounding_assumption: not applicable to randomized synthetic observation noise
```

E4 describes the simulator mechanism availability. It does not promote H3R to a general causal-understanding claim.

## 11. Statistical plan

Frozen generator/model seeds, selected prospectively and disjoint from the historical H1-H3 seeds:

```text
[223691, 965182, 537173, 538839, 124586]
```

```text
environment_count: 4
state_count: 6039 clean test rows across the 20 frozen environment x seed cells
intervention_count: 0
design: PAIRED
bootstrap_resamples: 10000
family_alpha: 0.05
candidate_comparisons: 4
per_candidate_two_sided_confidence_level: 0.9875
multiple_comparison_rule: Bonferroni across the four L1-L4 vs L0 primary contrasts
practical_equivalence_margin: 0.01 absolute risk
```

CI method: deterministic stratified paired bootstrap. Within each environment, resample its 5 seed-level cell effects with replacement, compute the environment mean, then average the four environment means with equal environment weight. The bootstrap RNG seed is `20260909`.

Aggregation order:

1. average noisy loss across 4 frozen noise replicates per row;
2. average rows within `(environment, seed)`;
3. compute candidate-minus-L0 paired effects in that cell;
4. average seed effects within environment;
5. average the four environment means equally.

Worst-case support veto: no candidate may receive `SUPPORTED_UNDER_TESTED_CONDITIONS` if any environment mean `E_noise(I,L0) > +0.02` or any realized-shift validator failure occurs.

No seed/environment may be dropped for unfavorable results. Invalid cells remain recorded and cause `INVALID_PROTOCOL`, `PROTOCOL_DEVIATION`, or `INCONCLUSIVE` according to cause.

## 12. Acceptance and stopping rule

Candidate-level support requires all of:

1. complete valid evidence for all 20 environment x seed cells;
2. multiplicity-adjusted 98.75% CI upper bound for `E_noise(I,L0) < -0.01`;
3. multiplicity-adjusted 98.75% CI upper bound for `DeltaR_clean_vs_L0(I) <= +0.02`;
4. worst-case support veto passes;
5. test lock and realized-shift validator remain intact.

Candidate-level `FALSIFIED_UNDER_TESTED_CONDITIONS` applies when valid complete evidence shows either:

- the adjusted CI lower bound for `E_noise(I,L0) > -0.01`, excluding the required practical improvement; or
- the adjusted CI lower bound for `DeltaR_clean_vs_L0(I) > +0.02`, clearly violating retained clean utility.

Otherwise a valid candidate comparison is `INCONCLUSIVE`.

Global H3R label:

- `SUPPORTED_UNDER_TESTED_CONDITIONS` if at least one candidate is supported;
- `FALSIFIED_UNDER_TESTED_CONDITIONS` if all four candidates are falsified;
- `INCONCLUSIVE` if none is supported and at least one remains inconclusive;
- `INVALID_PROTOCOL` if the frozen scientific contract is not realizable/valid;
- `PROTOCOL_DEVIATION` if decisive execution departs from the frozen contract without an approved amendment.

The decisive run stops after the frozen matrix is complete. No result-dependent retry, seed replacement, threshold change, candidate pruning, or noise retuning is permitted.

## 13. Pareto and cost

```text
pareto_reporting: DISABLED_FOR_H3R_v1.1
cost_acceptance: DISABLED_FOR_H3R_v1.1
cost_scalarization: NONE
```

Cost may be recorded diagnostically by later execution, but it cannot affect the v1.1 scientific verdict. Any future Pareto/cost acceptance requires an amendment or protocol version change before test access.

## 14. Test lock

Canonical lock assets:

- `protocols/h3r/h3r_test_manifest_v1.1.json`;
- `protocols/h3r/h3r_test_access_log_v1.1.md`;
- `protocols/h3r/h3r_protocol_v1.1.json`;
- `protocols/h3r/H3R_PROTOCOL_v1.1.sha256`.

The locked test manifest contains only deterministic identity/provenance hashes and counts. Generation/sealing did not compute candidate outputs or scientific metrics.

```text
test_generation_timestamp_utc: 2026-09-09T08:28:58.714121+00:00
candidate_lock_timestamp_utc: 2026-09-09T08:29:13.563725+00:00
protocol_freeze_timestamp_utc: 2026-09-09T08:29:13.563725+00:00
test_unlock_timestamp: null
scientific_test_access_count_at_freeze: 0
```

Test unlock requires a later explicit execution task after the freeze package has been committed from the MindForge parent repository. Commit/push is intentionally outside this task by owner instruction.

## 15. Claim boundary

Any H3R result is limited to:

- L1-L4 historical learner definitions retrained under this protocol;
- L0/PCA baseline;
- ENV-1 through ENV-4 simulator families at the frozen source/config hashes;
- five H3R seeds listed above;
- generator-native test support locked by the test manifest;
- the train-scale-normalized `L_inf`, `delta=0.10` observation-noise family;
- the shared logistic-regression probe contract;
- this aggregation, multiplicity, utility, and stopping rule.

H3R does not establish full causal understanding, transfer overall, canonical IRM/DANN/VAE/MLP superiority, robustness to mechanism-changing shifts, H4 counterfactual success, H5 minimal sufficiency, H6 generation, MindForge product behavior, real-world robustness, or human-like invariance.

## 16. Freeze governance

This successor is frozen before decisive H3R v1.1 model execution. Any semantic change to seeds, split support, candidates, baseline, noise family/magnitude, metric orientation, utility margin, statistical rule, acceptance logic, or test identity requires another versioned amendment with impact assessment before test unlock.

H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

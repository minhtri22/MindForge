# H3R2_CONFIRMATORY_V2_PROTOCOL_REVIEW

Status: `COMPLETE`

Protocol status: `READY_FOR_FREEZE`

Evidence access: `0`

Scientific verdict: `NOT_EXECUTED`

## Purpose

Review whether H3R2-CONFIRMATORY-v2 can be converted into a deterministic confirmatory contract before any fresh scientific evidence is accessed. This review does not freeze, authorize, execute, generate fresh test identity/seeds, or open H4.

## Scientific Question

Given a fixed reconstructed H3R representation, does a preregistered nonlinear readout recover more task-relevant utility than the historical linear readout beyond nonlinear uplift already available to the L0 control?

Primary target: M6 decoder/readout dependence.

## Claim Boundary

A future positive result may support only: under frozen reconstructed representations and the frozen readout contract, candidate-specific nonlinear recovery exceeds the generic L0 nonlinear uplift under the tested environments/states.

It cannot by itself prove M7, causal sufficiency, invariant representation, universal transfer, generation, or counterfactual validity.

## Historical Evidence Boundary

Preserved without re-adjudication:

- H3R: `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Q-H3R.1: `PARTIAL_MECHANISM_DIAGNOSIS`.
- H3R2: `INVALID_PROTOCOL_INPUT`.
- H3R2-R v1.0: `PROTOCOL_DEVIATION`.
- H3R2-R v1.1: `BLOCKED_BY_GOVERNANCE / NOT_EXECUTED`.
- M6: `EXPLORATORY_SUPPORTED / UNCONFIRMED`.
- M7: `EXPLORATORY_SUPPORTED / UNCONFIRMED`.
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`.

H3R2-R v1.0 is historical/pilot context only. No v1.0 observed value was used to choose a v2 acceptance threshold.

## 22-Item Preregistration Audit

`Pre-test frozen?` is `NO` for every row because the next task, not this review, performs the immutable freeze. `QA=PASS` means the item is now fully and exactly defined and is freeze-ready.

| # | Requirement | Defined? | Exact? | Pre-test frozen? | QA | Blocking issue |
|---|---|---|---|---|---|---|
| 1 | exact hypothesis | YES | YES | NO — next gate | PASS | none |
| 2 | primary estimand | YES | YES | NO — next gate | PASS | none |
| 3 | RelativeRecovery formula | YES | YES | NO — next gate | PASS | none |
| 4 | clean-recovery margin | YES | YES | NO — next gate | PASS | none |
| 5 | reproducibility fraction | YES | YES | NO — next gate | PASS | none |
| 6 | noise non-inferiority margin | YES | YES | NO — next gate | PASS | none |
| 7 | validation→test tolerance | YES | YES | NO — next gate | PASS | none |
| 8 | L0 baseline-control rule | YES | YES | NO — next gate | PASS | none |
| 9 | CI/statistical procedure | YES | YES | NO — next gate | PASS | none |
| 10 | multiple-comparison handling | YES | YES | NO — next gate | PASS | none |
| 11 | missing/invalid-cell policy | YES | YES | NO — next gate | PASS | none |
| 12 | sample-size/power rule | YES | YES | NO — next gate | PASS | none |
| 13 | nonlinear readout architecture | YES | YES | NO — next gate | PASS | none |
| 14 | equal-budget definition | YES | YES | NO — next gate | PASS | none |
| 15 | train/validation/test separation | YES | YES | NO — next gate | PASS | none |
| 16 | fresh test identity policy | YES | YES | NO — next gate | PASS | none |
| 17 | representation reconstruction contract | YES | YES | NO — next gate | PASS | none |
| 18 | seed policy | YES | YES | NO — next gate | PASS | none |
| 19 | stopping rule | YES | YES | NO — next gate | PASS | none |
| 20 | one-shot evidence-access rule | YES | YES | NO — next gate | PASS | none |
| 21 | provenance schema | YES | YES | NO — next gate | PASS | none |
| 22 | deterministic adjudication function | YES | YES | NO — next gate | PASS | none |

## RelativeRecovery Audit

Risk is clean error rate in `[0,1]`; lower is better. For candidate `Li`, readout `p`, and paired cell `c`:

`Gap_p(i,c) = R_clean(Li,p,c) - R_clean(L0,p,c)`.

`NetRecovery(i,c) = Gap_linear(i,c) - Gap_degree2(i,c)`.

Aggregate by equal-weight mean over valid ENV×historical-state-seed cells.

`RelativeRecovery(i) = NetRecovery(i) / Gap_linear(i)` only when the simultaneous lower CI for `Gap_linear(i)` is at least `0.05`; otherwise the candidate is not eligible for a recovery claim.

Positive NetRecovery/RelativeRecovery is good. `0` means no candidate-specific recovery beyond L0. `1` RelativeRecovery means full closure of the fresh linear candidate-vs-L0 gap.

Result: `PASS` — one canonical formula, orientation, aggregation, denominator gate and sign convention.

## L0 Control Audit

`NetRecovery = (R_i,linear - R_i,degree2) - (R_0,linear - R_0,degree2)` algebraically subtracts generic nonlinear uplift available to L0. Criterion E additionally requires the simultaneous lower CI of NetRecovery to be above `0`.

A candidate therefore cannot pass by improving under degree-2 readout when L0 improves equally or more.

Result: `PASS`.

## Threshold Audit

Frozen candidate values for the next freeze task:

- baseline clean gap: `0.05` error-rate units;
- clean NetRecovery margin: `0.02`;
- RelativeRecovery margin: `0.25`;
- reproducibility: `>=0.70` valid cells and success in `>=3/4` environments;
- noise non-inferiority margin: `0.01` excess noise-risk units;
- validation→test degradation tolerance: `0.02`;
- family alpha: `0.05`; four candidates use Bonferroni `alpha_i=0.0125`, i.e. `98.75%` two-sided candidate CIs;
- minimum valid cells: `18/20`, with `>=4/5` in every environment;
- primary NetRecovery CI half-width: `<=0.02`; wider is `INCONCLUSIVE`.

All justification is prospective and recorded in `THRESHOLD_JUSTIFICATION_v2.md`; no acceptance boundary is fitted to v1.0 outcomes.

Result: `PASS`.

## Deterministic Adjudication Audit

`DECISION_RULE_v2.md` and `adjudicate_v2.py` map identity/integrity state plus frozen candidate metrics to exactly one of:

`SUPPORTED_UNDER_TESTED_CONDITIONS`, `PARTIALLY_SUPPORTED`, `FALSIFIED_UNDER_TESTED_CONDITIONS`, `INCONCLUSIVE`, `PROTOCOL_FAILURE`.

Ten synthetic cases A–J were checked. All expected and actual verdicts match. No real experimental metric was passed to the adjudicator.

Result: `PASS`.

## Statistical Audit

Primary unit: paired `ENV × historical-state-seed` cell. There are exactly four historical environments and five reconstructed historical state seeds, hence 20 planned cells. Inference is conditioned on these tested environments/states.

CI: 20,000-replicate nonparametric bootstrap, stratified by environment and resampling the five state-seed cells within each environment. The same bootstrap indices are used across learners/readouts. Bonferroni protects the four candidate-level confirmatory comparisons. No adaptive increase in sample size and no scientific rerun is permitted after evidence access.

Result: `PASS`.

## Readout Budget Audit

Historical reconstruction records common representation output dimension `8` for L0-L4. Linear readout remains logistic regression (`lbfgs`, L2, `C=1.0`, `max_iter=1000`). Nonlinear readout remains fixed degree-2 polynomial features (`include_bias=false`) followed by the same logistic regression. Architecture search and hyperparameter search counts are zero.

Degree-2 has more coefficients than linear; this is explicit, fixed prospectively, equal across L0-L4 for common dimension 8, and its generic capacity effect is controlled by the L0 difference-in-differences estimand. Training data, optimization rule, stopping limit, regularization, seed budget and selection budget are otherwise identical.

Result: `PASS`.

## Fresh-Test Contract

No v2 test seed or dataset identity was generated in this review. Future authorization must create exactly one fresh prospective identity per planned cell, prove zero overlap with historical/Q-H3R.1/H3R2-R identities, lock dataset/split/artifact hashes, and set scientific test access to `0` before execution.

## Provenance Audit

Future execution must bind at minimum `source`, `config`, `seed`, `model_state`, `dataset_identity`, `artifact`, `hash`, plus protocol/decision/metric/representation/readout/test-manifest/runner hashes. Exact H3R reconstruction fidelity remains provenance evidence only.

Result: `PASS`.

## Adversarial QA

All requested attack classes A–T were reviewed. Current blockers: `P0=0`, `P1=0`. One non-scientific P2 remains: the local checkout used before this review was stale relative to the canonical remote branch; the freeze task must synchronize to the canonical review commit before creating an immutable freeze.

## P0/P1/P2

- P0: `0`
- P1: `0`
- P2: `1`

## Final Gate

`FREEZE_READY`

`PROTOCOL_STATUS = READY_FOR_FREEZE`

Next authorized action: `H3R2_CONFIRMATORY_V2_PROTOCOL_FREEZE`.

This review does not perform that freeze and does not authorize evidence access.
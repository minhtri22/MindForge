# REVIEW_BEFORE_H4

## Scope

Independent scientific QA review of the OIR-PPV lineage after H3R, Q-H3R.1, H3R2, and H3R2-R. This review does not rerun evidence, repair historical results, introduce post-hoc decision criteria, or open H4.

## Reviewed Evidence

Reviewed the historical H3R and Q-H3R.1 lineage, H3R2 invalid-input closure, H3R2-R reconstruction/prospective protocol and runner contracts, seed/identity/run/reconstruction manifests, raw-evidence manifest and canonical prospective summary, H3R2-R RESULTS/QA/CLOSURE reports and closure provenance, PLAN/governance requirements, and the formal H4 definition and historical H1-H4 gate sequence.

## Historical Status

The immutable states remain:

- H3R: `FALSIFIED_UNDER_TESTED_CONDITIONS`
- Q-H3R.1: `PARTIAL_MECHANISM_DIAGNOSIS`
- H3R2: `INVALID_PROTOCOL_INPUT`
- H3R2-R: `PROTOCOL_DEVIATION`
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`

## What Is Proven

H3R reconstruction is `RECONSTRUCTION_CONFIRMED`: source snapshot `e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51` reproduces 100/100 historical train-representation SHA-256 values with `mismatch_count = 0`. This establishes reconstruction fidelity for the frozen representation path only.

H3R2-R execution integrity is `EXECUTION_INTEGRITY_PASS`: 20 fresh unique seeds, zero historical overlap, 20/20 cells, 800 raw rows, no rerun, evidence access `0 -> 1`, preserved raw evidence, and fixed source/protocol identities.

The hardened provenance chain identifies source, config, seed, reconstructed model state, dataset identity, artifacts and hashes, plus environment, preprocessing, runner, protocol, split identity, and artifact manifest.

## What Is Not Proven

Reconstruction does not prove M6, M7, an invariant representation claim, or H4. Execution integrity does not create scientific validity when the prospective decision rule is incomplete.

H3R2-R did not prospectively freeze a complete confirmatory adjudication rule. In particular, the pre-test protocol lacks a clean-recovery acceptance margin, reproducibility threshold, noise non-inferiority margin, validation-to-test tolerance, baseline/control decision rule, CI/statistical procedure, and a defined RelativeRecovery decision metric. Those omissions cannot be repaired after evidence access.

All H3R2-R numerical interpretation beyond the frozen reporting contract is therefore `DESCRIPTIVE ONLY`.

## H3R Reconstruction Assessment

`RECONSTRUCTION_CONFIRMED`.

The exact historical representation path was reproduced at the stated source snapshot with 100/100 SHA-256 matches and zero mismatches. The reconstruction manifest is itself hashed and linked into closure provenance. This is historical replay fidelity, not historical scientific proof.

## H3R2-R Execution Assessment

`EXECUTION_INTEGRITY_PASS`.

The prospective run used 20 fresh seeds with five seeds per L1-L4 environment, no historical seed overlap, 20 total cells, 800 raw rows, no rerun, and a one-way evidence-access transition. Source, protocol, runner, data/split, representation/model-state, and artifact identities are traceable.

A reporting inconsistency remains in `RESULTS.md`: it describes aggregation as 20 seeds x 4 environments = 80 values, while the canonical summary and run manifest define 20 total cells with five seeds per environment. The per-environment L0 linear values in `RESULTS.md` also disagree with the canonical prospective summary. This is a P1 reporting/provenance defect; it does not authorize modification of consumed evidence.

A second P1 provenance inconsistency exists in `CLOSURE_PROVENANCE_v1.json`. The sealed evidence-access event at Git head `82861e2d406dc48b9dad4501e7d3b5935428d241` records runner SHA-256 `fb70812c9d7d9e0165c4a81ad106a9b13965817c3ef7592dbcf11ab989228d95` and protocol SHA-256 `a40a6737a29f3f1476cec810667074985cdc4e65c103c819c70a9ecb9ce67b26`; direct hashing of those files at that Git head reproduces the access-event values. `CLOSURE_PROVENANCE_v1.json` records different runner/protocol hashes. The one-shot access event, Git head, identity lock, raw artifacts, and run manifest still make the actual execution boundary recoverable, so this is a recoverable provenance defect rather than a reason to rewrite consumed evidence.

## H3R2-R Scientific Assessment

`CONFIRMATORY_ADJUDICATION = NOT_AVAILABLE`.

The protocol deviation is P0 because the missing pre-test decision criteria block a valid confirmatory conclusion. Documenting the omission after evidence access does not fix it. Nonlinear degree-2 readout improvement, clean/noisy risks, noise deltas, L0 controls, L1-L4 behavior, and environment heterogeneity may be discussed only descriptively.

No new RelativeRecovery, threshold, statistical test, or confirmatory verdict is introduced by this review.

## M6 Status

`EXPLORATORY_SUPPORTED / UNCONFIRMED`.

Q-H3R.1 provides exploratory support for decoder/probe mismatch as a candidate explanation, and H3R2-R supplies descriptive readout-complexity evidence consistent with that possibility. The evidence does not causally isolate M6 from competing explanations and lacks prospective confirmatory adjudication.

## M7 Status

`EXPLORATORY_SUPPORTED / UNCONFIRMED`.

Q-H3R.1 also supports nonlinear-interaction failure as a competing exploratory mechanism. Better nonlinear decoding does not prove nonlinear interaction failure and does not prove invariant representation. H3R2-R therefore does not upgrade M7 to a confirmatory claim.

## H4 Eligibility

Scientific gate classification: `H4_ELIGIBLE`.

The formal H4 hypothesis is the counterfactual claim `D_cf(I) < D_cf(M)` against SCM-derived counterfactual ground truth, with `D_cf` defined over predicted versus SCM counterfactual outcomes. The historical gate sequence requires the H3 stage to be closed before H4 protocol/query freeze. H3R is closed by an explicit negative adjudication. No later authorized document reviewed here makes confirmatory H3R2/M6/M7 success a formal H4 prerequisite.

Accordingly, H3R2-R does not provide confirmatory evidence for H4, but its protocol deviation also does not create a new prerequisite that the formal H4 definition does not contain. H4 eligibility comes from completion of the prior formal gate, not from treating H3R2-R descriptive results as a PASS.

H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`. Before any H4 evidence access, H4 must still prospectively freeze its own counterfactual metric/query set, SCM ground-truth separation, interventions/controls, decision rule, identities, and provenance. Eligibility is not authorization to open or run H4.

## Confirmatory Gap

A new H3R2 confirmatory experiment is **not required as a prerequisite to H4 under the currently identified formal gate**. It would be scientifically useful only if the owner wants a confirmatory claim about M6/M7 or adopts a new policy that requires such confirmation before H4. Such a policy would have to be prospective; it cannot be retrofitted into the consumed H3R2-R run.

If H3R2 confirmation is pursued later, a new protocol must freeze before evidence access: exact hypothesis, primary endpoint, exact metric formula, RelativeRecovery definition, clean-recovery threshold, reproducibility threshold, noise non-inferiority margin, validation-test tolerance, L0 baseline rule, CI/statistical procedure, seed policy, fresh test identity, readout budget, stopping rule, and failure rule. These are pre-registration requirements, not repairs to H3R2-R.

## Research Integrity

The reviewed closure materials preserve the required distinctions: representation != mechanism; causal sufficiency != transfer; transfer != generation; generation != counterfactual validity; diagnostic != confirmatory evidence; execution integrity != scientific validity; historical reconstruction != historical proof.

The principal scientific defect is explicitly preserved as `PROTOCOL_DEVIATION`, rather than repaired post hoc. Provenance hardening improves traceability but does not retroactively restore confirmatory validity. Both P1 findings must remain documented: `RESULTS.md` disagrees with canonical execution evidence, and the closure provenance runner/protocol hashes disagree with the sealed evidence-access identities. Neither defect may be resolved by rewriting consumed evidence in this review.

## Final QA Verdict

- Review: `COMPLETE`
- H3R reconstruction: `RECONSTRUCTION_CONFIRMED`
- H3R2-R execution: `EXECUTION_INTEGRITY_PASS`
- H3R2-R confirmatory adjudication: `NOT_AVAILABLE`
- M6: `EXPLORATORY_SUPPORTED / UNCONFIRMED`
- M7: `EXPLORATORY_SUPPORTED / UNCONFIRMED`
- H4 scientific eligibility: `H4_ELIGIBLE`
- H4 operational state: `NOT_OPENED / DEFERRED_BY_OWNER`
- Confirmatory H3R2 before H4: `NOT_REQUIRED`
- QA findings: `P0=1, P1=2, P2=0`
- Recommended next state: `REVIEW_COMPLETE__DEFER`

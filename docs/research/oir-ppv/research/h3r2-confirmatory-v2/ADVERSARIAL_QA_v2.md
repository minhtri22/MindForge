# H3R2-CONFIRMATORY-v2 Adversarial QA

Review target: protocol definition only. No scientific evidence was generated or accessed.

| Attack | Resolution | QA |
|---|---|---|
| A estimand ambiguity | one primary NetRecovery difference-in-differences formula | PASS |
| B metric direction ambiguity | every metric has explicit orientation | PASS |
| C hidden baseline dependence | L0 appears inside primary estimand and criterion E | PASS |
| D nonlinear capacity confound | architecture fixed; common dim=8; generic nonlinear uplift subtracted via L0; parameter counts recorded | PASS |
| E candidate cherry-picking | L1-L4 all tested; ANY_ONE rule predeclared | PASS |
| F environment cherry-picking | ENV-1..4 all predeclared; equal environment weighting | PASS |
| G seed cherry-picking | five historical state seeds fixed; future test-seed generation rule fixed; no post-test exclusion | PASS |
| H validation leakage | validation uses historical train data only; no test input | PASS |
| I test leakage | architecture/thresholds/metrics fixed before test identity/evidence | PASS |
| J threshold leakage | thresholds justified prospectively; v1.0 cannot tune acceptance | PASS |
| K multiple comparison leakage | Bonferroni four-candidate family fixed | PASS |
| L missing-data bias | 18/20 and >=4/5 per ENV rule; no silent replacement | PASS |
| M power deficiency | fixed 20-cell population plus CI precision gate; wide CI => INCONCLUSIVE | PASS |
| N adaptive stopping | one decisive execution; no early success stop | PASS |
| O post-hoc rerun | no rerun after access 1; new protocol/evidence required | PASS |
| P representation mutation | exact reconstructed states/hash gate; no fit/update path | PASS |
| Q decoder selection leakage | exactly one linear and one degree-2 config; no search | PASS |
| R provenance gaps | explicit representation/test/freeze/runner/adjudicator hashes required | PASS |
| S nondeterministic adjudication | executable finite-state adjudicator + synthetic cases | PASS |
| T contradictory acceptance criteria | priority ordering and candidate states are explicit | PASS |

## Additional checks

The historical H3R2-R v1.0 reporting inconsistency (its narrative cell-count wording differs from canonical manifests/summary) is preserved as historical debt and is not used as a v2 source of scientific truth. Canonical manifests and reconstruction artifacts govern identity/provenance.

No v1.0 acceptance threshold was copied from observed outcomes.

## Severity

P0: `0`

P1: `0`

P2: `1`

P2-001: the local checkout observed before this review was stale relative to canonical remote branch `codex/oir-lineage-cleanup`. This is operational, not scientific. The freeze task must synchronize to the review commit before producing an immutable freeze bundle.

Freeze-readiness condition `P0=0` and `P1=0` is satisfied.
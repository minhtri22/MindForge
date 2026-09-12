# H3R2-CONFIRMATORY-v2 Deterministic Adjudication Dry Run

Only synthetic dummy metrics were used. The synthetic harness simulates a future post-execution `access_count=1`; actual H3R2-CONFIRMATORY-v2 scientific evidence access remains `0`.

| Case | Synthetic condition | Expected | Actual | Result |
|---|---|---|---|---|
| A | one candidate clears A-E with adjusted CIs | SUPPORTED_UNDER_TESTED_CONDITIONS | SUPPORTED_UNDER_TESTED_CONDITIONS | PASS |
| B | all eligible candidates definitively miss clean recovery | FALSIFIED_UNDER_TESTED_CONDITIONS | FALSIFIED_UNDER_TESTED_CONDITIONS | PASS |
| C | clean/generalization/L0 pass; exactly reproducibility fails | PARTIALLY_SUPPORTED | PARTIALLY_SUPPORTED | PASS |
| D | clean-recovery CI crosses confirmatory boundary / precision unresolved | INCONCLUSIVE | INCONCLUSIVE | PASS |
| E | raw candidate nonlinear uplift exists but L0 uplift cancels it; NetRecovery fails | FALSIFIED_UNDER_TESTED_CONDITIONS | FALSIFIED_UNDER_TESTED_CONDITIONS | PASS |
| F | insufficient reproducibility only | PARTIALLY_SUPPORTED | PARTIALLY_SUPPORTED | PASS |
| G | noise non-inferiority fails only | PARTIALLY_SUPPORTED | PARTIALLY_SUPPORTED | PASS |
| H | validation→test degradation definitively exceeds tolerance | FALSIFIED_UNDER_TESTED_CONDITIONS | FALSIFIED_UNDER_TESTED_CONDITIONS | PASS |
| I | only 17/20 valid cells | INCONCLUSIVE | INCONCLUSIVE | PASS |
| J | one multiplicity-adjusted full-support candidate, other candidates fail/uncertain under predeclared ANY_ONE rule | SUPPORTED_UNDER_TESTED_CONDITIONS | SUPPORTED_UNDER_TESTED_CONDITIONS | PASS |

Synthetic protocol-integrity failure was also checked separately: hash/access/representation/rerun violation deterministically returns `PROTOCOL_FAILURE` before scientific criteria.

Dry-run result: `10/10 PASS` plus integrity-gate PASS.

No H3R2-R v1.0 metric was passed into the adjudicator or used to modify its rules.
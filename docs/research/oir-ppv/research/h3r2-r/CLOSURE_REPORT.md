# H3R2-R Closure Report

Closure state: **PROTOCOL_DEVIATION**

Recommended transition: **REVIEW_BEFORE_H4**

## What was established

H3R historical state reconstruction succeeded exactly: 100/100 train-representation SHA-256 comparisons matched with zero mismatches. The one-shot H3R2-R prospective execution then completed all 20 cells using 20 fresh seeds with no overlap with historical seeds. Scientific access advanced from zero to one and the decisive execution was not rerun.

The observed risks and noise deltas are preserved in `prospective_execution_v1/H3R2R_PROSPECTIVE_SUMMARY_v1.json` and summarized in `RESULTS.md`. They are retained as descriptive evidence.

## Why no confirmatory H3R2-R verdict is assigned

The pre-test protocol did not freeze the quantitative acceptance thresholds or statistical decision plan required by the task. This was discovered only after the prospective output had already been consumed. Backfilling those criteria now would turn the confirmatory decision into a post-hoc decision.

For that reason this closure intentionally does not label H3R2-R as `SUPPORTED`, `PARTIALLY_SUPPORTED`, or `FALSIFIED`. The correct status of this execution is `PROTOCOL_DEVIATION`.

`RelativeRecovery` is likewise not defined by the frozen protocol or repository evidence. No post-hoc formula is introduced.

## Preserved scientific state

| Item | Closure state |
|---|---|
| Historical H3R | `FALSIFIED_UNDER_TESTED_CONDITIONS` |
| Q-H3R.1 | `PARTIAL_MECHANISM_DIAGNOSIS` |
| H3R reconstruction | `EXACT_100_OF_100` |
| H3R2-R execution integrity | `PASS` |
| H3R2-R confirmatory adjudication | `PROTOCOL_DEVIATION` |
| H4 | `NOT_OPENED / DEFERRED_BY_OWNER` |
| Next state | `REVIEW_BEFORE_H4` |

## Governance decisions

No thresholds, seeds, readout definitions, raw outputs, historical findings, or evidence hashes are changed to improve the result. No decisive rerun is performed. No H4 work is opened.

If H3R2-R is later retried as a confirmatory experiment, it requires a new prospective protocol that freezes all acceptance margins, reproducibility rules, baseline-control rules, validation-to-test tolerance, CI/statistical procedure, and any derived metric formula before any new evidence is accessed. New prospective evidence must then be generated under that frozen protocol.

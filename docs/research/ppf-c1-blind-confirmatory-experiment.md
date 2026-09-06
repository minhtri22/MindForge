# PPF-C1 — Blind Confirmatory Experiment

Starting commit: `aa90af6ba0f45903d99cec4829355962cb613fa2`.

## Purpose and frozen hypothesis

C1 was designed only to test the already-selected L5 mechanism `T1 = B9 + E1 Observability Eligibility` against frozen `T0 = B9` on a new protected holdout. It was not a mechanism-discovery stage and did not authorize T2–T7, new thresholds, Model/Kernel changes, or production placement.

The preregistered hypothesis was that explicit observability eligibility would reduce false active claims under unavailable or unknown observation state while preserving `SUPPORTED` recall and correction/deletion lifecycle correctness.

## Preregistration

Preregistration was written before any C1 history generation.

- canonical preregistration SHA-256: `ed63bd5a3dcd2364b5bb9fd13f70d34e6be11513e8ec8a4c2e272f13a8ce92e7`
- canonicalization rule: SHA-256 over canonical UTF-8 JSON with sorted keys and compact separators, excluding only `canonical_preregistration_sha256`
- persons: 12
- truth configurations: 12
- STANDARD / HIGH-RISK: 8 / 4
- registered histories: 64
- structural holdouts: 4
- focused counterfactual pairs: 8 / 16 paired histories
- rerolls allowed: 0
- seed namespace: `mindforge-ppf-c1-confirmatory-v1`

The eight focused pairs covered two full-observability/permission-loss pairs, two normal-observation/data-delayed pairs, two direct `OBSERVABLE_NON_OCCURRENCE`/`NO_OBSERVATION` pairs, one observability-loss/lifecycle pair, and one observability-loss/unknown-context pair.

## One-shot generation outcome

The canonical generation attempt was executed exactly once. It constructed all 64 registered histories in memory and ran generator QA before persisting the benchmark.

The arithmetic and isolation controls passed:

- 12 persons / 12 configs / 64 histories
- 8 STANDARD / 4 HIGH-RISK
- 4 structural holdouts
- 8/8 focused pair contracts
- zero prior person/config/case/history-identity overlap
- truth leaks: 0
- future leaks: 0
- rerolls: 0

Generator QA nevertheless failed the mandatory L2-validity gate. Of 650 visible events, 598 were L2-valid and 52 were invalid. Every reported invalidity came from the same generator defect: observability-loss records used `missingness_reason = C1_OBSERVATION_LIMITATION`, which is not a member of the frozen PPF-L2 missingness-reason enum.

The frozen enum permits `MISSING_BY_DESIGN`, `SENSOR_NON_COLLECTION`, `PLATFORM_RESTRICTION`, `PERMISSION_LIMITATION`, `DEVICE_DISCONNECTED`, `WEARABLE_NON_WEAR`, `SAMPLING_GAP`, `SYNC_DELAY`, `HISTORY_UNAVAILABLE`, and `UNKNOWN`.

This failure occurred before benchmark persistence. `benchmarks/ppf_c1/` was therefore not written.

## Required stop

The C1 protocol states that generator QA failure produces `C1 = REVISE` and forbids T0/T1 evaluation. It also forbids replacing cases, changing seeds, or regenerating after an unfavorable/invalid generation attempt.

Accordingly:

- generator source was not repaired and rerun in this task;
- no C1 dataset lock was created;
- no confirmatory run lock was created;
- no private C1 truth was accessed for scoring;
- semantic confirmatory run count is 0;
- T0 and T1 have no C1 metrics;
- the primary and observable-nonoccurrence specificity rules are `NOT_EVALUATED`.

The L5 result therefore remains exploratory DEV + VALIDATION evidence and is **not blind-confirmed** by C1.

## Frozen prior research

C1 did not modify L3 datasets, L4 evidence, L5 DEV/VALIDATION results, the L5 mechanism lock, or the selected E1 mechanism. The failure is an execution/protocol defect in the new C1 generator representation, not evidence that T1 generalized or failed to generalize.

## C1 gates

| Gate | Result | Evidence |
| --- | --- | --- |
| C1-G1 | PASS | prior frozen research untouched during C1 work |
| C1-G2 | PASS | canonical preregistration hash valid |
| C1-G3 | PASS | 12 persons / 12 configs / 64 generated in the one attempt |
| C1-G4 | PASS | 8 STANDARD / 4 HIGH-RISK |
| C1-G5 | PASS | zero prior identity overlap in generator QA |
| C1-G6 | PASS | 4 structural holdouts |
| C1-G7 | PASS | 8 focused pairs; one pair per paired history |
| C1-G8 | PASS | 64 registered/generated/retained in attempt; 0 rerolls |
| C1-G9 | **FAIL** | 598/650 visible events L2-valid; 52 invalid |
| C1-G10 | PASS | truth leak 0; future leak 0 |
| C1-G11 | PASS | preregistered T0 points to frozen B9 source |
| C1-G12 | PASS | preregistered T1 points to frozen L5 E1 source/lock |
| C1-G13 | NOT REACHED | dataset lock forbidden after QA failure |
| C1-G14 | NOT REACHED | run lock forbidden |
| C1-G15 | NOT REACHED | semantic run count 0 |
| C1-G16 | NOT REACHED | no confirmatory runner invocation after failure |
| C1-G17 | NOT EVALUATED | primary rule requires valid locked dataset |
| C1-G18 | NOT EVALUATED | specificity rule requires valid locked dataset |
| C1-G19 | PASS | no mechanism discovery/tuning performed |
| C1-G20 | PASS | research ledger updated in closure commit |

## Verdict

**REVISE — GENERATOR/PROTOCOL EXECUTION FAILURE.**

C1 did not test the scientific hypothesis because the new holdout failed the pre-evaluation L2 validity gate. No inference about T1 confirmatory generalization is permitted from this attempt.

Any future C1 attempt must be a separately reviewed protocol repair/re-preregistration decision. This task authorizes no further stage.

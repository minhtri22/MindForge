# PPF-L4 Minimal / Stupid Baselines

Status: **COMPLETE / BASELINES FALSIFIED AS SUFFICIENT PPF MECHANISM**

PPF-L4 asks a deliberately narrow question: how far can fixed, deterministic, obviously-limited heuristics get on the frozen PPF-L3 benchmark before any new mechanism is justified?

Architecture boundary remains frozen:

```text
Model != Kernel.
The Model owns learned representations/capabilities.
The Kernel owns only proven universal primitives.
Plugins own feature-specific mechanisms and semantics.
Hosts own composition.
PPF is optional extension/plugin research.
L4 cannot self-authorize Model or Kernel changes.
```

## Baselines

The suite is frozen before FINAL evaluation:

| ID | Baseline | Fixed rule |
|---|---|---|
| B0 | Always Abstain | always `INSUFFICIENT_EVIDENCE` |
| B1 | Always Supported | always `SUPPORTED` |
| B2 | Last Observation | last determinate observation decides supported vs insufficient |
| B3 | Any Occurrence | any visible occurrence -> supported |
| B4 | Raw Count Threshold | 3 raw occurrence records -> supported |
| B5 | Naive Frequency | >=3 determinate records and occurrence frequency >=0.60 |
| B6 | Recency Heuristic | >=2 occurrences in latest 3 determinate records |
| B7 | Naive Majority | >=3 determinate records and strict global occurrence majority |
| B8 | Context-Keyed Majority | strict majority within latest visible context key, >=3 records |
| B9 | Lifecycle-Naive Rule | latest explicit correction/delete/supersede control wins; otherwise B7 |
| B10 | Provenance-Naive Counter | count source records independently; threshold 3 |
| B11 | Provenance-Dedup Counter | drop replica/derived recurrence and deduplicate opportunity IDs; threshold 3 |

These constants are baseline falsification knobs, not PPF truth definitions and not production admission thresholds.

## Evaluation order

The required execution order is:

```text
DEV
-> VALIDATION
-> BASELINE LOCK
-> FINAL one-shot
```

Before the lock, FINAL evaluator-private truth/expected-answer artifacts must not be read. The lock records SHA-256 hashes of the baseline implementation, evaluator implementation, DEV result, VALIDATION result, and exact B0-B11 registry/parameters. FINAL execution refuses to run without a valid lock and refuses to overwrite an existing FINAL result.

The baseline method receives only the frozen method-visible files:

```text
history.json
checkpoints.json
```

Evaluator truth, family labels, expected answers, identifiability, pair membership, and scope are loaded only after predictions have been produced. They are used only for scoring/slicing.

## Metric rule

No weighted aggregate score is introduced. Report the vector independently:

```text
exact semantic-state accuracy
SUPPORTED precision/recall status proxies
false discovery rate
false promotion rate
negative-state exact accuracy
lifecycle exact accuracy
hard active-return violations
breakdowns by expected state / identifiability / family / truth kind / scope / counterfactual template
```

The current generated L3-v1 expected-answer contract is checkpoint semantic-state only. Therefore exact pattern-scope matching is not claimed by L4; truth scope is only an evaluator-side slice.

## Prohibitions

L4 does not modify frozen L3 datasets, generator truth, oracle semantics, Model, Kernel, host integration, or production plugin code. No baseline is tuned from FINAL outcomes, no final reroll is permitted, and no post-final threshold change can be presented as the same confirmatory run.

## Execution evidence

Execution completed in the frozen order:

```text
DEV -> VALIDATION -> BASELINE LOCK -> FINAL ONE-SHOT
```

Lock SHA-256:

```text
477619a6375621a4514a07baa37e2f112e6e9b8709917c7ea075484de0744006
```

FINAL contains 616 checkpoint/evaluation units:

```text
SUPPORTED:              149
INSUFFICIENT_EVIDENCE:  288
CONFLICTING_EVIDENCE:    24
UNKNOWN_CONTEXT:         31
NOT_OBSERVABLE:          86
STALE:                    3
USER_REJECTED:           15
SUPERSEDED:               5
DELETED:                 15
```

### Baseline result matrix

Exact semantic-state accuracy and FINAL false-promotion rate:

| Baseline | DEV | VALIDATION | FINAL | FINAL false promotion |
|---|---:|---:|---:|---:|
| B0 | 0.5314 | 0.5314 | 0.4675 | 0.0000 |
| B1 | 0.2850 | 0.2850 | 0.2419 | 1.0000 |
| B2 | 0.3961 | 0.4203 | 0.3458 | 0.6124 |
| B3 | 0.2947 | 0.2899 | 0.2419 | 1.0000 |
| B4 | 0.6135 | 0.6184 | 0.5844 | 0.5482 |
| B5 | 0.6232 | 0.6329 | 0.5942 | 0.3961 |
| B6 | 0.6087 | 0.6135 | 0.5536 | 0.4668 |
| B7 | 0.6184 | 0.6329 | 0.5990 | 0.4604 |
| B8 | 0.6715 | 0.6184 | 0.5487 | 0.2120 |
| B9 | **0.7391** | **0.7536** | **0.6558** | 0.3854 |
| B10 | 0.6135 | 0.6184 | 0.5844 | 0.5482 |
| B11 | 0.6280 | 0.6232 | 0.5844 | 0.5482 |

No single scalar decides a winner. The table is descriptive only; the metric vector and hard violations remain authoritative.

### Important hard-failure evidence

`B9 Lifecycle-Naive Rule` is the strongest exact-state baseline and correctly prevents active returns after explicit correction/deletion in FINAL:

```text
deleted_active_return_violations:      0
correction_resurrection_violations:    0
```

But it still fails materially on observation/context semantics:

```text
FINAL exact_state_accuracy:                 0.6558
FINAL false_promotion_rate:                 0.3854
FINAL stale_as_current_violations:          3
FINAL not_observable_as_current_violations: 77
FINAL unknown_context_positive_violations:  31
FINAL conflict_positive_violations:          8
```

`B8 Context-Keyed Majority` lowers FINAL false promotion to 0.2120, but only reaches 0.5487 exact-state accuracy and still fails lifecycle/observability cases. `B0 Always Abstain` has zero false promotion but zero positive recall. Provenance deduplication alone (`B11`) does not improve FINAL result over raw counting (`B4`) on this protected split.

## L4 scientific decision

The result is not `PPF PASS` and not a production recognizer.

The tested stupid baselines establish that these individual shortcuts are insufficient:

```text
raw recurrence counting
global frequency/majority
short recency windows
single visible context bucketing
explicit lifecycle controls alone
provenance deduplication alone
```

The smallest failure clusters exposed by FINAL are now concrete:

1. observability/coverage must be separated from behavioral negative evidence;
2. stale/current state needs explicit temporal handling;
3. unknown context and conflicting evidence require first-class abstention;
4. explicit correction/deletion/supersession must dominate passive recurrence;
5. context-sensitive evidence cannot be reduced to one naive latest-context majority;
6. provenance deduplication is necessary for evidence hygiene but is not sufficient for recognition.

These observations are evidence for a separately authorized L5 minimum-missing-mechanism experiment. L4 itself makes no Model or Kernel recommendation and does not authorize L5 implementation.

## Regression / immutability note

Focused L4 tests: **6/6 PASS**.

The frozen L3 suite was rerun from a clean detached snapshot at exact L3 HEAD `b94645cc9d69a50a098683e543489ba01fda0057`: **55/55 PASS**.

Running the same L3 suite inside the L4 worktree yields 55 passing tests and six phase-scope failures because old L3 gates explicitly encode `L4` as forbidden scope. E1 confirms G1-G11 PASS and only E1-G12 fails, listing the newly authorized `tools/research/ppf_l4/` and `tests/research/ppf_l4/` paths. No frozen L3 generator, dataset, oracle, or test file was modified to silence those guards.

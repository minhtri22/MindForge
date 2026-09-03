# Track A Benchmark v1 — Independent Semantic Review

Status: **REVISE — MATERIALIZED BENCHMARK NOT READY FOR FINAL FREEZE**

Branch: `research/track-a-benchmark-v1`

Reviewed artifacts:

- `track-a-capability-v1/calibration.jsonl`
- `track-a-capability-v1/development.jsonl`
- `track-a-capability-v1/test.jsonl`
- `track-a-capability-v1/human-review-sample.jsonl`

Review scope:

```text
Deep stratified review: 140 / 140 sample cases
Full semantic/structural audit: 1,400 / 1,400 benchmark cases
Families: A1-A7
```

## Verdict

```text
N3.1 MATERIALIZATION: PASS
AUTOMATED STRUCTURAL QA: PASS
INDEPENDENT SEMANTIC REVIEW: REVISE
BENCHMARK FINAL FREEZE: BLOCKED
N3.R1-B QWEN EXECUTION: BLOCKED UNTIL REGENERATED BENCHMARK PASSES REVIEW
N4 SIZE SWEEP: NOT AUTHORIZED
```

The benchmark is structurally reproducible and its quotas/counterfactual mechanics are useful, but the current semantic truth and split design contain systematic defects that would distort candidate evaluation.

## Severity policy

```text
CRITICAL
- wrong or underdetermined benchmark truth
- a correct model could be penalized by the frozen label
- held-out leakage that materially weakens falsification

MAJOR
- repeated unnatural phrasing or weak realism that biases a family
- scoring semantics inconsistent with the stated capability

MINOR
- punctuation/noise/wording quality that does not change truth
```

## Finding SR-01 — exact-name entity resolution incorrectly forced to clarify

Severity: **CRITICAL / SYSTEMIC**

Affected families:

```text
A2 personal entity resolution
A6 clarification decision
```

Affected cases detected in the full 1,400-case audit:

```text
72 cases total
A2: 52
A6: 20
```

The recurring fixture contains both:

```text
Tuấn
Tuấn Anh
```

but cases such as:

```text
"Gọi Tuấn"
"call Tuấn"
"Call Tuan"
```

are sometimes labeled `clarification_required = true` merely because `Tuấn Anh` also exists.

This is not a sound default truth policy. An exact full-name match to `Tuấn` is normally sufficient to resolve `Tuấn`; a longer distinct contact name `Tuấn Anh` does not automatically make the exact reference ambiguous.

A candidate that correctly chooses the exact-name contact would therefore be penalized.

Deep-review sample exposure:

```text
6 / 140 sample cases
```

Required correction:

- freeze an explicit entity-matching policy;
- use genuinely ambiguous same-surface references when clarification is intended, e.g. two contacts sharing the same display name or an underspecified relation/reference;
- regenerate A2/A6 affected cases rather than patching labels manually.

## Finding SR-02 — A5 argument extraction translates content instead of extracting it

Severity: **CRITICAL / SYSTEMIC**

Affected family:

```text
A5 argument extraction
```

Detected full-benchmark cases:

```text
10 cases
```

Example input:

```text
message Linh: I'm late 20 phút
```

Expected argument currently contains:

```text
tôi về muộn 20 phút
```

The benchmark family is defined as argument extraction. Unless an explicit normalization/translation contract is separately frozen, the extracted message payload should preserve the user's source content rather than silently translate it.

A model returning the literal source payload could be scored wrong even though it performed extraction correctly.

Deep-review sample exposure:

```text
4 / 140 sample cases
```

Required correction:

- define whether message payload scoring is literal extraction or normalized semantic content;
- for v1, prefer literal/canonical span extraction to avoid adding a translation task to A5;
- regenerate affected cases and scorer fixtures.

## Finding SR-03 — held-out template leakage is complete

Severity: **CRITICAL / BENCHMARK DESIGN**

For every family A1-A7:

```text
calibration template IDs ∩ held-out template IDs = 25 / 25
 development template IDs ∩ held-out template IDs = 25 / 25
```

There is also substantial exact utterance overlap between calibration/development and held-out test.

Observed calibration-vs-test exact utterance overlaps:

```text
A1 16
A2 14
A3 15
A4 11
A5 11
A6 14
A7 11
```

Observed development-vs-test overlaps:

```text
A1 20
A2 15
A3 15
A4 16
A5 13
A6 17
A7 12
```

The current generator uses the same 25 template IDs across all splits. Because calibration/development are explicitly available for evaluation/prompt work while held-out is supposed to remain protected, this weakens the held-out set into a template-recognition test.

Dates, times, distractors, and state values make individual JSON inputs unique, but that does not remove semantic/template leakage.

Required correction:

- create split-disjoint semantic template/scenario families;
- held-out must contain unseen wording/templates and preferably unseen template-composition patterns;
- keep controlled entity recurrence only where explicitly required for personal-entity tests;
- add an automated split-leakage gate before final freeze.

## Finding SR-04 — A7 calculator counterfactual has underdetermined routing truth

Severity: **MAJOR / POSSIBLY CRITICAL**

Affected held-out counterfactual cases:

```text
40 arithmetic cases total
20 labeled LOCAL_MODEL
20 labeled EXTERNAL
```

The counterfactual changes only:

```text
available_local_capabilities: ["calculator"] -> []
```

for an utterance such as:

```text
"Tính 18 nhân 7"
```

The expected route changes from `LOCAL_MODEL` to `EXTERNAL`.

This is not yet semantically justified. A local learned model may itself be capable of trivial arithmetic even if a separately declared `calculator` capability is absent. Conversely, if `available_local_capabilities` is intended to be the exhaustive list of what the local model/runtime can do, that meaning must be frozen explicitly and `LOCAL_MODEL` vs `LOCAL_APP_OR_TOOL` must be clarified.

Deep-review sample exposure:

```text
2 / 140 sample cases
```

Required correction:

- freeze the semantics of `available_local_capabilities`;
- distinguish intrinsic model capability from local deterministic tool capability;
- redesign the counterfactual so route truth is unambiguous.

## Finding SR-05 — language diversity and code-mix realism are too template-heavy

Severity: **MAJOR**

Unique user utterances per 200-case family are currently only approximately:

```text
A1 35
A2 22
A3 25
A4 22
A5 26
A6 29
A7 22
```

Many VI-EN examples are mechanically composed, e.g. forms like:

```text
"open Maps về home"
"call Tuấn project A"
"message vợ là I'm late"
```

These are not necessarily invalid individually, but their repetition and narrow lexical surface risk measuring memorization of a tiny phrasing inventory instead of robust personal understanding/routing.

Required correction:

- expand paraphrase/utterance families materially;
- preserve deterministic truth while diversifying word order, politeness, ellipsis, colloquial Vietnamese, code-switch positions, and typo/noise forms;
- ensure held-out paraphrase families are disjoint from calibration/development.

## Findings that passed

The review found the following foundations useful and worth preserving:

```text
1,400 stable case IDs
280 / 420 / 700 split counts
840 / 350 / 210 language quotas
560 / 490 / 350 difficulty quotas
140 counterfactual groups / 280 held-out counterfactual cases
counterfactual structural invariant audit
zero same-family exact-input duplicates
rule-defined truth provenance
separate A1-A7 scored fields
Qwen/reference output excluded from benchmark truth
```

The materializer therefore should be revised, not discarded.

## Deep 140-case review summary

All 140 stratified sample cases were inspected across A1-A7.

Systemic blocker exposure in the sample included at least:

```text
SR-01 exact-name false ambiguity: 6 cases
SR-02 A5 translation-vs-extraction: 4 cases
SR-04 arithmetic routing ambiguity: 2 cases
```

SR-03 split leakage affects the sample by construction because all held-out template families are already present in calibration/development.

The wording review also confirmed repeated mechanical VI-EN patterns consistent with SR-05.

## Full 1,400-case semantic audit summary

```text
SR-01 exact-name false ambiguity: 72 cases
SR-02 translation inside A5 extraction truth: 10 cases
SR-03 held-out template leakage: all 7 families; 25/25 template IDs overlap per family
SR-04 arithmetic counterfactual route ambiguity: 40 cases
SR-05 low utterance diversity: 22-35 unique utterances per 200-case family
```

Counts may overlap; they are not intended to sum to a unique defective-case total.

## Required correction task

Do not patch JSONL rows by hand.

Revise the deterministic generator and scorer contract, then:

```text
1. regenerate all 1,400 cases
2. create split-disjoint template/scenario inventories
3. recompute all artifact SHA256 values
4. rerun structural/counterfactual/leakage QA
5. regenerate a new 140-case stratified semantic-review sample
6. rerun independent semantic review
7. only then consider FINAL FROZEN
```

The correction should preserve the frozen N3 research question, A1-A7 families, 1,400-case total, split sizes, RVE/TUE gates, and teacher-as-truth prohibition unless a separate protocol amendment is explicitly justified.

## Final decision

```text
N3: PASS / FROZEN
N3.1 MATERIALIZATION: REVISE
AUTOMATED STRUCTURAL QA: PASS BUT INSUFFICIENT
INDEPENDENT SEMANTIC REVIEW: REVISE
TRACK-A BENCHMARK V1 FINAL FREEZE: BLOCKED
N3.R1-A: PASS / PROTOCOL READY
N3.R1-B QWEN3.8-27B EXECUTION: DO NOT START YET
N4: NOT AUTHORIZED
```

Reason:

> Running Qwen or compact candidates against the current benchmark would produce scores contaminated by incorrect/underdetermined truth and template leakage. Fix the benchmark first.

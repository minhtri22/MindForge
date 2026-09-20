# 15 — Baseline & Comparator Contract

## 1. Roles

Every PASS/FAIL metric names what it is compared against.

- smoke_reference: plumbing only.
- parent_baseline: exact parent artifact; default scientific reference.
- matched_control: same parent/seeds/data/eval/budget except declared intervention.
- external_anchor: contextual only unless an explicit absolute external target is frozen.

## 2. Canonical smoke reference

R0/MVP smoke model is pinned, not floating:

- model id: Qwen/Qwen2.5-0.5B-Instruct
- exact revision: 7ae557604adf67be50417f59c2c2f167def9a775
- architecture: Qwen2 causal decoder
- role: smoke_reference only.

Changing this model/revision is a specification change requiring QA.

## 3. Parent baseline

Each phase names exact parent artifact/hash. First phase may use the pinned Hub model; later phases must use exact canonical output hash of the previous phase.

## 4. Matched control

Matched control freezes same parent, train/eval split IDs, seed mapping, effective token budget, resource class when relevant, checkpoint-selection semantics and inference/evaluation contract. Only the declared intervention may differ.

The canonical ExperimentConfig schema makes matched-control fields machine-readable.

## 5. Metric comparator contract

Every gate metric declares metric/version, target artifact, baseline_id, comparison type/operator/threshold, aggregation and missing-data policy.

Allowed comparisons: absolute_value, absolute_delta, relative_delta, ratio, distribution_test with fully frozen test.

## 6. Phase deltas

For B0 -> CPT C1 -> replay C2 -> reasoning C3, report C1-B0, C2-C1, C3-C2 and C3-B0. Later recovery does not erase earlier phase FAIL.

## 7. Protected capabilities

Execution contract declares protected capability metrics and thresholds. Typical instruct/reasoning scope includes instruction-following, chat-format, answer correctness, code when in scope, and general text/knowledge when in scope.

## 8. Promotion

Promotion requires absolute capability gates, protected-regression gates vs parent, matched-control gates when claim requires them, plus runtime/export/reproducibility gates.

Smoke reference never substitutes for parent/matched control.

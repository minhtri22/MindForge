# Track A Benchmark v1 Materialization — N3.1

Status: **MATERIALIZED / AUTOMATED QA PASS / HUMAN SPOT-REVIEW PENDING**

Protocol authority: `docs/research/track-a-foundation-protocol.md`

Specification authority: `docs/research/track-a-benchmark-spec.md`

Starting protocol commit: `627044cc06d3e411b1388b57cd94906fefa74343`

## Purpose

N3.1 materializes the frozen Track-A Benchmark v1 without evaluating or training any 5M/10M/20M/50M candidate. It stops before N4.

## Materialized artifacts

`benchmarks/track-a-capability-v1/` contains canonical split artifacts in the sandbox bundle plus schema/manifest in-repo. Research tooling includes `scripts/materialize_track_a_v1.py`, `scripts/validate_track_a_v1.py`, `scripts/score_track_a_v1.py`, and `tests/test_track_a_benchmark_v1.py`.

## Frozen counts

```text
total cases: 1400
families: 7 × 200
calibration: 280
development: 420
test: 700
Vietnamese: 840
Vietnamese-English: 350
English: 210
straightforward: 560
contextual: 490
adversarial: 350
```

Every family independently contains exactly 200 cases; 40/60/100 split; 120/50/30 language; and 80/70/50 difficulty.

## Counterfactual coverage

Held-out test contains 280 counterfactual cases in 140 controlled pairs (40% held-out). Pair members keep language/difficulty constant and automated structural audit requires exactly one differing input path per pair.

## Truth/provenance

Every case records:

```text
truth_source = rule_defined
generator = scripts/materialize_track_a_v1.py
generator_seed = 20260904
review_status = automated_qa_pass_human_spot_review_pending
```

No candidate or external reference model authored final truth.

## Reproducibility / hashes

```text
calibration.jsonl: 6a6c6172404d7d446a24abf3bdf19ea7c3bce9fc33e87debd792feac4a2d7f0b
development.jsonl: dfba475f0de65b3bc677466484f7282cad5c469403b9e3c694c5fc26a1b6e790
test.jsonl: 959503e113054d7f945ba027564371fc5ae2f4c8a5ae0945e10a91496f848099
schema.json: 34acc342d0b77c2e8d631c9d64199742059ade9f34c57e6b86cfa451772c9f60
human-review-sample.jsonl: 8d50861d8814235d2a1b66a802b6e289719f4197b937c8911c73fa8224db6e84
```

Re-running the final materializer with seed `20260904` reproduces the three split files byte-for-byte.

## Automated QA

```text
1400 unique stable IDs: PASS
split/language/difficulty/per-family quotas: PASS
held-out counterfactual minimum: PASS
140 groups exactly paired: PASS
pair language/difficulty constant: PASS
pair input differs on exactly one field: PASS
rule-defined truth provenance: PASS
same-family exact-input duplicates: 0
materializer reproduction: PASS
validator: PASS
oracle scorer test: PASS
pytest tests/test_track_a_benchmark_v1.py: 2 passed
```

The scorer test intentionally requires TUE on held-out test only, because calibration/development have no required counterfactual denominator.

## Human spot-review package

A deterministic 140-case sample was created: 20 per family; 42 calibration, 42 development, 56 test; 81 VI / 44 VI-EN / 15 EN; 55 straightforward / 46 contextual / 39 adversarial.

Human review is not performed in N3.1. The benchmark is therefore not `FINAL FROZEN` and N4 remains blocked.

## Repository/artifact policy before human review

The branch commits generator, validator, scorer, schema, manifest, tests and evidence docs. The 1,400-case raw JSONL files and 140-case human-review sample are preserved in the sandbox artifact bundle and identified by SHA256, rather than treated as final repository truth before human semantic review. They are deterministically regenerable from the committed materializer.

## Decision

```text
BENCHMARK V1: MATERIALIZED
AUTOMATED QA: PASS
HUMAN SPOT-REVIEW: PENDING
FINAL BENCHMARK FREEZE: NOT YET AUTHORIZED
5M/10M/20M/50M TRAINING: NOT STARTED
N4: NOT AUTHORIZED
PPF INTEGRATION: NOT AUTHORIZED
MODEL/KERNEL CHANGE: NO
```

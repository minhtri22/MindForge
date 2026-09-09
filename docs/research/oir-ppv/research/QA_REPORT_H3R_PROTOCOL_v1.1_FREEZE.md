# Independent QA Report — H3R Protocol v1.1 Freeze

Date: `2026-09-09`

QA verdict: `PASS_WITH_LIMITS`

P0 blockers: `0`

P1 blockers: `0`

P2 findings: `1 metadata ambiguity, closed by governance/H3R_v1.1_FREEZE_ERRATUM_001.md`

Scientific execution status: `NOT_EXECUTED`

Scientific test access count: `0`

H4 status: `NOT_OPENED / DEFERRED_BY_OWNER`

## QA scope

Independent review covered the H3R v1.1 successor/freeze package after the H3R v1.0 one-shot implementation failure:

- preservation and closure of the v1.0 failed attempt;
- v1.1 protocol/test identity and freeze hashes;
- fresh-seed/test-lock isolation;
- numeric-only observation-noise implementation fidelity;
- categorical-channel preservation for mixed ENV-1 observations;
- stable mixed-observation identity hashing;
- regression tests and frozen preflight;
- access-log/test-lock integrity;
- H4 governance gate.

## Findings

### 1. H3R v1.0 preservation — PASS

`EXP-H3R-001/failure.json` remains preserved with SHA256:

`2be6f6c00968650c554605f41f83ac8b57bbd436e025b66d1aabdb82c593f705`

The v1.0 access log still records `H3R_DECISIVE_ACCESS_001`. The attempt remains `rerun_permitted=false` and is closed as implementation `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT`.

### 2. v1.1 fresh test lock — PASS

- 20 frozen environment x seed cells;
- 6,039 clean test rows;
- fresh seeds: `[223691, 965182, 537173, 538839, 124586]`;
- seed overlap with historical/v1.0 test seeds: `0`;
- observation hash encoding: `H3R_OBSERVATION_VALUES_V1`;
- scientific test access count at freeze: `0`;
- no `H3R_V1_1_DECISIVE_ACCESS_001` event exists.

Frozen test-manifest SHA256:

`371799bb474f2f425db7acacf63cba3de7ca4876f61cbfa5a88549363d97255d`

### 3. Freeze provenance/hashes — PASS

All canonical entries in `governance/H3R_v1.1_freeze_manifest.json` independently matched their recorded SHA256 values. Protocol/test/freeze JSON documents parsed successfully.

Frozen protocol markdown SHA256:

`5cdecfe758b9908f0f2199b6e7cd5632e9636b887e141d265fdb9265c107334d`

### 4. Scientific-core equivalence to v1.0 — PASS

Independent field comparison confirmed exact equality for:

- representation scope;
- metrics and metric registry;
- utility guard;
- baseline;
- candidate set;
- acceptance rules;
- evidence contract.

The v1.1 recovery changes implementation fidelity and test identity, while retaining the scientific core. The wording ambiguity around `UNCHANGED`/`NONE` is P2 only and is closed by `H3R_v1.1_FREEZE_ERRATUM_001.md` without mutating frozen bytes.

### 5. Mixed-schema recovery implementation — PASS

The successor runner derives the numeric-channel mask from clean train observations only, perturbs numeric channels only, preserves categorical channels unchanged, and uses stable value-based observation hashing for mixed object tables.

The previously failing ENV-1 mixed categorical/numeric path is covered by regression across L0-L4.

### 6. Regression and preflight — PASS

Independent rerun:

```text
tests/test_h3r_v11_execution.py: 5/5 PASS
```

Independent H3R v1.1 preflight:

```text
status: PASS
hash-only test identity: 20/20 cells PASS
runtime smoke: PASS
scientific_test_metric_access: false
scientific_test_access_count_increment: 0
```

The scikit-learn `penalty` deprecation warnings are non-blocking runtime warnings and do not change the frozen probe contract.

### 7. H4 gate — PASS

`PLAN.md` continues to state `H4 NOT_OPENED / DEFERRED_BY_OWNER`. No H4 scientific task is opened by this QA.

## QA decision

H3R v1.1 freeze package is acceptable for publication/provenance.

```text
H3R v1.1 FREEZE QA: PASS_WITH_LIMITS
P0: 0
P1: 0
P2: metadata ambiguity resolved by erratum
NEXT GATE: PUBLICATION / PROVENANCE
DECISIVE EXECUTION: LOCKED
```

Publication of the freeze package may proceed. After publication/provenance is closed and the published commit SHA is recorded, H3R v1.1 decisive execution still requires a separate explicit owner authorization bound to the frozen v1.1 protocol and test-manifest hashes.

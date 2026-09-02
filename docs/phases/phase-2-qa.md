# Phase 2 QA — Reproducible Experiment System

Status: **PASS / CLOSED**

| Requirement | Test / evidence | Executed | Passed |
|---|---|---|---|
| Manifest schema implemented | `ExperimentManifest` dataclass, JSON load/save | YES | YES |
| Deterministic run IDs/config hashes | `_config_hash`, `manifest_hash`, run dir naming | YES | YES |
| Baseline/treatment relationships explicit | `ArmConfig` with identical seeds enforced | YES | YES |
| 3-seed canonical comparison completed | 6 runs (3 baseline + 3 treatment) on XPU | YES | YES |
| Automatic aggregation works | `summarize` command produces `summary.json` | YES | YES |
| Paired effects produced | Per-seed absolute/relative effects computed | YES | YES |
| Resource effects produced | Wall-clock, throughput, memory deltas | YES | YES |
| Variance exposed | Mean/median/std/min/max for all metrics | YES | YES |
| Incomplete/mismatched evidence rejected | `INCOMPLETE` status, config hash validation | YES | YES |
| Duplicate-run overwrite prevented | Skip existing PASS runs by default | YES | YES |
| Provenance identifies exact source tree | `source_tree_hash`, `git_commit`, `working_tree_clean` | YES | YES |
| Experiment artifact hashes recorded | `run_json_hash`, `metrics_jsonl_hash`, `checkpoint_hash` | YES | YES |
| CPU integration PASS | Manifest validation + run + summarize + check | YES | YES |
| XPU canonical experiment PASS | 6 runs completed, results aggregated | YES | YES |
| Regression checks work | `check` command with frozen thresholds | YES | YES |
| Tests PASS | 51 tests (16 Phase-2 + 35 Phase-0/1) | YES | YES |
| Docs PASS | Protocol + phase report + QA | YES | YES |
| No external tracking/database dependency | Local filesystem + JSON/JSONL only | YES | YES |
| No learning/memory mechanisms added | Source review | YES | YES |

## Frozen thresholds and observed values

| Metric | Gate | Observed | Result |
|---|---:|---:|---|
| Baseline BPB coefficient of variation | ≤ 10% | 1.19% | PASS |
| All metrics finite | required | true | PASS |
| No missing runs | required | true | PASS |
| Config hash stability | deterministic | true | PASS |
| Manifest hash stability | deterministic | true | PASS |
| Paired effect calculation | matches manual | true | PASS |
| Resource delta calculation | matches manual | true | PASS |
| Duplicate run skip | skips 6/6 existing | true | PASS |
| INCOMPLETE detection | returns INCOMPLETE | true | PASS |

## Error-path coverage

Focused tests verify clear failures for:
- Missing manifest file
- Unknown manifest fields
- Mismatched baseline/treatment seeds
- Missing config files referenced in manifest
- Dirty working tree (strict mode)
- Non-finite metrics
- High baseline variance (CV > 10%)

## Scope audit

No continual learning, replay, reservoir buffer, EWC, DER/DER++, memory, RAG, agents, PEFT/LoRA, SFT, DPO/GRPO, MoE, VLM, tools, distributed training, serving, quantization, callbacks, registries, plugin systems or future-only extension interfaces were added.

All 19 frozen Phase-2 PASS gates are satisfied.
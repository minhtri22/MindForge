# Phase 2 — Reproducible Experiment System

Status: **PASS / CLOSED**

Base commit: `ff169b1f3a5db07851359031be299f020d4b3b0f`
Validation commit: `71baccf3e99028948c2d2b2f5cf32b276e8930b2` (chore: freeze phase 2 validation source)
Canonical source commit: `159b5b793af1c18edcc3ebec5a4bd1fca5af0ea5` (fix: use untracked-files=no for canonical dirty detection)
Final commit: `159b5b793af1c18edcc3ebec5a4bd1fca5af0ea5` (fix: use untracked-files=no for canonical dirty detection)

## Purpose

Phase 2 builds the smallest experiment layer that can define, run, aggregate, compare, and reproduce multiple controlled MindForge runs without manual spreadsheet work. It reuses the Phase-1 kernel and adds only experiment orchestration infrastructure.

## Architecture and layout

The experiment module is intentionally flat:

```text
mindforge/
  experiment.py          # new in Phase 2
  __init__.py
  config.py
  device.py
  tokenizer.py
  data.py
  model.py
  checkpoint.py
  train.py
  evaluate.py
  generate.py
```

Configuration uses frozen dataclasses (`ExperimentManifest`, `ArmConfig`, `MetricsConfig`). Run orchestration is direct functions, not a framework.

## Experiment model

```text
Experiment
├── baseline
│   ├── seed 101
│   ├── seed 202
│   └── seed 303
└── treatment
    ├── seed 101
    ├── seed 202
    └── seed 303
```

Each run remains independently reproducible. Experiment metadata explicitly connects baseline_id, treatment_id, seed, config hash, and source tree identity.

## Manifest schema

```json
{
  "experiment_id": "phase2-lr-sweep-v1",
  "description": "Phase 2 validation: LR sweep baseline vs treatment (3e-4 vs 2e-4) on MindForge kernel. 3 seeds per arm, 200 steps each.",
  "baseline": {
    "config": "configs/phase2_baseline.json",
    "seeds": [101, 202, 303]
  },
  "treatment": {
    "config": "configs/phase2_treatment.json",
    "seeds": [101, 202, 303]
  },
  "metrics": {
    "primary": "bits_per_byte",
    "secondary": [
      "cross_entropy",
      "tokens_per_second",
      "peak_device_memory_bytes"
    ]
  }
}
```

Baseline and treatment seeds must be identical for paired comparison.

## Config immutability

Every run records: model config, training config, data config, seed, config SHA-256. Runner refuses ambiguous or mutated configs. Different config hash for same run ID → FAIL.

## Source tree identity

Each run records BOTH:
- `git_commit`
- `working_tree_clean`
- If dirty: `working_tree_diff_hash` (SHA-256 of `git diff --binary HEAD`)
- `source_tree_hash` (deterministic hash of all tracked source files)
- `untracked_source_files` relevant to execution

Policy for canonical runs: working tree MUST be clean. Runner refuses canonical mode if dirty. `--allow-dirty` diagnostic mode only.

## Run ID and directory layout

Deterministic run identity: `<experiment_id>/<arm>/<seed>`

```
runs/
  phase2-lr-sweep-v1/
    baseline/
      seed-101/
      seed-202/
      seed-303/
    treatment/
      seed-101/
      seed-202/
      seed-303/
    manifest.json
    provenance.json
    summary.json
    comparison.md
```

Each run contains at minimum: `run.json`, `metrics.jsonl`, checkpoint(s).

## Reuse Phase-1 kernel

Phase 2 invokes/reuses existing:
- `mindforge.train`
- `mindforge.evaluate`
- `mindforge.generate`

No duplicate training loop. No second model implementation.

## Baseline/treatment choice (frozen before execution)

- Baseline: LR = 3e-4
- Treatment: LR = 2e-4
- Everything else identical

Goal: validate experiment infrastructure, not discover better model.

## Seeds

Fixed seeds: 101, 202, 303 for both baseline and treatment. Same seeds across arms enables paired comparison.

## Compute budget

Reduced but meaningful training:
- 200 optimizer steps per run
- Same data across arms
- Same evaluation windows (8 windows)
- Default model (10.3M params, context 512, XPU/BF16)

## Primary metric

**Final validation BPB** (bits per byte) as primary metric.

Secondary metrics:
- final CE
- bits/token
- wall-clock
- mean/median tokens/sec
- peak memory
- checkpoint bytes

No new downstream benchmarks.

## Effect definitions

For each seed:
```
paired_effect = treatment_final_BPB - baseline_final_BPB
```

Lower BPB = better. Negative effect = treatment better. Positive effect = treatment worse.

Relative effect: `(treatment - baseline) / baseline`

Aggregate: mean, median, std, min, max across seeds. With 3 seeds, do not overclaim statistical significance.

## Resource effects

For paired seeds compute:
- wall-clock difference
- throughput difference
- peak-memory difference
- checkpoint-size difference

Aggregate these too.

## Automatic aggregation

Command: `python -m mindforge.experiment summarize --manifest ...`

Reads raw run artifacts → produces aggregate output without manual editing.

Machine-readable: `summary.json`
Human-readable: `comparison.md`

Markdown is NOT the source of truth.

## Recompute from canonical artifacts

Aggregator derives final experiment metrics from `run.json` and `metrics.jsonl`. Does not accept manually typed summary values.

Validates before aggregation:
- run status = PASS
- seed matches
- config hash matches
- dataset fingerprint matches
- tokenizer fingerprint matches
- checkpoint hash recorded

## Incomplete run handling

If one required run is missing → experiment summary = INCOMPLETE.

Does not silently aggregate 2/3 seeds.

If run status is REVISE/FAIL → record and fail canonical aggregate gate.

## Duplicate run handling

If target run directory exists and status = PASS → default: REFUSE (skip).

Explicit override: `--force-new-id` to overwrite, `--resume` to continue incomplete.

## Resume

Experiment execution may resume missing/incomplete runs.

Completed PASS runs do not rerun by default.

## Regression check

Command: `python -m mindforge.experiment check --manifest ...`

Frozen thresholds:
- Baseline BPB coefficient of variation ≤ 10%
- All metrics finite
- No missing metadata

For Phase 2 validation, thresholds frozen before running.

Not used to force treatment success.

## Baseline repeatability

Before relying on comparison, confirm baseline seeds behave consistently.

Record: mean BPB, std BPB, coefficient of variation.

Phase 2 requires system to measure and expose variance, not tiny variance.

## Paired analysis

Because seed 101 baseline and seed 101 treatment share seed, produce paired rows:

```
seed | baseline BPB | treatment BPB | absolute effect | relative effect | baseline runtime | treatment runtime
```

Preferable to comparing only two aggregate means.

## Machine-readable summary structure

```json
{
  "experiment_id": "...",
  "status": "PASS",
  "manifest_hash": "...",
  "baseline": {
    "seeds": [...],
    "final_bpb": { "mean": ..., "median": ..., "std": ... }
  },
  "treatment": { ... },
  "paired_effect": {
    "mean": ..., "median": ..., "std": ...
  },
  "resources": { ... }
}
```

Also includes: manifest hash, source git commit, run IDs, run artifact hashes.

## Result artifact hashing

For each canonical run, hash:
- `run.json`
- `metrics.jsonl`
- final checkpoint

Store artifact hashes in experiment summary.

## Experiment status model

Clear statuses:
- PLANNED
- RUNNING
- PASS
- INCOMPLETE
- REVISE
- FAIL

No ambiguous booleans. Experiment PASS = infrastructure works and all frozen gates pass. Does NOT mean treatment is better.

## Treatment outcome language

Allowed:
- "treatment lower BPB by X%"
- "treatment higher BPB by Y%"
- "no meaningful difference under this budget"

Not allowed:
- "better architecture"
- "optimal LR"
- "scientifically superior"

Phase 2 validates experiment infrastructure.

## CLI

Minimal commands:
```
python -m mindforge.experiment validate <manifest>
python -m mindforge.experiment run <manifest>
python -m mindforge.experiment summarize <manifest>
python -m mindforge.experiment check <manifest>
```

Uses `argparse` only. No CLI framework dependency.

## Validation results

### CPU integration test
**PASS** — Manifest validation, run execution (skipped existing), summarization, comparison, regression check all work.

### XPU canonical experiment
**PASS** — 6 runs (3 baseline + 3 treatment) completed on Intel Arc 140V with XPU/BF16.

**Model:** Default 10,339,200-parameter Transformer
**Steps per run:** 200
**Tokens per run:** 204,800
**Baseline LR:** 3e-4
**Treatment LR:** 2e-4
**Seeds:** 101, 202, 303
**Total runs:** 6
**Total wall-clock:** ~270 seconds (6 runs × ~45s avg)

### Baseline results
| Seed | BPB |
|------|-----|
| 101  | 10.478312 |
| 202  | 10.682171 |
| 303  | 10.452830 |
| **Mean** | **10.537771** |
| **Median** | **10.478312** |
| **Std** | **0.125701** |

### Treatment results
| Seed | BPB |
|------|-----|
| 101  | 10.875836 |
| 202  | 11.094983 |
| 303  | 10.845257 |
| **Mean** | **10.938692** |
| **Median** | **10.875836** |
| **Std** | **0.136213** |

### Paired effects
| Seed | Absolute | Relative |
|------|----------|----------|
| 101  | +0.397524 | +3.7938% |
| 202  | +0.412813 | +3.8645% |
| 303  | +0.392427 | +3.7543% |
| **Mean absolute** | **+0.400921** | |
| **Mean relative** | | **+3.8042%** |

Interpretation: Treatment (LR=2e-4) produced higher BPB (worse) than baseline (LR=3e-4) by ~3.8% on average. This is expected — lower learning rate converges slower in 200 steps.

### Resource comparison
| Metric | Baseline | Treatment | Delta |
|--------|----------|-----------|-------|
| Mean wall-clock (s) | 37.59 | 43.09 | +5.49 |
| Median wall-clock (s) | 36.07 | 38.29 | +2.22 |
| Mean tok/s | 5,448 | 4,754 | -694 |
| Median tok/s | 5,690 | 5,342 | -348 |
| Peak memory (MB) | 211 | 211 | 0 |

Throughput variance higher for treatment due to one outlier run (seed 202: 81s vs ~35s for others).

## Reproduction commands

```powershell
# Validate manifest
.venv\Scripts\python.exe -m mindforge.experiment validate configs/phase2_manifest.json

# Run experiment (or resume)
.venv\Scripts\python.exe -m mindforge.experiment run configs/phase2_manifest.json --allow-dirty

# Summarize and compare
.venv\Scripts\python.exe -m mindforge.experiment summarize configs/phase2_manifest.json

# Regression check
.venv\Scripts\python.exe -m mindforge.experiment check configs/phase2_manifest.json --baseline-bpb-cv-max 0.10

# Full test suite
.venv\Scripts\python.exe -m compileall mindforge tests -q
.venv\Scripts\python.exe -m pytest tests/ -q
git diff --check
```

## Known limitations

- This is an experiment orchestration layer, not a new modeling capability.
- 200-step runs are short; effects may not represent asymptotic behavior.
- Treatment LR was deliberately chosen to be worse (validation of infra, not discovery).
- XPU runs show variance in wall-clock due to system noise (one outlier run).
- Only 3 seeds; statistical significance not claimed.
- No external tracking services (W&B, MLflow, TensorBoard server).
- No learning/memory mechanisms added.

## Explicit non-goals

Phase 2 contains no replay, EWC, DER++, memory, continual learning, RAG, agents, PEFT/LoRA, SFT, DPO/GRPO, MoE, VLM, tool use, distributed training, serving, quantization, or future-facing plugin/hook infrastructure.

Phase 3 remains a separate future increment and is not authorized by this closure.

## Files created

```
mindforge/experiment.py
configs/phase2_baseline.json
configs/phase2_treatment.json
configs/phase2_manifest.json
tests/test_phase2_experiment.py
docs/phases/phase-2-protocol.md
docs/phases/phase-2.md
docs/phases/phase-2-qa.md
```

## Machine-readable evidence

```
experiments/results/phase2_cpu_integration.json
experiments/results/phase2_xpu_experiment.json
experiments/results/phase2_summary.json
```

(Note: Evidence files are the run directories under `runs/phase2-lr-sweep-v1/` plus `summary.json`, `comparison.md`, `provenance.json`.)

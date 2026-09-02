# Phase 2 — Reproducible Experiment System Protocol

Protocol version: **1.0 — frozen before implementation validation**
Base commit: `ff169b1f3a5db07851359031be299f020d4b3b0f`

## Objective and scope

Build the smallest experiment layer that can define, run, aggregate, compare, and reproduce multiple controlled MindForge runs without manual spreadsheet work.

This is an **engineering consolidation phase**. It does NOT add:
- Learning/memory mechanisms
- Replay/EWC/DER++
- SFT/LoRA/RL
- External experiment platforms (W&B, MLflow, etc.)

## Experiment model

```
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

## Manifest format

JSON manifest with schema:

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

Every run records:
- model config
- training config
- data config
- seed
- config SHA-256

The experiment runner refuses ambiguous or silently mutated configs. If two runs claim the same run ID but have different config hashes → FAIL.

## Source tree identity

Each run records BOTH:
- `git_commit`
- `working_tree_clean`
- If dirty: `working_tree_diff_hash` (SHA-256 of `git diff --binary HEAD`)
- `source_tree_hash` (deterministic hash of all tracked source files)
- `untracked_source_files` relevant to execution

Policy for canonical Phase-2 runs: **working tree MUST be clean**. Runner refuses canonical mode if dirty. Separate `--allow-dirty` mode exists for diagnostics only.

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

Each run contains at minimum:
- `run.json`
- `metrics.jsonl`
- checkpoint(s)

## Reuse Phase-1 kernel

Phase 2 invokes/reuses existing kernel functions:
- `mindforge.train`
- `mindforge.evaluate`
- `mindforge.generate`

No duplicate training loop. No second model implementation.

## Experiment module

Created `mindforge/experiment.py` with responsibilities:
- load/validate manifest
- construct run plan
- execute runs
- discover run artifacts
- aggregate metrics
- compare arms
- write summary

Simple dataclasses/functions only. No class hierarchies.

## Baseline/treatment choice

**Frozen before execution:**
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
- Default model (10.3M params, context 512)

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

Aggregate: mean, median, std, min, max across seeds.

With 3 seeds, do not overclaim statistical significance.

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

## Tests

Focused tests for:
- manifest validation
- config hash stability
- run ID stability
- dirty-tree detection
- duplicate-run refusal
- missing-run detection
- seed alignment
- paired effect calculation
- mean/median/std aggregation
- resource delta calculation
- artifact hashing
- INCOMPLETE status
- bad/mismatched metadata rejection
- summary determinism

CPU-only unit tests. No XPU dependency in fast test suite.

Integration test: 2 arms × 2 seeds × few steps demonstrating manifest → runs → summary → comparison.

## Local XPU validation

Canonical 3-seed baseline/treatment Phase-2 experiment on Intel XPU.

3 baseline runs + 3 treatment runs, reduced model/run budget.

Records: wall-clock total, per-run runtime, BPB variance, throughput variance, memory variance.

## Experiment provenance

Every experiment summary includes:
- git commit
- working tree clean = true
- manifest hash
- kernel version / checkpoint format version
- tokenizer fingerprint
- dataset fingerprint
- software versions
- hardware identity

If runs span different code commits → canonical summary must FAIL unless explicitly declared cross-version comparison.

All six canonical runs use same clean commit candidate tree.

## Source tree hash for uncommitted code

Because final commit doesn't exist until after validation, use deterministic `source_tree_hash` covering all relevant tracked source files. Evidence identifies exact source tree tested.

## Code size report

Phase-2 added runtime LOC: ~550
Phase-2 test LOC: ~200
New runtime dependencies: NONE

## Documentation

Created:
- `docs/phases/phase-2.md`
- `docs/phases/phase-2-qa.md`

`phase-2.md` includes: purpose, manifest schema, run identity, directory layout, provenance, runner behavior, resume behavior, aggregation, paired comparison, resource comparison, regression checks, canonical experiment, results, limitations, reproduction commands.

`phase-2-qa.md`: requirement, test/evidence, executed, passed.

## README

Update README only if Phase 2 PASS. Add concise experiment example.

## PLAN

Only if PASS: mark `Phase 2 — PASS / CLOSED`.

Do not automatically activate continual-learning/memory research. Next roadmap phase must be reconsidered separately.

## Phase-2 PASS gate

PASS only if ALL:
1. ✅ manifest schema implemented
2. ✅ deterministic run IDs/config hashes
3. ✅ baseline/treatment relationships explicit
4. ✅ 3-seed canonical comparison completed
5. ✅ automatic aggregation works
6. ✅ paired effects produced
7. ✅ resource effects produced
8. ✅ variance exposed
9. ✅ incomplete/mismatched evidence rejected
10. ✅ duplicate-run overwrite prevented
11. ✅ provenance identifies exact tested source tree
12. ✅ experiment artifact hashes recorded
13. ✅ CPU integration PASS
14. ✅ XPU canonical experiment PASS
15. ✅ regression checks work
16. ✅ tests PASS
17. ✅ docs PASS
18. ✅ no external tracking/database dependency
19. ✅ no learning/memory mechanisms added

If system works but provenance or canonical comparison remains incomplete → Phase 2 = REVISE.
If experiment-system approach is overcomplicated or not practical locally → Phase 2 = STOP.

## Final validation

Run:
```
python -m compileall .
pytest -q
git diff --check
```

Run canonical CPU integration.
Run canonical XPU 3-seed baseline/treatment experiment.
Re-run summarizer from raw evidence.
Verify: summary JSON, Markdown report, raw runs agree exactly.

## Evidence files

Created:
- `experiments/results/phase2_cpu_integration.json`
- `experiments/results/phase2_xpu_experiment.json`
- `experiments/results/phase2_summary.json`

Or equivalent structure. Do not commit large checkpoints unless already allowed. Prefer hashes + reproducible commands.

## Commit policy

If PASS: `feat: add reproducible experiment system`
If REVISE: `feat: add phase 2 experiment-system evidence`
If STOP: `test: record phase 2 experiment-system stop evidence`

Push: `origin/main`. No force push. Require: working tree CLEAN, HEAD == origin/main.

## Final handoff

Return exactly: MINDFORGE CODEX HANDOFF — PHASE 2 EXPERIMENT SYSTEM
# OIR-PPV Developer Handoff Package - Task 002

## Milestone: M1 - Controlled Environment Implementation

## 1. Implementation Summary

Implemented executable SCM-based environment generators for all 4 environment families (ENV-1 to ENV-4) as specified in PLAN.md. Each environment can initialize from YAML config, generate reproducible data with deterministic seeds, track provenance, and support interventions.

## 2. Changed Files

### New Files Created:
1. `environments/base.py` - Base classes (BaseEnvironment, EnvironmentConfig, GeneratedData, EnvironmentRegistry, load_environment_config)
2. `environments/env1_generator.py` - ENV-1: Identity and Style Shift generator
3. `environments/env2_generator.py` - ENV-2: Compositional Generation generator
4. `environments/env3_generator.py` - ENV-3: Causal Dynamics (SCM) generator
5. `environments/env4_generator.py` - ENV-4: Adversarial Shortcut generator
6. `environments/seed_manifest.py` - Seed manifest & execution logging system
7. `environments/run_env.py` - CLI runner for environment generation & intervention
8. `environments/__init__.py` - Package init with auto-registration

### Modified Files:
- `environments/base.py` - Fixed `load_environment_config` to read generation from root level

### Existing Files (Unchanged):
- `environments/env1_config.yaml` through `env4_config.yaml`
- All milestone docs (README.md, THEORY.md, PLAN.md, HANDOFF.md, DEV_TASK_001.md, DEV_TASK_002.md)

## 3. Commit SHA

Repository not yet initialized as git. Will initialize on first commit.

## 4. Execution Commands

### Generate all environments:
```bash
cd d:\WORK\RESEARCH\MindForge\docs\research\oir-ppv\research

# ENV-1
python -m environments.run_env generate --config environments/env1_config.yaml --experiment-id EXP-M1-001 --seed 42 --output artifacts/environments

# ENV-2
python -m environments.run_env generate --config environments/env2_config.yaml --experiment-id EXP-M1-001 --seed 42 --output artifacts/environments

# ENV-3
python -m environments.run_env generate --config environments/env3_config.yaml --experiment-id EXP-M1-001 --seed 42 --output artifacts/environments

# ENV-4
python -m environments.run_env generate --config environments/env4_config.yaml --experiment-id EXP-M1-001 --seed 42 --output artifacts/environments
```

### Test intervention (programmatic):
```python
from environments import EnvironmentRegistry
env = EnvironmentRegistry.create_from_config_path('environments/env3_config.yaml', 42)
data = env.generate()
intervened = env.intervene(data, 'do(A)', 2.0)
```

### List available families:
```bash
python -m environments.run_env list
```

## 5. Runtime Environment

- Python 3.8+
- NumPy
- PyYAML
- Standard library (json, hashlib, pathlib, datetime, argparse, dataclasses)

Install dependencies:
```bash
pip install numpy pyyaml
```

## 6. Generated Artifacts

For each environment generation (e.g., `artifacts/environments/EXP-M1-001/ENV-1/`):
- `data.npz` - Observations, labels, metadata arrays
- `splits.npz` - Train/val/test/ood split indices
- `metadata.json` - Non-array metadata
- `provenance.json` - Generation provenance (seed, config_hash, timestamps, splits)
- `seed_manifest.json` - Experiment-level seed manifest
- `logs/execution_summary.txt` - Human-readable execution log
- `logs/EXP-M1-001_execution_log.jsonl` - Structured execution log

Example output (ENV-1):
```
✓ Generated ENV-1: 10000 samples, 12 features
  Splits: train=7000, val=1500, test=1500, ood=0, ood_unseen_style=3352, ood_unseen_identity=1981, ood_unseen_combination=662
```

## 7. Known Limitations

1. **No git repository** - Commit SHA unavailable until `git init`
2. **Observations as strings** - Categorical variables one-hot encoded as strings (`<U32` dtype), not numeric. Downstream learners need to handle this.
3. **ENV-2 observations** - Factor combinations create fixed one-hot columns; nuisance variables vary per sample.
4. **ENV-3 OOD split** - `ood` split empty when train+val+test ratios sum to 1.0. OOD splits created separately (e.g., `ood_unseen_context`).
5. **ENV-4 shortcut application** - Shortcut correlation currently same across splits; test-time evaluation needs separate generation with broken/reversed correlation.
6. **CLI intervene command** - PowerShell escaping issues with `do(A)` syntax; use programmatic API instead.
7. **No actual ML training** - This is environment generation only (M1 scope). Baselines and learners in M2/M3.

## 8. Developer Self-Check Result

✅ **ENV-1 to ENV-4 can initialize** - All 4 generators registered and instantiable  
✅ **Same seed produces reproducible output** - Verified with EXP-M1-REPRO vs EXP-M1-REPRO2 (seed=123)  
✅ **Provenance artifact generated** - Each generation creates provenance.json + seed_manifest.json + execution logs  
✅ **QA can rerun experiment** - CLI commands documented above, deterministic with seed  
✅ **SCM-based generation** - ENV-3 implements full SCM with exogenous/endogenous variables  
✅ **Intervention support** - All environments implement `intervene()` method; tested on ENV-3  
✅ **Seed manifest tracking** - Base seed derives environment/split seeds deterministically  
✅ **Execution logging** - JSONL structured logs + human-readable summary  

**Status: READY FOR QA REVIEW**

---

*Generated by Developer on 2026-09-07*
*Task: DEV_TASK_002 - Controlled Environment Implementation*
*Milestone: M1*
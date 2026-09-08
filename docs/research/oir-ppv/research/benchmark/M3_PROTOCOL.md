# M3 OIR-PPV Pipeline Benchmark Protocol

## Version
M3-Protocol-v1.0

## Overview
This document defines the standardized benchmark protocol for M3 OIR-PPV pipeline evaluation. It specifies experiment schema, required artifacts, seeds, provenance, and evaluation metrics.

---

## 1. Experiment Schema

### 1.1 Configuration Structure
```yaml
experiment:
  id: "EXP-M3-XXX"           # Unique identifier
  name: "Descriptive name"
  milestone: "M3"
  description: "..."

environment:
  family: "ENV-1|ENV-2|ENV-3|ENV-4"
  config_path: "path/to/env.yaml"
  seed: 42
  splits: ["train", "val", "test"]

pipeline:
  invariant_extractor:
    type: "PCA|MLP|OIRInvariantExtractor|..."
    # Component-specific params
    invariant_dim: 64
    seed: 42
  
  generator:
    type: "Linear|OIRManifestationGenerator|..."
    output_dim: 10
    invariant_dim: 64
    context_dim: 5
    nuisance_dim: 3
    seed: 42

evaluation:
  enabled: true
  metrics:
    - "invariant_consistency"
    - "generation_validity"
    - "reconstruction_quality"
    - "invariant_preservation"
    - "context_response"
    - "diversity"
    - "distribution_similarity"
  intervention_targets: ["do(A)", "do(Z)", "do(N)"]
  counterfactual: true
  causal_validation: true
  dependency_analysis: true

output:
  base_dir: "artifacts/pipeline"
  save_intermediate: true
  save_generated: true
  save_evaluation: true

provenance:
  track_config_hashes: true
  track_seeds: true
  track_timing: true
```

---

## 2. Required Artifacts

For every M3 experiment, the following artifacts MUST be generated:

| Artifact | Path | Description |
|----------|------|-------------|
| Evaluation Results | `artifacts/pipeline/{exp_id}/evaluation.json` | Full evaluation metrics |
| Generated Data | `artifacts/pipeline/{exp_id}/generated.npz` | Generated manifestations + invariants |
| Experiment Results | `artifacts/pipeline/{exp_id}/results.json` | Complete experiment record |
| Provenance | `artifacts/pipeline/{exp_id}/provenance.json` | Config hashes, seeds, timing |
| Causal Validation | `artifacts/pipeline/{exp_id}/causal_validation.json` | Intervention-based invariance tests |
| Dependency Analysis | `artifacts/pipeline/{exp_id}/dependency_analysis.json` | Context/nuisance sensitivity |

### 2.1 Evaluation.json Schema
```json
{
  "invariant_metrics": {
    "invariance_score": 0.0-1.0,
    "context_sensitivity": 0.0-1.0,
    "nuisance_sensitivity": 0.0-1.0,
    "predictive_utility": 0.0-1.0,
    "effective_rank": int,
    "explained_variance": 0.0-1.0,
    "config_hash": "hex"
  },
  "generation_metrics": {
    "reconstruction_mse": float,
    "reconstruction_mae": float,
    "invariant_preservation": 0.0-1.0,
    "context_response": 0.0-1.0,
    "diversity_score": float,
    "novelty_score": 0.0-1.0,
    "distribution_similarity": 0.0-1.0,
    "config_hash": "hex"
  },
  "overall_score": 0.0-1.0,
  "timestamp": "ISO8601"
}
```

### 2.2 Provenance.json Schema
```json
{
  "experiment_id": "EXP-M3-XXX",
  "environment": {
    "family": "ENV-3",
    "seed": 42,
    "config_hash": "hex"
  },
  "invariant_extractor": {
    "type": "OIRInvariantExtractor",
    "config_hash": "hex"
  },
  "generator": {
    "type": "OIRManifestationGenerator",
    "config_hash": "hex"
  },
  "evaluation_config_hash": "hex",
  "causal_validation_config_hash": "hex",
  "dependency_analysis_config_hash": "hex"
}
```

---

## 3. Seeds and Determinism

| Component | Seed Source | Derivation |
|-----------|-------------|------------|
| Environment | Base seed (config) | Direct |
| Invariant Extractor | Base seed | Direct |
| Generator | Base seed | Direct |
| Evaluation | Base seed | Direct |
| Causal Validation | Base seed | Direct |
| Dependency Analysis | Base seed | Direct |

All components MUST accept `seed` parameter and use `np.random.default_rng(seed)` for reproducibility.

---

## 4. Standardized Metrics

### 4.1 Invariant Metrics
| Metric | Range | Description |
|--------|-------|-------------|
| `invariance_score` | [0,1] | Stability under nuisance intervention (1=perfect) |
| `context_sensitivity` | [0,1] | Sensitivity to context (lower=more invariant) |
| `nuisance_sensitivity` | [0,1] | Sensitivity to nuisance (lower=more invariant) |
| `predictive_utility` | [0,1] | Accuracy using I for downstream prediction |
| `effective_rank` | int | Effective dimensionality of I |
| `explained_variance` | [0,1] | Variance captured by top components |

### 4.2 Generation Metrics
| Metric | Range | Description |
|--------|-------|-------------|
| `reconstruction_mse` | [0,∞) | MSE between generated and target |
| `reconstruction_mae` | [0,∞) | MAE between generated and target |
| `invariant_preservation` | [0,1] | Correlation between I(original) and I(generated) |
| `context_response` | [0,1] | Generated observations respond to context |
| `diversity_score` | [0,∞) | Average pairwise distance in generated set |
| `novelty_score` | [0,∞) | Distance from training samples |
| `distribution_similarity` | [0,1] | Distribution match (real vs generated) |

### 4.3 Causal Validation Metrics
| Metric | Range | Description |
|--------|-------|-------------|
| `avg_nuisance_invariance` | [0,1] | Mean invariance under do(N) interventions |
| `avg_context_invariance` | [0,1] | Mean invariance under do(Z) interventions |
| `overall_invariance` | [0,1] | Average of nuisance and context invariance |
| `failure_cases` | list | Interventions where invariance_score < 0.5 |

### 4.4 Dependency Analysis Metrics
| Metric | Range | Description |
|--------|-------|-------------|
| `max_context_sensitivity` | [0,1] | Max linear sensitivity to context |
| `max_nuisance_sensitivity` | [0,1] | Max linear sensitivity to nuisance |
| `context_leakage_detected` | bool | True if context sensitivity > 0.3 |
| `nuisance_leakage_detected` | bool | True if nuisance sensitivity > 0.3 |
| `shortcut_learning_score` | [0,1] | (max_nuisance + max_context) / 2 |

---

## 5. Evaluation Protocol

### 5.1 Baseline Comparison
All M3 experiments MUST be comparable to M2 baselines (B0-B5):
- Use same environment configs
- Use same seeds
- Report same metric names
- Enable `evaluation.enabled: true`

### 5.2 Causal Validation
Every M3 experiment SHOULD run causal validation:
- Interventions: `do(N)`, `do(Z)` at minimum
- Values: At least 3 values per intervention target
- Report: `avg_nuisance_invariance`, `avg_context_invariance`, `failure_cases`

### 5.3 Dependency Analysis
Every M3 experiment SHOULD run dependency analysis:
- Report: `max_nuisance_sensitivity`, `nuisance_leakage_detected`
- Report: `shortcut_learning_score`

### 5.4 Overall Score
```
overall_score = 
  0.3 * invariant_metrics.invariance_score +
  0.2 * invariant_metrics.predictive_utility +
  0.2 * generation_metrics.invariant_preservation +
  0.15 * generation_metrics.context_response +
  0.15 * generation_metrics.distribution_similarity
```

---

## 6. Learner Replacement Protocol

### 6.1 Interface Contracts
New learners MUST implement:
- `EncoderLearner`: `fit()`, `encode()`, `get_output_dim()`, `get_config_hash()`
- `PredictorLearner`: `fit()`, `predict()`, `predict_proba()`, `get_config_hash()`
- `DecoderLearner`: `fit()`, `decode()`, `get_config_hash()`

### 6.2 Registration
```python
from pipeline.learners import LearnerRegistry

@LearnerRegistry.register_encoder("MyEncoder")
class MyEncoder(EncoderLearner):
    ...

@LearnerRegistry.register_predictor("MyPredictor")
class MyPredictor(PredictorLearner):
    ...

@LearnerRegistry.register_decoder("MyDecoder")
class MyDecoder(DecoderLearner):
    ...
```

### 6.3 Configuration
```yaml
pipeline:
  invariant_extractor:
    type: "MyEncoder"
    output_dim: 64
    custom_param: value
  
  generator:
    type: "MyDecoder"
    output_dim: 10
    custom_param: value
```

---

## 7. Backward Compatibility

### 7.1 M2 Regression
- All M2 benchmark commands MUST still execute
- M2 results format unchanged
- B0-B5 baselines must produce same results

### 7.2 M3-M2 Comparison
- M3 experiments can reference M2 results
- Use same environment configs and seeds
- Report delta: `M3_score - M2_baseline_score`

---

## 8. Acceptance Checklist

Before M3 experiment is accepted:
- [ ] All required artifacts generated
- [ ] Evaluation.json matches schema
- [ ] Provenance.json matches schema
- [ ] Causal validation completed (if enabled)
- [ ] Dependency analysis completed (if enabled)
- [ ] Seeds documented for all components
- [ ] Config hashes recorded
- [ ] Overall score computed
- [ ] M2 regression tests pass
- [ ] Protocol version recorded in experiment

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| M3-Protocol-v1.0 | 2026-09-08 | Initial protocol freeze |

---

*This protocol is frozen for M3. Changes require new protocol version.*
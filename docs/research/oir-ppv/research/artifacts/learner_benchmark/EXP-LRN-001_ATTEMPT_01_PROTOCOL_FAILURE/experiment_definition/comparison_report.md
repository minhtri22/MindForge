# OIR-PPV Standard Learner Benchmark - EXP-LRN-001

## Status
Frozen matrix created. Reference learner implementations audited.

## Learner Contract Audit

### Existing API
The accepted learner interface from `DEV_TASK_008` uses:

- `EncoderLearner` with methods: `fit(observations, context=None, labels=None, nuisance=None)`, `encode(observations)`, `get_output_dim()`, `get_config_hash()`
- `PredictorLearner` with methods: `fit(invariant, labels)`, `predict(invariant)`, `predict_proba(invariant)`, `get_config_hash()`
- `DecoderLearner` with methods: `fit(invariant, context, nuisance, targets)`, `decode(invariant, context, nuisance)`, `get_config_hash()`

No `get_metadata` method is defined in the accepted API. Metadata is returned via `fit` return dicts.

## Learner Implementations

### L0 - PCA
- **Status**: Implemented in `pipeline/learners.py` as `PCAEncoder`
- **Contract**: Complies with `EncoderLearner`
- **Training**: Unsupervised PCA fit
- **Fidelity**: Faithful

### L1 - MLP encoder
- **Status**: `MLPEncoder` exists but is placeholder (fit marks fitted, encode falls back to PCA)
- **Contract**: Complies with `EncoderLearner`
- **Training**: NOT implemented - placeholder
- **Fidelity**: Adapted placeholder

### L2 - VAE
- **Status**: `AutoencoderEncoder` implemented with numpy gradient descent
- **Contract**: Complies with `EncoderLearner`
- **Training**: Trainable autoencoder with reconstruction loss
- **Fidelity**: Adapted surrogate VAE (deterministic mean output)
- **Reference**: Kingma and Welling, 2013

### L3 - IRM-style encoder
- **Status**: NOT implemented
- **Contract**: N/A
- **Note**: Surrogate IRM-style not yet available

### L4 - DANN encoder
- **Status**: NOT implemented
- **Contract**: N/A
- **Note**: DANN surrogate not yet available

## Implementation Gaps

1. MLPEncoder requires gradient-based training implementation
2. IRM-style encoder not implemented
3. DANN encoder not implemented
4. Learner metadata serialization needs standardization
5. Common contract tests missing

## Next Steps

- Implement gradient training for MLPEncoder
- Create IRM-style surrogate encoder
- Create DANN surrogate encoder
- Add shared contract tests
- Run smoke validation per learner

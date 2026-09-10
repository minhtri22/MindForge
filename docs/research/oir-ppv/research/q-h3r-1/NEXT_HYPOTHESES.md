# Q-H3R.1 Next Hypotheses

These are candidates only. None is opened or authorized by Q-H3R.1.

## P1 candidate — H3R.2

- `hypothesis_id`: `H3R.2`
- `mechanism`: decoder/readout mismatch over nonlinear representation geometry
- `prediction`: with a prospectively frozen nonlinear probe family and equalized probe budget, at least one candidate will retain clean utility substantially better than under the H3R v1.1 linear probe while preserving or improving the noise effect relative to L0
- `intervention`: replace only the frozen downstream probe family in a new protocol version; keep representation families and paired noise contract fixed
- `expected_signature`: candidate clean gap vs L0 shrinks materially and the improvement reproduces across ENV/seeds
- `falsification_condition`: nonlinear probe fails to close the clean gap or closes it only through unstable/noisy overfit
- `required_benchmark`: new prospectively frozen H3R successor with fresh test identity/seeds
- `relationship_to_H3R`: direct successor mechanism test; H3R v1.1 stays closed
- `requires_new_model_training`: probe retraining yes; representation retraining per new protocol only if frozen prospectively

## P2 candidate — H3X

- `hypothesis_id`: `H3X`
- `mechanism`: nonlinear interaction information survives but is not linearly accessible
- `prediction`: explicit interaction recoverability will explain more of candidate clean-performance variance than latent dimension, nuisance recoverability, or support shift
- `intervention`: prospectively freeze interaction-sensitive versus additive probes on new validation/test environments
- `expected_signature`: interaction-sensitive probe uplift is consistent and largest where linear accuracy is weakest
- `falsification_condition`: interaction uplift disappears under held-out confirmatory data or is matched by additive controls
- `required_benchmark`: dedicated interaction-recoverability benchmark with equal capacity controls
- `relationship_to_H3R`: explains representation readout behavior without rerunning H3R v1.1
- `requires_new_model_training`: no new representation training required for first decisive version

## P3 candidate — Q-H3R.2

- `hypothesis_id`: `Q-H3R.2`
- `mechanism`: residual clean task-information loss after nonlinear decoding
- `prediction`: after controlling decoder expressivity, a smaller but reproducible candidate-vs-L0 gap remains in task-variable/label recoverability
- `intervention`: compare equal-capacity diagnostic decoders plus direct task-variable recoverability on fresh environments/seeds
- `expected_signature`: residual gap remains after nonlinear readout and tracks task-variable recoverability
- `falsification_condition`: equal-capacity nonlinear decoders remove the gap and task-variable recoverability matches L0
- `required_benchmark`: new frozen clean-information benchmark; no H3R v1.1 test reuse
- `relationship_to_H3R`: isolates residual M1 from M6/M7
- `requires_new_model_training`: representation reuse may be sufficient if benchmark freezes it prospectively

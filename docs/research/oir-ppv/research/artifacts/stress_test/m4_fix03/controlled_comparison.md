# Controlled Comparison

Seed: `42`. Numerical tolerance: `1e-09`.

| Variant | Reconstruction MSE | Predictive accuracy |
| --- | ---: | ---: |
| placeholder | 0.59421355 | 0.98400000 |
| untrained | 0.28160511 | 0.80000000 |
| trained | 0.23815564 | 0.84800000 |

## Derived checks

- encoder_loss_decreased: `True`
- decoder_loss_decreased: `True`
- trained_mse_below_untrained: `True`
- trained_mse_below_placeholder: `True`

Learning demonstrated: `True`.

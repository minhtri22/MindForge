# Controlled Comparison

Seed: `42`. Numerical tolerance: `1e-09`.

| Variant | Reconstruction MSE | Predictive accuracy |
| --- | ---: | ---: |
| placeholder | 0.44488293 | 0.81666667 |
| untrained | 0.21271521 | 0.78333333 |
| trained | 0.23334915 | 0.81666667 |

## Derived checks

- encoder_loss_decreased: `True`
- decoder_loss_decreased: `True`
- trained_mse_below_untrained: `False`
- trained_mse_below_placeholder: `True`

Learning demonstrated: `False`.

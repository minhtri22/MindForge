# Experiment Comparison: phase2-lr-sweep-v1

Primary metric: bits_per_byte
Seeds: [101, 202, 303]

## Baseline
- Mean bits_per_byte: 10.537771
- Median: 10.478312
- Std: 0.125701

## Treatment
- Mean bits_per_byte: 10.938692
- Median: 10.875836
- Std: 0.136213

## Paired Effects
- Seed 101: baseline=10.478312, treatment=10.875836, abs=0.397524, rel=3.7938%
- Seed 202: baseline=10.682171, treatment=11.094983, abs=0.412813, rel=3.8645%
- Seed 303: baseline=10.452830, treatment=10.845257, abs=0.392427, rel=3.7543%

## Resources
- wall_clock_seconds: baseline_mean=14.16, treatment_mean=13.46, delta=-0.70
- peak_device_memory_bytes: baseline_mean=211125760.00, treatment_mean=211125760.00, delta=0.00

# OIR-PPV v0.13.11 Replay Simulator

## Purpose

This simulator package exists to make historical failure replay reproducible by independent reviewers.

It compares:

- OIR-PPV v0.11 baseline behavior
- OIR-PPV v0.13.10 treatment behavior

using the frozen seed registry:

`docs/research/oir-ppv/artifacts/seeds/v0.13.11_seed_registry.json`

## Reproducibility rules

1. Do not change seeds.
2. Do not tune parameters after seeing results.
3. Record simulator version with every result.
4. Treat reconstructed seeds as reconstructed, not historical runtime dumps.

## Expected artifacts

- baseline_results.json
- treatment_results.json
- comparison_report.json

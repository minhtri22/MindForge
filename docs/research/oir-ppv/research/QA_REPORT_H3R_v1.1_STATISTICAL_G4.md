# QA REPORT — H3R v1.1 G4 STATISTICAL QA

Date: 2026-09-09
Role: Independent statistical reviewer
Experiment: `EXP-H3R-002`

## Verdict

- GATE_VERDICT: `PASS`
- SCIENTIFIC_VERDICT_RECOMPUTED: `FALSIFIED_UNDER_TESTED_CONDITIONS`
- P0/P1: none.
- Input evidence: 20/20 valid paired environment-seed cells from the immutable decisive execution.

## Frozen statistical contract checked

- Stratification: four environments, five frozen H3R seeds per environment.
- Bootstrap: 10,000 paired stratified resamples.
- Bootstrap seed: `20260909`.
- Candidate CI: two-sided `98.75%` per candidate.
- Practical noise margin: `0.01`.
- Clean utility margin: `0.02`.
- Worst-environment veto: every environment mean `E_noise <= +0.02`.

## Independent recomputation

| Candidate | E_noise estimate | 98.75% CI | Clean gap estimate | 98.75% CI | Worst-env veto | Verdict |
| --- | ---: | --- | ---: | --- | --- | --- |
| L1 | -0.017787 | [-0.026892, -0.008857] | +0.214052 | [+0.164540, +0.263763] | PASS | FALSIFIED |
| L2 | -0.016718 | [-0.024945, -0.008413] | +0.178006 | [+0.118736, +0.244234] | PASS | FALSIFIED |
| L3 | -0.015782 | [-0.024945, -0.006424] | +0.211479 | [+0.155465, +0.269306] | PASS | FALSIFIED |
| L4 | -0.013456 | [-0.022282, -0.004218] | +0.209575 | [+0.163943, +0.254754] | PASS | FALSIFIED |

The independent recomputation matches `h3r_summary.json` to floating-point tolerance (maximum absolute difference below `6e-17`) when the frozen manifest seed order is preserved.

## Rule application

No candidate satisfies support because each `E_noise` upper CI is above `-0.01`, and each candidate also has a clean-risk CI far above the allowed `+0.02` utility margin.

All four candidates satisfy the frozen falsification rule through clean utility loss: each lower CI for `DeltaR_clean_vs_L0` is greater than `+0.02`.

Therefore the global rule recomputes to:

`FALSIFIED_UNDER_TESTED_CONDITIONS`.

No threshold, seed, baseline, learner, margin, bootstrap setting, or result-dependent choice was changed.

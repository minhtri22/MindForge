# OIR-PPV Audit Fix-3 — Simulator Reconstruction Plan

## Purpose

This document defines the reconstruction plan required before claiming OIR-PPV experimental validation.

The previous audit identified that the OIR-PPV v0.1-v0.13.10 chain currently represents hypothesis evolution and experiment design. This phase reconstructs the minimum executable simulator lineage required for reproducible validation.

## Reconstruction Principle

Do not rebuild the entire historical chain unless required.

The goal is not to recreate every exploratory step, but to preserve causal evolution:

```
Failure
  -> architectural change
  -> new capability
  -> next failure discovered
```

## Required Executable Milestones

| Version | Purpose | Priority |
|---|---|---|
| v0.11 | Baseline failure model | P0 |
| v0.12 | Exploration extension | P2 |
| v0.13 | Hierarchy extension | P2 |
| v0.13.3 | Intervention validation | P1 |
| v0.13.8 | Minimal generative invariant | P1 |
| v0.13.10 | Final treatment candidate | P0 |

## Minimum Required Artifact Per Version

Each executable simulator version must contain:

```
versions/
  vX.Y.Z/
    simulator.py
    config.json
    README.md
```

Required metadata:

- version identifier
- hypothesis being tested
- added capability
- known limitation
- seed policy
- metrics produced

## Validation Path

After reconstruction:

```
v0.11
  |
  | historical failure replay
  v
v0.13.10
```

using identical:

- seed
- failure case
- environment
- evaluation metrics

## Experimental Gate

A validation claim is allowed only after:

1. Simulator source exists.
2. Config is frozen.
3. Runner executes successfully.
4. Raw JSON outputs are committed.
5. Comparison report is generated from raw outputs.

## Current Status

| Component | Status |
|---|---|
| Hypothesis lineage | Verified |
| Protocol | Verified |
| Failure definitions | Verified |
| Executable lineage | Pending reconstruction |
| Historical replay | Pending |
| Validation claim | Blocked |

## Next Action

Reconstruct P0 simulators first:

1. v0.11 baseline
2. v0.13.10 treatment
3. Execute S11-A/B/C replay
4. Only then decide whether intermediate versions need full reconstruction.

# OIR-PPV Audit Fix-2 — Simulator Lineage Verification

## Purpose

This document audits the simulator lineage before any historical replay claim.

Rule:

> A simulator version is not considered experimental evidence until source code, configuration, execution path, and output provenance are verified.

## Verification Status Legend

| Status | Meaning |
|---|---|
| VERIFIED | Source/config/execution artifact exists and can be reproduced |
| RECONSTRUCTED | Design exists, artifact reconstruction required |
| DESIGN_ONLY | Conceptual evolution only |
| PENDING | Not verified yet |

---

## Simulator Lineage Audit

| Version | Hypothesis Role | Source | Config | Executable | Status |
|---|---|---|---|---|---|
| v0.11 | Reward + frequency baseline | Pending verification | Pending verification | Pending | RECONSTRUCTED |
| v0.12 | Add exploration capability | Pending verification | Pending verification | Pending | RECONSTRUCTED |
| v0.13 | Hierarchy modeling | Pending verification | Pending verification | Pending | RECONSTRUCTED |
| v0.13.1 | Blind hierarchy discovery | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.2 | Dependency graph attack | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.3 | True intervention validation | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.4 | Confounder rejection | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.5 | Competing causal hypotheses | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.6 | Cross-environment invariance | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.7 | Environment stress testing | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.8 | Minimal generative invariant | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.9 | Novel manifestation prediction | Pending verification | Pending verification | Pending | DESIGN_ONLY |
| v0.13.10 | Full treatment candidate | Pending verification | Pending verification | Pending | RECONSTRUCTED |

---

## Required Closure Before Replay

The following must exist for each version used in experiments:

```
versions/
  vX.Y.Z/
    simulator.py
    config.json
    README.md
```

Required execution chain:

```
seed
  ↓
frozen failure case
  ↓
simulator version
  ↓
runner
  ↓
raw execution output
```

---

## Current Research Claim Level

Current state:

```
hypothesis evolution        VERIFIED
experiment design           VERIFIED
simulator history           RECONSTRUCTED / DESIGN_ONLY
historical replay evidence  PENDING
validation claim             NOT ALLOWED
```

No validation claim should be made until raw replay artifacts exist.

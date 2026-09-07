# OIR-PPV Audit Fix-3 — Phase A P0 Reconstruction Execution Plan

## Objective

Reconstruct the minimum executable evidence chain required before historical replay.

The goal is not to recreate every exploratory milestone, but to establish a reproducible baseline/treatment comparison.

## P0 Scope

### Baseline

Simulator:
- v0.11

Purpose:
- reproduce historical failure conditions
- establish raw baseline behavior

Required artifacts:
- simulator.py
- config.json
- README.md

### Treatment

Simulator:
- v0.13.10

Purpose:
- test whether invariant-oriented architecture improves over baseline

Required artifacts:
- simulator.py
- config.json
- README.md

## Execution Constraints

The following must remain identical between baseline and treatment:

- seed
- failure case definition
- environment parameters
- evaluation protocol

Only simulator architecture may differ.

## Required Experiments

Initial replay set:

- S11-A Frequency Trap
- S11-B Reward Shortcut
- S11-C Surface Pattern

## Acceptance Gate

Phase A passes only when:

1. v0.11 reproduces expected historical failure modes.
2. v0.13.10 can be executed under the same protocol.
3. Raw outputs are committed before interpretation.

## Forbidden Claims

No validation claim is allowed until raw execution artifacts exist.

Current phase status:

P0_RECONSTRUCTION_PENDING

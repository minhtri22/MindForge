# OIR-PPV Simulator Version Lineage

This directory freezes simulator evolution for reproducibility.

Rules:
- Each version must have independent source code.
- No future logic may be backported into older versions.
- Every experiment must declare simulator version and seed registry.

Versions covered:
- v0.11 baseline reward/frequency selector
- v0.12 challenger/exploration
- v0.13 hierarchy
- v0.13.1 blind hierarchy
- v0.13.2 dependency attack
- v0.13.3 intervention validation
- v0.13.4 confounder attack
- v0.13.5 competing hypotheses
- v0.13.6 cross-environment
- v0.13.7 intervention stress
- v0.13.8 minimal generative invariant
- v0.13.9 novel manifestation prediction
- v0.13.10 hypothesis generation/self experiment

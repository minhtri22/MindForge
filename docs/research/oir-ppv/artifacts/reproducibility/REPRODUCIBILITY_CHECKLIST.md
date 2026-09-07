# OIR-PPV Reproducibility Checklist

## Goal

Enable an independent reviewer to reproduce OIR-PPV historical replay experiments.

## Required artifacts

- [ ] Versioned simulator source for every architecture milestone
- [ ] Version-specific configuration
- [ ] Frozen seed registry
- [ ] Failure case provenance
- [ ] Replay runner
- [ ] Raw execution output
- [ ] Comparison report

## Validation rule

A result is valid only when:

1. Seed is identical.
2. Environment definition is identical.
3. Failure mechanism is documented.
4. Simulator version is pinned.
5. Raw output is committed.

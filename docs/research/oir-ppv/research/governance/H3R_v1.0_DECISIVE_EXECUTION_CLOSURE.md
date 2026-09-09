# H3R v1.0 Decisive Execution Closure

Status: `CLOSED / PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT`

## Frozen attempt identity

- Protocol: `OIR-PPV-H3R v1.0`
- Experiment: `EXP-H3R-001`
- Owner authorization SHA256: `83b0459bd4e0a7ea9d076545740810a8b63eb4254daf1f93d06f63acbd812d51`
- Scientific access event: `H3R_DECISIVE_ACCESS_001` at `2026-09-09T10:14:12.113926+00:00`
- Scientific test access count consumed: `1`
- Failure artifact SHA256: `2be6f6c00968650c554605f41f83ac8b57bbd436e025b66d1aabdb82c593f705`
- Failure time: `2026-09-09T10:14:12.123258+00:00`
- Rerun permitted: `false`

## Closure finding

The decisive attempt failed before completing the first scientific cell with:

```text
ValueError: could not convert string to float: np.str_('circle')
```

The frozen v1.0 protocol already required `variables_affected = all numeric observation channels only`. ENV-1 contains a mixed observation table whose `shape` channel is categorical. The v1.0 runner nevertheless cast the full train/test observation matrices to `float` while preparing observation noise. That implementation did not faithfully realize the frozen numeric-only perturbation contract.

The protocol semantics remain realizable. The failed execution is therefore closed as an implementation `PROTOCOL_DEVIATION`, not as scientific support, falsification, or `INVALID_PROTOCOL`.

## One-shot boundary

`EXP-H3R-001`, its access event, authorization snapshot, runtime/pre-execution artifacts, and `failure.json` are immutable evidence. The scientific access count is not reset and H3R v1.0 must not be rerun or overwritten.

## Recovery rule

Recovery proceeds only through versioned successor H3R v1.1 with:

- unchanged v1.0 scientific estimand, baseline/candidates, noise magnitude, metrics, margins, bootstrap, multiplicity, and stopping rule;
- train-only numeric-channel detection;
- categorical-channel preservation validation;
- stable mixed-observation identity hashing;
- fresh test seeds/test lock with access count `0` at freeze;
- separate owner authorization after v1.1 freeze/publication.

H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

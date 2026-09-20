# MSA-0 — Endpoint Measurement Contract

Status: **FROZEN PROGRAM-LEVEL CONTRACT**

## E1 — terminal accuracy

Argmax correctness over the full canonical evaluation set at the frozen
terminal checkpoint, step `250`.

Independent rationale: it is the original KCL acquisition/performance
measurement and directly measures task correctness.

Role: **MANDATORY SENTINEL**. It may not be dropped post-CPRM.

## E2 — terminal cross-entropy loss

`cross_entropy(logits, target)` over the same full evaluation set at the same
terminal checkpoint.

Independent rationale: KCL-1 `evaluate()` already emitted `loss` before
ACO/CPRM, with no new training behavior required.

Role: **MANDATORY CO-MEASUREMENT**.

MSA-1 must collect E1 and E2 from the same endpoint state and may not keep only
the metric with more variance after seeing outcomes.

Existing learning-curve AUC may remain diagnostic because it predates MSA, but
it is not an endpoint candidate and cannot determine MSA-1 PASS alone.

Confidence margin, calibration error, alternative losses, early stopping time,
and time-to-criterion are not authorized MSA-1 primary measures.

# POST_H3R_FRONTIER_AMENDMENT_001

Date: 2026-09-12

## Scope

Governance-only amendment resolving the post-H3R research frontier. This document authorizes protocol review and preregistration work only. It does not authorize experiment execution, fresh test identity, seed generation, decisive evidence access, result collection, or a scientific verdict.

## Historical state

- H3R: `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS`
- Q-H3R.1: `PARTIAL_MECHANISM_DIAGNOSIS`
- H3R2: `INVALID_PROTOCOL_INPUT`
- H3R2-R v1.0: `PROTOCOL_DEVIATION`
- H3R2-R v1.1: `BLOCKED_BY_GOVERNANCE / NOT_EXECUTED`
- M6: `EXPLORATORY_SUPPORTED / UNCONFIRMED`
- M7: `EXPLORATORY_SUPPORTED / UNCONFIRMED`
- H4: `NOT_OPENED / DEFERRED_BY_OWNER`

These states are preserved and are not re-adjudicated by this amendment.

## Owner decision

`DEFER_H4`

`AUTHORIZE_H3R2_CONFIRMATORY_V2_PROTOCOL_REVIEW`

`NOT_AUTHORIZE_H3R2_CONFIRMATORY_V2_EVIDENCE_ACCESS`

H3R2-CONFIRMATORY-v2 status is therefore:

`AUTHORIZED_FOR_PROTOCOL_REVIEW`

and separately:

`EVIDENCE_ACCESS_NOT_AUTHORIZED`

## Reason

The current lineage leaves unresolved whether the H3R clean-utility failure is substantially attributable to M6 decoder/readout dependence rather than true loss of task-relevant information in the fixed representation. Q-H3R.1 provides exploratory mechanism diagnosis but does not settle M6 confirmatorily. H3R2-R v1.0 remains a protocol deviation and cannot be upgraded post hoc.

A narrowly scoped confirmatory protocol may therefore be designed and adversarially reviewed before any fresh decisive evidence is accessed. This is a governance decision, not a scientific result.

## Scientific claim boundary

The strongest prospective claim that H3R2-CONFIRMATORY-v2 may be designed to adjudicate is:

> Under a frozen reconstructed representation and a preregistered equal-budget readout comparison, nonlinear readout recovers more task-relevant utility than the historical linear readout, beyond any uplift observed in the L0 control.

Nonlinear recovery does not establish causal sufficiency of the representation. H3R2-CONFIRMATORY-v2 primarily targets M6. It must not confirm M7 merely from nonlinear readout improvement.

## H4 boundary

H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

H4 and H3R2-CONFIRMATORY-v2 are alternative post-H3R research directions. H3R2-CONFIRMATORY-v2 is not added as a prerequisite for H4. The owner currently chooses protocol review for H3R2-CONFIRMATORY-v2 first. Any later H4 opening requires a separate owner frontier decision.

Even if a future H3R2-CONFIRMATORY-v2 experiment succeeds, H4 does not open automatically. Closure must return to an owner frontier decision.

## Authorization boundary

Authorized now:

- protocol review;
- preregistration drafting;
- adversarial protocol QA;
- definition of metrics, thresholds, controls, statistics, provenance, and deterministic adjudication;
- review of the frozen reconstructed-representation contract.

Not authorized now:

- fresh seed generation;
- fresh test identity generation;
- decisive evidence access;
- experiment execution;
- result collection;
- scientific adjudication;
- H4 protocol execution or H4 evidence access.

## Permanent frontier rule

After scientific closure, the next hypothesis or experiment does not open automatically. Governance must explicitly classify the frontier as one of:

1. confirmatory follow-up;
2. new hypothesis;
3. research stop/park.

Conceptual gate:

```text
Scientific Closure
        |
        v
Mechanism Status
        |
        v
Evidence Debt
        |
        v
Owner Frontier Decision
        |
  +-----+-----+
  |     |     |
  v     v     v
Confirmatory  New H  Stop/Park
```

This rule governs research progression; it is not scientific evidence.

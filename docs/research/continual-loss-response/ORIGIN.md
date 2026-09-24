# CLRM-0 — Origin and Non-Rescue Rationale

Status: **FROZEN PROGRAM ORIGIN**

## Parent

CLRM starts from exact MSA closure:

```text
64138ab9cb09dcb56a387d3b1f500063eff8302d
```

The parent program established and independently replicated:

```text
terminal accuracy             coarse / ceiling-compressed
terminal cross-entropy loss   informative
```

under the unchanged current synthetic substrate.

## Why CLRM exists

KCL established that fixed global optimizer-boundary policies are insufficient
and that A/B/C policy effects are heterogeneous.

CPRM then asked whether a prospectively frozen four-component continuous
response vector had sufficient response geometry to justify predictor fitting.

CPRM-1 returned:

```text
NEGATIVE_RESPONSE_GEOMETRY_NOT_QUALIFIED
```

because its joint contract required all four components to qualify and
`final_current_accuracy` failed in all nine policy×stage cells.

MSA was opened upstream rather than modifying CPRM after outcomes. MSA-1 and
fresh MSA-3 replication established that terminal CE loss retains endpoint
information while terminal accuracy is reproducibly coarse.

CLRM therefore asks a new question under a new response definition.

## Why this is not CPRM-2

CLRM does not:

- continue CPRM numbering;
- remove only `final_current_accuracy` from the CPRM vector;
- promote CPRM-1's three passing components into a replacement target;
- fit on CPRM-1 outcomes;
- use MSA-1/MSA-3 values to select features or hyperparameters;
- reinterpret CPRM-1 as a predictor result.

The CLRM primary response vector is redefined prospectively in CE-loss space
from continual-learning semantics:

1. acquisition on the new/current task;
2. retention over tasks seen before the boundary.

This target exists independently of which individual CPRM-1 components happened
to pass.

## Program boundary

CLRM starts with specification and measurement-support qualification.

Predictor fitting is forbidden until the new CLRM response vector independently
qualifies on a fresh cohort under its own frozen support contract.

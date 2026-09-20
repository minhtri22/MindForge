# MSA-0 — Substrate Difficulty Contract

Status: **FROZEN PROGRAM-LEVEL CONTRACT**

## MSA-1 current-substrate rule

MSA-1 must use the current canonical KCL-compatible substrate **unchanged**.

Forbidden in MSA-1:

- reducing or increasing training steps;
- changing batch size;
- changing optimizer or learning rate;
- changing replay fraction;
- changing model capacity;
- changing relation count;
- inventing new task mappings;
- selecting easier/harder seeds;
- changing policy definitions;
- changing the four-task order.

If both mandatory endpoint measurements satisfy a future preregistered
saturation criterion, `CURRENT_SUBSTRATE_ENDPOINT_SATURATED` is a valid
conclusion. No automatic "make it harder" transition follows.

## Conditional MSA-2

A substrate-structure study may be designed only after MSA-1 closes and a
formal transition decision justifies it.

If opened, MSA-2 must use a small finite set of substrate/task constructions
whose constructors existed before CPRM. Permissible source families are limited
to pre-CPRM KCL task constructors already present in repository history,
including KCL-1 candidate mappings and KCL-5/5.1 task-family constructors.

MSA-0 does not rank those families by difficulty and does not select one.

## Prohibited adaptive difficulty search

Never run a variant, inspect endpoint geometry, make it harder/easier, and rerun
until informative.

The canonical 250-step endpoint remains fixed for MSA-1.

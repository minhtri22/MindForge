# Track A External Reference Model Policy

Status: **FROZEN POLICY / NO REFERENCE MODEL ADMITTED YET**

Protocol authority: `docs/research/track-a-foundation-protocol.md`

## 1. Purpose

Track A may use a strong external model as a quality reference, teacher candidate, or error-analysis aid without confusing that model with the compact 5M/10M/20M/50M candidates.

Reference models exist to answer:

> How much capability does the compact candidate retain relative to a stronger external model on the same frozen Track-A benchmark?

They do not redefine the Track-A research question.

## 2. Reference model role

A qualified reference may be used for:

```text
quality-ceiling comparison
candidate scenario proposal
error taxonomy assistance
training-example proposal in a separately authorized task
future distillation research after benchmark failure is demonstrated
```

A reference model is not:

```text
a Track-A size-sweep candidate
benchmark ground-truth authority
part of the MindForge kernel
part of the MKS TokenModel contract
a required production dependency
a PPF component
```

## 3. Teacher-as-truth prohibition

External-model output must never become held-out benchmark truth merely because the model is strong.

If a reference model proposes a scenario or label:

```text
proposal -> independent rule/human review -> benchmark truth
```

not:

```text
reference output -> benchmark truth
```

This applies to calibration, development, and especially held-out cases.

## 4. Qualification gate

Before a named reference is admitted, a separate qualification task must record:

```text
model identity/version
source and license
access method
quantization/runtime if local
prompt/template version
context limit used for Track-A evaluation
decoding settings
reproducibility constraints
hardware/resource envelope where relevant
availability risks
benchmark contamination/leakage considerations
```

The qualification task must end with:

```text
ADMIT AS REFERENCE
REVISE
or
REJECT
```

## 5. Benchmark fairness

Reference and compact candidates must receive semantically equivalent benchmark inputs.

A reference model must not receive hidden benchmark metadata, expected labels, privileged personal-state fields, or tool descriptions unavailable to the compact candidate.

If different prompt formats are required by different model families, the semantic information content must remain equivalent and prompt versions must be recorded.

## 6. Reference scores do not set truth thresholds after the fact

RVE/TUE thresholds are frozen in the Track-A Foundation Protocol before reference-model evaluation.

Therefore a strong or weak reference score may not be used to retroactively move the compact-model success gates.

Reference results are descriptive context, not threshold-tuning authority.

## 7. Distillation is deferred

Distillation is not authorized by N3.

It may be proposed only after:

```text
Track-A Benchmark v1 is materialized and frozen
AND
at least one compact candidate is evaluated
AND
measured failure indicates teacher supervision may address a specific gap
```

A distillation task must compare against the corresponding non-distilled baseline and report incremental value.

## 8. Qwen3.8-27B status

Current status:

```text
Qwen3.8-27B: PROPOSED EXTERNAL REFERENCE CANDIDATE
QUALIFICATION: NOT YET EXECUTED
ADMISSION: NOT YET GRANTED
```

It may be evaluated in a separate `Track-A External Reference Qualification` task.

N3 does not download it, run it, integrate it, adapt the MKS model contract, or make it a dependency.

## 9. Model-contract non-trigger

The existence of an external reference model alone does not trigger a new MKS contract revision.

The PyTorch-bound `TokenModel` v0 contract is reconsidered only when a second proven runtime/model implementation must participate through that boundary and cannot do so without inappropriate lifecycle emulation, or when a demonstrated current consumer needs a missing capability.

Reference evaluation may remain outside the MindForge runtime contract.

## 10. Final policy state

```text
REFERENCE POLICY: FROZEN
REFERENCE MODEL REQUIRED FOR N3 PASS: NO
REFERENCE MODEL ADMITTED: NONE
QWEN3.8-27B: PROPOSED / NOT QUALIFIED
TEACHER-AS-TRUTH: FORBIDDEN
DISTILLATION: NOT AUTHORIZED
MODEL-CONTRACT CHANGE: NOT AUTHORIZED
```

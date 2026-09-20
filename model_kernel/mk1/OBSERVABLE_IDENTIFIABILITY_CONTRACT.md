# MK-1 Observable Identifiability Contract v0.1

Status: **FROZEN SPECIFICATION / NOT EXECUTED**

Date: **2026-09-21**

## 1. Purpose

KCL established that replicated mechanism structure does not guarantee that regime identity is predictable from the observable state available at the decision boundary.

MK-1 therefore requires every target field to declare exactly what observable evidence can identify it.

## 2. Inference boundary

The only admissible information for primary MK-1 prediction is:

- the current raw observation;
- current task/context explicitly included in the sample;
- current-session text/state explicitly serialized into that same input.

Forbidden:

- later turns;
- future-task examples;
- downstream policy outcomes;
- counterfactual outcomes;
- gold action/decision labels;
- hidden simulator state;
- episodic retrieval;
- external memory not serialized into the current input.

## 3. Field contract

Every primary field in Z and every direct canonical target field in C must be registered with:

| Contract item | Required |
|---|---|
| field name | yes |
| target family | Z1/Z2/Z3/Z4/C1/C2/C3/C4/C5 |
| observable source span or source object | yes |
| derivation rule | yes |
| whether target is categorical/continuous/relational | yes |
| whether thresholding is involved | yes |
| forbidden-information audit | yes |
| deterministic baseline availability | yes/no with reason |
| expected ambiguity mode | yes |
| evaluation metric | yes |

No field may enter the primary target after training begins.

## 4. Identifiability preflight

Before training, construct a target-only audit that verifies:

1. every gold field can be traced to the current sample's canonical observable source;
2. removing forbidden future/counterfactual metadata leaves the gold target unchanged;
3. target construction can be rerun from the frozen current-input gold object;
4. no field is generated from the final downstream action;
5. no class depends on a distinction absent from the serialized current input;
6. gold canonical C is reconstructed by the frozen R from gold Z with exact 100% identity.

## 5. Ambiguity handling

If the observable input genuinely underdetermines a field, the dataset must encode one of:

- UNKNOWN;
- AMBIGUOUS;
- SET-VALUED admissible target;

or remove that field from primary adjudication.

The protocol forbids forcing a single gold class when the frozen observable information does not identify one.

## 6. Admission gate

The contract passes only if:

- 100% of primary Z and C target fields have complete field contracts;
- zero forbidden-information violations exist;
- zero primary samples require hidden/future information for gold reconstruction;
- all known underdetermined cases are explicitly represented as ambiguity rather than silently assigned a point label;
- gold C == R(gold Z) for 100% of admitted scenes.

Failure verdict:

`OBSERVABLE_IDENTIFIABILITY_CONTRACT_FAIL`

This blocks training.

## 7. Scientific interpretation

Passing this contract proves only that the target is **defined from observable information**. It does not prove that a model can learn it.

Learnability remains the empirical question of MK-1.

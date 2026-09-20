# MK-1 Observable Identifiability Contract v0.1

Status: **FROZEN / CONSISTENCY-EXTENDED UNDER AMENDMENT 001 / NOT EXECUTED**

Date: **2026-09-21**

Original pre-extension blob:

`2d5b5f92a8787c244dc13f1b4d1111054d30ee71`

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

Amendment 001 freezes exact output vocabularies and does not contain dynamic UNKNOWN/AMBIGUOUS classes.

Therefore, if the serialized current input genuinely underdetermines any primary Z or C field:

- the scene is **not admissible** to the primary MK-1 cohort;
- it must be recorded in a pre-training exclusion ledger with the underdetermined field and reason;
- it cannot be relabeled to a convenient point class;
- it cannot be moved selectively between TRAIN/VALIDATION/PRISTINE after observing model behavior.

The renderer/generator may avoid producing such scenes prospectively, but the zero-fresh preflight must prove the exclusion logic without inspecting any scientific model outcome.

## 6. Admission gate

The contract passes only if:

- 100% of primary Z and C target fields have complete field contracts;
- zero forbidden-information violations exist;
- zero primary samples require hidden/future information for gold reconstruction;
- zero admitted primary scenes contain an underdetermined Z or C target;
- every excluded underdetermined scene is recorded before training and never silently point-labeled;
- gold C == R(gold Z) for 100% of admitted scenes.

Failure verdict:

`OBSERVABLE_IDENTIFIABILITY_CONTRACT_FAIL`

This blocks training.

## 7. Scientific interpretation

Passing this contract proves only that the target is **defined from observable information**. It does not prove that a model can learn it.

Learnability remains the empirical question of MK-1.

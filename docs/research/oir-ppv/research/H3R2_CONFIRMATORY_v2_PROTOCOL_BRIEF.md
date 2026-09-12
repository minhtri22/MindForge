# H3R2_CONFIRMATORY_v2_PROTOCOL_BRIEF

Status: `AUTHORIZED_FOR_PROTOCOL_REVIEW`

Evidence access: `NOT_AUTHORIZED`

## Research question

> Given a fixed reconstructed H3R representation, does a properly controlled nonlinear readout recover significantly more task utility than the historical linear readout, beyond any improvement observed in the L0 control?

This brief defines protocol-review requirements only. It does not define or execute a final experiment.

## Conceptual comparison

- L0 + linear
- L0 + nonlinear
- L1 + linear
- L1 + nonlinear
- L2 + linear
- L2 + nonlinear
- L3 + linear
- L3 + nonlinear
- L4 + linear
- L4 + nonlinear

The final design remains subject to protocol review and preregistration.

## Claim boundary

Primary target: M6, decoder/readout dependence.

M7, nonlinear interaction failure, remains separate. Nonlinear readout improvement alone cannot confirm M7 and cannot prove that the representation is causally sufficient.

## Representation contract

The protocol must distinguish historical representation, reconstructed representation, and newly trained representation.

The primary confirmatory test must use a `FROZEN_RECONSTRUCTED_REPRESENTATION`. Encoder retraining is prohibited for the primary test after protocol freeze.

The reconstruction contract must identify at minimum:

- source;
- config;
- seed;
- model_state;
- dataset_identity;
- artifact;
- hash.

Where available it must also bind environment, preprocessing, runner, protocol, split identity, and artifact manifest. If the required historical model state cannot be reconstructed with the declared fidelity, protocol review must stop rather than substitute a newly trained model and call it historical.

## Readout-control requirement

The scientific comparison is candidate-specific recovery beyond L0 nonlinear uplift. The protocol must control readout capacity and selection by freezing:

- parameter budget;
- optimization budget;
- training data;
- validation data;
- search budget;
- seed budget;
- architecture search;
- hyperparameter search;
- early stopping;
- regularization.

L0 control is mandatory. The comparison must distinguish general nonlinear uplift from recovery specific to L1-L4.

## Required preregistration items

Before any execution can be authorized, the protocol review must freeze all of the following:

1. exact falsifiable hypothesis;
2. primary estimand;
3. RelativeRecovery formula and orientation;
4. clean-recovery margin;
5. reproducibility fraction, numerator/denominator and weighting;
6. noise non-inferiority margin;
7. validation-to-test tolerance;
8. L0 baseline-control rule;
9. confidence-interval/statistical procedure;
10. multiple-comparison handling and candidate-level/overall decision rule;
11. missing/invalid-cell policy;
12. sample-size/power rule;
13. nonlinear readout architecture;
14. equal-budget definition;
15. train/validation/test separation;
16. fresh identity policy;
17. representation reconstruction contract;
18. seed policy and historical-overlap rule;
19. stopping rule;
20. one-shot evidence-access and rerun rule;
21. provenance schema;
22. deterministic adjudication function mapping frozen metrics to a verdict without post-test human rule invention.

No verdict-relevant item may be left to post-test judgment.

## Future freeze gate

Protocol review may proceed to a future freeze proposal only after adversarial QA establishes that two independent implementations using the same frozen inputs and observations would reach the same scientific verdict. Any unresolved P0/P1 protocol ambiguity blocks execution authorization.

A future protocol freeze or successful experiment does not automatically open H4. H4 remains a separate owner frontier decision.

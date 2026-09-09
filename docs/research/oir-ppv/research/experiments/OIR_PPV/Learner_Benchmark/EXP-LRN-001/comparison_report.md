# EXP-LRN-001 Reference Learner Comparison

## Status

Full matrix execution complete: 100/100 cells; failures: 0.

This report compares reference learner families. It does not establish OIR-PPV or MindForge superiority.

## Fidelity

| ID | Learner | Fidelity | Deviation |
| --- | --- | --- | --- |
| L0 | PCA | faithful | Uses scikit-learn PCA with deterministic full SVD behavior. |
| L1 | Supervised MLP encoder | adapted | Compact full-batch classifier used as the nonlinear representation baseline. |
| L2 | Variational Autoencoder | adapted | Compact full-batch VAE; posterior mean is used for deterministic evaluation. |
| L3 | IRM-style encoder | surrogate | Risk-variance surrogate across explicit context domains; not canonical IRMv1. |
| L4 | Domain-Adversarial encoder | adapted | Compact full-batch DANN with task head, domain head, and gradient reversal. |

## Aggregate results

| Learner | ENV | Seeds | Accuracy | AUROC | Unseen | Gen. delta | Invariance | Context leaks | Nuisance leaks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L0 | ENV-1 | 5 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.8444 | 0 | 0 |
| L0 | ENV-2 | 5 | 0.7208 | 0.9167 | null | null | 0.8747 | 0 | 0 |
| L0 | ENV-3 | 5 | 0.9474 | 0.9966 | 0.5919 | -0.3476 | null | 4 | 2 |
| L0 | ENV-4 | 5 | 0.9489 | 0.9937 | 0.9533 | -0.0467 | 0.8054 | 0 | 1 |
| L1 | ENV-1 | 5 | 0.6658 | 0.8447 | 0.3247 | -0.3989 | 0.8099 | 5 | 1 |
| L1 | ENV-2 | 5 | 0.3360 | 0.6462 | null | null | 0.8247 | 4 | 1 |
| L1 | ENV-3 | 5 | 0.7395 | 0.9212 | 0.4242 | -0.3462 | 0.7823 | 5 | 2 |
| L1 | ENV-4 | 5 | 0.8889 | 0.9785 | 0.8756 | -0.1144 | 0.8069 | 2 | 3 |
| L2 | ENV-1 | 5 | 0.6657 | 0.8300 | 0.3118 | -0.3855 | 0.7906 | 5 | 2 |
| L2 | ENV-2 | 5 | 0.3665 | 0.6752 | null | null | 0.8016 | 4 | 3 |
| L2 | ENV-3 | 5 | 0.7619 | 0.9071 | 0.1763 | -0.5961 | 0.7785 | 5 | 2 |
| L2 | ENV-4 | 5 | 0.9167 | 0.9869 | 0.9156 | -0.0766 | 0.7626 | 2 | 5 |
| L3 | ENV-1 | 5 | 0.6595 | 0.8356 | 0.3247 | -0.3932 | 0.8104 | 5 | 1 |
| L3 | ENV-2 | 5 | 0.3703 | 0.6644 | null | null | 0.8244 | 4 | 0 |
| L3 | ENV-3 | 5 | 0.7428 | 0.9205 | 0.4415 | -0.3296 | 0.7848 | 5 | 2 |
| L3 | ENV-4 | 5 | 0.8867 | 0.9788 | 0.8778 | -0.1129 | 0.8069 | 2 | 3 |
| L4 | ENV-1 | 5 | 0.6760 | 0.8375 | 0.3247 | -0.3782 | 0.8177 | 3 | 1 |
| L4 | ENV-2 | 5 | 0.3267 | 0.6192 | null | null | 0.8275 | 4 | 1 |
| L4 | ENV-3 | 5 | 0.7750 | 0.9223 | 0.4415 | -0.3423 | 0.7919 | 5 | 2 |
| L4 | ENV-4 | 5 | 0.8833 | 0.9796 | 0.8822 | -0.1080 | 0.8061 | 2 | 4 |

## Failed cells

None.

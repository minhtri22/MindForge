# H3 Closure Report — EXP-H3-001

Status: `READY_FOR_QA_REVIEW`  
Authority: `DEVELOPER_CANDIDATE_ONLY`  
Global developer candidate: `NOT_SUPPORTED`

ENV-1, ENV-2 and ENV-4 provide task-preserving paired nuisance interventions. ENV-3 is retained as inapplicable for decisive H3 evidence because its existing `do(N)` recomputes `Y` and task labels.

| Learner | Pairs | mean Δ task degradation vs L0 | mean Δ leakage vs L0 | mean Δ predictive utility vs L0 | mean Δ do(N) invariance vs L0 | Degenerate | Candidate |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| L1 | 15/15 | 0.019717 | 0.025900 | -0.259663 | 0.073115 | True | NOT_SUPPORTED |
| L2 | 15/15 | 0.014343 | 0.094590 | -0.240252 | 0.062986 | True | NOT_SUPPORTED |
| L3 | 15/15 | 0.021214 | 0.025657 | -0.251078 | 0.072522 | True | NOT_SUPPORTED |
| L4 | 15/15 | 0.023407 | 0.025085 | -0.261193 | 0.072354 | True | NOT_SUPPORTED |

## Learner × environment summaries

| Learner | Environment | Complete seeds | mean |Delta_N| | mean Leak_N | mean predictive utility | mean do(N) invariance | ENV-4 shortcut score | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L0 | ENV-1 | 5/5 | 0.000000 | 0.195299 | 1.000000 | 0.984008 | null | 0 |
| L0 | ENV-2 | 5/5 | 0.037250 | 0.251396 | 0.720750 | 0.816548 | null | 0 |
| L0 | ENV-3 | 0/5 | null | null | null | null | null | 0 |
| L0 | ENV-4 | 5/5 | 0.051111 | 0.292402 | 0.948889 | 0.759504 | 0.243306 | 0 |
| L1 | ENV-1 | 5/5 | 0.034503 | 0.259174 | 0.665761 | 0.940580 | null | 0 |
| L1 | ENV-2 | 5/5 | 0.050417 | 0.252715 | 0.336000 | 0.902186 | null | 0 |
| L1 | ENV-3 | 0/5 | null | null | null | null | null | 0 |
| L1 | ENV-4 | 5/5 | 0.062593 | 0.304910 | 0.888889 | 0.936637 | 0.284760 | 0 |
| L2 | ENV-1 | 5/5 | 0.039094 | 0.315482 | 0.665716 | 0.932026 | null | 0 |
| L2 | ENV-2 | 5/5 | 0.049333 | 0.318425 | 0.366500 | 0.877700 | null | 0 |
| L2 | ENV-3 | 0/5 | null | null | null | null | null | 0 |
| L2 | ENV-4 | 5/5 | 0.042963 | 0.388960 | 0.916667 | 0.939291 | 0.356194 | 0 |
| L3 | ENV-1 | 5/5 | 0.035763 | 0.258266 | 0.659488 | 0.939960 | null | 0 |
| L3 | ENV-2 | 5/5 | 0.055500 | 0.250989 | 0.370250 | 0.900884 | null | 0 |
| L3 | ENV-3 | 0/5 | null | null | null | null | null | 0 |
| L3 | ENV-4 | 5/5 | 0.060741 | 0.306815 | 0.886667 | 0.936783 | 0.279078 | 0 |
| L4 | ENV-1 | 5/5 | 0.032389 | 0.254472 | 0.675977 | 0.938881 | null | 0 |
| L4 | ENV-2 | 5/5 | 0.061750 | 0.243077 | 0.326750 | 0.900692 | null | 0 |
| L4 | ENV-3 | 0/5 | null | null | null | null | null | 0 |
| L4 | ENV-4 | 5/5 | 0.064444 | 0.316802 | 0.883333 | 0.937550 | 0.300923 | 0 |

Matrix cells: complete=75, failed=0, inapplicable=25.

Claim boundary: tested L1-L4 configurations versus frozen L0/PCA under the supported task-preserving nuisance interventions and frozen seeds only. This report does not establish nuisance robustness in general and does not alter H1/H2 or start H4.

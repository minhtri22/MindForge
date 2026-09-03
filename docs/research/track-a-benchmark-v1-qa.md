# Track A Benchmark v1 — Final Automated QA

Status: **PASS / SEMANTIC R1 CORRECTION VALIDATED**

## Scope

This QA validates the final `r1-semantic-correction` materialization after the independent semantic review returned REVISE on the first materialization.

## Gate results

| Gate | Result |
|---|---|
| exactly 1,400 cases | PASS |
| exactly 200 per A1-A7 | PASS |
| split matrix 280/420/700 | PASS |
| language 840/350/210 | PASS |
| difficulty 560/490/350 | PASS |
| unique case IDs | PASS |
| same-family exact-input duplicates | PASS — zero |
| held-out counterfactual coverage | PASS — 280 cases / 140 pairs |
| counterfactual pair input difference | PASS — exactly one path |
| split-disjoint template IDs | PASS |
| calibration-vs-held-out exact utterance overlap | PASS — zero |
| development-vs-held-out exact utterance overlap | PASS — zero |
| wrapper/noise-stripped core surface overlap | PASS — zero |
| exact-name entity policy | PASS |
| A5 literal extraction policy | PASS |
| A7 route semantics | PASS |
| deterministic materializer | PASS |
| oracle scorer tests | PASS — 2 passed |
| semantic invariant audit | PASS — 0 CRITICAL / 0 MAJOR |
| Qwen/reference used as truth | NO |
| candidate model training | NO |
| PPF/model/kernel modification | NO |

## Diversity diagnostics

Final unique utterance counts per 200-case family:

```text
A1 123
A2 113
A3 110
A4 109
A5 107
A6 113
A7 118
```

Unique VI-EN utterances per 50-case family:

```text
A1 34
A2 35
A3 30
A4 30
A5 32
A6 35
A7 36
```

These counts are diagnostics, not a universal diversity threshold. The essential held-out leakage gates are independently PASS.

## Decision

```text
AUTOMATED QA: PASS
SEMANTIC RE-REVIEW: PASS
BENCHMARK V1: FINAL FROZEN
N3.R1-B: MAY PROCEED AS A SEPARATE LOCAL-HARDWARE TASK
N4: NOT AUTHORIZED
```

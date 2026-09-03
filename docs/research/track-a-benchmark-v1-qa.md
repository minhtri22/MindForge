# Track A Benchmark v1 — Automated QA

Status: **PASS / HUMAN SEMANTIC SPOT-REVIEW STILL REQUIRED**

## Scope

This QA checks materialization correctness, deterministic scoring, quotas, counterfactual structure, reproducibility, and obvious leakage/duplication properties. It does not claim human semantic acceptance of all 1,400 cases.

## Gate results

| Gate | Result |
|---|---|
| exactly 1,400 cases | PASS |
| exactly 200 per A1-A7 | PASS |
| split matrix 280/420/700 | PASS |
| language 840/350/210 | PASS |
| difficulty 560/490/350 | PASS |
| per-family language/difficulty/split quotas | PASS |
| unique case IDs | PASS |
| same-family exact-input duplicates | PASS — zero |
| held-out counterfactual minimum | PASS — 280 cases |
| counterfactual group structure | PASS — 140 pairs |
| pair language/difficulty held constant | PASS |
| pair input field-difference count | PASS — exactly one per pair |
| truth independent of candidate/reference output | PASS |
| deterministic materializer | PASS |
| canonical split reproduction | PASS |
| validator execution | PASS |
| oracle scorer test | PASS — 2 tests |
| N4 candidate training absent | PASS |
| PPF/model/kernel modification absent | PASS |

## Counterfactual structural audit

All 140 held-out pairs differ on exactly one input path. The declared change path is family-specific: A1 foreground reference; A2 personal contacts; A3 conversation language; A4 available actions; A5 last dictated text; A6 personal contacts; A7 available local capabilities.

## Adversarial coverage

Materialized records cover the frozen ambiguity, similar-entity, irrelevant-state, context/preference conflict, missing argument, unavailable tool, local/external trap, world-knowledge trap, stale fact, code-mix, noisy text, clarification, similar-tool, unsupported-action, and counterfactual tags.

## Known limitation

Rule/template QA cannot establish that Vietnamese phrasing and ambiguous cases are natural enough for a final benchmark. `review_status` therefore remains `automated_qa_pass_human_spot_review_pending`.

Human spot-review is a closure gate, not cosmetic review.

## Decision

```text
N3.1 AUTOMATED QA: PASS
BENCHMARK MATERIALIZATION: PASS
HUMAN SEMANTIC SPOT-REVIEW: REQUIRED
BENCHMARK FINAL FREEZE: PENDING
N4: BLOCKED
```

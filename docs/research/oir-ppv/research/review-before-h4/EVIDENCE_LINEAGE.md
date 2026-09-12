# Evidence Lineage

```text
H3R
  [historical, confirmatory adjudication]
  FALSIFIED_UNDER_TESTED_CONDITIONS
  |
  v
Q-H3R.1
  [historical, exploratory diagnostic]
  PARTIAL_MECHANISM_DIAGNOSIS
  |  M6 ~= M7 candidate support only
  v
H3R2
  [prospective intent, invalid]
  INVALID_PROTOCOL_INPUT
  |
  v
H3R reconstruction
  [reconstructed historical representation]
  RECONSTRUCTION_CONFIRMED
  |  100/100 SHA-256 matches, mismatch_count=0
  |  reconstruction != historical proof
  v
H3R2-R
  [prospective execution, descriptive scientific evidence]
  EXECUTION_INTEGRITY_PASS
  PROTOCOL_DEVIATION
  |  confirmatory adjudication = NOT_AVAILABLE
  v
REVIEW_BEFORE_H4
  [independent QA review]
  H4 scientific gate: ELIGIBLE
  H4 operational state: NOT_OPENED / DEFERRED_BY_OWNER
```

Evidence-class boundaries:

- `historical`: consumed adjudication/evidence from the original lineage.
- `reconstructed`: replay fidelity for the historical representation path; not a new scientific confirmation.
- `prospective`: execution performed after protocol/identity freeze with fresh seeds.
- `descriptive`: numerical observations that may be reported without a confirmatory decision claim.
- `confirmatory`: requires a complete pre-evidence decision rule; unavailable for H3R2-R.
- `invalid`: H3R2's scientific input condition was invalid.
- `deferred`: H4 remains unopened by owner decision.

The formal H4 branch tests counterfactual validity separately from H3R2 mechanism diagnosis. The identified historical gate requires H3 closure before H4 protocol/query freeze; it does not authorize treating descriptive H3R2-R evidence as proof of H4.

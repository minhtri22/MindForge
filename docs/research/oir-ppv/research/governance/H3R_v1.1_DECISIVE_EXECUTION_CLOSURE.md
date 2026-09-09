# H3R v1.1 DECISIVE EXECUTION CLOSURE

Date: 2026-09-09
Protocol: `OIR-PPV-H3R v1.1`
Experiment: `EXP-H3R-002`

## Closure

- Status: `CLOSED_WITH_LIMITS / NO_RERUN`.
- Scientific verdict: `FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Final QA gate: `PASS_WITH_LIMITS`.
- Scientific access count: exactly `1` decisive event.
- Matrix: `20/20` valid cells, `6039/6039` frozen test rows.
- Decisive evidence commit: `f15fa5784bf0c59b48ad4513abca4a105d6f31b9`.
- Frozen protocol SHA256: `5cdecfe758b9908f0f2199b6e7cd5632e9636b887e141d265fdb9265c107334d`.
- Frozen test-manifest SHA256: `371799bb474f2f425db7acacf63cba3de7ca4876f61cbfa5a88549363d97255d`.

All four candidates L1-L4 are falsified under the frozen decision rule. Directional mean noise improvements do not meet the required adjusted support margin, and every candidate violates the frozen clean-utility margin relative to L0/PCA.

`governance/H3R_v1.1_DECISIVE_EVIDENCE_ERRATUM_001.md` records one P2 provenance-only mismatch in the redundant per-cell observation-hash field. Correct frozen identity was enforced before metric access; decisive evidence is preserved without repair.

No further H3R v1.1 scientific execution is permitted. H4 remains unopened and deferred by owner decision.

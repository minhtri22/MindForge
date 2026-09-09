# OIR-PPV Research Status v1.0

| Item | Status |
| --- | --- |
| Ontology v1.0 | `PRINCIPLE-LEVEL LOCKED` |
| Formal Spec v1.0 | `FINAL / SPECIFICATION_CLOSED_AFTER_FIX_01` |
| H1 | `HISTORICAL / PROTOCOL-BOUND / CLOSED_WITH_LIMITS` |
| H2 | `FALSIFIED_UNDER_TESTED_CONDITIONS / PROTOCOL-BOUND / CLOSED` |
| H3 | `HISTORICAL / CLOSED_WITH_LIMITS / NOT_SUPPORTED / PRESERVED` |
| H3R | `v1.0 CLOSED PROTOCOL_DEVIATION / NO SCIENTIFIC VERDICT / NO RERUN; v1.1 CLOSED_WITH_LIMITS / FALSIFIED_UNDER_TESTED_CONDITIONS / NO RERUN` |
| H4 | `NOT YET INSTANTIATED UNDER FORMAL v1.0 / NOT OPENED` |
| H5 | `NOT YET INSTANTIATED UNDER FORMAL v1.0` |
| H6 | `NOT YET INSTANTIATED UNDER FORMAL v1.0` |
| historical v0.13.10 | `hypothesis/design checkpoint; not verified historical implementation evidence` |

## Current frontier

H3 is closed by independent QA evidence. H3R v1.0 consumed its one-shot test access and is preserved as `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT`; rerun is forbidden. H3R v1.1 consumed exactly one separately owner-authorized decisive access and completed `EXP-H3R-002` with 20/20 valid cells and 6039/6039 frozen test rows. G3 execution integrity is `PASS_WITH_LIMITS`, G4 statistical QA is `PASS`, G6 adversarial review is `PASS_WITH_LIMITS`, and final scientific classification is `FALSIFIED_UNDER_TESTED_CONDITIONS`.

H3R v1.1 is closed `CLOSED_WITH_LIMITS / NO_RERUN`. The retained P2 debt is a redundant post-check observation-hash metadata mismatch documented in `H3R_v1.1_DECISIVE_EVIDENCE_ERRATUM_001.md`; correct frozen identity was enforced before metric access. The next frontier requires an explicit owner decision. H4 remains unopened by owner decision.

## H3 metadata debt retained

The accepted `correction_v3/h3_summary_v3.json` embeds `"version": 2`. This is retained as a metadata erratum because correcting the frozen file would alter accepted evidence bytes without changing science.

# OIR-PPV Research Status v1.0

| Item | Status |
| --- | --- |
| Ontology v1.0 | `PRINCIPLE-LEVEL LOCKED` |
| Formal Spec v1.0 | `FINAL / SPECIFICATION_CLOSED_AFTER_FIX_01` |
| H1 | `HISTORICAL / PROTOCOL-BOUND / CLOSED_WITH_LIMITS` |
| H2 | `FALSIFIED_UNDER_TESTED_CONDITIONS / PROTOCOL-BOUND / CLOSED` |
| H3 | `HISTORICAL / CLOSED_WITH_LIMITS / NOT_SUPPORTED / PRESERVED` |
| H3R | `v1.0 CLOSED PROTOCOL_DEVIATION / NO SCIENTIFIC VERDICT; v1.1 FROZEN / PUBLISHED / QA_PASS_WITH_LIMITS / NOT EXECUTED / TEST LOCKED` |
| H4 | `NOT YET INSTANTIATED UNDER FORMAL v1.0 / NOT OPENED` |
| H5 | `NOT YET INSTANTIATED UNDER FORMAL v1.0` |
| H6 | `NOT YET INSTANTIATED UNDER FORMAL v1.0` |
| historical v0.13.10 | `hypothesis/design checkpoint; not verified historical implementation evidence` |

## Current frontier

H3 is closed by independent QA evidence. H3R v1.0 consumed its one-shot test access and is preserved as `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT`; rerun is forbidden. H3R v1.1 is the fresh successor, frozen with a new test lock, independently QA-reviewed `PASS_WITH_LIMITS` with `P0=0/P1=0`, and published at commit `723dac1f291206a1daa5d7e45ffa21ffe7f3a312`. The active frontier is a separate owner authorization for H3R v1.1 decisive execution. H4 remains unopened by owner decision.

H3R v1.1 decisive execution is not authorized. Freeze QA and publication/provenance are complete with P0=0/P1=0, remote publication verified, and the v1.1 scientific access count remains 0. A separate later owner authorization is still required to unlock decisive execution.

## H3 metadata debt retained

The accepted `correction_v3/h3_summary_v3.json` embeds `"version": 2`. This is retained as a metadata erratum because correcting the frozen file would alter accepted evidence bytes without changing science.

# OIR-PPV Claim Registry v1.0

Allowed `formal_v1_reinterpretation_status` values:

`UNCHANGED`, `NARROWED`, `REQUIRES_REEVALUATION`, `NOT_APPLICABLE`.

| Claim | Historical / current classification | Protocol binding | formal_v1_reinterpretation_status | Boundary |
| --- | --- | --- | --- | --- |
| H1 Compression | `CLOSED_WITH_LIMITS / SUPPORTED_WITH_LIMITS` | Frozen H1 protocol; exact-row MEM comparator; ENV-1..4; seeds 42/123/456/789/1011 | `UNCHANGED` | Does not establish superiority to RAW or memory architectures in general. |
| H2 Transfer | `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS` | Frozen H2 paired OOD protocol; L1-L4 vs L0/PCA; ENV-1/3/4 x 5 seeds | `UNCHANGED` | Does not falsify invariant learning in general, canonical methods, MindForge, or untested environments. |
| H3 Nuisance Robustness | `CLOSED_WITH_LIMITS / NOT_SUPPORTED` | Historical pre-Formal-v1 H3; correction-v3 accepted with metadata limits | `NARROWED` | Selected targets only: background_noise/ENV-1, occlusion/ENV-2, spurious_feature/ENV-4; ENV-3 inapplicable. Historical evidence remains preserved. |
| H3R Revised Robustness v1.0 | `CLOSED / PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT` | `OIR-PPV-H3R v1.0`; consumed one-shot test access | `NOT_APPLICABLE` | Implementation cast mixed ENV-1 observations to float before completing the first cell. Evidence is preserved; rerun is forbidden. |
| H3R Revised Robustness v1.1 | `PROTOCOL FROZEN / PUBLISHED / QA_PASS_WITH_LIMITS / NOT_EXECUTED / TEST_LOCKED` | `OIR-PPV-H3R v1.1`; observation-channel noise; L1-L4 vs L0/PCA; ENV-1..4; fresh frozen test lock | `NOT_APPLICABLE` | No scientific verdict yet. Freeze QA has P0=0/P1=0; publication commit is `723dac1f291206a1daa5d7e45ffa21ffe7f3a312`; scientific test access count remains 0. |

## H3R identity

```text
relation_to_historical_h3: REVISED_SUCCESSOR
v1.0_execution_status: CLOSED_PROTOCOL_DEVIATION_NO_SCIENTIFIC_VERDICT
current_protocol_version: v1.1
protocol_semantics: FORMAL_SPEC_v1.0
execution_status: NOT_EXECUTED
evidence_status: NONE_YET
freeze_status: FROZEN_PUBLISHED_QA_PASS_WITH_LIMITS
supersedes_protocol_semantics: true
supersedes_historical_evidence: false
```

`REQUIRES_REEVALUATION` is not assigned to H1-H3 merely because Formal Spec v1.0 now exists. A future re-evaluation must cite a concrete incompatibility that materially affects the historical claim.

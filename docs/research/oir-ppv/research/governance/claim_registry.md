# OIR-PPV Claim Registry v1.0

Allowed `formal_v1_reinterpretation_status` values:

`UNCHANGED`, `NARROWED`, `REQUIRES_REEVALUATION`, `NOT_APPLICABLE`.

| Claim | Historical / current classification | Protocol binding | formal_v1_reinterpretation_status | Boundary |
| --- | --- | --- | --- | --- |
| H1 Compression | `CLOSED_WITH_LIMITS / SUPPORTED_WITH_LIMITS` | Frozen H1 protocol; exact-row MEM comparator; ENV-1..4; seeds 42/123/456/789/1011 | `UNCHANGED` | Does not establish superiority to RAW or memory architectures in general. |
| H2 Transfer | `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS` | Frozen H2 paired OOD protocol; L1-L4 vs L0/PCA; ENV-1/3/4 x 5 seeds | `UNCHANGED` | Does not falsify invariant learning in general, canonical methods, MindForge, or untested environments. |
| H3 Nuisance Robustness | `CLOSED_WITH_LIMITS / NOT_SUPPORTED` | Historical pre-Formal-v1 H3; correction-v3 accepted with metadata limits | `NARROWED` | Selected targets only: background_noise/ENV-1, occlusion/ENV-2, spurious_feature/ENV-4; ENV-3 inapplicable. Historical evidence remains preserved. |
| H3R Revised Robustness | `PROTOCOL v1.0 FROZEN / NOT_EXECUTED` | `OIR-PPV-H3R v1.0`; observation-channel noise; L1-L4 vs L0/PCA; ENV-1..4; new frozen seeds | `NOT_APPLICABLE` | Protocol frozen only. No H3R scientific evidence yet; test remains locked. |

## H3R identity

```text
relation_to_historical_h3: REVISED_SUCCESSOR
protocol_semantics: FORMAL_SPEC_v1.0
execution_status: NOT_EXECUTED
evidence_status: NONE_YET
freeze_status: FROZEN
supersedes_protocol_semantics: true
supersedes_historical_evidence: false
```

`REQUIRES_REEVALUATION` is not assigned to H1-H3 merely because Formal Spec v1.0 now exists. A future re-evaluation must cite a concrete incompatibility that materially affects the historical claim.

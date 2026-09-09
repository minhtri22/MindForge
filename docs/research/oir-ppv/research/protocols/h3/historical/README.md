# Historical H3 Protocol Record

## Identity

```text
hypothesis_id: H3
status: HISTORICAL_PROTOCOL
evidence: PRESERVED
protocol_semantics: PRE-FORMAL-v1
verdict: CLOSED_WITH_LIMITS / NOT_SUPPORTED
superseded_by_protocol_semantics: H3R
superseded_evidence: false
```

Historical H3 remains a valid protocol-bound result. Its semantics and evidence are preserved exactly; H3R is a revised successor protocol and does not replace the historical result.

## Frozen sources and provenance

- branch recorded by independent QA: `oir-ppv-research`
- source HEAD recorded by independent QA: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- frozen protocol: `benchmark/M3_PROTOCOL.md`
- protocol identity: `M3-Protocol-v1.0`
- protocol SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- reference benchmark: `EXP-LRN-001` (`ACCEPTED_WITH_LIMITS`)
- EXP-LRN-001 manifest SHA256: `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`
- accepted developer handoff: `HANDOFF_011_H3_v3.md`
- handoff SHA256: `d837112092ddafe0393772133b118ab1888d63de555725330966ab85ef59fea9`
- independent QA: `QA_REPORT_HANDOFF_011_H3_v3.md`
- accepted closure report: `experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v3/H3_CLOSURE_REPORT_v3.md`
- closure report SHA256: `4e717c6863f0f06cfb0496b804828492b8bbb4402ce7f45cac6c3ea323ecc497`
- correction-v3 execution manifest SHA256: `666f007c18df39fd27b6d9ffe42d691b3db18281aee9a053ff7c92b97caa969a`
- correction-v3 source manifest SHA256: `af52a6cebdf18e7032fb9ca5fa0255bbb400cc2a46af8069bf0ae8ea134142d4`
- v1 preservation manifest SHA256: `f7aa648559e66ec2d884406b960aff511d73af042af9e7c49d6a59402f8ddfeb`

## Tested scope

- learners: `L1 MLP`, `L2 VAE`, `L3 IRM-style surrogate`, `L4 DANN`
- primary frozen baseline: `L0/PCA`
- environments: `ENV-1`, `ENV-2`, `ENV-3`, `ENV-4`
- seeds: `42, 123, 456, 789, 1011`
- full matrix: `5 learners x 4 environments x 5 seeds = 100 cells`
- eligible candidate-vs-L0 pairs: `60/60`
- task-preserving intervention records: `225/225` valid over eligible cells
- ENV-3: retained as `INAPPLICABLE` because its selected `do(N)` changes `Y` and task labels

Primary H3 criteria were paired nuisance task degradation, nuisance leakage, and retained factual predictive utility. Raw latent shift was retained only as `SCALE_SENSITIVE_DIAGNOSTIC_ONLY`.

## Frozen scientific conclusion

`CLOSED_WITH_LIMITS / NOT_SUPPORTED`

Defensible claim boundary:

> Under selected targets `background_noise` in ENV-1, `occlusion` in ENV-2, and `spurious_feature` in ENV-4, across seeds 42, 123, 456, 789, and 1011, the tested L1-L4 adapted/surrogate configurations do not improve the frozen paired H3 criteria over L0/PCA. ENV-3 is inapplicable because its `do(N)` changes `Y` and task labels.

This result does not generalize to untested nuisance targets, canonical external learner implementations, external environments, MindForge, or nuisance robustness in general.

## Preservation and reinterpretation rule

Historical H3 may be reinterpreted only with an explicit claim boundary. Reinterpretation may narrow a claim; it may not silently change the historical estimand, thresholds, targets, seeds, baseline, learner identities, evidence, or verdict.

## Metadata erratum

`experiments/OIR_PPV/H3_Closure/EXP-H3-001/correction_v3/h3_summary_v3.json` is the accepted correction-v3 summary but contains the embedded field `"version": 2`. Its path, filename, source/runtime/execution hashes, and scientific encoding identify correction v3 correctly. This is a P2 metadata erratum and the frozen summary must not be overwritten solely to change that field.


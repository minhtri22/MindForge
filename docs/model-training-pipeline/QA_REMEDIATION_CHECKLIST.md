# QA Remediation Checklist — Evidence-Governed Model Training Pipeline

> Branch: `docs/evidence-model-training-pipeline`
>
> Baseline reviewed commit: `48c6cb3adca69d44142ad231e555f2cf77d652b1`
>
> Rule: this file is created **before remediation**. Every finding starts as `TODO`. During remediation, each item must be updated with a concrete repository ref proving the fix. No finding may be marked `DONE` from prose alone.

## Severity legend

- `BLOCKER`: must be resolved before implementation lock / M1-M2.
- `HIGH`: must be resolved before confirmatory/release execution.
- `MEDIUM/LOW`: may remain only with explicit documented rationale.

## BLOCKER findings

| ID | Status | Finding | Required remediation | Proof ref |
|---|---|---|---|---|
| B-01 | TODO | Config dialects conflict (`data` vs `datasets`, GGUF keys, reasoning keys). | One canonical ExperimentConfig schema; all examples conform. | — |
| B-02 | TODO | AC-01 example contains placeholders and cannot PASS. | Pin a real tiny reference model/revision and real fixtures. | — |
| B-03 | TODO | Missing machine schemas for experiment, execution contract, data manifest, evaluation. | Add JSON Schemas and validation rules. | — |
| B-04 | TODO | One-level run state machine cannot represent CPT → SFT → reasoning SFT phases. | Define RunState + PhaseState, parent artifacts, terminal states. | — |
| B-05 | TODO | Checkpoint selection is not phase-scoped. | Bind selection rule to phase_id, metric, direction, tie-breaker. | — |
| B-06 | TODO | Checkpoint schema is weaker than resume/provenance prose. | Schema optimizer/scheduler/RNG/sampler/token-position state. | — |
| B-07 | TODO | Packing/shuffle/sampling semantics undefined. | Freeze TokenStreamContract including BOS/EOS, packing, truncation, sampling. | — |
| B-08 | TODO | Streaming/multi-worker resume token position undefined. | Persist shard/document/sample/sequence/shuffle-buffer/worker RNG state. | — |
| B-09 | TODO | Required gate matrix does not exist. | Add run-class × gate matrix for smoke/development/calibration/confirmatory/release. | — |
| B-10 | TODO | Deterministic parity conflicts with Modelfile temperature=0.7/top_p=0.9. | Add frozen inference-generation contract and derive runtime configs from it. | — |
| B-11 | TODO | Reasoning response schema conflicts with reasoning-off/hidden modes. | Define visible/hidden/off/unsupported semantics and nullable/omitted fields. | — |
| B-12 | TODO | Training reasoning serialization is conflated with runtime reasoning extraction. | Separate model serializer, runtime parser, normalized API. | — |
| B-13 | TODO | Non-empty reasoning is required by AC but schema allows empty string. | Enforce minLength / parser status / mode constraints. | — |
| B-14 | TODO | Evidence ZIP/checksum design can become circular. | Define payload manifest, ZIP creation order, external ZIP checksum. | — |
| B-15 | TODO | Code evaluation lacks execution sandbox contract. | Define no-network sandbox, quotas, timeout, temp/read-only FS policy. | — |
| B-16 | TODO | No workspace/run locking or atomic state-write contract. | Define exclusive locks, atomic writes, fsync/rename and crash recovery. | — |
| B-17 | TODO | Baseline/comparator contract is missing. | Add smoke reference, exact parent baseline, matched control, optional external anchor; define metric comparator fields. | — |

## HIGH findings

| ID | Status | Finding | Required remediation | Proof ref |
|---|---|---|---|---|
| H-01 | TODO | Wikipedia snapshot identity is underspecified. | Pin edition/language/dump type/URI/checksum/tooling. | — |
| H-02 | TODO | Public-code reference corpus is unspecified. | Choose/pin at least one concrete reference path or fixture manifest. | — |
| H-03 | TODO | Code-license granularity is too weak. | Define release policy for repo/file license provenance and unknown-license behavior. | — |
| H-04 | TODO | No secret/credential scanning for code corpora. | Add secret scanner/quarantine/report contract. | — |
| H-05 | TODO | No PII handling policy for public text. | Add PII scan/filter/quarantine/report policy. | — |
| H-06 | TODO | Near-dedup algorithm is not frozen. | Pin algorithm, normalization, signature parameters and threshold. | — |
| H-07 | TODO | Contamination detector parameters are undefined. | Pin normalization/window/hash/match threshold and action policy. | — |
| H-08 | TODO | Freshness protection guards seeds but not fresh data/splits. | Add freshness registry for seeds, split IDs and fixture IDs. | — |
| H-09 | TODO | Regression baseline is undefined. | Every metric gate must name baseline/comparator. | — |
| H-10 | TODO | Catastrophic-forgetting suite is undefined. | Define protected-capability suite and aggregation. | — |
| H-11 | TODO | Matched comparator is not first-class in config. | Add comparator/control objects and matched budget/seed rules. | — |
| H-12 | TODO | Optimizer/scheduler reset vs carry across phases is undefined. | Add explicit phase transition policy. | — |
| H-13 | TODO | epochs/max_steps/max_tokens precedence undefined. | Define one stop policy and precedence/validation. | — |
| H-14 | TODO | Warmup unit undefined. | Require unit = steps/tokens/ratio with resolved count. | — |
| H-15 | TODO | `precision: auto` is not reproducible after lock. | Resolve auto before lock and persist exact dtype policy. | — |
| H-16 | TODO | Device/backend resolution not frozen. | Persist backend/device class/kernel determinism policy. | — |
| H-17 | TODO | LoRA/merged/canonical artifact semantics unclear. | Define adapter artifact, merged artifact and promotion/export rules. | — |
| H-18 | TODO | Split GGUF artifacts are not modeled. | Add shard-set manifest and Ollama wildcard packaging support. | — |
| H-19 | TODO | llama.cpp compatibility inspection is too open-ended. | Define pinned converter capability inspection evidence. | — |
| H-20 | TODO | “High-fidelity GGUF” dtype semantics conflict. | Define preserve-source/explicit F16/BF16 policy. | — |
| H-21 | TODO | Runtime adapter may mutate host by installing tools. | Locate-only by default; installation requires explicit action/policy. | — |
| H-22 | TODO | Ephemeral Ollama model collision/cleanup semantics undefined. | Namespaced ephemeral names; ownership marker; safe cleanup. | — |
| H-23 | TODO | Disk threshold/space estimation undefined. | Add preflight estimator and minimum headroom formula/policy. | — |
| H-24 | TODO | Checkpoint atomic-write protocol undefined. | Temp-write → verify → fsync → atomic rename + completeness marker. | — |
| H-25 | TODO | Hash-chained lineage lacks external seal. | Seal final head hash in evidence manifest/commit/signature. | — |
| H-26 | TODO | LLM-judge reproducibility contract absent. | Pin judge model/revision/prompt/generation and retain raw response. | — |
| H-27 | TODO | Reasoning non-empty metric is too weak. | Add task/verifier-aware rationale checks; keep non-empty as format gate only. | — |
| H-28 | TODO | Instruction replay ratio/budget after CPT undefined. | Freeze replay source, budget, mixture and stop rule. | — |
| H-29 | TODO | AC-04 “minimal equivalent” is a loophole. | Remove loophole or precisely define permitted equivalent evidence. | — |
| H-30 | TODO | Unsupported-architecture fixture can become supported upstream. | Use deterministic synthetic unsupported fixture/adapter. | — |
| H-31 | TODO | Local agent has no path ownership/do-not-touch contract inside MindForge. | Restrict writes to pipeline-owned paths unless explicitly approved. | — |
| H-32 | TODO | Software-development lineage and training-run lineage are conflated. | Define two distinct lineages and cross-reference rule. | — |

## Completion criteria

Remediation is complete only when:

1. all BLOCKER rows are `DONE` with concrete refs;
2. all HIGH rows are `DONE` or explicitly `DEFERRED` with rationale and non-release restriction;
3. examples validate against schemas;
4. one canonical config vocabulary remains;
5. run/phase state transitions are machine-defined;
6. baseline/comparator semantics are machine-defined;
7. a second QA pass reports no unresolved BLOCKER;
8. `SHA256SUMS` is regenerated after the final documentation state.

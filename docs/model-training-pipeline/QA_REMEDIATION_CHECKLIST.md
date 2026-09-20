# QA Remediation Checklist — Evidence-Governed Model Training Pipeline

> Branch: docs/evidence-model-training-pipeline
>
> Baseline reviewed commit: 48c6cb3adca69d44142ad231e555f2cf77d652b1
>
> Pre-remediation checklist commit: c8c5f6196127d04da08f40030017c667ada95b66
>
> Main remediation commit: 3048a781bad312d4be0abde112fae1ad2bc7913f
>
> Concrete-fixture completion commit: cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5

## BLOCKER findings

| ID | Status | Finding | Remediation | Proof ref |
|---|---|---|---|---|
| B-01 | DONE | Config dialects conflict | Canonical schema + examples | [schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/experiment_config.schema.json) [examples](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/examples/end_to_end_small.yaml) |
| B-02 | DONE | AC-01 example had placeholders | Pinned real smoke model + concrete fixtures | [example](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/examples/end_to_end_small.yaml) [fixtures](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/tests/fixtures/data/reasoning_mini.jsonl) |
| B-03 | DONE | Missing machine schemas | Experiment/execution/data/evaluation schemas added | [schemas](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/execution_contract.schema.json) |
| B-04 | DONE | One-level state machine | RunState + PhaseState defined | [state contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) [run schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/run_manifest.schema.json) |
| B-05 | DONE | Checkpoint selection not phase-scoped | phase_id/metric/direction/tie-breaker required | [config schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/experiment_config.schema.json) |
| B-06 | DONE | Checkpoint schema weaker than resume prose | Recoverable state schema expanded | [checkpoint schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/checkpoint_manifest.schema.json) |
| B-07 | DONE | Packing/shuffle/sampling undefined | TokenStreamContract defined | [data contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) |
| B-08 | DONE | Streaming/multi-worker resume undefined | ResumeCursor defined | [resume contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) |
| B-09 | DONE | Required gate matrix absent | Run-class gate matrix added | [gate matrix](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| B-10 | DONE | Parity vs Modelfile sampling conflict | Frozen inference contract + generated Modelfile parameters | [inference contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) [template](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/templates/Modelfile.template) |
| B-11 | DONE | Reasoning off/hidden schema conflict | Mode semantics + conditional schema | [reasoning contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md) [schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/reasoning_response.schema.json) |
| B-12 | DONE | Training serializer conflated with runtime parser | Three-layer model defined | [reasoning contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md) |
| B-13 | DONE | Empty reasoning could schema-PASS | Visible mode requires minLength 1 | [reasoning schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/reasoning_response.schema.json) |
| B-14 | DONE | Circular evidence checksum risk | Payload -> ZIP -> external checksum order defined | [evidence contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md) |
| B-15 | DONE | Code-eval sandbox absent | No-network/quotas/temp FS sandbox contract | [sandbox contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md) |
| B-16 | DONE | No run locking/atomic state contract | Exclusive lock + atomic writes/checkpoint protocol | [concurrency contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md) |
| B-17 | DONE | Baseline/comparator contract absent | Smoke/parent/matched-control/external-anchor defined | [baseline contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/15_BASELINE_COMPARATOR_CONTRACT.md) |

## HIGH findings

| ID | Status | Finding | Proof ref |
|---|---|---|---|
| H-01 | DONE | Wikipedia identity underspecified | [data contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) [pinned example](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/examples/train_wikipedia_cpt.yaml) |
| H-02 | DONE | Public code corpus unspecified | [CodeSearchNet example](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/examples/train_code_cpt.yaml) |
| H-03 | DONE | Code license granularity weak | [security contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md) [code example](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/examples/train_code_cpt.yaml) |
| H-04 | DONE | No code secret scan | [security contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md) |
| H-05 | DONE | No PII policy | [security contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md) |
| H-06 | DONE | Near-dedup algorithm not frozen | [data contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) |
| H-07 | DONE | Contamination params undefined | [data contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) |
| H-08 | DONE | Freshness only guarded seeds | [freshness registry](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md) |
| H-09 | DONE | Regression baseline undefined | [baseline contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/15_BASELINE_COMPARATOR_CONTRACT.md) [evaluation schema](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/schemas/evaluation_contract.schema.json) |
| H-10 | DONE | Catastrophic-forgetting suite undefined | [protected suite](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/15_BASELINE_COMPARATOR_CONTRACT.md) |
| H-11 | DONE | Matched comparator not first-class | [baseline contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/15_BASELINE_COMPARATOR_CONTRACT.md) |
| H-12 | DONE | Optimizer/scheduler phase carry undefined | [phase transition](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-13 | DONE | Stop-rule precedence undefined | [stop rule](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-14 | DONE | Warmup unit undefined | [warmup contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-15 | DONE | precision:auto not lock-safe | [config lifecycle](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-16 | DONE | Device/backend not frozen | [resource resolution](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-17 | DONE | LoRA/merged artifact semantics unclear | [artifact semantics](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/16_CANONICAL_CONFIG_STATE_MACHINE.md) |
| H-18 | DONE | Split GGUF not modeled | [GGUF shard contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| H-19 | DONE | llama.cpp inspection too open | [capability evidence](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| H-20 | DONE | High-fidelity dtype conflict | [dtype policy](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| H-21 | DONE | Runtime adapter could mutate host | [security contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md) |
| H-22 | DONE | Ollama ephemeral collision/cleanup undefined | [Ollama safety](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| H-23 | DONE | Disk threshold undefined | [resource preflight](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/19_GATE_MATRIX_INFERENCE_CONTRACT.md) |
| H-24 | DONE | Checkpoint atomic writes undefined | [atomic checkpoint protocol](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md) |
| H-25 | DONE | Lineage lacked external seal | [external seal](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md) |
| H-26 | DONE | LLM judge contract absent | [judge contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md) |
| H-27 | DONE | Reasoning non-empty too weak | [reasoning metrics](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/18_REASONING_CAPABILITY_RUNTIME_CONTRACT.md) |
| H-28 | DONE | Instruction replay budget undefined | [training phase contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/04_TRAINING_PIPELINE.md) |
| H-29 | DONE | AC-04 minimal-equivalent loophole | [AC-04](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/11_ACCEPTANCE_CRITERIA.md) |
| H-30 | DONE | Unsupported arch fixture unstable | [test plan](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/10_TEST_PLAN.md) [fixture](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/tests/fixtures/model/unsupported_config.json) |
| H-31 | DONE | Agent path ownership absent | [agent prompt](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/AGENT_MASTER_PROMPT.md) |
| H-32 | DONE | Development/run lineages conflated | [lineage contract](https://github.com/minhtri22/MindForge/blob/cd2b13b7c7467bd6b6e8253a5b2f827f94a0bbe5/docs/model-training-pipeline/21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md) |

## Completion criteria

- All 17 BLOCKER findings have implementation-readable proof refs.
- All 32 HIGH findings have proof refs.
- QA round 2 must independently verify these claims; DONE here is remediation status, not self-certifying final QA.
- SHA256SUMS must be regenerated after QA round 2 and any QA-driven patch.

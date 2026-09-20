# 19 — Gate Matrix & Inference Contract

## 1. Run-class gate matrix

A gate is either REQUIRED, OPTIONAL, or FORBIDDEN for each run class.

| Gate | smoke | development | calibration | confirmatory | release |
|---|---|---|---|---|---|
| G0 Environment | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| G1 Data integrity | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| G2 Model/runtime compatibility | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| G3 Zero-training preflight | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| G4 Training health | REQUIRED when training | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| G5 Quality | FORMAT/SMOKE | OPTIONAL/DEV | REQUIRED | REQUIRED | REQUIRED |
| G6 Export | REQUIRED for E2E smoke | OPTIONAL | OPTIONAL | REQUIRED if export claim | REQUIRED |
| G7 llama.cpp runtime | REQUIRED for E2E smoke | OPTIONAL | OPTIONAL | REQUIRED if target | REQUIRED |
| G8 Ollama runtime | REQUIRED for E2E smoke | OPTIONAL | OPTIONAL | REQUIRED if target | REQUIRED |
| G9 Reproducibility QA | MICRO-REPLAY | OPTIONAL | REQUIRED for lock qualification | REQUIRED | REQUIRED |
| G10 Promotion | FORBIDDEN | FORBIDDEN | FORBIDDEN | OPTIONAL artifact qualification | REQUIRED |

Fresh seed/split/fixture access is FORBIDDEN in smoke/development/calibration. Confirmatory/release may access only resources enumerated in the frozen execution contract.

## 2. Gate result schema semantics

Every gate emits:

```json
{
  "gate_id":"G5",
  "status":"PASS|FAIL|INVALID|SKIPPED",
  "required":true,
  "contract_hash":"...",
  "inputs":["artifact/hash"],
  "metrics":[],
  "reasons":[],
  "evidence_refs":[]
}
```

`SKIPPED` on a REQUIRED gate is not PASS.

## 3. Evaluation metric contract

Every metric used by adjudication must specify:

- metric_id/version;
- target artifact;
- fixture set id/hash;
- baseline/comparator id;
- comparison type/operator/threshold;
- aggregation unit/method;
- missing-data policy;
- direction;
- required flag.

No free-text metric may directly drive PASS/FAIL.

## 4. Catastrophic-forgetting gate

Protected capability metrics are evaluated at:
- parent baseline;
- after every training phase;
- final artifact.

If a phase breaches threshold, the phase is `PHASE_FAIL`. A later phase may recover final capability but must not rewrite that historical verdict; report both failure and recovery.

## 5. InferenceGenerationContract

Runtime parity must use one frozen generation contract:

```yaml
inference:
  prompt_fixture_set: tests/fixtures/eval_v1
  max_new_tokens: 256
  temperature: 0.0
  top_p: 1.0
  top_k: 0
  seed: 42
  stop_policy: model_template
  context_length: 2048
  stream: false
```

Runtime adapters translate this contract into backend-specific arguments. If a backend cannot represent a field exactly, compatibility report records deviation and parity adjudicator decides according to pre-frozen tolerance.

Modelfile generation must not silently introduce temperature/top_p defaults that differ from this contract.

## 6. Runtime parity

Same prompt fixture + same normalized generation semantics are run on:

1. HF canonical;
2. high-fidelity GGUF in llama.cpp;
3. each required quantized GGUF in llama.cpp;
4. Ollama packaged target.

Compare task metrics and format/capability behavior, not exact text.

## 7. High-fidelity GGUF

Execution contract selects exactly one policy:

- `preserve_source`: converter chooses supported dtype preserving source fidelity;
- `f16`;
- `bf16`.

The resolved converter output type is recorded. The phrase “high-fidelity GGUF” never implies a fixed dtype by itself.

Quantization starts only after high-fidelity artifact load/inference PASS.

## 8. Split GGUF artifact model

GGUF artifact can be:
- `single_file`;
- `shard_set`.

Manifest for shard_set contains ordered filenames + SHA-256 + aggregate directory hash. Ollama packaging uses the exact supported wildcard/list form for the pinned version.

## 9. llama.cpp capability evidence

Preflight against pinned llama.cpp commit must retain:

- commit SHA;
- converter path/hash;
- build flags;
- output of converter/model capability inspection;
- tiny conversion/load result when feasible;
- tokenizer/chat-template compatibility result.

“Registry says supported” alone is not enough for release.

## 10. Ollama ephemeral model safety

Ephemeral test name:

```text
pipeline-test-<run_id>-<artifact_hash_prefix>
```

Before create:
- ensure no existing model of same name unless it has this run ownership marker;
- never overwrite arbitrary user model.

Cleanup deletes only model names created by current run and recorded in runtime manifest.

## 11. Disk/resource preflight

Estimate required free storage before training/export:

```text
required = dataset_cache
         + peak_training_checkpoint_set
         + canonical_hf
         + high_fidelity_gguf
         + quantized_targets
         + evidence_temp
         + safety_headroom
```

Default smoke safety headroom = max(2 GiB, 20% estimated peak). Real contract freezes policy/bytes. If insufficient: G0 FAIL before training.

## 12. LLM judge contract

If a judge is used, it is just another pinned runtime artifact. Its model revision, prompt hash, decoding contract, parser, raw outputs and retry policy are evidence. Objective verifier overrides judge when available.

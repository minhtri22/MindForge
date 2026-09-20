# 16 — Canonical Config & State-Machine Contract

## 1. Single source of truth

`schemas/experiment_config.schema.json` là vocabulary canonical duy nhất. Examples và CLI phải validate schema trước side effect.

Canonical vocabulary:

- phase data key: `datasets` (không dùng `data` bên trong phase);
- GGUF high-fidelity key: `export.gguf.high_fidelity`;
- reasoning key: `reasoning.mode`, `reasoning.transport_preference`, `reasoning.fallback_transport`;
- stop rule: đúng **một** trong `max_steps|max_tokens|max_epochs`;
- warmup: object có `unit` + `value`;
- precision: unresolved `auto` chỉ hợp lệ ở DRAFT/PREFLIGHT; execution lock phải có `resolved_precision`.

YAML include/profile chỉ là authoring convenience. Trước hash/lock phải expand thành canonical normalized JSON-equivalent rồi ghi `frozen/run_config.yaml`.

## 2. Config lifecycle

```text
AUTHOR CONFIG
  -> parse
  -> schema validate
  -> resolve includes/profiles
  -> resolve model revision
  -> resolve device/backend/precision
  -> resolve dataset snapshots
  -> resolve tool versions
  -> semantic validation
  -> canonical serialization
  -> hash
  -> FROZEN CONFIG
```

Confirmatory/release không cho lock nếu còn placeholder, unresolved ref, `auto`, `latest`, hoặc `main`.

Smoke/development được phép author bằng mutable source ref, nhưng source ref phải được resolve SHA và frozen **trước train**.

## 3. Run classes

- `smoke`: plumbing, không claim quality.
- `development`: sửa code/tune; fresh registry bị cấm.
- `calibration`: dùng calibration evidence để khóa thresholds/hyperparameters.
- `confirmatory`: execution locked, fresh evidence one-shot.
- `release`: confirmatory-qualified artifact + runtime/security/license/repro gates.

## 4. Run state machine

Canonical RunState:

```text
DRAFT
 -> PREPARED
 -> PREFLIGHT_PASS
 -> EXECUTION_LOCKED
 -> RUNNING
 -> EVALUATED
 -> ADJUDICATED_PASS | ADJUDICATED_FAIL | INVALID
 -> EXPORTED
 -> RUNTIME_VERIFIED
 -> REPRO_VERIFIED
 -> PROMOTED
```

Không phải run nào cũng đi đến PROMOTED; smoke có thể kết thúc `RUNTIME_VERIFIED`.

Transition chỉ hợp lệ khi gate matrix cho run class cho phép. `INVALID` là terminal đối với scientific evidence; repair tạo `run_id` mới với `supersedes_run_id`.

## 5. Phase state machine

Mỗi phase có độc lập:

```text
PLANNED
 -> INPUT_READY
 -> TRAINING
 -> TRAINED
 -> CHECKPOINT_SELECTED
 -> PHASE_EVALUATED
 -> PHASE_PASS | PHASE_FAIL | PHASE_INVALID
```

Run không được sang phase kế nếu phase hiện tại yêu cầu `PHASE_PASS` nhưng chưa PASS.

Mỗi phase manifest bắt buộc có:

- `phase_id`, `phase_type`;
- exact parent artifact/hash;
- dataset IDs + frozen fingerprints;
- stop rule;
- optimizer/scheduler transition policy;
- checkpoint-selection rule;
- selected checkpoint hash;
- phase metric outputs;
- child artifact ID.

## 6. Phase transition policy

Mặc định giữa CPT -> SFT/reasoning SFT:

- model weights: carry;
- optimizer: reset;
- scheduler: reset;
- AMP scaler: reset;
- dataloader/sampler: new;
- RNG: derive from phase seed according to frozen policy.

Carry optimizer/scheduler chỉ hợp lệ khi explicit:

```yaml
transition:
  optimizer: carry
  scheduler: carry
  rationale: "..."
```

và backend chứng minh state compatibility.

## 7. Stop-rule semantics

Exactly one stop rule:

```yaml
stop:
  kind: max_tokens
  value: 5000000
```

Không cho đồng thời epochs + steps + tokens. Nếu author config dùng convenience fields, resolver phải biến thành một canonical stop object hoặc FAIL ambiguity.

## 8. Warmup semantics

```yaml
warmup:
  unit: ratio   # ratio | steps | tokens
  value: 0.03
  resolved_value: 150000
  resolved_unit: tokens
```

`resolved_*` bắt buộc trước execution lock.

## 9. Precision/device resolution

Trước lock phải frozen:

- framework/backend;
- device class;
- resolved precision (fp32/fp16/bf16/...);
- mixed-precision/scaler policy;
- deterministic flags;
- known nondeterministic kernels;
- device-count and world-size.

Run chuyển machine sau lock chỉ được tiếp tục nếu execution contract cho phép resource-class equivalence; nếu không -> INVALID/new run.

## 10. Artifact semantics for LoRA/PEFT

`adapter_checkpoint` không phải canonical standalone model.

Pipeline định nghĩa:

1. `base_artifact`;
2. `adapter_artifact`;
3. `merged_hf_artifact` nếu export standalone;
4. `canonical_training_artifact`;
5. `canonical_export_artifact`.

GGUF/Ollama standalone release phải dùng merged artifact trừ khi pinned runtime path hỗ trợ adapter và execution contract explicitly chọn đường đó.

## 11. Dirty code/worktree

Confirmatory/release lock yêu cầu exact source commit và `dirty=false`. Development có thể dirty nhưng phải record patch hash và không được promote artifact đó như confirmatory evidence.

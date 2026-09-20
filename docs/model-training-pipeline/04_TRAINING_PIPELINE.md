# 04 — Training Pipeline

## 1. Training modes

### `cpt`
Causal LM continued pretraining trên raw token stream.

### `sft`
Instruction/chat fine-tuning, bảo toàn chat template.

### `reasoning_sft`
SFT với target gồm reasoning trace và final answer tách biệt.

### `lora_sft`
Adapter path. Export phải ghi rõ base model identity. Nếu Ollama adapter import không phù hợp với quantization/training path, pipeline phải merge thành full Safetensors trước GGUF export.

### `pretrain_from_scratch`
Thiết kế interface cho tương lai, nhưng không phải acceptance requirement MVP.

## 2. Khuyến nghị workflow chuẩn

```text
reasoning-capable/instruct base
        ↓
CPT Wikipedia + code (nếu cần domain knowledge)
        ↓
Instruction replay / SFT
        ↓
Reasoning SFT
        ↓
Fresh evaluation
        ↓
Export
```

Lý do: CPT raw corpus có thể làm suy giảm instruction-following/reasoning style; pipeline bắt buộc đo catastrophic forgetting trước và sau mỗi phase.

## 3. Trainer config bắt buộc

- model/base artifact ID + hash;
- precision;
- sequence length;
- batch size + gradient accumulation;
- learning rate;
- optimizer;
- scheduler + warmup;
- weight decay;
- gradient clipping;
- epochs/max steps/max tokens;
- seed;
- dataloader seed;
- save/eval cadence;
- activation checkpointing;
- mixed precision policy;
- PEFT config nếu có;
- loss mask rules cho chat/reasoning;
- max wall-clock/resource limits.

## 4. Determinism

Pipeline phải phân loại run:

- `strict_deterministic` nếu backend/hardware cho phép;
- `best_effort_reproducible` nếu kernel không deterministic.

Phải record flags, library versions, GPU driver/backend và các known nondeterministic ops.

## 5. Loss masking

SFT chat phải support mask user/system tokens, chỉ tính loss trên assistant target theo config.

Reasoning SFT phải support separate weights:

```yaml
loss:
  answer_weight: 1.0
  reasoning_weight: 1.0
```

Không hardcode reasoning dài hơn = tốt hơn.

## 6. Checkpoint cadence

Checkpoint phải có hai lớp:

- recoverable training checkpoints;
- canonical selected checkpoint.

Garbage collection chỉ được xóa recoverable checkpoints sau khi canonical + evidence bundle đã verify.

## 7. Health monitors

Fail-fast configurable khi:

- NaN/Inf loss/grad;
- tokenizer/data mismatch;
- exploding grad sustained;
- zero effective tokens;
- disk budget below threshold;
- checkpoint hash/write verification fails.

Không tự thay LR/batch để cứu run confirmatory.

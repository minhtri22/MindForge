# 04 — Training Pipeline

## 1. Modes

cpt, sft, reasoning_sft, lora_sft. Pretrain-from-scratch là future scope.

## 2. Standard chain

Exact parent baseline -> CPT -> instruction replay/SFT -> reasoning SFT -> fresh evaluation -> export/runtime verification.

Mỗi phase có state/evaluation riêng và parent/child artifact hashes.

## 3. Phase config

Freeze datasets, exactly one stop rule, resolved precision/device, sequence length, batch/grad accumulation, LR/optimizer, scheduler/warmup unit, weight decay/clipping, seeds, checkpoint cadence, loss masks/weights, resource limits và optimizer/scheduler reset-or-carry.

Canonical stop/state semantics ở 16_CANONICAL_CONFIG_STATE_MACHINE.md.

## 4. Instruction replay

Replay không phải rescue tùy ý. Source, mixture/token budget, stop rule và thresholds phải freeze trước phase. CPT phase FAIL vẫn được ghi dù later replay recovery.

## 5. Reproducibility

Record backend/device/precision/deterministic flags/nondeterministic ops. precision:auto phải resolve trước lock.

## 6. Checkpoint/resume

Dùng checkpoint schema + atomic protocol. Confirmatory exact-resume không được silently downgrade thành best-effort.

## 7. PEFT

Adapter artifact, merged HF artifact và canonical export artifact là identities khác nhau. Standalone GGUF release dùng merged artifact trừ khi pinned runtime path explicit support adapter mode.

## 8. Health monitors

Policy freeze cho NaN/Inf, tokenizer mismatch, gradient failure, zero effective loss tokens, disk insufficiency và checkpoint verify fail. Không auto đổi LR/batch/seed trong confirmatory.

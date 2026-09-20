# 04 — Training Pipeline

## 1. Modes

cpt, sft, reasoning_sft, lora_sft.

## 2. Phase graph

Each phase explicitly names parent_ref. A downstream phase cannot start until its parent phase has selected and COMMITTED its canonical checkpoint by that phase's frozen checkpoint-selection rule.

Standard example:
model -> domain_cpt -> instruction_sft -> reasoning_sft.

## 3. Per-phase contract

Every phase owns:
- parent_ref;
- datasets;
- phase-scoped TokenStreamContract;
- one stop rule;
- resolved precision/device;
- LR/optimizer/scheduler/warmup;
- phase seed/dataloader seed;
- checkpoint cadence;
- checkpoint selection;
- loss mask/weights;
- resource limits;
- optimizer/scheduler reset-or-carry.

## 4. CPT -> replay

Instruction replay is a declared phase, not informal rescue. Source, budget/mixture, stream semantics and thresholds freeze before execution. Earlier phase verdict remains historical evidence.

## 5. Checkpoint/resume

Exact resume restores phase stream/sampler state and gradient-accumulation micro-step. Partial/uncommitted checkpoints are never parents.

## 6. PEFT

Adapter, merged HF and export artifacts remain separately identified. Standalone GGUF uses merged artifact unless pinned target explicitly supports adapter mode.

## 7. Health policy

NaN/Inf, data/tokenizer mismatch, zero effective loss tokens, resource exhaustion and checkpoint verification failure follow frozen FAIL/INVALID policy; no auto scientific rescue.

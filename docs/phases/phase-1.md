# Phase 1 — Compact End-to-End Kernel

Status: **PASS / CLOSED**

Base commit: `bba9360b87c947202115386a3c6ea1f68b9735b9`

## Purpose

Phase 1 consolidates the validated Phase-0 path into one small reusable local LLM kernel:

```text
dataset → tokenizer → Transformer → training → checkpoint → evaluation → generation
```

It is an engineering consolidation phase. No continual learning, replay, memory, RAG, agents, PEFT, framework hooks, callback buses, registries, distributed training, serving, quantization or speculative extension interfaces were added.

## Architecture and layout

The reusable package is intentionally flat:

```text
mindforge/
  __init__.py
  config.py
  device.py
  tokenizer.py
  data.py
  model.py
  checkpoint.py
  train.py
  evaluate.py
  generate.py
```

Configuration uses frozen dataclasses (`ModelConfig`, `TrainingConfig`, `DataConfig`, `KernelConfig`). Device selection and synchronization are direct functions, not a backend hierarchy.

## Default model

```text
vocab_size       16,384
d_model          320
n_heads          8
n_layers         4
max_context      512
ff_mult          4
dropout          0.0
positions        learned embeddings
normalization    pre-norm + final LayerNorm
MLP              GELU, 4x expansion
LM head          bias-free, tied to token embedding
parameters       10,339,200 exactly
```

## Default training

```text
optimizer         AdamW
peak LR           3e-4
weight decay      0.1
gradient clip     1.0
schedule          5% linear warmup, cosine decay to 10% peak
micro-batch       1 context
accumulation      2
effective batch   2 contexts
seed              2026
```

## Device policy

`auto` resolves XPU → CUDA → CPU. The validated target is Intel Arc 140V with PyTorch XPU and BF16. CPU uses FP32 under `auto` and is supported for tests, preprocessing, smoke runs and fallback. CUDA uses ordinary PyTorch selection only; no CUDA-specific optimization exists.

Explicit unavailable device requests fail rather than silently falling back.

## Tokenizer and data flow

The only tokenizer implementation is MindForge byte-level BPE with NFC normalization, ByteLevel pre-tokenizer/decoder and fixed special tokens `<|endoftext|>`, `<|unk|>`. The default vocabulary is 16,384.

The data module accepts ordinary UTF-8 files and prepared `.npy` token arrays. It provides deterministic split/batch behavior and SHA-256-backed provenance. Wikimedia acquisition remains outside the kernel.

## Training flow

The training loop is direct single-device PyTorch: deterministic step-indexed batches, gradient accumulation, AdamW, frozen LR schedule, clipping, periodic independent-style validation, checkpointing, resume, tokens/sec and peak-memory reporting. Each run writes `run.json` and `metrics.jsonl`.

## Checkpoint format

Phase-1 checkpoints have `format_version = 1` and contain model state, optimizer state, step, model/training configuration, tokenizer and dataset fingerprints, seed, metadata and Python/NumPy/Torch RNG state. Loading rejects missing fields, unknown versions and identity mismatches.

CPU exact-resume validation produced identical final tensors, zero loss delta and identical evaluation output. XPU resume is intentionally a functional contract rather than a cross-run bitwise promise.

## Evaluation

The standalone evaluator consumes only checkpoint, tokenizer and token-array artifacts. It reports CE, bits/token and BPB. BPB is computed from total natural-log NLL divided by `log(2)` times the actual represented UTF-8 bytes; it is not inferred from token count.

Repeated evaluation is frozen at `<= 1e-6` absolute CE/BPB delta. The observed XPU repeat delta was exactly `0.0`.

## Generation

Generation is minimal autoregressive decoding with context cropping. Greedy is the default. Optional temperature/top-k sampling uses a CPU-seeded generator so fixed checkpoint/prompt/config/seed reproduces token IDs. There are no chat templates, roles, streaming or server semantics.

## Validation results

CPU end-to-end smoke: **PASS**. A 29,664-parameter fixture model trained 4 steps, checkpointed, resumed exactly, independently evaluated and generated text. Final BPB was `11.948391479103112`; resume loss delta was `0.0`.

Local XPU/BF16 integration: **PASS** on Intel Arc 140V. The default 10,339,200-parameter model trained 100 steps / 102,400 tokens and then functionally resumed from step 50 to step 100. Canonical continuous-run wall clock was `16.575575599999866 s`, mean throughput `10072.553508676194 tok/s`, median throughput `11149.095405334912 tok/s`, and peak XPU memory `211125760 bytes`. BPB improved from `71.02420255831706` initial to `11.339613281591234` after 100 steps.

Phase-0 parity: **PASS**. Loading the frozen legacy Baseline-0 weights into the identical Phase-1 architecture and evaluating with the Phase-1 evaluator reproduced final BPB exactly: `9.034118696437462` vs `9.034118696437462` (`0.0%` relative difference). Phase-1 median throughput was `17.28%` lower than the frozen Baseline-0 median, within the `25%` gate; measured peak XPU memory was `16.57%` lower.

Machine-readable evidence:

- `experiments/results/phase1_cpu_smoke.json`
- `experiments/results/phase1_xpu_validation.json`
- `experiments/results/phase1_parity.json`

## Reproduction commands

Use the repository XPU environment for hardware evidence:

```powershell
.\.venv\Scripts\python.exe experiments/phase1_validate.py cpu
.\.venv\Scripts\python.exe experiments/phase1_validate.py xpu
.\.venv\Scripts\python.exe experiments/phase1_validate.py parity
.\.venv\Scripts\python.exe -m compileall .
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

Public kernel commands are:

```text
python -m mindforge.tokenizer train --input ... --output ...
python -m mindforge.data prepare --tokenizer ... --train-text ... --validation-text ... --output-dir ...
python -m mindforge.train --config ...
python -m mindforge.evaluate --checkpoint ... --tokenizer ... --tokens ...
python -m mindforge.generate --checkpoint ... --tokenizer ... --prompt ...
```

## Known limitations

- This is a base language-model kernel, not an instruction/chat model.
- XPU functional resume is validated, but cross-device or XPU bitwise determinism is not claimed.
- The 100-step XPU run is a bounded integration run, not a language-quality benchmark.
- Throughput comparison uses the same architecture/data/context/batch/device/dtype and compares per-step sustained behavior against the frozen Baseline-0; the historical Baseline-0 trained for 1,000 steps.
- CUDA is supported only through ordinary PyTorch device selection and was not target-hardware validated in Phase 1.

## Explicit non-goals

Phase 1 contains no replay, EWC, DER++, memory, continual learning, RAG, agents, LoRA/PEFT, SFT, preference/RL training, MoE, VLM, tool use, distributed training, production serving, quantization or future-facing plugin/hook infrastructure.

Phase 2 remains a separate future increment and is not authorized by this closure.

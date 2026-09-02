# Phase 0 QA Plan

This plan distinguishes whether a check exists, whether it was executed on the local target machine, and whether the observed result passed. A missing or unexecuted check is never treated as PASS.

## Static checks

| Check | Exists | Executed | Passed | Evidence |
|---|---|---|---|---|
| Python byte-compilation | YES | YES | YES | `python -m compileall .` |
| Git whitespace validation | YES | Pending final gate | Pending | `git diff --check` |

## Unit tests

| Check | Exists | Executed | Passed | Evidence |
|---|---|---|---|---|
| Model parameter scales near 10M/25M/50M/100M targets | YES | YES | YES | `tests/test_phase0_local.py` |
| Synthetic domain transition generator correctness | YES | YES | YES | `tests/test_phase0_local.py` |
| CPU forward/backward/optimizer changes parameters | YES | YES | YES | `tests/test_phase0_local.py` |
| CPU checkpoint round-trip | YES | YES | YES | `tests/test_phase0_local.py` |

The repository contained no tests at base commit `5d95db1`; the pre-change `pytest -q` run reported `no tests ran`.

## Integration tests

| Check | Exists | Executed | Passed | Evidence |
|---|---|---|---|---|
| Phase 0 hardware probe end to end | YES | YES | YES | `experiments/results/phase0_hardware_probe.json` |
| Practical model-envelope sweep | YES | YES | YES | `experiments/results/phase0_model_envelope.json` |
| Three-seed reproducibility run | YES | YES | YES | `experiments/results/phase0_reproducibility.json` |
| Continual-learning baseline + replay treatment | YES | YES | REVISE | `experiments/results/phase0_continual_local.json` |

## Hardware tests

| Check | Exists | Executed | Passed | Notes |
|---|---|---|---|---|
| CPU FP32 matrix multiplication | YES | YES | YES | 2048x2048 benchmark |
| XPU FP32 matrix multiplication | YES | YES | YES | Actual Arc 140V device observed |
| CPU FP32 forward/backward/optimizer | YES | YES | YES | Full train step |
| XPU FP32 forward/backward/optimizer | YES | YES | YES | Full train step |
| XPU FP16 forward/backward/optimizer | YES | YES | YES | Tensor and parameter dtype verified on `xpu:0` |
| XPU BF16 forward/backward/optimizer | YES | YES | YES | Tensor and parameter dtype verified on `xpu:0` |
| CPU FP16/BF16 backward | YES | YES | NO | oneDNN reports unsupported bf16/f16 backward on this platform |
| CUDA path | Conditional | NO | N/A | No CUDA device is present |

## Numerical correctness tests

CPU and XPU use the same tiny Transformer weights and fixed input. The local gate is maximum absolute FP32 logit difference <= `2e-3`; bit identity is not required. The observed maximum absolute difference was `1.52587890625e-05`, so this check passed.

Checkpoint round-trip uses a maximum output difference tolerance of `1e-6`; observed difference was `0.0`.

## Reproducibility tests

Three fixed seeds (`101`, `202`, `303`) train the same tiny architecture and deterministic synthetic domain. Each seed must reduce held-out loss. All three passed. This proves the local mechanism and deterministic data protocol; it does not prove dataset viability for a real corpus.

## Checkpoint/resume tests

The resume test compares an uninterrupted 8-step run with a 4-step + save/load + 4-step run using identical step-indexed data. Maximum parameter difference must be <= `1e-6`; observed difference was `0.0`.

## Continual-learning tests

Frozen protocol before comparison:

- tiny plain Transformer, FP32 on XPU;
- domain A transition offset `+1`, domain B offset `+2`;
- 30 A steps followed by 30 B steps;
- batch size 16, context 32, AdamW, learning rate 0.003;
- seeds `101`, `202`, `303`;
- treatment is fixed 50/50 B/A replay while training B;
- no hyperparameter tuning after observing baseline results.

The baseline did not exhibit forgetting: mean A loss changed from `3.2091` before B to `2.8120` after B, i.e. forgetting metric `A_after_B - A_before_B = -0.3971`. Therefore the continual-learning probe is REVISE. Replay further improved A but cannot be claimed as an anti-forgetting success because the baseline had no forgetting signal.

## Failure-mode tests

Meaningful failures are retained as evidence:

- the initial global PyTorch build was `2.12.0+cpu`; `torch.xpu.is_available()` was false;
- CPU FP16 and BF16 backward failed with `DNNL does not support bf16/f16 backward on the platform with avx2_vnni_2`;
- the synthetic continual-learning protocol failed to produce untreated forgetting;
- CUDA was not tested because no CUDA device exists.

OOM probing is intentionally bounded. No tested 10M-100M / context 256-2048 XPU configuration OOMed, so repeated forced OOM attempts were not performed.

## Known limitations

- P0.3 tokenizer strategy and P0.4 real-dataset viability are not addressed by this local hardware harness.
- P0.6 has loss/checkpoint comparison primitives but not the full planned evaluation contract (bits/token and deterministic generation sanity checks).
- P0.8 has a plain Transformer training mechanism but no real-corpus Baseline-0 yet.
- Intel Arc 140V is integrated/shared-memory hardware. WMI reports `AdapterRAM` about 2 GB while the device label says `16GB`; these fields are not treated as equivalent to dedicated VRAM. XPU allocator peak and process RSS are reported separately.
- Single-step throughput measurements are local research-envelope measurements, not production or marketing benchmarks.
- CPU 2048x2048 matmul throughput showed large run-to-run variance in this session; it is kept as raw diagnostic evidence but is not used to rank backends.

## Exit criteria

Phase 0 may be marked PASS only when all Phase 0 questions in `PLAN.md` have evidence. For this local-validation increment:

- P0.1 PASS requires real target-hardware forward, backward, optimizer, checkpoint and representative timing evidence.
- P0.2 PASS requires measured model/context configurations and resource/throughput evidence.
- P0.5 PASS requires at least three seeds plus checkpoint resume correctness.
- P0.9 PASS requires a protocol that actually exposes untreated forgetting; the current protocol does not.
- P0.10 may only proceed when a controlled memory-value signal exists.

Because P0.3, P0.4, P0.6 and P0.8 remain incomplete and P0.9 needs revision, overall Phase 0 remains REVISE and Phase 1 must not start.

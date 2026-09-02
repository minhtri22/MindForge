# Phase 0 — Local Hardware Validation

## 1. Executive result

**REVISE**

The target laptop proves that Intel XPU is genuinely usable for MindForge research: FP32/FP16/BF16 full training steps execute on the Arc 140V, CPU/XPU FP32 numerical agreement is within the frozen tolerance, checkpoint round-trip passes, and measured 10M-100M Transformer configurations through context 2048 all run successfully on XPU.

Phase 0 as a whole does not pass yet. Tokenizer/dataset/evaluation/Baseline-0 evidence is still incomplete, and the current continual-learning protocol does not produce untreated forgetting, so P0.9 must be redesigned rather than tuned to force a treatment win.

## 2. Machine under test

- OS: Microsoft Windows 11 Home Single Language, version `10.0.26200`, build `26200`, 64-bit.
- WSL: WSL2 is present; default distribution reported as `docker-desktop`. Native Windows Python was used for all measurements.
- CPU: Intel Core Ultra 7 258V, 8 physical cores / 8 logical processors.
- RAM: 33,916,248,064 bytes (~31.58 GiB). At the initial environment probe, Windows reported ~16.64 GiB available.
- GPU: Intel Arc 140V GPU, device label `Intel(R) Arc(TM) 140V GPU (16GB)`.
- GPU driver: `32.0.101.8860`.
- WMI `AdapterRAM`: 2,147,479,552 bytes (~2.0 GiB). Because this is an integrated/shared-memory GPU and conflicts with the device label, this value is recorded but is not treated as dedicated usable VRAM.

## 3. Base commit tested

`5d95db1f325c277a75a28b47f9c72500e48c6fa3` (`docs: add evidence-gated development plan`)

## 4. Environment

Initial global environment:

- Python `3.13.12` from Miniforge.
- PyTorch `2.12.0+cpu`.
- CUDA version: none; `torch.cuda.is_available() == False`.
- XPU API attribute existed but `torch.xpu.is_available() == False` and device count was 0.

Isolated validation environment:

- `.venv` created with CPython `3.12.10`.
- pip `26.2.1`.
- PyTorch `2.12.1+xpu` from the official PyTorch XPU wheel index.
- `torch.xpu.is_available() == True`, XPU count 1, observed device `Intel(R) Arc(TM) 140V GPU (16GB)`.
- CUDA unavailable, so no CUDA benchmark was run.
- Complete Python package snapshot: `requirements-phase0-lock.txt`.

No Intel Extension for PyTorch was added; the native PyTorch XPU wheel and its Intel runtime dependencies were sufficient for the tested workloads.

## 5. Test matrix

| Test | Backend | Config | Result | Metric | Notes |
|---|---|---|---|---|---|
| Matmul | CPU | FP32, 2048x2048 | PASS | functional PASS; throughput unstable | Latest raw run ~5.5 GFLOP/s; isolated diagnostics ranged ~182-346 GFLOP/s, so CPU matmul speed is not used as a stable claim |
| Matmul | XPU | FP32, 2048x2048 | PASS | ~2064.8 GFLOP/s in latest hardware probe | Output observed on `xpu:0` |
| Full train step | CPU | FP32, tiny Transformer | PASS | device/dtype/update verified | forward + loss + backward + AdamW step |
| Full train step | CPU | FP16 | FAIL | backend error | DNNL backward unsupported |
| Full train step | CPU | BF16 | FAIL | backend error | DNNL backward unsupported |
| Full train step | XPU | FP32 | PASS | device/dtype verified | no silent CPU fallback |
| Full train step | XPU | FP16 | PASS | device/dtype verified | no silent CPU fallback |
| Full train step | XPU | BF16 | PASS | device/dtype verified | no silent CPU fallback |
| Checkpoint round-trip | XPU | FP32 | PASS | max output delta `0.0` | tolerance `1e-6` |
| CPU vs XPU numerical | CPU/XPU | FP32 tiny deterministic | PASS | max abs delta `1.5259e-05` | tolerance `2e-3` |
| 3-seed train | XPU | FP32 tiny | PASS | all 3 held-out losses decreased | seeds 101/202/303 |
| Resume equivalence | XPU | 8 steps vs 4+4 | PASS | max parameter delta `0.0` | tolerance `1e-6` |
| Continual baseline | XPU | A → B, 3 seeds | REVISE | mean forgetting `-0.3971` | no untreated forgetting signal |
| Replay treatment | XPU | fixed 50/50 replay | INCONCLUSIVE | forgetting `-2.1615` | cannot claim anti-forgetting win without baseline forgetting |

## 6. Hardware feasibility

P0.1 is **PASS** for the target machine.

The important distinction is that the initial global environment could not use XPU, while the isolated PyTorch XPU environment could execute real training. XPU capability was validated with actual model parameters and output tensors resident on `xpu:0`, followed by backward and AdamW optimizer update. FP16 and BF16 also completed on XPU with the requested dtype observed on parameters/logits.

CPU remains a valid FP32 fallback. CPU FP16/BF16 backward is not supported by the tested oneDNN path on this machine and must not be advertised as supported.

## 7. Model envelope

Primary sweep: Intel XPU, BF16, micro-batch 1, effective batch 1, one full training step after bounded warm-up where applicable. Peak memory is PyTorch XPU maximum allocated memory for the measured step.

| Nominal size | Actual params | Context | Step time | Tokens/s | XPU peak allocated |
|---|---:|---:|---:|---:|---:|
| ~10M | 10,391,040 | 256 | 0.205 s | 1,249 | 101 MiB |
| ~10M | 10,391,040 | 512 | 0.053 s | 9,750 | 167 MiB |
| ~10M | 10,391,040 | 1024 | 0.601 s | 1,704 | 359 MiB |
| ~10M | 10,391,040 | 2048 | 1.707 s | 1,200 | 1,204 MiB |
| ~25M | 27,317,248 | 256 | 0.407 s | 629 | 268 MiB |
| ~25M | 27,317,248 | 512 | 0.215 s | 2,379 | 320 MiB |
| ~25M | 27,317,248 | 1024 | 0.429 s | 2,386 | 530 MiB |
| ~25M | 27,317,248 | 2048 | 0.565 s | 3,624 | 1,631 MiB |
| ~50M | 51,857,920 | 256 | 0.207 s | 1,234 | 503 MiB |
| ~50M | 51,857,920 | 512 | 0.095 s | 5,372 | 554 MiB |
| ~50M | 51,857,920 | 1024 | 0.755 s | 1,355 | 826 MiB |
| ~50M | 51,857,920 | 2048 | 1.479 s | 1,385 | 2,494 MiB |
| ~100M | 102,377,472 | 256 | 0.136 s | 1,881 | 994 MiB |
| ~100M | 102,377,472 | 512 | 0.420 s | 1,221 | 1,013 MiB |
| ~100M | 102,377,472 | 1024 | 0.769 s | 1,332 | 1,389 MiB |
| ~100M | 102,377,472 | 2048 | 3.164 s | 647 | 4,066 MiB |

All 16 XPU configurations passed forward, backward and optimizer step; none OOMed.

Clean CPU controls were run before any XPU allocations to avoid shared-memory contamination:

| Model | Context | Step time | Tokens/s | Process RSS after |
|---|---:|---:|---:|---:|
| ~10M FP32 CPU | 256 | 0.380 s | 674 | ~1.04 GiB |
| ~10M FP32 CPU | 512 | 0.552 s | 928 | ~1.07 GiB |

For iterative research, the conservative default envelope is **~50M parameters, context 1024, micro-batch 1, BF16, XPU**. It leaves substantial memory headroom while keeping the model large enough to be more informative than the smallest probe configurations. ~100M/context 2048 is technically supported, but at ~647 tok/s and ~4.0 GiB XPU allocated for a single step it is a boundary configuration rather than the recommended default. Throughput varies enough across short runs that these values should be treated as local envelope measurements, not stable performance rankings.

## 8. Correctness

- XPU forward/backward/AdamW update: PASS in FP32, FP16 and BF16.
- CPU forward/backward/AdamW update: PASS in FP32; FP16/BF16 backward unsupported.
- XPU checkpoint save/load: PASS, output max absolute difference `0.0`.
- CPU/XPU FP32 deterministic comparison: PASS, max absolute logit difference `1.52587890625e-05` against tolerance `2e-3`.
- Checkpoint resume equivalence: PASS, maximum parameter difference `0.0` after 8 total steps.

## 9. Reproducibility

Same tiny Transformer/config and deterministic synthetic domain, three seeds:

| Seed | Eval loss before | Eval loss after | Reduction | Result |
|---:|---:|---:|---:|---|
| 101 | 43.62 | 5.23 | 38.39 | PASS |
| 202 | 43.16 | 4.33 | 38.83 | PASS |
| 303 | 45.84 | 5.32 | 40.52 | PASS |

P0.5 local mechanism is **PASS**. This does not substitute for P0.4 real-dataset evidence.

## 10. Continual learning

Frozen three-seed baseline means:

- A before B: `3.2091`
- A after B: `2.8120`
- B after B: `2.1796`
- Forgetting (`A_after_B - A_before_B`): `-0.3971`

The negative forgetting metric means learning B improved A under this synthetic protocol. Therefore the protocol does not expose the phenomenon P0.9 is meant to measure.

Fixed replay treatment means:

- A before B: `3.2091`
- A after B: `1.0476`
- B after B: `2.8070`
- Forgetting: `-2.1615`
- Numerical change vs baseline forgetting: `1.7644` loss points in the direction of lower A loss.

This treatment is **inconclusive as an anti-forgetting treatment**. It preserves/improves A more, but there was no untreated forgetting to prevent and it worsened B-after-B relative to baseline (`2.8070` vs `2.1796`). No tuning was performed to force a positive result.

## 11. Failures discovered

1. Initial global `torch 2.12.0+cpu` could not access XPU despite the physical Arc 140V being present.
2. CPU FP16 and BF16 backward fail in the tested DNNL path.
3. The first model-envelope implementation ran CPU controls after XPU allocations, making process RSS unsuitable as clean CPU evidence. The harness was corrected to run CPU controls before XPU initialization and P0.2 was re-run; superseded RSS values are not used.
4. CPU matmul throughput is highly unstable in this session. A diagnostic showed that XPU runtime initialization can depress CPU matmul in the same process, but large variance also remained across reordered/fresh runs. CPU dense-matmul speed is therefore retained as raw evidence but not used as a stable comparative claim.
5. The continual-learning synthetic domains are positively transferable rather than interfering, so they fail to produce a forgetting signal.
6. Pre-change repository had no automated tests (`pytest -q` reported no tests).

## 12. Fixes made

- Added `experiments/phase0_local_validate.py`: Phase 0-only measurement harness for hardware, envelope, reproducibility and continual-learning probes.
- Added `tests/test_phase0_local.py`: regression checks for parameter scales, data generator, training step and checkpoint round-trip.
- Added `.gitignore` for local environment/cache/checkpoint artifacts.
- Added `requirements-phase0.txt` and `requirements-phase0-lock.txt` to isolate and reproduce the local validation environment.
- Added this report and `docs/phases/phase-0-qa.md`.

No Phase 1 kernel or roadmap expansion was implemented.

## 13. Remaining unknowns

- P0.3: existing vs project-trained tokenizer on representative Vietnamese/English text.
- P0.4: smallest useful real corpus, deterministic split and data fingerprint.
- P0.6: full planned evaluation harness including bits/token and deterministic generation sanity checks.
- P0.8: real-corpus Baseline-0 with expected loss curve/runtime/memory/evaluation behavior.
- P0.9: a task/domain pair that produces measurable untreated forgetting.
- P0.10: explicit memory value is not testable until a controlled memory/forgetting signal exists.
- Long-run XPU stability/thermal behavior is not established by these short probes.

## 14. Evidence gate

| Gate | Status | Reason |
|---|---|---|
| P0.1 Hardware feasibility | PASS | Real Arc 140V full train steps, dtype checks, checkpoint and numerical comparison measured |
| P0.2 Practical model envelope | PASS | 10M-100M x 256-2048 measured on XPU BF16; CPU controls measured |
| P0.3 Tokenizer assumption | REVISE | Not tested in this increment |
| P0.4 Dataset viability | REVISE | Not tested in this increment |
| P0.5 Training reproducibility | PASS | 3 seeds + deterministic resume equivalence |
| P0.6 Evaluation harness viability | REVISE | Loss comparison exists; full planned eval/generation contract incomplete |
| P0.7 Experiment protocol | PASS | Machine-readable JSON records include provenance, hardware/software, config, seeds/status and relevant metrics |
| P0.8 Baseline-0 | REVISE | Plain Transformer mechanism exists, but no real-corpus Baseline-0 yet |
| P0.9 Continual-learning feasibility | REVISE | Current protocol produces negative forgetting |
| P0.10 Memory hypothesis probe | STOP | No controlled memory-value/forgetting signal exists yet; do not build explicit memory architecture |

Overall Phase 0 status: **REVISE**.

## 15. Recommendation

**Repeat experiment.**

Do not start Phase 1. Keep the validated XPU/BF16 hardware strategy and ~50M/context-1024 default research envelope. Complete P0.3/P0.4/P0.6/P0.8, then redesign P0.9 around intentionally non-transferable/interfering A/B tasks with a frozen falsifiable forgetting criterion. Only reopen P0.10 if that task produces a reproducible memory-value signal.

## Reproduction commands

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.12.1+xpu --index-url https://download.pytorch.org/whl/xpu
.\.venv\Scripts\python.exe -m pip install -r requirements-phase0.txt

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe experiments\phase0_local_validate.py hardware
.\.venv\Scripts\python.exe experiments\phase0_local_validate.py envelope
.\.venv\Scripts\python.exe experiments\phase0_local_validate.py repro
.\.venv\Scripts\python.exe experiments\phase0_local_validate.py continual
```

Machine-readable evidence is under `experiments/results/`.

# Phase 0 — Real Language Baseline Validation

Base commit: `1b0d9b016c2eaff8922693f7f6d496b597f29927`

## Executive result

Real Language Baseline slice: **PASS**.

P0.3, P0.4, P0.6 and P0.8 are PASS/FROZEN. Overall Phase 0 remains **REVISE** because P0.9 remains REVISE and P0.10 remains blocked/stopped. Phase 1 must not start from this increment.

## P0.3 — Tokenizer assumption

Status: **PASS / FREEZE**. Decision: **TRAIN MINDFORGE TOKENIZER**.

The candidates are Qwen/Qwen2.5-0.5B tokenizer at revision `060db6499f32faf8b98477b0a26969ef7d8b9987` and the project-trained byte-level BPE with vocabulary 16,384. Both round-trip the frozen probes, produce valid token IDs, and have zero unexpected unknown tokens.

Compression on the held-out probes:

| Metric | Qwen | MindForge |
|---|---:|---:|
| VI tokens/byte | 0.2428276470 | 0.2191536132 |
| EN tokens/byte | 0.2369852066 | 0.2551279068 |
| Mixed tokens/byte | 0.2379584542 | 0.2356629645 |

Corrected same-byte smoke BPB:

| Candidate | Final BPB |
|---|---:|
| Qwen | 12.4814268033 |
| MindForge | 9.7144598975 |

The first smoke implementation had reported Qwen `12.1943` and MindForge `9.9998`, but it selected tokenizer-specific token-position windows and therefore did not guarantee identical UTF-8 spans. Those values are retained only as superseded failure evidence. Protocol revision 2 fixed the comparison before the final P0.3 decision by scoring 12 shared text samples totaling 6,140 exact UTF-8 bytes with a BOS prefix so every sample token is predicted.

Final integrity checks passed: both candidates use the same frozen corpus/split; MindForge tokenizer training uses only `train.vi.txt` and `train.en.txt`; rebuilding from those files reproduces the 16,384-entry vocabulary exactly and reproduces probe IDs; the 12 fair-sample hashes are shared; and perplexity is never used for cross-tokenizer ranking. Machine-readable details are in `experiments/results/phase0_tokenizer_integrity.json`.

## P0.4 — Dataset viability

Status: **PASS / FREEZE**. Recommended development corpus: **1M tokens**.

Source is official Wikimedia Vietnamese and English Wikipedia dumps, snapshot `20260801`. Corpus fingerprint: `c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696`.

Article-level SHA-256 split integrity passed with zero train/validation article-ID overlap. Extracted counts are VI 1,685 train / 358 validation and EN 1,360 train / 175 validation.

| Development pool | Initial BPB | Final BPB | Final-vs-best reversal |
|---|---:|---:|---:|
| 1M | 44.5312765650 | 7.6334209184 | 0.0% |
| 10M | 44.5312765650 | 7.6226645714 | 0.0% |

The 10M pool improves final BPB over 1M by only **0.140911%**, below the frozen **5%** threshold required to justify the larger development pool. Therefore 50M and 100M are not required. “1M” is the selected deterministic development token pool, not the total available Wikimedia source corpus.

P0.3 still selects the MindForge tokenizer after the fairness correction, so the previously frozen P0.4 evidence remains valid and was not rerun.

## P0.6 — Evaluation harness viability

Status: **PASS / FREEZE**.

`experiments/phase0_real_language_eval.py` is a standalone evaluator with no dependency on the training entry point. It loads checkpoint/tokenizer/dataset metadata directly, checks the dataset fingerprint, evaluates 24 deterministic held-out windows twice, and runs bounded same-seed generation over frozen Vietnamese, English, mixed, and numeric/punctuation prompts.

The repeat tolerance was frozen at absolute CE/BPB delta `<= 1e-6`. Both initial and final checkpoint evaluations observed exact repeat deltas of `0.0`.

| Metric | Step 0 | Step 1000 |
|---|---:|---:|
| Cross entropy | 217.4166666667 | 26.3229166667 |
| Bits/token | 313.6659468066 | 37.9759413367 |
| BPB | 74.6181738948 | 9.0341186964 |

Step-0 checkpoint SHA-256 is `9299896c51f2f0c62111f232c53a8ea69ed933d111c2f7a21d5203f991a9f6cf`. Final checkpoint SHA-256 is `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`. Baseline training is wired to refuse execution unless the exact independently evaluated step-0 checkpoint hash/config/tokenizer/dataset fingerprint/seed match.

Generation sanity PASS means only: finite logits, valid token IDs, successful decode, deterministic same-seed output, and bounded length. It does not imply good language quality, reasoning, factuality, or chatbot capability.

## P0.8 — Baseline-0

Status: **PASS / FREEZE**.

Frozen identity:

- plain decoder-only Transformer; learned positional embedding; GELU MLP; tied LM head;
- vocabulary 16,384; `d_model=320`; 8 heads; 4 layers; MLP expansion 4x;
- exact parameter count: **10,339,200**;
- context 512; micro-batch 1; gradient accumulation 2; effective batch 2 contexts / 1,024 tokens per optimizer step;
- AdamW, learning rate `3e-4`, weight decay `0.1`, 5% linear warmup then cosine decay to 10% peak, gradient clip 1.0;
- seed 2026; 1,000 optimizer steps; 1,024,000 training tokens;
- MindForge BPE 16,384; deterministic 1M development pool;
- Intel XPU, BF16; validation every 100 steps plus step 0; checkpoint at step 500 and final.

The 11-point validation curve improves monotonically to the best/final BPB `9.0341186964`; final-vs-best reversal is `0`. Relative final BPB improvement from step 0 is **87.892871%**, far above the frozen 5% P0.8 threshold. The step-500 checkpoint reload/resume path passed, the final checkpoint reload/evaluation matched training BPB exactly, and generation sanity passed.

## Local research economics

- Wall-clock training time: **91.3329 s** for 1,024,000 training tokens.
- Equivalent wall-clock per 1M training tokens: approximately **89.19 s** on this run.
- Warmup excluded from throughput summary: 10 optimizer steps.
- Measured timing steps: 990.
- Mean throughput: **13,437.02 tokens/s**.
- Median throughput: **13,477.86 tokens/s**.
- Initial XPU allocated memory: **41,377,792 bytes**.
- Peak XPU allocated memory: **253,053,952 bytes**.
- Final XPU allocated memory: **124,160,000 bytes**.
- Final checkpoint: **62,100,623 bytes**, SHA-256 `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`.

The first 100-step block ran unusually fast (~23.0k median tokens/s), then sustained blocks varied non-monotonically rather than progressively degrading: step 101-500 medians were ~13.3-13.8k, step 501-900 ~11.2-14.9k, and the final block ~12.2k. No XPU reset, OOM, NaN/Inf, or allocator runaway occurred. Because thermal/power telemetry was deliberately not added, the early-to-sustained clock change is recorded as a caveat rather than assigned a causal explanation.

## Failure evidence retained

1. Hugging Face dataset endpoints repeatedly reset during corpus acquisition. Before comparative results, protocol revision 1 switched transport to official Wikimedia dumps without changing source family, split, metrics, or decision rules.
2. The original tokenizer smoke BPB did not guarantee the same UTF-8 spans across tokenizers. Protocol revision 2 corrected this; the old BPB values are superseded and not used for P0.3.
3. The first standalone-evaluator CLI execution wrote valid evidence but then failed while printing Vietnamese text to a Windows `cp1252` console. Terminal output was changed to ASCII-escaped JSON; evidence files remain UTF-8. The same checkpoint rerun passed.
4. The first Baseline-0 preflight attempt stopped before training because it checked the wrong JSON fingerprint field name. The check was corrected; no model update occurred in that failed attempt.
5. An otherwise-valid Baseline-0 run omitted requested initial/final allocated-memory telemetry. Protocol revision 3 added only telemetry/evidence wiring, and the exact frozen run was repeated without hyperparameter or threshold changes. The objective learning result reproduced exactly.

## Phase 0 gate table

| Gate | Status | Evidence |
|---|---|---|
| P0.1 Hardware feasibility | PASS / FROZEN | Prior local hardware validation |
| P0.2 Practical model envelope | PASS / FROZEN | Prior model-envelope validation; feasibility envelope only |
| P0.3 Tokenizer assumption | PASS / FROZEN | Corrected same-byte comparison + reproducibility audit |
| P0.4 Dataset viability | PASS / FROZEN | 1M selected by frozen 1M-vs-10M rule |
| P0.5 Training reproducibility | PASS / FROZEN | Prior three-seed + resume validation |
| P0.6 Evaluation harness viability | PASS / FROZEN | Standalone initial/final deterministic evaluator |
| P0.7 Experiment protocol | PASS / FROZEN | Prior protocol/provenance evidence |
| P0.8 Baseline-0 | PASS / FROZEN | Frozen 10.3392M real-language XPU/BF16 baseline |
| P0.9 Continual-learning feasibility | REVISE | Existing probe does not expose untreated forgetting |
| P0.10 Memory hypothesis probe | BLOCKED / STOP | No controlled memory-value signal; do not start memory work |

Overall Phase 0: **REVISE**.

## Raw evidence

- `experiments/results/phase0_tokenizer_comparison.json`
- `experiments/results/phase0_tokenizer_integrity.json`
- `experiments/results/phase0_dataset_viability.json`
- `experiments/results/phase0_real_language_initial_eval.json`
- `experiments/results/phase0_real_language_eval.json`
- `experiments/results/phase0_baseline0.json`

Raw Wikimedia dumps, normalized corpus files, token arrays, and model checkpoints remain ignored and are not committed.

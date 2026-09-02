# Phase 0 — Real Language Baseline Protocol

Protocol status: **FROZEN BEFORE COMPARATIVE RESULTS**

Base commit: `1b0d9b016c2eaff8922693f7f6d496b597f29927`

This protocol covers only P0.3 tokenizer assumption, P0.4 dataset viability, P0.6 evaluation-harness viability, and P0.8 Baseline-0. P0.9, P0.10, and Phase 1 are explicitly out of scope.

## Corpus sources

Primary source: official Wikimedia Wikipedia XML dumps, fixed snapshot `20260801`:

- Vietnamese: `https://dumps.wikimedia.org/viwiki/20260801/viwiki-20260801-pages-articles-multistream1.xml-p1p832082.bz2`.
- English: `https://dumps.wikimedia.org/enwiki/20260801/enwiki-20260801-pages-articles-multistream1.xml-p1p41242.bz2`.

Wikipedia article text is used because it is public, language-labelled, reproducible, and has explicit article provenance. Source article titles/IDs are retained in the local manifest. Wikipedia text is CC BY-SA; dump provenance is recorded with the result. No raw corpus is committed.

## Language mix and sampling

- 50% Vietnamese / 50% English by UTF-8 byte budget after normalization.
- Preserve article order from each dataset stream; do not random-web-scrape or cherry-pick articles.
- Normalize line endings to LF, Unicode NFC, strip NUL/control characters other than newline/tab, collapse runs of horizontal whitespace, and separate articles with two newlines.
- Build the mixed local corpus from equal normalized UTF-8 byte budgets per language. For staged token pools, take 64 deterministic contiguous token blocks spaced evenly across the full mixed training stream; this avoids a prefix-only pool being language-biased when the on-disk mixed file stores the two language halves sequentially.
- Local build target: enough source text for at least the 10M-token stage under the selected Baseline-0 tokenizer plus held-out validation. The 50M and 100M stages are not built/trained unless 10M evidence fails the P0.4 gate or shows no stable learning signal.

## Train/validation split

- Deterministic article-level split using SHA-256 of `<language>:<article-id>`.
- Validation when the first 16 bits of the digest fall in the lowest 5% of the range; otherwise train.
- Split is applied before concatenation to avoid chunk-level leakage of the same article.
- The final manifest records SHA-256 fingerprints of normalized train and validation bytes and the ordered article IDs used.

## Dataset-size sweep

Staged token budgets, measured after selecting the Baseline-0 tokenizer:

1. 1M training tokens.
2. 10M training tokens.
3. 50M only if 10M is insufficient or unstable.
4. 100M only if 50M evidence justifies the additional local cost.

For 1M vs 10M viability, the same smoke-model architecture and optimizer protocol are used; the training-token budget is held constant at 1M sampled training tokens so the comparison asks whether the larger source pool improves validation stability/generalization rather than merely buying more optimization steps. The 10M pool becomes the development-corpus candidate if it provides a real, stable learning curve without obvious validation reversal and is cheap enough to rebuild/rerun locally.

Frozen dataset-size decision rule:

- A stage is viable only if final validation BPB improves by at least 5% from step 0 and final BPB is no more than 2% worse than the best intermediate validation BPB (no material validation reversal).
- If both 1M and 10M are viable and 10M final BPB improves by less than 5% relative to 1M at the same training-token budget, select 1M as the smallest development corpus.
- If 1M fails viability and 10M passes, or 10M improves final BPB by at least 5%, select 10M.
- If 10M also fails, escalate to 50M before deciding P0.4. 100M remains conditional on 50M evidence.

## Tokenizer candidates

### A — existing tokenizer

`Qwen/Qwen2.5-0.5B` fast tokenizer, loaded from its published tokenizer files at a resolved Hugging Face commit. It is selected because Qwen2.5 is explicitly multilingual, covers Vietnamese and English, uses a byte-level/fallback-capable tokenizer path, and is Apache-2.0 licensed. Exact resolved commit, vocab size, special tokens, normalization/pre-tokenization metadata, and dependency versions are recorded.

### B — MindForge tokenizer

One byte-level BPE tokenizer trained only on the Phase-0 training corpus:

- implementation: Hugging Face `tokenizers`;
- vocab size: 16,384;
- minimum frequency: 2;
- byte-level pre-tokenizer/decoder;
- NFC-normalized corpus input;
- special tokens: `<|endoftext|>`, `<|unk|>`;
- no tokenizer framework or production abstraction is added.

## Tokenizer evaluation

Held-out validation is partitioned into Vietnamese-only, English-only, and deterministic mixed samples. Report for each candidate:

- tokens/character;
- tokens/UTF-8 byte;
- tokens/whitespace-delimited word;
- sequence expansion ratio relative to the MindForge tokenizer (MindForge = 1.0);
- vocabulary utilization on held-out text;
- unknown/fallback count;
- explicit Vietnamese diacritic, punctuation, numeric, and Vietnamese/English code-switch probes.

Tokenizer choice is not decided by vocabulary size or cross-tokenizer perplexity.

Frozen tokenizer decision rule:

1. A tokenizer with invalid IDs, non-round-tripping ordinary UTF-8 held-out/probe text, or unexpected `<unk>` use on the frozen probes cannot be selected.
2. Select the existing tokenizer only if its smoke-model BPB is at least 5% lower than MindForge BPE **and** its mixed held-out tokens/byte is no worse than 10% above MindForge BPE.
3. Otherwise select MindForge BPE if its smoke-model BPB is no worse than 5% above the existing tokenizer and its mixed held-out tokens/byte is no worse than 25% above the existing tokenizer. This tolerance explicitly prices the much smaller vocabulary/model footprint and project-local reproducibility.
4. If neither rule selects a tokenizer, P0.3 is REVISE rather than hand-tuned.

## Comparable language-model metric

Primary cross-tokenizer model metric: **bits per byte (BPB)** on the exact same held-out UTF-8 text bytes.

For an evaluated token sequence with total negative log-likelihood `NLL_nats` over predicted tokens and `B` UTF-8 bytes represented by those predicted spans:

`BPB = NLL_nats / (ln(2) * B)`.

Token-level cross-entropy, bits/token, and perplexity may be reported within a tokenizer but are not used to rank tokenizers with different token units.

## Model architecture

Plain decoder-only Transformer descendant of the existing Phase-0 model:

- token embedding + learned positional embedding;
- pre-norm causal self-attention/MLP residual blocks;
- GELU MLP;
- final layer norm;
- tied LM head;
- no RoPE experiment, MoE, memory, LoRA, retrieval, routing, or custom flash-attention architecture.

Smoke tokenizer-comparison model:

- `d_model=192`, `n_heads=6`, `n_layers=4`, `ff_mult=4`;
- context 256;
- micro-batch 2;
- BF16 on XPU;
- same architecture dimensions for both tokenizers; actual parameter counts are reported because vocabulary size differs;
- 256 optimization steps per tokenizer, fixed 131,072 training-token budget (`256 * 2 * 256`), seed 4242.

Baseline-0 model:

- MindForge/XPU Phase-0 boring Transformer;
- exact config: vocab `16,384`, `d_model=320`, `n_heads=8`, `n_layers=4`, MLP expansion `4x`, learned positional embedding, tied LM head;
- exact parameter count: `10,339,200`;
- context 512;
- micro-batch 1, gradient accumulation 2 (effective batch 2 contexts);
- BF16 on Intel XPU;
- seed 2026.

Baseline-size selection is frozen before the final run. The ~10M scale is selected over ~25M/~50M because the earlier hardware envelope already established ~10M/context-512 as materially cheaper than ~50M/context-1024, while the tokenizer and P0.4 smoke runs already show a strong real-language learning signal at <=5M parameters. P0.8 needs a repeatable research control, not the largest model that fits. A ~25M/~50M run is therefore not required unless this frozen ~10M Baseline-0 fails to produce a healthy learning curve for technical/scientific reasons. The previously validated ~50M/context-1024 envelope remains a hardware capability, not a mandatory Phase-0 training spend.

## Optimization and schedules

Smoke tokenizer comparison and dataset-size sweep:

- AdamW;
- learning rate `3e-4`;
- weight decay `0.1`;
- linear warm-up for 5% of steps, cosine decay to 10% of peak LR;
- gradient clipping at global norm 1.0;
- no hyperparameter tuning after comparative results.

Baseline-0:

- AdamW;
- learning rate `3e-4`;
- weight decay `0.1`;
- 5% linear warm-up then cosine decay to 10% peak;
- gradient clipping 1.0;
- 1,000 optimizer steps;
- 1,024 tokens/optimizer step effective (`context 512 * micro-batch 1 * accumulation 2`);
- total training-token budget: 1,024,000 tokens.
- checkpoint interval: step 500 and final step 1000; checkpoint weights remain local/ignored, while size/hash/metadata are committed as evidence.

## Evaluation cadence and metrics

- Fixed validation windows selected before training.
- Evaluate at step 0 and every 100 optimizer steps for Baseline-0, plus final step.
- Baseline/evaluator uses 24 evenly spaced deterministic validation windows across the selected tokenizer's held-out stream.
- Metrics: validation token cross-entropy, bits/token, BPB, NaN/Inf checks.
- Generation harness is independent of the training loop and uses frozen prompt strings for Vietnamese prose, English prose, factual-shaped prefix, punctuation/numeric text, and mixed Vietnamese/English.
- Generation sanity is a path/correctness test only: valid token IDs, finite logits, deterministic same-seed output, checkpoint can generate. No chat-quality claim.
- Independent repeated-evaluation tolerance is frozen at absolute delta `<= 1e-6` for cross-entropy and BPB on the same checkpoint/windows/config. Exact equality is accepted when naturally observed.

## Performance measurement

- At least 10 warm-up optimizer steps before throughput is summarized.
- Multi-step timing windows, synchronized with `torch.xpu.synchronize()` before/after timing.
- Baseline summary reports mean, median, and standard deviation across measured per-step throughput samples after warm-up.
- Record wall-clock, periodic loss, tokens/sec, and XPU initial/peak/final allocated memory through the full run.

## PASS / REVISE criteria

### P0.3 Tokenizer

PASS if both candidates are reproducibly measured on the same held-out text; fallback/unknown behavior is safe; and one choice can be justified by compression + normalized BPB + implementation cost without using cross-tokenizer perplexity as the deciding metric. Otherwise REVISE.

### P0.4 Dataset

PASS if deterministic article-level split/fingerprints exist, no direct article-ID overlap exists, at least the 1M and 10M staged pools are characterized, a real validation learning curve is observed, and one smallest practical development corpus can be chosen from evidence. If 10M does not provide a stable signal, escalate to 50M before deciding. Otherwise REVISE.

### P0.6 Evaluation

PASS if an independent Phase-0 eval command measures cross-entropy/bits-token/BPB for checkpoints, produces deterministic generation for frozen prompts, rejects invalid/non-finite outputs, and can distinguish step-0 vs trained checkpoint in the expected direction. Otherwise REVISE.

### P0.8 Baseline-0

PASS if the frozen plain Transformer run on real bilingual text completes without NaN/OOM, final validation BPB improves by at least 5% versus step 0, checkpoint/resume/evaluation/generation paths work, and the run records wall-clock, synchronized multi-step throughput statistics, memory, config, tokenizer, dataset fingerprint, seed, and curve. Otherwise REVISE.

## Protocol revisions

### Protocol revision 1 — corpus transport only

Reason: before any corpus/tokenizer/model comparative result was generated, the local machine repeatedly received connection resets from `huggingface.co` for both the `wikimedia/wikipedia` dataset endpoint and Hub API (`curl` and Python client), while official `dumps.wikimedia.org` was reachable. The Qwen tokenizer file endpoint was independently reachable/cached.

Before:

- Hugging Face wrapper `wikimedia/wikipedia`, configurations `20231101.vi` and `20231101.en`.

After:

- official Wikimedia `viwiki` and `enwiki` `20260801` pages-articles multistream split-1 XML/BZip2 files listed above.

Unchanged: Wikipedia source family/license, 50/50 language budget, normalization, article-level deterministic split, tokenizer candidates, model/training budgets, metrics, and all PASS/REVISE criteria.

### Protocol revision 2 — tokenizer BPB fairness correction

Reason: the first P0.3 smoke implementation selected evenly spaced validation windows in each tokenizer's token stream. Although both streams came from the same frozen validation corpus, different token boundaries meant the scored UTF-8 bytes were not guaranteed to be identical across tokenizers. This violates the already-frozen requirement that cross-tokenizer BPB use the exact same held-out bytes.

Before: 12 tokenizer-specific token windows from the full validation token arrays.

After: 12 deterministic 512-byte-position snippets from the same frozen `validation.mixed.txt`; UTF-8 boundary fragments are dropped once to create one shared list of text strings. Each tokenizer scores exactly those same strings. `<|endoftext|>` is used as a fixed BOS input so every token representing each sample is predicted, and BPB divides summed NLL by the exact original UTF-8 bytes of those shared strings.

Unchanged: tokenizer candidates, smoke architecture, seed, optimizer, training-token budget, compression metrics, decision thresholds, and the prohibition on using cross-tokenizer perplexity. P0.4 is not rerun unless this corrected P0.3 comparison changes the selected tokenizer or exposes another correctness defect.

### Protocol revision 3 — standalone step-0 evidence and memory telemetry

Reason: the final P0.6 integrity review required the initial Baseline-0 state to be evaluated by the standalone evaluator before training, rather than relying on an in-process step-0 metric. The first otherwise-valid Baseline-0 run also recorded peak XPU allocation but omitted the requested initial/final allocated-memory observations.

After correction, `baseline-init` creates one frozen step-0 checkpoint, the standalone evaluator records its hash/metrics, and Baseline-0 refuses to train unless that exact hash, dataset fingerprint, tokenizer, model config, and seed match the independent step-0 evidence. Initial/peak/final XPU allocated memory and descriptive first-vs-last sustained throughput summaries are recorded. The final evidence run repeats the exact same frozen model, optimizer, seed, token budget, data pool, and thresholds; no hyperparameter or decision-rule tuning is introduced.

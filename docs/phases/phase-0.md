# Phase 0 — Foundation Validation

## Purpose

Phase 0 existed to falsify uncertain assumptions before building the reusable MindForge kernel. It measured the target hardware, practical model envelope, tokenizer/data strategy, training reproducibility, evaluation path, Baseline-0, and the prerequisites for continual-learning/memory research.

## Final gate table

| Gate | Final status | Meaning |
|---|---|---|
| P0.1 Hardware feasibility | PASS / FROZEN | Intel XPU training works on the target machine |
| P0.2 Practical model envelope | PASS / FROZEN | Local model/context envelopes were measured |
| P0.3 Tokenizer assumption | PASS / FROZEN | MindForge byte-level BPE 16,384 selected |
| P0.4 Dataset viability | PASS / FROZEN | Deterministic 1M-token development pool selected |
| P0.5 Training reproducibility | PASS / FROZEN | Multi-seed and resume behavior validated |
| P0.6 Evaluation harness viability | PASS / FROZEN | Independent deterministic checkpoint evaluation validated |
| P0.7 Experiment protocol | PASS / FROZEN | Machine-readable provenance/evidence established |
| P0.8 Baseline-0 | PASS / FROZEN | Frozen real-language local baseline established |
| P0.9 Continual-learning feasibility | STOP / FROZEN | Bounded search did not yield a valid forgetting substrate |
| P0.10 Memory hypothesis probe | STOP / FROZEN | No controlled memory-value substrate; custom memory work not opened |

## Proven foundation

The verified local baseline is:

- target machine: Intel Core Ultra 7 258V with Intel Arc 140V and 32 GB class system memory;
- primary local training backend: Intel XPU;
- validated mixed precision: BF16 on XPU;
- tokenizer: MindForge byte-level BPE, vocabulary 16,384;
- data: deterministic Vietnamese/English Wikimedia corpus, snapshot `20260801`;
- corpus fingerprint: `c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696`;
- selected development pool: 1M tokens;
- Baseline-0: decoder-only Transformer, 10,339,200 parameters, context 512;
- Baseline-0 final validation BPB: `9.0341186964`, down from `74.6181738948` at step 0;
- checkpoint/resume: validated, including the step-500 resume path;
- final Baseline-0 checkpoint SHA-256: `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`;
- independent evaluator: repeated CE/BPB evaluation with observed repeat deltas `0.0` under the frozen `1e-6` tolerance;
- experiment provenance: deterministic dataset/tokenizer/checkpoint fingerprints and machine-readable JSON evidence.

Detailed evidence remains in the historical validation reports and `experiments/results/`.

## Stopped hypotheses

P0.9 attempted to establish a reproducible, controlled catastrophic-forgetting signal before testing any anti-forgetting treatment. The earlier synthetic `+1/+2` task produced positive transfer. A bounded replacement search then evaluated three pre-registered real/natural-language families. None satisfied the frozen qualification rule without post-outcome tuning, so P0.9 is STOP/FROZEN.

P0.10 depended on a controlled memory-value/forgetting substrate. Because P0.9 did not establish one, MindForge did not open a custom memory experiment. P0.10 is therefore STOP/FROZEN.

The raw and narrative evidence is preserved unchanged as falsification history. See [the deferred continual-learning/memory archive](../research/deferred/continual-learning-memory.md).

## Phase 0 decision

```text
CORE FOUNDATION: PASS
CONTINUAL-LEARNING RESEARCH HYPOTHESIS: STOP
CUSTOM MEMORY RESEARCH HYPOTHESIS: STOP
```

The Phase-0 closure does not relabel stopped hypotheses as successful. It separates the validated engineering foundation from research hypotheses that failed their bounded gates.

Overall project decision:

```text
PROCEED WITH COMPACT LOCAL LLM KERNEL DIRECTION
```

The active kernel remains deliberately small:

```text
dataset
→ tokenizer
→ Transformer
→ training
→ checkpoint
→ evaluation
→ generation
```

Continual learning, explicit memory and adaptive/pattern mechanisms are deferred research rather than active kernel requirements.

## Evidence map

- [Hardware and early Phase-0 evidence](phase-0-local-validation.md)
- [Real-language tokenizer/data/evaluator/Baseline-0](phase-0-real-language-validation.md)
- [Continual-learning frozen protocol](phase-0-continual-protocol.md)
- [Continual-learning STOP evidence](phase-0-continual-validation.md)
- [Consolidated QA state](phase-0-qa.md)

# Model Kernel Baseline Contract

Status: **MK-0 FROZEN BASELINE**

Baseline ID: **B0 — MKS-1 Compact Transformer**

## 1. Purpose

B0 is the control model for future Model Kernel studies.

MK-0 does not modify B0. Future model interventions must be compared against B0 or against a prospectively justified derivative while preserving a clear causal comparison.

## 2. Architectural parent

B0 is inherited from the current MKS-1 PASS/CLOSED state.

Authoritative architectural sources:

- docs/research/model-kernel-separation-closure.md
- docs/research/mindforge-architecture-invariants.md
- docs/research/model-contract-adr.md
- mindforge/config.py
- mindforge/model.py

At MK-0 creation, the relevant source blobs on research/model_kernel were:

- mindforge/config.py: 91a3f92ea2449a82fb2d03e0442cbf6e72980caf
- mindforge/model.py: 98b4368c2b594082f0b84cd010e2bcc3548ab3fc
- architecture invariants: bc39aa7a663f40cc8e56b0ec26704a72a4ed9c65
- model-contract ADR: fadc9fcd208d72b6d4ae457304f3092b2ab539df
- MKS closure document: f5f61d64b1cdf68036f510742d21ce280b56c3fb

## 3. B0 model configuration

Default ModelConfig:

| Field | Frozen B0 value |
|---|---:|
| vocab_size | 16,384 |
| d_model | 320 |
| n_heads | 8 |
| n_layers | 4 |
| max_context | 512 |
| ff_mult | 4 |
| dropout | 0.0 |

Architecture:

- decoder-style causal language model implemented with PyTorch TransformerEncoderLayer blocks under a causal mask;
- learned token embeddings;
- learned positional embeddings;
- pre-norm Transformer blocks;
- GELU feed-forward activation;
- final LayerNorm;
- bias-free LM head;
- LM-head weight tied to token-embedding weight.

Default parameter count validated by MKS-1:

**10,339,200 parameters**

## 4. Runtime contract

The frozen MKS-1 TokenModel runtime contract v0 requires:

~~~
context_limit
training
__call__(torch.Tensor) -> torch.Tensor
train(mode)
eval()
~~~

The contract is explicitly PyTorch-bound v0 and is not claimed to be a universal permanent ABI.

vocab_size is concrete model/config metadata, not a required TokenModel runtime-contract member.

## 5. Proven compatibility evidence

MKS-1 closure records:

- full pytest: 61 passed, 0 failed, 0 skipped;
- focused MKS tests: 10 passed;
- compileall: PASS;
- git diff --check: PASS;
- Phase-2 summarize/check: PASS;
- checkpoint reconstruction/restore: PASS;
- deterministic evaluation replay: PASS for the current replay configuration;
- deterministic greedy generation replay: exact across repeated runs;
- default parameter count: 10,339,200.

Canonical Phase-2 training was not rerun during MKS closure.

## 6. B0 scientific role

B0 is intentionally plain.

It does not contain:

- learned decision-state bottleneck;
- semantic auxiliary heads;
- candidate-ranking head;
- learned calibration/cardinal-value head;
- episodic memory module;
- retrieval admission controller;
- continual-learning controller;
- optimizer-boundary controller;
- invariant/counterfactual objective;
- sparse entity topology;
- NEXUS scheduler;
- ArcLLM runtime-specific model logic.

Absence of these mechanisms is a feature of the control condition.

## 7. Future comparison invariants

Before any future Model Kernel experiment, the protocol must declare which B0 properties remain fixed.

Unless a study explicitly targets one of them, preserve:

- tokenizer/vocabulary contract;
- context limit;
- training/evaluation data split policy;
- parameter/compute budget matching rule;
- optimizer/training budget;
- random-seed policy;
- evaluation metrics;
- checkpoint/evaluation/generation semantics;
- device/runtime measurement boundary.

If an intervention changes parameter count or compute, it must include a matched-capacity or matched-compute control when the difference could explain the outcome.

## 8. Baseline reconstruction gate

Before the first scientific Model Kernel training run, B0 must be reconstructable from the branch used for that experiment.

Minimum preflight:

1. instantiate default ModelConfig;
2. verify parameter count = 10,339,200;
3. run the frozen compatibility/unit tests relevant to model construction and runtime contract;
4. verify an existing compatible checkpoint can still be loaded/evaluated if that checkpoint is part of the comparison;
5. record Git SHA, config, dataset/version, seed, runtime/device, and artifact hashes.

This preflight is evidence integrity, not a new scientific result.

## 9. MK-0 boundary

No B0 code or behavior is changed in MK-0.

~~~
B0 = FROZEN CONTROL
MODEL TRAINING = NOT AUTHORIZED
MK-1 = NOT OPENED
~~~
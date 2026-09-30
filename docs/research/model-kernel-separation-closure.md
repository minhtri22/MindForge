# Model / Kernel Separation MKS-1 - Closure

Status: **PASS / CLOSED - FULL LOCAL EVIDENCE VALIDATED**

Branch: `refactor/mks-1-model-kernel-separation`

Starting architectural reference: `1b0392a2550ecee0e65941e0590f21507797610d`

MKS implementation head: `d17a5ed8eb5083049411cfafa382204edaafa79b`

Contract correction commit: `b25802e3cb3167c6811d9dc3ff51e60996a95fa6`

Closure evidence commit: `2c1d0bcf02875f6bb3ed3c81f9d6f731274e6285`

## Status

MKS-1 is closed at the contract level. The earlier REVISE state was caused by missing full local evidence in a sandbox-only closure attempt, not by a known model/kernel behavior mismatch.

The subsequent real-local validation established:

```text
MKS implementation: PASS
Model Contract ADR: PASS
Full regression: PASS
Phase-2 compatibility: PASS
Checkpoint compatibility: PASS
Evaluation replay: PASS
Generation replay: PASS
```

## ADR decision

ADR: `docs/research/model-contract-adr.md`

Final framework decision:

```text
PYTORCH-BOUND V0
```

Final required `TokenModel` contract:

```text
context_limit
training
__call__(torch.Tensor) -> torch.Tensor
train(mode)
eval()
```

`vocab_size` is not a required `TokenModel` member. `TransformerLM.vocab_size` and `ModelConfig.vocab_size` still exist as concrete-model/config metadata.

The ADR does not authorize a plugin system, adapter framework, framework-neutral ABI, physical package move, PPF integration, or Track A work.

## Full local validation environment

```text
Python: 3.12.10
PyTorch: 2.12.1+xpu
XPU available: YES
CUDA available: NO
OS: Windows 11
default parameter count: 10,339,200
```

## Regression results

```text
pytest tests/ -q: PASS
passed: 61
failed: 0
skipped: 0
focused MKS: PASS (10 passed)
compileall: PASS
git diff --check: PASS
```

## Phase-2 compatibility

Canonical Phase-2 training was not rerun.

Existing canonical summary:

```text
status: PASS
baseline mean BPB: 10.537770964151376
treatment mean BPB: 10.938692122871304
paired mean absolute effect: 0.40092115871992995
mean relative effect: 0.038041814491547137
manifest_hash: f3db682e905b9aa4aa8c6da557070d86d79fac9e0aeb02e4e9295d126b8fa968
```

Phase-2 summarize: PASS

Phase-2 check: PASS

## Real checkpoint replay

Checkpoint:

```text
runs\phase2-lr-sweep-v1\baseline\seed-101\checkpoint-step-200.pt
```

Replay result:

```text
format_version: 1
model reconstruction: PASS
parameter count: 10,339,200
state restore: PASS
optimizer restore: PASS
step: 200
```

## Evaluation replay

```text
device: cpu
dtype: float32
CE: 32.110002517700195
BPB: 10.473420541746082
repeat delta CE: 0.0
repeat delta BPB: 0.0
classification: DETERMINISTIC CURRENT REPLAY ONLY
```

This is not upgraded to historical parity verified because there was no exact pre-MKS fixture for this exact replay configuration.

## Generation replay

```text
prompt: The quick brown fox
seed: 42
max_new_tokens: 20
temperature: 0
token output exact across both runs: YES
text output exact across both runs: YES
```

## Source boundary audit

Runtime-facing `evaluate.py` and `generate.py` depend on `TokenModel`, not on `TransformerLM` internals.

Training/checkpointing remain research/tooling paths and use `create_model(ModelConfig)` for concrete model construction.

No PPF semantics, plugin framework, extension registry, model registry, external adapter layer, host/mobile concepts, or physical package restructure were added.

## Provenance hashes

These are distinct provenance values:

```text
manifest_hash:
f3db682e905b9aa4aa8c6da557070d86d79fac9e0aeb02e4e9295d126b8fa968

summary_file_sha256:
58335391E17FE1470C165BF4E94BF8A91D8E3812F2ECB2E945ADE50452FC0693

checkpoint_sha256:
6561FA2B354B317CF173FAAA5A5CC236A4584CB047DF3AFDB2871DABAE01778E

checkpoint_bytes:
62115779
```

## Gate table

| Gate | Status | Evidence |
|---|---|---|
| G1 - reason to separate now | PASS | concrete direct model/runtime coupling demonstrated |
| G2 - minimal/scoped model contract | PASS | ADR frozen; unused `vocab_size` removed; PyTorch-bound v0 scope explicit |
| G3 - compatibility tests | PASS | full pytest 61 passed; focused MKS 10 passed |
| G4 - Transformer conformance/construction | PASS | structural conformance + `create_model` path |
| G5 - frozen evidence regression | PASS | full regression, Phase-2 summarize/check, checkpoint/eval/generation replay |
| G6 - no PPF/plugin semantics | PASS | contract remains PPF/plugin-free |
| G7 - no speculative plugin framework | PASS | none introduced |

## Final closure decision

```text
MKS-1: PASS / CLOSED
TECHNICAL DEBT: RESOLVED AT CONTRACT LEVEL
G2 DESIGN BLOCKER: RESOLVED
G5 EVIDENCE BLOCKER: RESOLVED
MODEL CONTRACT: PYTORCH RUNTIME V0 / MINIMIZED
TRANSFORMER MATH: UNCHANGED
DEFAULT PARAMETER COUNT: 10,339,200
CHECKPOINT FORMAT: UNCHANGED
EVALUATION SEMANTICS: UNCHANGED
GENERATION SEMANTICS: UNCHANGED
CANONICAL PHASE-2 TRAINING RERUN: NO
PPF MODIFIED: NO
PHYSICAL PACKAGE MOVE: NO / NOT REQUIRED
TRACK A STARTED: NO
```

## Residual debt

- Future model-contract evolution remains evidence-gated.
- Physical package separation remains deferred unless independently justified.

## Deferred backlog - not executed

```text
N3 - Track A Foundation Protocol: PLANNED / NOT STARTED
N4 - Compact-model scaling envelope: PLANNED / NOT STARTED
N5 - Cross-device reproducibility: PLANNED / NOT STARTED
```

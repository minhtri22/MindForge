# Model / Kernel Separation MKS-1 — Closure Attempt

Status: **REVISE — G2 RESOLVED; G5 FULL LOCAL EVIDENCE STILL REQUIRED**

Branch: `refactor/mks-1-model-kernel-separation`

Starting closure HEAD: `8b10b49f8a5aef8e1911655a286c6ae59824126a`

Contract decision/correction commit: `b25802e3cb3167c6811d9dc3ff51e60996a95fa6`

Starting architectural reference: `1b0392a2550ecee0e65941e0590f21507797610d`

## Closure objective

This closure attempt followed the required sequence:

```text
N1 — full local regression/evidence validation
N2 — resolve Model Contract ADR
only if required — tiny bounded correction
revalidate
close or remain REVISE
```

The task did not run Track A, PPF, model scaling, package restructuring, plugin architecture, external adapters, ONNX, quantization, continual learning, or canonical Phase-2 training.

## Environment result for N1

A normal Git checkout could not be created in the execution sandbox because DNS resolution for `github.com` failed:

```text
fatal: unable to access 'https://github.com/minhtri22/MindForge.git/':
Could not resolve host: github.com
```

The GitHub connector was therefore used to inspect and modify the exact branch. It can access tracked UTF-8 repository content but does not provide the normal local checkout/runtime environment required for the complete historical pytest suite and real binary checkpoint replay.

Consequently this task does **not** claim execution of:

```text
full repository pytest tests/ -q
Phase-2 summarize command on a complete checkout
Phase-2 check command on a complete checkout
real historical .pt checkpoint evaluation/generation replay
```

These remain the MKS-G5 closure requirements.

## What was executable in sandbox

The previously reconstructed exact MKS changed subset remained available locally. Before and after the bounded contract correction, focused acceptance tests executed successfully.

Post-correction result:

```text
9 passed
compileall PASS
```

Focused coverage includes:

- default parameter count `10,339,200`;
- structural runtime-contract conformance;
- exact direct-vs-factory forward parity;
- invalid input/context validation behavior;
- deterministic one-step CPU training parity;
- `KernelConfig` compatibility;
- focused checkpoint v1 round-trip;
- evaluator runtime path;
- deterministic greedy generation.

This evidence is useful but does not substitute for MKS-G5 full historical evidence.

## Phase-2 historical evidence inspection

Tracked Phase-2 canonical artifacts remain present in the repository. The tracked canonical summary inspected after the MKS correction remains:

```text
status: PASS
experiment_id: phase2-lr-sweep-v1
manifest_hash: f3db682e905b9aa4aa8c6da557070d86d79fac9e0aeb02e4e9295d126b8fa968
baseline mean BPB: 10.537770964151376
treatment mean BPB: 10.938692122871304
paired mean absolute effect: 0.40092115871992995
```

No canonical Phase-2 training run was performed and no Phase-2 evidence file was changed by this task.

This is a static artifact integrity check, **not** a substitute for executing `mindforge.experiment summarize` and `check` in the real checkout.

## N2 — Model Contract ADR

ADR:

`docs/research/model-contract-adr.md`

### Decision — `vocab_size`

**REMOVE FROM THE REQUIRED RUNTIME CONTRACT.**

Repository/runtime review showed no current evaluator/generator consumer of `TokenModel.vocab_size`. The concrete model continues to expose vocabulary metadata and `ModelConfig.vocab_size` remains unchanged.

### Decision — framework binding

**PYTORCH-BOUND V0.**

`TokenModel` is explicitly a bounded contract for current proven PyTorch runtime consumers. It is not a universal permanent model ABI.

Current required surface after the correction:

```text
context_limit
training
__call__(torch.Tensor) -> torch.Tensor
train(mode)
eval()
```

The contract will be reconsidered only when a second proven model/runtime cannot satisfy v0 without inappropriate PyTorch lifecycle emulation, or a demonstrated current consumer needs a missing capability.

No framework-neutral redesign was authorized or implemented.

## Tiny bounded correction

Production code changed in this closure task:

```text
mindforge/model_contract.py
```

Change:

- remove `vocab_size` from `TokenModel` required protocol surface;
- explicitly document the protocol as a PyTorch runtime contract v0.

Test adjustment:

```text
tests/test_mks_model_kernel.py
```

The concrete `TransformerLM.vocab_size` property remains tested as concrete-model behavior, not as a runtime-contract requirement.

No Transformer mathematics, checkpoint schema, evaluator formula, generation algorithm, tokenizer behavior, optimizer semantics, model parameter count, or Phase-2 semantics changed.

## Source-boundary result

Current intended boundary remains:

```text
evaluate.py -> TokenModel -> context_limit + forward/train/eval
generate.py -> TokenModel -> context_limit + forward/eval
train.py -> create_model(ModelConfig) [research/tooling]
checkpoint.py -> create_model(ModelConfig) [research/tooling]
TransformerLM -> owns Transformer internals
```

No PPF semantics were introduced into the runtime contract.

No `PluginManager`, `ExtensionRegistry`, `HookBus`, `CapabilityRegistry`, `ProviderRegistry`, `ServiceContainer`, `EventBus`, model registry, external-model adapter, or physical `kernel/`/`models/` package structure was introduced.

## Gate reassessment

| Gate | Status | Evidence |
|---|---|---|
| MKS-G1 — reason to separate now | PASS | concrete direct model/runtime coupling demonstrated earlier |
| MKS-G2 — minimal/scoped model contract | **PASS** | ADR frozen; unused `vocab_size` removed; PyTorch v0 scope explicit |
| MKS-G3 — compatibility tests | PASS (focused) | tests frozen before refactor; post-correction focused UAT 9/9 PASS |
| MKS-G4 — Transformer conformance/construction | PASS | structural conformance + single `create_model` path |
| MKS-G5 — frozen evidence regression | **REVISE** | full checkout pytest, executable Phase-2 summarize/check, and real checkpoint replay unavailable in sandbox |
| MKS-G6 — no PPF/plugin semantics | PASS | contract remains PPF/plugin-free |
| MKS-G7 — no speculative plugin framework | PASS | none introduced |

## Final closure decision

```text
MKS-1: REVISE
TECHNICAL DEBT: PARTIALLY RESOLVED
G2 DESIGN BLOCKER: RESOLVED
G5 EVIDENCE BLOCKER: OPEN
MODEL CONTRACT: PYTORCH RUNTIME V0 / MINIMIZED
TRANSFORMER MATH: UNCHANGED
DEFAULT PARAMETER COUNT: 10,339,200
CHECKPOINT FORMAT: UNCHANGED
EVALUATION SEMANTICS: UNCHANGED
GENERATION SEMANTICS: UNCHANGED
CANONICAL PHASE-2 TRAINING RERUN: NO
PPF MODIFIED: NO
PHYSICAL PACKAGE MOVE: NO
TRACK A STARTED: NO
```

## Smallest remaining blocker

Run N1 on the real Windows checkout at `D:\WORK\RESEARCH\MindForge` on this branch:

```powershell
.venv\Scripts\python.exe -m pytest tests/ -q
.venv\Scripts\python.exe -m compileall mindforge tests -q
git diff --check
.venv\Scripts\python.exe -m mindforge.experiment summarize configs/phase2_manifest.json
.venv\Scripts\python.exe -m mindforge.experiment check configs/phase2_manifest.json --baseline-bpb-cv-max 0.10
```

Then replay one existing real compatible checkpoint through load/evaluate/deterministic-generate.

Do not rerun the six canonical Phase-2 training runs.

If all of those pass, no further architecture work is currently indicated and MKS-1 can be reviewed for `PASS / CLOSED` at the contract level.

## Deferred backlog — not executed

```text
N3 — Track A Foundation Protocol: PLANNED / NOT STARTED
N4 — Compact-model scaling envelope: PLANNED / NOT STARTED
N5 — Cross-device reproducibility: PLANNED / NOT STARTED
```

PPF continues independently.

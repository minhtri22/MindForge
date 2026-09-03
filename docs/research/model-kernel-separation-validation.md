# Model / Kernel Separation Validation - MKS-1

Status: **PASS / CLOSED - FULL LOCAL EVIDENCE VALIDATED**

Starting reference: `1b0392a2550ecee0e65941e0590f21507797610d`

Implementation branch: `refactor/mks-1-model-kernel-separation`

Closure evidence HEAD: `2c1d0bcf02875f6bb3ed3c81f9d6f731274e6285`

## Reason for activation

MKS-1 was activated from demonstrated current coupling, not hypothetical future models. Runtime-facing evaluation and generation code imported `TransformerLM` directly and reached through `model.config.max_context`; training and checkpointing constructed `TransformerLM` directly; `KernelConfig` named a research composition containing data, model, and training concerns.

## Historical context

Earlier sandbox-only validation was marked REVISE because the full repository checkout, full pytest suite, Phase-2 summarize/check commands, and real checkpoint replay were not executable there. That historical REVISE remains part of the chronology.

The subsequent real-local validation run closed that blocker. This document records the final current state after the real checkout evidence.

## Before dependency map

```text
evaluate.py -> TransformerLM -> model.config.max_context
generate.py -> TransformerLM -> model.config.max_context
train.py -> TransformerLM(config.model)
checkpoint.py -> TransformerLM(saved_model_config)
KernelConfig -> DataConfig + ModelConfig + TrainingConfig
```

## After dependency map

```text
evaluate.py -> TokenModel contract -> context_limit + forward/train/eval
generate.py -> TokenModel contract -> context_limit + forward/eval
train.py -> create_model(ModelConfig) [research/tooling construction]
checkpoint.py -> create_model(ModelConfig) [serialization/tooling construction]
TransformerLM -> structurally satisfies TokenModel
RunConfig -> DataConfig + ModelConfig + TrainingConfig [research/tooling]
KernelConfig -> backward-compatible legacy subclass of RunConfig
```

No physical `kernel/` or `models/` package move was performed.

## Minimal Model Contract

`mindforge/model_contract.py` defines one structural `typing.Protocol`, `TokenModel`, with only currently demonstrated runtime needs:

- `context_limit`
- `training`
- token forward call returning logits
- `train(mode)`
- `eval()`

`TokenModel` is a PyTorch-bound runtime contract v0, not a permanent universal model ABI.

The contract deliberately excludes Transformer internals, optimizer/training configuration, checkpoint format, PPF/personal-pattern semantics, mobile/host semantics, plugin concepts, external-model adapters, and capability enums/registries.

## Current Transformer

`TransformerLM.context_limit` remains the runtime context property required by `TokenModel`.

`TransformerLM.vocab_size` remains available as concrete-model metadata, backed by `config.vocab_size`, but `vocab_size` is not a required `TokenModel` protocol member.

`create_model(ModelConfig)` is the single concrete construction function. It is intentionally not a registry, provider, plugin system, or external-model adapter surface.

Transformer mathematics were not changed.

## Config responsibility

`RunConfig` names the data + model + training composition as research/tooling configuration. Existing `KernelConfig` is preserved as a frozen dataclass subclass for Phase-1/Phase-2 compatibility; its JSON field structure is unchanged.

## Validation results

The full local validation evidence established:

```text
pytest tests/ -q: PASS (61 passed, 0 failed, 0 skipped)
focused MKS tests: PASS (10 passed)
compileall: PASS
git diff --check: PASS
Phase-2 summarize: PASS
Phase-2 check: PASS
real checkpoint read/load: PASS
model reconstruction: PASS (10,339,200 params)
state restore: PASS
optimizer restore: PASS
evaluation replay: PASS (delta CE=0.0, delta BPB=0.0)
generation replay: PASS (token IDs exact, text exact)
canonical Phase-2 training rerun: NO
```

Evaluation replay classification is **DETERMINISTIC CURRENT REPLAY ONLY**. It is not claimed as historical parity against an unavailable pre-MKS fixture for the exact replay configuration.

## MKS gates

| Gate | Evidence | Status |
|---|---|---|
| G1 - reason to separate now | direct concrete-model/runtime coupling existed | PASS |
| G2 - minimal/scoped model contract | ADR frozen; unused `vocab_size` removed; PyTorch-bound v0 scope explicit | PASS |
| G3 - compatibility tests | full historical pytest suite + focused MKS tests passed | PASS |
| G4 - Transformer conformance/construction | structural conformance + `create_model` path | PASS |
| G5 - frozen evidence regression | full checkout pytest, Phase-2 summarize/check, real checkpoint replay, deterministic evaluation replay, deterministic generation replay | PASS |
| G6 - no PPF/plugin semantics | contract contains none | PASS |
| G7 - no speculative plugin framework | none introduced | PASS |

## Source/import boundary audit

Runtime-facing `evaluate.py` and `generate.py` no longer import `TransformerLM` and no longer inspect Transformer architecture internals.

Research/tooling code uses the single `create_model(ModelConfig)` construction path. `model.py` remains the owner of `TransformerLM` architecture internals.

`TokenModel` contains no PPF, personal-pattern, plugin, mobile, host, agent, tool-routing, registry, or capability-enum semantics.

No `PluginManager`, `ExtensionRegistry`, `HookBus`, `CapabilityRegistry`, `ProviderRegistry`, `ServiceContainer`, `EventBus`, model registry, external-model adapter, or physical `kernel/`/`models/` package structure was added.

## Phase-2 compatibility

Tracked Phase-2 canonical artifacts were read and summarized without rerunning canonical Phase-2 training. The existing summary remains:

```text
status: PASS
manifest_hash: f3db682e905b9aa4aa8c6da557070d86d79fac9e0aeb02e4e9295d126b8fa968
baseline mean BPB: 10.537770964151376
treatment mean BPB: 10.938692122871304
paired mean absolute effect: 0.40092115871992995
mean relative effect: 0.038041814491547137
```

## Physical package decision

**NO PACKAGE RESTRUCTURE.**

The demonstrated coupling was reduced with a small protocol, semantic properties, a concrete construction function, runtime type changes, and research-config naming. Moving files into `kernel/` and `models/` would add churn without additional proof at this stage.

## PPF non-interference

No PPF contract, truth semantics, benchmark, or evidence file was modified by MKS-1.

## Final decision

```text
MKS-1: PASS / CLOSED
TECHNICAL DEBT: RESOLVED AT CONTRACT LEVEL
MODEL RUNTIME CONTRACT: IMPLEMENTED
MODEL CONTRACT SCOPE: PYTORCH-BOUND V0
TRANSFORMER MATH: UNCHANGED
PHYSICAL PACKAGE MOVE: NOT PERFORMED
PPF MODIFIED: NO
PLUGIN FRAMEWORK ADDED: NO
```

Reason for PASS: all required evidence gates passed in the normal local repository checkout, and the final contract boundary no longer requires unused `vocab_size`.

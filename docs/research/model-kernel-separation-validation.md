# Model / Kernel Separation Validation — MKS-1

Status: **REVISE — CONTRACT SEPARATION IMPLEMENTED; FULL FROZEN-EVIDENCE VALIDATION PENDING**

Starting reference: `1b0392a2550ecee0e65941e0590f21507797610d`

Implementation branch: `refactor/mks-1-model-kernel-separation`

## Reason for activation

The current code had a real architectural coupling: runtime-facing evaluation/generation code imported `TransformerLM` directly and reached through `model.config.max_context`; training constructed `TransformerLM` directly; `KernelConfig` also named a research composition containing data, model, and training concerns. The separation task was therefore activated from demonstrated current coupling rather than a hypothetical future model.

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
- `vocab_size`
- `training`
- token forward call returning logits
- `train(mode)`
- `eval()`

The contract deliberately excludes:

- Transformer internals (`n_layers`, `n_heads`, `d_model`, attention implementation)
- optimizer/training configuration
- checkpoint format
- PPF/personal-pattern semantics
- mobile/host semantics
- plugin concepts
- external-model adapters
- capability enums/registries

## Current Transformer adapter path

No wrapper class was added. `TransformerLM` structurally satisfies `TokenModel` by adding two semantic properties:

```text
context_limit -> config.max_context
vocab_size -> config.vocab_size
```

`create_model(ModelConfig)` is the single concrete construction function. It is intentionally not a registry/provider/plugin system.

Transformer mathematics were not changed.

## Config responsibility

`RunConfig` now names the data + model + training composition as research/tooling configuration. Existing `KernelConfig` is preserved as a frozen dataclass subclass for Phase-1/Phase-2 compatibility; its JSON field structure is unchanged.

This removes the architectural implication that model/training configuration is owned by the future runtime kernel without requiring migration of frozen configs.

## Compatibility tests

A compatibility test was committed before the implementation refactor. The implementation then expanded the focused MKS test to cover:

- default parameter count = `10,339,200`
- structural `TokenModel` conformance
- exact direct-vs-factory forward parity
- unchanged state-dict key layout
- unchanged invalid-context/token/rank behavior
- legacy `KernelConfig` round-trip and exact legacy type preservation
- exact one-step CPU parameter/optimizer parity

Sandbox focused result:

```text
6 passed
compileall PASS for the focused reconstructed package
```

The sandbox network cannot resolve `github.com`, so the full repository could not be cloned into the execution container. Source was inspected through the GitHub connector and the focused changed subset was reconstructed locally for executable parity checks.

Because the frozen MKS PASS criteria require the complete historical pytest suite plus Phase-2 `summarize` and `check` against the existing repository artifacts, those gates are **not claimed as executed here**.

## MKS gates

| Gate | Evidence | Status |
|---|---|---|
| MKS-G1 — reason to separate now | direct concrete-model/runtime coupling existed | PASS |
| MKS-G2 — minimal behavioral contract | `TokenModel` uses only current eval/generation needs | PASS |
| MKS-G3 — compatibility suite | pre-refactor frozen test + focused parity expansion | PASS (focused) |
| MKS-G4 — Transformer adapter path | structural conformance + `create_model` | PASS |
| MKS-G5 — no regression to frozen kernel evidence | focused exact parity passes; full historical suite and Phase-2 summarize/check not executable in this sandbox | **REVISE** |
| MKS-G6 — no PPF/plugin semantics in Model Contract | contract contains none | PASS |
| MKS-G7 — no speculative universal plugin framework | none added | PASS |

## Parity results

### Model construction

PASS in focused sandbox: default model remains exactly `10,339,200` parameters.

### Forward

PASS in focused sandbox: direct `TransformerLM` and `create_model` paths with identical state produce exact equal logits (`max_abs_diff = 0`).

### Training

PASS in focused sandbox for a deterministic one-step CPU parity check: parameter tensors and optimizer parameter groups are exactly equal.

### Evaluation

Implementation change is boundary-only: `model.config.max_context` became `model.context_limit`, which resolves to the same integer for `TransformerLM`. Full frozen evaluator replay was not run in this sandbox, therefore final evidence gate remains REVISE.

### Generation

Implementation change is boundary-only: generation truncation now uses `model.context_limit`, which resolves to the same current value. Full checkpoint/tokenizer generation replay was not run in this sandbox, therefore final evidence gate remains REVISE.

### Checkpoint

Checkpoint payload keys/format/version were not changed. Concrete reconstruction now calls `create_model(saved_model_config)` rather than `TransformerLM(saved_model_config)`. Full historical checkpoint fixture/resume suite was not executed in this sandbox.

## Source/import boundary audit

Runtime-facing `evaluate.py` and `generate.py` no longer import `TransformerLM` and no longer inspect Transformer architecture internals.

Research/tooling code uses the single `create_model(ModelConfig)` construction path. `model.py` remains the only owner of `TransformerLM` architecture internals.

`TokenModel` contains no PPF, personal-pattern, plugin, mobile, host, agent, tool-routing, registry, or capability-enum semantics.

No `PluginManager`, `ExtensionRegistry`, `HookBus`, `CapabilityRegistry`, `ProviderRegistry`, `ServiceContainer`, or `EventBus` was added.

## Physical package decision

**NO PACKAGE RESTRUCTURE.**

The demonstrated coupling can be reduced with a small protocol, two semantic properties, one construction function, runtime type changes, and research-config naming. Moving files into `kernel/` and `models/` would add churn without additional proof at this stage.

## PPF non-interference

No PPF contract, truth semantics, benchmark, or evidence file was modified by MKS-1.

## Known residual debt

1. Full Phase-0/1/2 pytest validation must run in a normal repository checkout.
2. Phase-2 `summarize` and `check` must pass without rerunning the six canonical training runs.
3. Frozen checkpoint/evaluator/generation replay must be recorded from the real repository artifacts.
4. Physical package separation remains intentionally undecided; it is not required for architectural contract separation.

## Final decision

```text
MKS-1: REVISE
TECHNICAL DEBT: PARTIALLY RESOLVED
MODEL RUNTIME CONTRACT: IMPLEMENTED
TRANSFORMER MATH: UNCHANGED
PHYSICAL PACKAGE MOVE: NOT PERFORMED
PPF MODIFIED: NO
PLUGIN FRAMEWORK ADDED: NO
```

Reason for REVISE is evidence completeness, not a discovered behavioral mismatch. The next action is validation in the normal local MindForge checkout; do not redesign the contract or move packages unless that validation exposes a concrete issue.

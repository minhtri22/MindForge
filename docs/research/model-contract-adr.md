# Model Contract ADR

Status: **ACCEPTED FOR MKS-1 V0 SCOPE / NOT A UNIVERSAL PERMANENT CONTRACT**

Branch: `refactor/mks-1-model-kernel-separation`

Decision context head: `8b10b49f8a5aef8e1911655a286c6ae59824126a`

## Context

MKS-1 introduced `TokenModel` to remove direct runtime coupling from evaluation/generation code to `TransformerLM` internals. Focused UAT passed, but QA left two design questions unresolved:

1. whether `vocab_size` belongs in the runtime contract;
2. whether the current PyTorch-specific call/lifecycle semantics should be treated as a stable universal model contract.

This ADR resolves those questions without introducing a registry, adapter framework, plugin system, package restructure, or support for hypothetical future models.

## Current consumers

Current runtime consumers are:

```text
evaluate.py
  -> context_limit
  -> training
  -> eval()
  -> train(mode)
  -> forward logits

generate.py
  -> context_limit
  -> eval()
  -> forward logits
```

`TokenModel.vocab_size` is not consumed by these runtime paths. Vocabulary checks remain model/tooling concerns through `ModelConfig.vocab_size`, tokenizer validation, and `TransformerLM`'s own input validation.

Training and checkpointing are research/tooling paths and may remain explicitly PyTorch/model-specific in MKS-1.

## Decision 1 — `vocab_size`

**REMOVE FROM THE RUNTIME CONTRACT.**

Reason:

- no demonstrated runtime consumer requires it;
- retaining it would violate the MKS rule to derive the smallest contract from demonstrated use cases;
- removing it from `TokenModel` does not remove `ModelConfig.vocab_size`, the concrete `TransformerLM.vocab_size` property, tokenizer/model vocabulary checks, or checkpoint model configuration.

The concrete model may continue exposing `vocab_size`; it is simply not part of the required runtime boundary.

## Decision 2 — framework binding

**`TokenModel` is explicitly a PYTORCH-BOUND RUNTIME CONTRACT V0.**

The current contract may require:

```text
__call__(torch.Tensor) -> torch.Tensor
training: bool
train(mode)
eval()
context_limit
```

because those are directly used by current evaluation/generation paths and permit the current `TransformerLM` to satisfy the boundary structurally without wrapper infrastructure.

This decision does **not** claim:

- framework neutrality;
- support for external/non-PyTorch models;
- a permanent universal model ABI;
- a capability taxonomy;
- adapter/provider/registry architecture.

The contract is stable only for the current proven MindForge PyTorch runtime use cases.

## Rejected alternatives

### Framework-neutral redesign now

Rejected because no second proven model currently demonstrates a concrete incompatibility with the v0 boundary. Creating tensor-neutral request/response objects or lifecycle adapters now would solve a hypothetical future problem and increase architecture surface without evidence.

### Universal model capability enum

Rejected. No current consumer requires it.

### Provider/adapter/registry framework

Rejected. MindForge currently has one proven model implementation; a framework would be speculative complexity.

### Keep `vocab_size` "for future use"

Rejected because future possibility is not demonstrated current need.

## Why no plugin/adapter framework

MKS-1 separates the current learned model from runtime consumers. It does not solve model discovery, plugin composition, external inference, or multi-backend serving. Those concerns require independent evidence and activation gates.

## Compatibility implications

The bounded correction authorized by this ADR removes only `vocab_size` from the `TokenModel` protocol. It does not change:

```text
Transformer mathematics
ModelConfig.vocab_size
TransformerLM.vocab_size
checkpoint format/version
training semantics
evaluator semantics
generation algorithm
tokenizer validation
Phase-2 evidence
```

Existing `TransformerLM` behavior remains unchanged.

## Upgrade trigger

Reconsider this ADR only when a **second proven model implementation or runtime path** cannot satisfy the PyTorch v0 contract without inappropriate emulation of PyTorch tensor/lifecycle semantics, or when a demonstrated current consumer requires a capability not expressible by the v0 boundary.

"We may want other models someday" is not an upgrade trigger.

## Relationship to MKS-1

This ADR resolves the design part of MKS-G2:

- unused contract surface is removed;
- framework binding is explicit and bounded;
- the contract is no longer described as a universal permanent abstraction.

MKS-1 still cannot be declared PASS/CLOSED until MKS-G5 full frozen-evidence regression is completed in a normal local checkout with the real repository artifacts.

## Relationship to PPF

None. PPF remains an independent greenfield research track. This ADR neither imports PPF semantics into the model boundary nor authorizes PPF integration.

## Final decision

```text
ADR DECISION — vocab_size: REMOVE FROM RUNTIME CONTRACT
ADR DECISION — framework binding: PYTORCH-BOUND V0
UNIVERSAL MODEL CONTRACT CLAIM: NO
PLUGIN/ADAPTER FRAMEWORK: NO
PHYSICAL PACKAGE MOVE: NO
PPF INTEGRATION: NO
```

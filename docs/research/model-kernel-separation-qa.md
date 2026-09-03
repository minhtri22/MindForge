# Model / Kernel Separation MKS-1 — QA Report

Status: **REVISE — IMPLEMENTATION QUALITY GOOD; CONTRACT MINIMALITY/STABILITY NEEDS ONE MORE DECISION**

Branch: `refactor/mks-1-model-kernel-separation`

Implementation head reviewed: `d17a5ed8eb5083049411cfafa382204edaafa79b`

Related UAT: `docs/research/model-kernel-separation-uat.md`

## Executive assessment

MKS-1 moved the code in the intended direction with a small change set and no package/framework explosion. Runtime-facing evaluation and generation no longer depend directly on `TransformerLM` internals; model construction is centralized behind one simple function; the Transformer mathematics remain unchanged; legacy `KernelConfig` serialization remains compatible.

The implementation is materially better than the starting state.

However, QA does **not** recommend declaring the Model Contract permanently stable yet. Two contract-quality findings remain:

1. `TokenModel.vocab_size` is present in the runtime contract but is not required by the current `evaluate.py` or `generate.py` consumer paths reviewed here.
2. `TokenModel` freezes PyTorch-specific `torch.Tensor` call types plus `training/train/eval` semantics into what is described as the runtime-facing Model Contract. This is justified by the current evaluator/generator implementation, but it is tighter than the technical-debt note's warning against prematurely freezing exact tensor/API details.

These findings do not invalidate current Transformer behavior or the UAT result. They do mean MKS-G2 should remain under review before calling the contract a stable long-term model/kernel boundary.

## QA dimensions

| Dimension | Assessment | Notes |
|---|---|---|
| Behavioral correctness | GOOD | focused parity/UAT found no mismatch |
| Transformer preservation | PASS | architecture/math unchanged except semantic properties/factory |
| Runtime decoupling | GOOD | evaluator/generator depend on `TokenModel` rather than concrete Transformer |
| Contract size | SMALL | one `Protocol`, no registry/provider/plugin framework |
| Contract minimality | REVISE | `vocab_size` appears unused by current runtime consumers |
| Framework neutrality | REVISE | contract imports `torch` and exposes mutable train/eval semantics |
| Backward config compatibility | PASS | `KernelConfig` remains exact legacy subclass and round-trips as legacy type |
| Checkpoint compatibility | GOOD / focused PASS | format remains v1; focused round-trip passed; historical artifact replay still pending |
| PPF isolation | PASS | no PPF semantic/evidence change in MKS branch |
| Scope discipline | PASS | no package move, plugin framework, model registry, mobile/agent work, or external model adapters |
| Evidence completeness | REVISE | full historical pytest and Phase-2 summarize/check still require normal checkout |

## Detailed findings

### QA-01 — Runtime contract exposes an apparently unused `vocab_size`

Severity: **MEDIUM — DESIGN QUALITY**

The current runtime consumers reviewed are:

```text
evaluate.py -> context_limit + training/eval/train + forward logits
generate.py -> context_limit + eval + forward logits
```

Neither path uses `TokenModel.vocab_size`.

Training/checkpoint tooling continues to use `ModelConfig.vocab_size` outside the runtime contract.

This means `vocab_size` currently looks like extra surface rather than a demonstrated runtime requirement. Under the MKS rule "derive the smallest contract from demonstrated use cases", this should be explicitly justified or removed in a later code-authorized task.

No code change is made by this QA task.

### QA-02 — Runtime contract is PyTorch-specific

Severity: **MEDIUM — ARCHITECTURE RISK**

The contract currently freezes:

```text
__call__(torch.Tensor) -> torch.Tensor
training: bool
train(mode)
eval()
```

This is sufficient and convenient for the current PyTorch `TransformerLM`, evaluator, and generator. It also makes `TransformerLM` structurally satisfy the contract without a wrapper.

The risk is architectural: the debt note explicitly aims for model replaceability and cautions against prematurely freezing exact tensor/API details. A future local/external or non-PyTorch model could be forced through PyTorch-style lifecycle semantics even if those semantics are not intrinsic to the runtime capability.

QA recommendation is **not** to add adapters/frameworks now. Instead, before MKS-1 is CLOSED, decide and document one of two positions:

```text
A. TokenModel is intentionally a current PyTorch runtime contract, not the final universal Model Contract.

or

B. The stable Model Contract must become framework-neutral; PyTorch train/eval/tensor behavior belongs in a current-model adapter/tooling boundary.
```

Do not implement option B until a dedicated bounded change is authorized and current evidence shows it is required.

### QA-03 — Checkpoint path remains model/tooling-specific by design

Severity: **LOW / ACCEPTED**

`save_checkpoint` accepts `nn.Module` and requires `.config` to be a `ModelConfig`; `load_checkpoint` reconstructs through `create_model(saved_model_config)`.

This is not currently treated as a kernel-runtime violation because checkpointing/training were explicitly classified as research/tooling concerns. It preserves checkpoint v1 and avoids forcing training serialization into the runtime `TokenModel` contract.

QA accepts this boundary for MKS-1.

### QA-04 — `KernelConfig` compatibility approach is appropriate

Severity: **NONE / PASS**

Introducing `RunConfig` removes the misleading architecture implication that data/model/training composition is runtime-kernel ownership, while `KernelConfig` remains a frozen subclass so legacy loading still returns the legacy type and JSON shape.

This is a good compatibility-first compromise. Removing `KernelConfig` now would add migration churn without architectural benefit.

### QA-05 — No physical package move is the correct current decision

Severity: **NONE / PASS**

The current evidence does not justify creating `mindforge/kernel/` and `mindforge/models/`. Contract separation provides the meaningful dependency improvement with much less churn.

Do not perform folder restructuring merely to make the repository look layered.

## Gate reassessment

| Gate | QA status | Reason |
|---|---|---|
| MKS-G1 | PASS | concrete direct Transformer/runtime coupling was demonstrated |
| MKS-G2 | **REVISE** | contract is small but `vocab_size` is apparently unused and PyTorch-specific surface requires an explicit stability decision |
| MKS-G3 | PASS (focused) | compatibility behavior was frozen before refactor and executable focused tests pass |
| MKS-G4 | PASS | current Transformer conforms structurally; one plain construction path exists |
| MKS-G5 | **REVISE** | full historical suite + Phase-2 summary/check + real artifact replay pending |
| MKS-G6 | PASS | no PPF/plugin semantics in contract |
| MKS-G7 | PASS | no speculative plugin framework |

## QA decision

```text
MKS-1 IMPLEMENTATION QUALITY: GOOD
MKS-1 UAT (FOCUSED): PASS
MKS-1 QA: REVISE
MKS-1 OVERALL: REVISE
TECHNICAL DEBT: PARTIALLY RESOLVED
```

The reason is not a behavioral regression. It is that the evidence is incomplete and the contract should not yet be called permanently minimal/stable without resolving QA-01/QA-02 at the design-decision level.

---

# Next Plan While PPF Continues Independently

PPF remains a separate greenfield research track and must not be coupled to this work.

Recommended order:

## N1 — Close MKS-1 on the normal local checkout

Priority: **P0 / immediate**

Run, without changing code first:

```powershell
.venv\Scripts\python.exe -m pytest tests/ -q
.venv\Scripts\python.exe -m compileall mindforge tests -q
git diff --check
.venv\Scripts\python.exe -m mindforge.experiment summarize configs/phase2_manifest.json
.venv\Scripts\python.exe -m mindforge.experiment check configs/phase2_manifest.json --baseline-bpb-cv-max 0.10
```

Also replay an existing real checkpoint through checkpoint load/evaluation/generation where practical.

Do **not** rerun the six canonical Phase-2 training runs.

Then decide QA-01/QA-02 explicitly before changing MKS status to PASS/CLOSED.

## N2 — Freeze a Model Contract ADR, not another framework

Priority: **P0 after N1**

Create a short architecture decision record answering:

```text
Is TokenModel a deliberately PyTorch-bound v0 contract?
or
Must the stable model/kernel contract be framework-neutral now?
```

Also decide whether `vocab_size` has a demonstrated runtime consumer.

This step should be documentation/decision first. Only authorize code if the decision requires a concrete bounded correction.

No registry, provider system, capability enum, plugin bus, or external-model adapter should be introduced.

## N3 — Track A foundation protocol for MindForge-Mobile

Priority: **P1; can proceed in parallel with PPF once MKS closure is understood**

Do research/protocol work only:

```text
question: how small can the model be while still performing personal understanding/routing?
candidate sizes: 5M / 10M / 20M / 50M
```

Freeze a capability benchmark before model-size experiments. Candidate tasks:

- intent classification;
- personal entity resolution;
- context-conditioned interpretation;
- tool/app selection;
- argument extraction;
- clarification decision;
- local-vs-external routing.

No mobile runtime integration yet.

## N4 — Compact-model scaling envelope

Priority: **P1/P2 after Track-A benchmark freeze**

Use the existing simple Transformer family to measure a bounded size sweep. The purpose is evidence, not architecture novelty.

Measure at least:

```text
quality on frozen Track-A tasks
training/inference latency
RAM/model footprint
throughput
```

Only after evidence should a <=20M target become a claim rather than a hypothesis.

## N5 — Cross-device reproducibility

Priority: **P2**

Once a small Track-A candidate is selected, reproduce on at least two device classes where available (for example Intel XPU and NVIDIA/CPU). This tests whether MindForge's local-first evidence is portable rather than specific to one backend.

## N6 — Repository/provenance hygiene

Priority: **low-risk maintenance only**

Clean up tracked runtime-noise such as `.agentloop` heartbeat files in a separate housekeeping change if they still interfere with clean-tree/provenance checks.

Do not mix this maintenance with model/kernel architecture commits.

---

# Explicit non-plan

While PPF is running, do **not** spend time on:

```text
physical kernel/model folder moves
plugin framework
model registry
external LLM adapters
Hugging Face abstraction
ONNX/mobile runtime integration
quantization stack
PPF integration
continual learning/memory reopening
agent framework
```

Those items need their own evidence-backed activation gate.

## Recommended immediate action

```text
1. Run N1 in the normal local checkout.
2. Review the real artifact results.
3. Resolve the two Model Contract QA findings as an ADR/decision.
4. Only then mark MKS-1 PASS/CLOSED or authorize one tiny correction.
5. In parallel, prepare Track-A benchmark protocol while PPF continues independently.
```

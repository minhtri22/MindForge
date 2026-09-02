# R1 — Open-Source Learning / Memory Architecture Survey

## Executive conclusion

**R1: PASS.** Ten credible projects were longlisted and six were inspected in depth at immutable commits. The source-backed Phase-1 implication is:

```text
Phase-1 architectural changes required: NONE
Phase-1 extension points worth preserving: NONE
```

If a future gate justifies continual learning, start with a **minimal reservoir experience-replay sidecar**, informed by Mammoth and cross-checked against Avalanche. Use Avalanche as a reference oracle, not a dependency. Online EWC is the next no-raw-replay candidate. DER++ is technically credible but language-model logit storage makes it a later comparison.

Mem0, LangMem and Letta are application/inference-memory systems. They do not update model weights and do not justify a memory interface inside the compact kernel. Mem0 is the best surveyed external-memory reference if a separate product requirement appears.

This research does not reopen P0.9, claim that a mechanism works in MindForge, or authorize implementation.

## MindForge constraints

The filter is a decoder-only Transformer around 10M–50M parameters on Windows 11, Intel Core Ultra 7 258V, 32 GB RAM, one Intel Arc 140V XPU, PyTorch XPU and BF16. The kernel remains a direct dataset-to-generation path. CUDA-specific kernels, multi-GPU assumptions, server stacks and hosted embedding/LLM requirements count against fit.

## Search methodology

Research was performed on 2026-09-02. Official upstreams were discovered across continual learning, parameter isolation and external memory. Metadata, license, branch, immutable HEAD, activity, releases and weak popularity signals were recorded. Shortlisted candidates were then inspected in actual source at exact SHAs; README marketing was not accepted as mechanism evidence.

No package was installed, no source was vendored and no MindForge treatment benchmark was run. Reproducible metadata is in [the JSON inventory](data/r1-candidates.json); scores and mechanism-level comparisons are in [the matrices](r1-candidate-matrix.md).

## Longlist

| # | Official upstream | Track | Commit | Branch | License | Stack | Activity/release | Stars/forks* | Outcome |
|---:|---|---|---|---|---|---|---|---:|---|
| 1 | [ContinualAI/avalanche](https://github.com/ContinualAI/avalanche) | continual framework | `eb075be393e1f458b2c352514ff6c17b5a2c0f4e` | master | MIT | Python/PyTorch | 2025-03-11; v0.6.0 | 2,088/321 | shortlist |
| 2 | [aimagelab/mammoth](https://github.com/aimagelab/mammoth) | continual methods | `e75a491c69fd729edeb01431afb753d9157d9a81` | master | MIT | Python/PyTorch | 2026-05-20 | 837/158 | shortlist |
| 3 | [GMvandeVen/continual-learning](https://github.com/GMvandeVen/continual-learning) | comparative CL | `e6d795aa81b9cef742b8de76cb71222d4d1ce00b` | master | MIT | Python/PyTorch | 2025-11-05; `article` | 1,878/345 | reference |
| 4 | [facebookresearch/agem](https://github.com/facebookresearch/agem) | A-GEM | `45421499483b28935491251e9e821c55e8b3c089` | main | MIT | TensorFlow/notebooks | 2019-02-28; archived | 210/37 | reject implementation |
| 5 | [kuc2477/pytorch-ewc](https://github.com/kuc2477/pytorch-ewc) | minimal EWC | `4afaa6666d6b4f1a91a110caf69e7b77f049dc08` | master | MIT | Python/PyTorch | 2019-06-29 | 286/48 | historical reference |
| 6 | [huggingface/peft](https://github.com/huggingface/peft) | adapters/isolation | `871cad819e5da703216a97e60a6e126d3147bee5` | main | Apache-2.0 | Python/PyTorch/Transformers | 2026-09-02; v0.20.0 | 21,619/2,471 | shortlist |
| 7 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | application memory | `9a7924befd7026e41e445ba809370009e5e985a6` | main | Apache-2.0 | Python/providers/vector stores | 2026-09-02; ts-v3.1.8 | 64,578/7,569 | shortlist |
| 8 | [letta-ai/letta-code](https://github.com/letta-ai/letta-code) | stateful agent memory | `6394c7fcc6123e324efc7d1272dac34a8a11d9bf` | main | Apache-2.0 | TypeScript/agent runtime | 2026-09-01 | 3,190/387 | shortlist; reject dependency |
| 9 | [getzep/graphiti](https://github.com/getzep/graphiti) | temporal graph memory | `11538f6d45561bcce9a4400b374fb2dc533dccb6` | main | Apache-2.0 | Python/graph DB/providers | 2026-09-01; mcp-v1.1.0 | 30,525/3,100 | reject dependency |
| 10 | [langchain-ai/langmem](https://github.com/langchain-ai/langmem) | application memory | `f8c7ebd6110c124a36995dab645a8cb0eb0b8210` | main | MIT | Python/LangChain/LangGraph | 2026-09-02 | 1,638/187 | shortlist |

\*Stars/forks are weak inventory signals only and are not scoring inputs.

The named `letta-ai/letta` was also pinned at `4511fa0bc91f68fbab32b91f694617271ea9012b`. Its current [README](https://github.com/letta-ai/letta/blob/4511fa0bc91f68fbab32b91f694617271ea9012b/README.md) says `main` is a landing page and directs source inspection to `letta-code`; V1 is retired. The survey therefore evaluates the official successor instead of presenting historical V1 as current.

Primary references: [Avalanche](https://www.jmlr.org/papers/v24/23-0130.html), [DER++](https://arxiv.org/abs/2004.07211), [EWC](https://arxiv.org/abs/1612.00796), [A-GEM](https://arxiv.org/abs/1812.00420), [LoRA](https://arxiv.org/abs/2106.09685), [Mem0](https://arxiv.org/abs/2504.19413), and [MemGPT](https://arxiv.org/abs/2310.08560).

## Shortlist

1. Mammoth — compact reservoir/DER implementations.
2. Avalanche — maintained replay/EWC/A-GEM reference oracle.
3. Hugging Face PEFT — mature language-model adapter isolation.
4. Mem0 — external extraction, reconciliation and retrieval.
5. Letta Code — current stateful-agent runtime with git-backed memory.
6. LangMem — extraction/manage/search tools over LangGraph stores.

## Continual-learning analysis

Mammoth's [`ReservoirSampling` and `Buffer`](https://github.com/aimagelab/mammoth/blob/e75a491c69fd729edeb01431afb753d9157d9a81/utils/buffer.py) own bounded examples and optional labels/logits. Avalanche independently implements [`ReservoirSamplingBuffer`](https://github.com/ContinualAI/avalanche/blob/eb075be393e1f458b2c352514ff6c17b5a2c0f4e/avalanche/training/storage_policy.py); its [`ReplayPlugin`](https://github.com/ContinualAI/avalanche/blob/eb075be393e1f458b2c352514ff6c17b5a2c0f4e/avalanche/training/plugins/replay.py) composes current data with buffer data before an experience and updates storage afterward. The mechanism therefore needs no model-internal hook.

Mammoth's [`Derpp.observe`](https://github.com/aimagelab/mammoth/blob/e75a491c69fd729edeb01431afb753d9157d9a81/models/derpp.py) combines current loss, MSE against stored logits and replay-label loss; the inspected code performs two replay draws/forwards. Full vocabulary logits per replay position make DER++ materially less attractive for language modeling than plain token replay.

Avalanche's [`EWCPlugin`](https://github.com/ContinualAI/avalanche/blob/eb075be393e1f458b2c352514ff6c17b5a2c0f4e/avalanche/training/plugins/ewc.py) owns saved parameters and diagonal importances, adds a quadratic loss before backward and runs an extra importance pass after each experience. Online mode can retain one snapshot/importance pair; separate mode grows per experience. It is standard PyTorch but still requires an LM-specific gate and frozen lambda protocol.

Avalanche's [`AGEMPlugin`](https://github.com/ContinualAI/avalanche/blob/eb075be393e1f458b2c352514ff6c17b5a2c0f4e/avalanche/training/plugins/agem.py) computes a reference gradient from memory before every iteration and may project the current flattened gradient. The extra forward/backward and full-gradient materialization are disproportionate for the first single-XPU prototype.

PEFT's [`PeftModel`](https://github.com/huggingface/peft/blob/871cad819e5da703216a97e60a6e126d3147bee5/src/peft/peft_model.py) wraps a base model and owns named adapter state. [`LoraModel`](https://github.com/huggingface/peft/blob/871cad819e5da703216a97e60a6e126d3147bee5/src/peft/tuners/lora/model.py) injects low-rank layers and supports routing/merging. This applies to decoder LMs, but isolated adapters are not shared continual learning and the complete dependency stack is unnecessary for Phase 1.

These upstreams are mostly vision/classification oriented. Their mechanics may port; their benchmark results, image transforms, labels and task IDs do not establish LM effectiveness.

## Memory analysis

Training memory changes optimization; external memory changes inference context/tools. They must not share a generic kernel API.

Mem0's [`Memory`](https://github.com/mem0ai/mem0/blob/9a7924befd7026e41e445ba809370009e5e985a6/mem0/memory/main.py) composes LLM, embedder, vector store, optional reranker and history storage. [`MemoryConfig`](https://github.com/mem0ai/mem0/blob/9a7924befd7026e41e445ba809370009e5e985a6/mem0/configs/base.py) exposes these dependencies. Writes use LLM extraction/reconciliation plus embedding/persistence; reads use semantic/lexical ranking. It is a credible application-memory layer, not model learning.

LangMem's [`knowledge/extraction.py`](https://github.com/langchain-ai/langmem/blob/f8c7ebd6110c124a36995dab645a8cb0eb0b8210/src/langmem/knowledge/extraction.py) uses chat models and structured extraction; [`create_manage_memory_tool`](https://github.com/langchain-ai/langmem/blob/f8c7ebd6110c124a36995dab645a8cb0eb0b8210/src/langmem/knowledge/tools.py) performs namespace-scoped CRUD over LangGraph `BaseStore`. This is understandable composition but remains an agent/store layer with external-model assumptions.

Letta Code's [`memory-filesystem.ts`](https://github.com/letta-ai/letta-code/blob/6394c7fcc6123e324efc7d1272dac34a8a11d9bf/src/agent/memory-filesystem.ts) resolves agent-scoped memory and initializes/synchronizes git-backed state; [`memory-runtime.ts`](https://github.com/letta-ai/letta-code/blob/6394c7fcc6123e324efc7d1272dac34a8a11d9bf/src/agent/memory-runtime.ts) routes local/backend capability; [`memory.ts`](https://github.com/letta-ai/letta-code/blob/6394c7fcc6123e324efc7d1272dac34a8a11d9bf/src/agent/memory.ts) creates persona/human blocks. This transparent persistent agent state requires an agent/runtime boundary, not a Transformer boundary.

Graphiti was rejected before deep shortlist because temporal graph extraction/retrieval needs a graph database plus LLM/embedding infrastructure while providing no Phase-1 training function.

## Candidate deep dives

### Mammoth

- **Commit/license:** `e75a491c69fd729edeb01431afb753d9157d9a81`, MIT.
- **Entry/state:** `Buffer`, `ReservoirSampling`, `Derpp.observe`, and the `ContinualModel.observe` contract; method subclasses own optimizer and buffer.
- **Assumptions:** PyTorch classification datasets, labels, transforms, usually vision tensors; SGD/Adam/AdamW.
- **Cost/fit:** reservoir is low-cost and backend-neutral; DER++ adds logits and replay forwards. Re-map storage to deterministic LM sequences/masks.
- **Risk/decision:** vision evidence does not transfer. **`CLONE-MINIMAL` selected algorithm only.**

### Avalanche

- **Commit/license:** `eb075be393e1f458b2c352514ff6c17b5a2c0f4e`, MIT.
- **Entry/state:** replay/storage/EWC/A-GEM plugins intercept strategy lifecycle and own buffer, importance or gradient state.
- **Assumptions:** Avalanche datasets/experiences/tasks plus supervised criterion and optimizer.
- **Cost/fit:** ordinary PyTorch mechanics are plausibly XPU-portable; full framework adoption would replace MindForge's simple loop.
- **Risk/decision:** broad classification abstractions. **`REFERENCE`; not a dependency.**

### Hugging Face PEFT

- **Commit/license:** `871cad819e5da703216a97e60a6e126d3147bee5`, Apache-2.0.
- **Entry/state:** `PeftModel` and `LoraModel` wrap recognized modules and own named adapter parameters/configurations.
- **Assumptions:** Transformers, Accelerate, Hub and safetensors integrations.
- **Cost/fit:** low-rank overhead is modest; full upstream XPU behavior was not tested and is outside R1.
- **Risk/decision:** routing/growth per task and no anti-forgetting guarantee. **`REFERENCE`; Phase 6 only if measured.**

### Mem0

- **Commit/license:** `9a7924befd7026e41e445ba809370009e5e985a6`, Apache-2.0.
- **Entry/state:** `Memory`, `MemoryConfig`, factories and vector-store interface; persistent identity-scoped items/history.
- **Write/read:** LLM extract/reconcile, embed/store, then vector/BM25/rerank retrieval.
- **Cost/fit:** model calls and store operations dominate; local providers are possible but consume separate RAM/models.
- **Risk/decision:** operational/provider complexity. **Best external candidate; `REFERENCE` outside kernel.**

### Letta Code

- **Commit/license:** landing `letta@4511fa0...`; successor `letta-code@6394c7f...`, Apache-2.0.
- **Entry/state:** agent blocks plus scoped git-backed Markdown, constraints, synchronization and backend routing.
- **Write/read:** agent file operations write versioned state; files are surfaced through agent context/tools.
- **Cost/fit:** storage is modest; the complete TypeScript agent/server/channel/tool system is not.
- **Risk/decision:** category mismatch. **`REJECT` dependency; concept reference only.**

### LangMem

- **Commit/license:** `f8c7ebd6110c124a36995dab645a8cb0eb0b8210`, MIT.
- **Entry/state:** structured extraction/reflection and manage/search tools over namespaced `BaseStore` records.
- **Cost/fit:** LLM and optional embedding calls plus LangChain/LangGraph/trustcall/Pydantic.
- **Risk/decision:** agent ecosystem coupling and LLM-controlled writes. **`REFERENCE`.**

## Framework-vs-mechanism conclusions

- Do not depend on Avalanche or Mammoth; borrow only a frozen algorithmic kernel when evidence authorizes it.
- Do not call PEFT a continual-learning solution; it supplies parameter isolation.
- Do not place Mem0, Letta, LangMem or Graphiti in the model package; they own application state/context policy.
- Do not infer language-model effectiveness from vision continual-learning benchmarks.

## Recommended future candidates

**Tier A — future minimal prototype:** reservoir replay; online EWC; DER++ only as a later bounded comparison.

**Tier B — reference:** Avalanche; PEFT; Mem0/LangMem outside the kernel.

**Tier C — inappropriate dependency/first treatment:** Letta Code, Graphiti, GEM/A-GEM, stale standalone method repos.

## Phase-1 architecture implications

**NONE.** No shortlisted source demonstrates that ordinary Python composition is insufficient.

| Possible extension | Candidate | Why composition works | Cost now | Cost deferred | Decision |
|---|---|---|---|---|---|
| callbacks/hooks | Avalanche plugins | a treatment can own/wrap a trainer step | broad event contract | targeted trainer edit | do not add |
| batch provenance/replay source | replay/DER | compose iterators; treatment records deterministic IDs | contaminates core batch API | small sidecar | do not add |
| auxiliary checkpoint state | replay/EWC/adapters | version treatment sidecar/schema when selected | speculative compatibility | explicit migration | do not add |
| generic evaluation hooks | CL methods | call independent evaluator at explicit boundaries | hidden flow | experiment orchestration | do not add |
| kernel memory API | Mem0/Letta/LangMem | application layer owns context/retrieval | conflates weight and retrieval memory | separate package | reject |

The existing Python module boundary is sufficient. Phase 1 should make the plain dataset/model/trainer/checkpoint/evaluator path coherent before any treatment exists.

## What not to build

- Generic plugin/callback buses, replay base classes or task routers.
- Arbitrary checkpoint payloads “for later”.
- Adapter registries before Phase 6 evidence.
- Vector DBs, embedding services, knowledge graphs or agent runtimes.
- Multiple anti-forgetting methods before a valid substrate exists.

## Final recommendation

Close R1 with no Phase-1 architecture changes. If a new independent requirement later reopens continual learning, pre-register one LM experiment and clone only reservoir replay plus deterministic serialization/tests, using Avalanche as a semantic cross-check. Consider online EWC second; do not install either framework. If an application later needs conversational memory, evaluate Mem0 against a plain local retrieval baseline outside the kernel. P0.9 and P0.10 remain `STOP / FROZEN`.

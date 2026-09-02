# R1 — Candidate and Mechanism Matrices

Status: **PASS**

Evidence date: **2026-09-02**

MindForge base: `971c0f7d453a62ee8c8da20f2710cb4c6cdfaecb`

Scores describe fit for a compact local MindForge kernel, not general project quality. Stars and forks are inventory metadata only and do not enter the score.

## Weighted project matrix

Weights: relevance 25%, simplicity 20%, local hardware fit 15%, portability/separability 15%, reproducibility 10%, dependency burden 10%, license 5%. Components are scored 1–5.

| Project | Rel. | Simple | Local | Portable | Repro. | Dep. | License | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Mammoth | 5 | 4 | 4 | 4 | 4 | 3 | 5 | **4.20** | `CLONE-MINIMAL` selected mechanisms only |
| Avalanche | 4 | 3 | 4 | 4 | 5 | 2 | 5 | **3.75** | `REFERENCE` |
| pytorch-ewc | 2 | 5 | 4 | 5 | 1 | 5 | 5 | **3.70** | `REFERENCE`; stale unofficial example |
| facebookresearch/agem | 3 | 4 | 2 | 4 | 3 | 4 | 5 | **3.40** | `REJECT` implementation |
| GMvandeVen/continual-learning | 3 | 3 | 4 | 3 | 3 | 4 | 5 | **3.35** | `REFERENCE` |
| Hugging Face PEFT | 3 | 3 | 4 | 3 | 5 | 2 | 5 | **3.35** | `REFERENCE` |
| LangMem | 2 | 3 | 2 | 3 | 3 | 2 | 5 | **2.60** | `REFERENCE` |
| Mem0 | 2 | 2 | 2 | 3 | 4 | 1 | 5 | **2.40** | `REFERENCE` outside kernel |
| Letta Code | 1 | 1 | 2 | 2 | 4 | 1 | 5 | **1.80** | `REJECT` as kernel dependency |
| Graphiti | 1 | 1 | 1 | 2 | 3 | 1 | 5 | **1.55** | `REJECT` as kernel dependency |

A compact stale implementation can score well on size while remaining a poor copy source. Provenance therefore keeps `pytorch-ewc` below Mammoth/Avalanche in the recommendation.

## Continual-learning mechanism matrix

| Mechanism | Source inspected | LLM applicability | Extra memory | Extra compute | Loop invasiveness | XPU portability | Isolated size | Strengths | Main failure mode | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| Naive sequential | MindForge P0.9 | native | none beyond optimizer | 1x | none | proven baseline | existing | required control | uncontrolled forgetting/transfer | retain baseline |
| Experience replay | Avalanche `ReplayPlugin`; Mammoth `Buffer` | high if LM sampling/masking is defined | bounded examples/tokens | about 1x with mixed/larger batch | batch composition | high, ordinary PyTorch | ~100–200 LOC + tests | model-agnostic and interpretable | retention/privacy and replay-ratio choices | **Tier A** |
| Reservoir replay | Avalanche/Mammoth reservoir classes | high | O(capacity) samples | O(1) expected write | outside model | high; CPU buffer viable | ~30–80 LOC + serialization/tests | uniform bounded stream sample | token/document sampling unit matters | **best candidate; `CLONE-MINIMAL` later** |
| DER | Mammoth buffer/logit pattern | medium | samples + historical logits | replay forward | custom loss/batch source | high in principle | ~100–200 LOC | preserves past function | LM vocabulary logits are large | `REFERENCE` |
| DER++ | Mammoth `Derpp.observe` | medium-low initially | samples + labels + logits | two replay forwards in inspected code | custom train step | portable PyTorch | ~150–250 LOC | distillation + supervised replay | storage/tuning burden; vision evidence | later bounded comparison |
| Online EWC | Avalanche `EWCPlugin` | medium-high mechanically | ~2x trainable parameters for snapshot + diagonal importance | extra post-stage data pass + per-step penalty | additive loss/end-stage pass | high | ~100–200 LOC | no raw replay data | Fisher approximation and lambda sensitivity | Tier A, second choice |
| Separate EWC | Avalanche `EWCPlugin` | medium | ~2x parameters per experience | as above | additive loss | high | ~120–220 LOC | per-experience state | unbounded growth | `REJECT` |
| A-GEM | Avalanche `AGEMPlugin`; archived official repo | medium | samples + one full gradient vector | memory forward/backward every step + projection | backward interception | standard ops but costly | ~150–250 LOC | explicit gradient constraint | near-2x backward and flat-gradient handling | `REFERENCE` |
| GEM | literature/framework references | medium-low locally | samples + gradients per prior task | multiple backwards + constrained solve | high | portable concept, poor economics | >300 LOC + solver | strong constraints | cost grows with task count | `REJECT` |
| Adapter isolation / LoRA | PEFT `PeftModel`, `LoraModel` | high | low-rank parameters per domain/task | modest | model wrapping/routing | likely for plain PyTorch; upstream XPU unverified | large upstream | avoids overwriting frozen base | task routing; not shared continual learning | `REFERENCE` |
| Prompt-based methods | PEFT prompt-learning stack | medium | prompt parameters per task | context/attention consumed by prompt tokens | input/model wrapper | portable in principle | medium | isolates parameters | routing and prompt growth | `REFERENCE` |

Avalanche and Mammoth are primarily classification/vision frameworks. Their buffer, loss and lifecycle mechanics are portable; their benchmark outcomes, augmentations, task IDs, labels and image tensor assumptions are **not evidence for decoder-only language models**.

## Memory matrix

| System/mechanism | Type | Weights modified? | External DB | Embedder | External LLM | Write policy | Read policy | Local path | Runtime burden | Training relevance | Kernel relevance | Decision |
|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|
| Replay buffer | model-learning | through training | no | no | no | reservoir/exemplar | sample into train batch | yes | low | direct | future trainer sidecar | clone later only |
| EWC state | model-learning | through penalty | no | no | no | snapshot + importance | penalty term | yes | low/medium | direct | future trainer sidecar | clone later only |
| Mem0 | inference/application | no | vector store; graph optional | yes | yes | extract/reconcile/embed/store | vector/BM25/rerank search | possible with local providers | high | none | none | best external reference |
| Letta Code MemFS | inference/application/agent state | no | git-backed filesystem/backend | no intrinsic embedder | agent needs LLM | agent edits scoped Markdown, git syncs | context/tools read files | yes | very high full runtime | none | none | reject dependency |
| LangMem | inference/application | no | LangGraph `BaseStore` | common for semantic search | yes | structured extractor or CRUD tool | namespace store search | possible | medium/high | none | none | reference |
| Graphiti | temporal structured application memory | no | graph DB | yes | yes | extract entities/relations | graph/vector/hybrid | possible but heavy | very high | none | none | reject |
| Plain local retrieval | inference/application | no | files/SQLite sufficient | optional | no | explicit application write | lexical/exact | yes | low | none | none until product gate | defer |

## Tiers

### Tier A — future prototype only after a new gate

1. Reservoir experience replay — `CLONE-MINIMAL` from Mammoth, cross-checked against Avalanche.
2. Online EWC — `CLONE-MINIMAL` from Avalanche when raw replay is unacceptable.
3. DER++ — bounded comparison only after estimating LM logit storage.

### Tier B — reference only

1. Avalanche for maintained implementations and test/lifecycle semantics.
2. PEFT for future adapter isolation, not continual learning by itself.
3. Mem0 and LangMem for a future application-memory study outside the kernel.

### Tier C — not appropriate for the compact kernel

1. Letta Code and Graphiti as dependencies.
2. GEM/A-GEM as first local treatments.
3. Stale standalone A-GEM/EWC repositories as code-copy sources.

## Phase-1 boundary decision

**Architectural changes required: `NONE`. Extension points worth preserving: `NONE`.**

Ordinary Python composition is sufficient: replay can compose the batch iterator; EWC can add trainer-owned loss/state; adapters can wrap selected modules if Phase 6 authorizes them; application memory belongs above generation. Adding callback buses, replay APIs, arbitrary checkpoint payloads or memory interfaces now would freeze contracts before a valid task exists. Deferring a small targeted trainer/application change is cheaper.

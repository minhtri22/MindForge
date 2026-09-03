# MindForge Plan

## Operating rule

Every phase is a **thin vertical slice** and must produce something runnable and measurable. A phase may be committed as complete only when its QA and evidence gates pass. Failed or ambiguous evidence changes the roadmap instead of being hidden by additional architecture.

## Phase lifecycle

For every phase:

1. freeze the hypothesis and exit criteria;
2. implement the smallest slice in sandbox;
3. run automated tests;
4. run phase-specific QA and reproducibility checks;
5. collect machine-readable evidence;
6. classify `PASS`, `REVISE`, or `STOP`;
7. on PASS, write `docs/phases/phase-N.md` containing design, test plan, results, limitations and exact reproduction commands;
8. only then commit/push the phase.

## Phase 0 — Prove the foundations

Phase 0 is a falsification phase, not project setup. Anything on which later architecture depends but which is still uncertain is tested here.

### P0.1 Hardware feasibility

Prove which of CPU/XPU/CUDA can execute the required forward, backward, optimizer, mixed-precision where applicable, and checkpoint workloads reliably. Measure correctness, step time, tokens/s, memory and unsupported operations.

**Target-specific gate:** Intel Arc/XPU claims may only PASS on an actual compatible target machine. Sandbox CPU results cannot be used as proxy evidence.

### P0.2 Practical model envelope

Benchmark small configurations (approximately 10M/25M/50M/100M where feasible) across context lengths such as 256/512/1024/2048. Record memory, tokens/s, step latency, stable batch and checkpoint size. Supported configs must come from measurements, not guesses.

### P0.3 Tokenizer assumption

Compare an existing suitable tokenizer with a project-trained tokenizer on representative Vietnamese and English text. Measure compression/tokenization efficiency, fallback behavior, vocabulary use and pipeline complexity. Do not build tokenizer infrastructure unless benefit is demonstrated.

### P0.4 Dataset viability

Find the smallest corpus that produces a useful learning curve and supports fast repeated experiments. Establish deterministic train/validation splits and data fingerprints.

### P0.5 Training reproducibility

Run a tiny config over at least 3 seeds. Verify consistent qualitative curves, deterministic data ordering where promised, correct checkpoint resume, and sufficient metadata to reproduce a run.

### P0.6 Evaluation harness viability

Before advanced treatments exist, prove the harness can compare two checkpoints reliably. Initial metrics: validation cross-entropy, bits/token or equivalent, and deterministic generation sanity checks; add downstream tasks only if cheap and relevant.

### P0.7 Experiment protocol

Define a machine-readable run record including identity/provenance, seed, hardware/dtype, model config, data/tokenizer fingerprints, training config, wall time, throughput, memory and results.

### P0.8 Baseline-0

Train one plain Transformer with no memory, MoE, RL, LoRA, retrieval or routing. Establish expected loss curve, runtime, memory and evaluation behavior.

### P0.9 Continual-learning feasibility probe

Train on dataset A, continue on B, evaluate A-before-B, A-after-B and B-after-B. Measure acquisition and untreated forgetting. No anti-forgetting mechanism yet.

### P0.10 Memory hypothesis probe

Only after a task with measurable memory value exists, compare Baseline-0 with the smallest crude memory treatment. Measure recall/recovery/forgetting plus compute and memory overhead. If there is no controlled signal, explicit generalized memory architecture is STOPPED.

### Phase 0 exit criteria

Phase 0 passes only when evidence answers:

1. which hardware backend is practical;
2. which model/context envelope is practical;
3. which tokenizer strategy is justified;
4. which small dataset supports rapid experiments;
5. whether training is reproducible;
6. whether evaluation distinguishes meaningful changes;
7. what Baseline-0 is;
8. how much untreated forgetting occurs;
9. whether explicit memory has a measurable signal worth pursuing.

A target-hardware claim cannot be waived merely because sandbox tests pass.

## Roadmap Decision After Phase 0

Phase 0 is closed with two different kinds of outcomes that must not be conflated:

```text
P0.1 PASS / FROZEN
P0.2 PASS / FROZEN
P0.3 PASS / FROZEN
P0.4 PASS / FROZEN
P0.5 PASS / FROZEN
P0.6 PASS / FROZEN
P0.7 PASS / FROZEN
P0.8 PASS / FROZEN
P0.9 STOP / FROZEN
P0.10 STOP / FROZEN
```

The core engineering foundation passed: local Intel XPU/BF16 training, tokenizer/data strategy, reproducibility, evaluation, checkpoint/resume and Baseline-0 are validated. The bounded continual-learning search did not establish a scientifically usable real-language catastrophic-forgetting substrate, so custom continual-learning and custom memory research are stopped rather than tuned until they produce the desired result.

This STOP is a bounded falsification result. It does not claim catastrophic forgetting or memory mechanisms are impossible. Future learning/memory capabilities may be adopted, ported, adapted or minimally cloned from established open-source mechanisms when independently justified.

Project decision:

```text
CORE FOUNDATION: PASS
CONTINUAL-LEARNING RESEARCH HYPOTHESIS: STOP
CUSTOM MEMORY RESEARCH HYPOTHESIS: STOP

PROCEED WITH COMPACT LOCAL LLM KERNEL DIRECTION
```

Canonical core path:

```text
dataset → tokenizer → Transformer → training → checkpoint → evaluation → generation
```

See [docs/phases/phase-0.md](docs/phases/phase-0.md) for the canonical closure summary and [docs/research/deferred/continual-learning-memory.md](docs/research/deferred/continual-learning-memory.md) for the stopped-research archive.

## R1 — Open-Source Learning/Memory Architecture Survey

Status: **PASS / CLOSED (research-only)**.

R1 will survey established open-source learning and memory mechanisms to determine architectural boundaries and whether any future extension point is justified. It is not a P0.9 retry, not an implementation phase, and must not introduce candidate frameworks or mechanisms into the kernel.

R1 occurs before Phase 1 only to answer whether the minimal kernel needs any concrete future-facing boundary. The default is YAGNI: R1 does not block the minimal Phase-1 core unless source-backed research identifies a cheap, specific interface requirement.

R1 inspected ten open-source projects and six shortlisted candidates at immutable commits. It selected minimal reservoir replay as the leading future mechanism, retained Avalanche as a reference rather than a dependency, and classified Mem0/Letta/LangMem-style memory as an application concern outside the model kernel. The source-backed boundary decision is:

```text
PHASE-1 ARCHITECTURAL CHANGES REQUIRED: NONE
PHASE-1 EXTENSION POINTS TO PRESERVE: NONE
```

See [docs/research/r1-open-source-learning-memory.md](docs/research/r1-open-source-learning-memory.md) and [docs/research/r1-candidate-matrix.md](docs/research/r1-candidate-matrix.md). This closes R1 without starting Phase 1 or reopening P0.9/P0.10.

## Phase 1 — Compact End-to-End Kernel

Status: **PASS / CLOSED**.

Turn validated Phase-0 prototypes into a clean reusable local LLM kernel:

```text
dataset → tokenizer → Transformer → training → checkpoint → evaluation → generation
```

Required: one primary architecture, single-device training, gradient accumulation, supported mixed precision, checkpoint/resume, seeds, backend abstraction validated in Phase 0, and independent evaluation/inference entry points.

**QA gate:** unit tests + integration smoke train + checkpoint round-trip + resume equivalence + deterministic eval + malformed-config/error-path tests.

Phase 1 closed with all frozen gates passing: exact CPU resume, real Intel Arc 140V XPU/BF16 training/resume/evaluation/generation, exact Phase-0 final-BPB parity, and throughput/memory within the pre-registered regression tolerances. No R1 learning/memory candidates or speculative extension points were introduced. See [docs/phases/phase-1.md](docs/phases/phase-1.md) and [docs/phases/phase-1-qa.md](docs/phases/phase-1-qa.md).

## Phase 2 — Reproducible experiment system

Status: **PASS / CLOSED**.

Add experiment manifests, baseline/treatment relationships, automatic provenance, multi-seed aggregation, result comparison and regression checks.

**QA gate:** a 3-seed baseline/treatment pair can produce mean/variance/effect summary plus compute/memory difference from machine-readable results without manual spreadsheet work.

Phase 2 closed with all frozen gates passing: manifest schema, deterministic run IDs, baseline/treatment relationships, 3-seed canonical XPU comparison, automatic aggregation, paired effects, resource effects, variance exposure, incomplete evidence rejection, duplicate-run protection, exact source-tree provenance, artifact hashing, CPU integration, XPU experiment, regression checks, tests, and documentation. No external tracking services or learning/memory mechanisms added. See [docs/phases/phase-2.md](docs/phases/phase-2.md) and [docs/phases/phase-2-qa.md](docs/phases/phase-2-qa.md).

## Parallel architecture transition — Model / Kernel Separation

Status: **TECHNICAL DEBT IDENTIFIED / NON-BLOCKING / PHYSICAL REFACTOR NOT AUTHORIZED**.

The validated Phase-1/Phase-2 implementation places the Transformer model, training, checkpoint, evaluation, generation and experiment tooling inside the same `mindforge/` package. `model.py` is already source-modular, but there is no architectural Model Contract separating the learned model from the future Kernel Runtime.

Target architecture distinguishes:

```text
MindForge Model Component
MindForge Kernel Runtime
Plugins / Extensions
Hosts / Products
Research / Tooling
```

with the boundary:

```text
Kernel Runtime <-> Model Contract <-> Model Component
```

This transition is deliberately **parallel to and non-blocking for PPF**. PPF-L3/L4/L5 research may continue independently. Model/kernel separation must not alter PPF semantics, benchmark truth, or use PPF as justification for speculative kernel changes.

Do not begin with folder/package moves. Before physical refactor, a separately authorized task must first freeze the smallest behavior-based Model Contract and compatibility tests, then adapt the current Transformer through that boundary and prove no relevant regression.

Activation gates:

```text
MKS-G1 — concrete reason to separate now
MKS-G2 — minimal model/kernel behavioral contract
MKS-G3 — compatibility test suite
MKS-G4 — current Transformer adapter path
MKS-G5 — no regression to frozen kernel evidence
MKS-G6 — no PPF/plugin semantics in Model Contract
MKS-G7 — no speculative universal plugin framework
```

Only after these gates PASS may physical package restructuring be authorized.

See [docs/research/model-kernel-separation-technical-debt.md](docs/research/model-kernel-separation-technical-debt.md) and [docs/research/mindforge-architecture-invariants.md](docs/research/mindforge-architecture-invariants.md).

## Phase 3 — First research slice: continual learning — INACTIVE / DEFERRED

Historical roadmap intent, superseded as an active commitment by the P0.9 STOP evidence. It may be reconsidered only after R1 or future independent evidence provides a justified substrate.

Use Phase 0 evidence to select exactly one minimal anti-forgetting treatment (for example replay, a small explicit buffer, or regularization), never all at once.

Measure A-before-B, A-after-B, B acquisition, forgetting, recovery speed and resource overhead.

**QA gate:** same seeds/data/compute protocol, treatment isolation verified, statistical summary generated, negative controls included where feasible.

## Phase 4 — Memory as a measurable mechanism — INACTIVE / DEFERRED

Historical roadmap intent, superseded as an active commitment by P0.10 STOP/BLOCKED. It may be reconsidered only after R1 or future independent evidence demonstrates measurable memory value.

Enter only if Phase 0/3 evidence supports explicit memory. Start with a minimal interface (`write`, `read`, `gate`, `measure`) rather than RAG/vector DB/knowledge graph/agents.

Questions: when to write, what to store, when to recall, whether recall helps, cost, interference, and forgetting/demotion.

**QA gate:** memory-off reproduces baseline; memory-on effect is reproducible; irrelevant-memory control measures harm/interference; overhead is reported.

## Phase 5 — Adaptive learning — INACTIVE / DEFERRED

Historical roadmap intent. It is not an active commitment and may be reconsidered only after R1 or future evidence justifies the prerequisite continual-learning/memory substrate.

Candidate hypotheses include adaptive write/replay, error- or novelty-triggered storage, concept formation, consolidation and demotion. Each is a separate treatment.

**QA gate:** one causal change per experiment, frozen thresholds/provenance, ablations and negative controls.

## Phase 6 — Instruction tuning

Add a narrow SFT path only after the research kernel is stable. Purpose: test whether discovered mechanisms survive post-training, not to build the best chatbot.

LoRA/PEFT is added only if resource measurements justify it.

## Phase 7 — Preference / reinforcement learning

Conditional progression: simple preference optimization → DPO or equivalent → GRPO only for a concrete research question. Never add RL methods to complete a feature checklist.

## Phase 8 — Scaling

Scale one dimension at a time: model size, data size, context length, or compute. Determine whether discovered effects disappear, persist or strengthen.

## Explicitly deferred

MoE, VLM, agents, RAG, tool calling, distributed/multi-node training, quantization, production serving and mobile inference are not commitments. They enter only when a research/product question requires them.

## Feature admission test

Every proposed feature must answer:

1. What question are we trying to answer?
2. What baseline does it compete against?
3. What metric can falsify the hypothesis?
4. What is the smallest implementation capable of testing it?

MindForge prefers one complete 500-line experiment over a 5,000-line architecture for experiments not yet proven worth running.

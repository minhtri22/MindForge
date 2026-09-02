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

## Phase 1 — End-to-end kernel

Turn successful Phase 0 prototypes into a clean path:

```text
dataset → tokenizer → Transformer → training → checkpoint → evaluation → generation
```

Required: one primary architecture, single-device training, gradient accumulation, supported mixed precision, checkpoint/resume, seeds, backend abstraction validated in Phase 0, and independent evaluation/inference entry points.

**QA gate:** unit tests + integration smoke train + checkpoint round-trip + resume equivalence + deterministic eval + malformed-config/error-path tests.

## Phase 2 — Reproducible experiment system

Add experiment manifests, baseline/treatment relationships, automatic provenance, multi-seed aggregation, result comparison and regression checks.

**QA gate:** a 3-seed baseline/treatment pair can produce mean/variance/effect summary plus compute/memory difference from machine-readable results without manual spreadsheet work.

## Phase 3 — First research slice: continual learning

Use Phase 0 evidence to select exactly one minimal anti-forgetting treatment (for example replay, a small explicit buffer, or regularization), never all at once.

Measure A-before-B, A-after-B, B acquisition, forgetting, recovery speed and resource overhead.

**QA gate:** same seeds/data/compute protocol, treatment isolation verified, statistical summary generated, negative controls included where feasible.

## Phase 4 — Memory as a measurable mechanism

Enter only if Phase 0/3 evidence supports explicit memory. Start with a minimal interface (`write`, `read`, `gate`, `measure`) rather than RAG/vector DB/knowledge graph/agents.

Questions: when to write, what to store, when to recall, whether recall helps, cost, interference, and forgetting/demotion.

**QA gate:** memory-off reproduces baseline; memory-on effect is reproducible; irrelevant-memory control measures harm/interference; overhead is reported.

## Phase 5 — Adaptive learning

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

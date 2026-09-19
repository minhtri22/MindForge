# MindForge

> Build small. Prove first. Scale only what survives contact with reality.

MindForge is a compact, local-first LLM kernel built to make training, evaluation and experimentation practical on consumer hardware. It is inspired by the clarity of **nanochat** and the breadth of **MiniMind**, while deliberately being neither a feature collection nor a purely educational Transformer.

The project grows through **thin, measurable, usable vertical slices**. Every uncertain assumption is tested before dependent architecture is added.

## Principles

1. **Thin slices over feature breadth** — build only what a concrete experiment needs.
2. **Prove before architecture** — uncertain assumptions belong in Phase 0.
3. **End-to-end before sophisticated** — raw text → tokenizer → train → checkpoint → eval → generation.
4. **Claims require baselines** — every treatment answers “better than what?”.
5. **Local-first, cloud-optional** — constrained hardware is a first-class target; cloud is for scale, not comprehension.
6. **Evidence gates development** — PASS advances; REVISE changes the experiment; STOP removes unsupported scope.

## Borrowed deliberately

From nanochat: small understandable code, cohesive end-to-end training, explicit evaluation, compute awareness, reproducibility, strong baselines, minimal abstraction.

From MiniMind: the option to explore SFT, PEFT, preference/RL methods, distillation, memory, continual learning, routing/MoE, and agents **only when justified by a measurable question**.

## Non-goals

MindForge is not a Hugging Face replacement, production serving platform, benchmark leaderboard, paper-implementation catalog, or miniature ChatGPT clone.

## First vertical slice

The first usable kernel must:

1. prepare a small text dataset;
2. train or load a tokenizer;
3. construct a tiny Transformer;
4. train it;
5. save and resume checkpoints;
6. measure validation loss;
7. generate text;
8. record experiment metadata.

## Research discipline

Each experiment records at minimum: experiment id, git commit, seed, model config, parameter count, dataset/token count, context length, batch/effective batch, optimizer/LR/steps, device/dtype, peak memory, wall-clock time, train/validation loss, and evaluation results.

Comparisons hold dataset, tokenizer, seeds, compute budget, and evaluation set constant whenever practical.

## Evidence states

- **PASS** — evidence supports continuing.
- **REVISE** — promising but the implementation or experiment must change.
- **STOP** — the assumption failed; dependent architecture is not built.

A STOP result is useful evidence.

## Hardware policy

Core model code avoids backend-specific assumptions. Device selection is explicit. Target-machine capability is measured, never inferred from specifications.

Phase 0 validated **Intel XPU + BF16** as the primary local training backend on the target Intel Arc 140V machine. CPU remains useful for preprocessing, tests, diagnostics and FP32 fallback. Other backends remain conditional on direct evidence.

## Model policy

The initial model stays deliberately boring: embedding, pre-norm attention/MLP residual blocks, final norm, LM head. Novel research starts around a strong boring baseline.

## Validated foundation

Phase 0 established a reproducible local foundation: MindForge byte-level BPE with a 16,384-token vocabulary, deterministic Vietnamese/English Wikimedia data, a 1M-token development pool, a ~10.34M-parameter Baseline-0, checkpoint/resume, independent evaluation, and machine-readable experiment provenance. See [docs/phases/phase-0.md](docs/phases/phase-0.md).

Phase 1 turns that evidence into a working compact end-to-end kernel under `mindforge/`. The default 10,339,200-parameter model is validated on Intel Arc 140V with XPU/BF16, including training, checkpoint/resume, independent evaluation and generation. See [docs/phases/phase-1.md](docs/phases/phase-1.md).

Phase 2 adds a reproducible experiment system: manifests, baseline/treatment relationships, multi-seed execution, automatic aggregation, paired comparison, resource comparison, and regression checks — all from machine-readable records without external dependencies. See [docs/phases/phase-2.md](docs/phases/phase-2.md).

Minimal command surface:

```text
python -m mindforge.tokenizer train --input ... --output ...
python -m mindforge.data prepare --tokenizer ... --train-text ... --validation-text ... --output-dir ...
python -m mindforge.train --config ...
python -m mindforge.evaluate --checkpoint ... --tokenizer ... --tokens ...
python -m mindforge.generate --checkpoint ... --tokenizer ... --prompt ...
python -m mindforge.experiment validate <manifest>
python -m mindforge.experiment run <manifest>
python -m mindforge.experiment summarize <manifest>
python -m mindforge.experiment check <manifest>
```

The active core direction is intentionally narrow:

```text
dataset
→ tokenizer
→ Transformer
→ training
→ checkpoint
→ evaluation
→ generation
```

Continual learning, explicit memory and adaptive/pattern mechanisms are **not yet core architecture commitments**. They are being investigated in a separate evidence-gated research track on `research/kernel-cl`. Negative results do not automatically terminate the track; they narrow the next admissible hypothesis while keeping unqualified mechanisms out of the stable kernel.

### Active Kernel Continual Learning research

The Kernel-CL track has progressed through controlled baseline, replay, long-horizon, optimizer-boundary, boundary-state, failure-mode and target-identifiability experiments. The current chain is documented append-only in [Lineage.md](Lineage.md) and under [docs/research/kernel-continual-learning/](docs/research/kernel-continual-learning/).

As of KCL-6.5.9.5:

- fixed global optimizer-boundary policies still do not satisfy the joint plasticity + retention + robustness contract;
- KCL-6.5.9.1 independently replicated positive-class boundary-regime heterogeneity;
- KCL-6.5.9.2 showed that the four-class `SAFE_ACTION_SET-v1` target is not qualified as predictable from stage + global H1-H9 boundary state;
- KCL-6.5.9.3 showed that neither richer pre-boundary LRBS-v1 state nor a zero-step future-task probe prospectively resolved the broad `A_ONLY` identifiability problem;
- KCL-6.5.9.4 established that `A_ONLY` is structurally heterogeneous and independently replicated two stable mechanism targets:
  - `MECH{P,R}`;
  - `MECH{P+R,R}`;
- KCL-6.5.9.5 then tested whether those two mechanism-specific targets are more identifiable than monolithic `A_ONLY` under the same frozen S2 representation and same class-balanced L2 logistic model family;
- KCL-6.5.9.5 result: **NEGATIVE — `NO_MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN`**;
- validation S2 macro recall:
  - `A_ONLY = 0.6155` — qualified;
  - `MECH{P,R} = 0.6863` — qualified, but gain over `A_ONLY` was only `+0.0708`, below the frozen `+0.10` threshold;
  - `MECH{P+R,R} = 0.5765` — not qualified;
- richer S2 contributed only marginal macro-recall gain over stage/global-state diagnostics, so target refinement alone does not explain the remaining identifiability gap;
- no adaptive boundary classifier/controller is qualified;
- protected confirmatory seeds remain untouched;
- KCL-7 is **not started**.

The next scientifically admissible direction is **not** a stronger classifier or another target-only split. A new milestone must first preregister a mechanistic representation hypothesis — especially one addressing the unresolved `MECH{P+R,R}` interaction — and compare it against the frozen S2 baseline on an entirely fresh non-confirmatory cohort. Until that hypothesis is frozen, the KCL chain stops at KCL-6.5.9.5.

## Roadmap

MindForge uses an evidence-driven capability roadmap:

```text
Question → smallest experiment → evidence → decision → next capability
```

See [PLAN.md](PLAN.md).

Research scope and deferred hypotheses are indexed in [docs/research/README.md](docs/research/README.md).

## Success criterion

MindForge succeeds when a research question can be expressed as:

```text
baseline + one meaningful change + controlled experiment + measurement
```

without weeks of framework work.

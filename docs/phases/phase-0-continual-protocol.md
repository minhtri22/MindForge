# Phase 0 — P0.9 Continual-Learning Feasibility Protocol

Protocol status: **PRE-REGISTERED BEFORE QUALIFICATION OUTCOMES**

Base commit: `0c0fb52ac5ce214fdaa0e577b499066606cb1b5b`

Scope is only P0.9 untreated continual-learning feasibility. P0.10, memory, replay, EWC, regularization treatments, distillation, adapters, and Phase 1 are out of scope.

## Research question and hypothesis

Question: can the frozen MindForge real-language baseline produce a reproducible, controlled catastrophic-forgetting signal on real language-modeling tasks?

Hypothesis: at least one bounded, pre-registered real-language A/B domain pair will be independently learnable, yet sequential untreated A→B training will degrade held-out A beyond a frozen meaningful threshold and beyond an equal-budget A→A control.

The experiment is falsifiable. Failure to establish that signal yields `REVISE`; inability to qualify any of the three bounded candidate families yields `STOP`.

## Frozen starting point

- Starting checkpoint: P0.8 `baseline0-final.pt`.
- Required SHA-256: `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`.
- Model: 10,339,200-parameter plain decoder-only Transformer, vocab 16,384, `d_model=320`, 8 heads, 4 layers, MLP 4x, learned positions, tied LM head.
- Tokenizer: frozen MindForge byte-level BPE 16,384.
- Dataset source family: frozen Wikimedia VI/EN snapshot `20260801` plus, only for candidate C3, deterministic natural-language conflict sentences using ordinary corpus vocabulary.
- Required corpus fingerprint: `c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696`.
- Backend/dtype: Intel XPU / BF16.

The P0.8 identity is not modified.

## Bounded qualification search

Exactly three candidate families are evaluated; no fourth candidate may be introduced in this increment.

### C1 — language specialization

- A: frozen Vietnamese Wikipedia training/validation split.
- B: frozen English Wikipedia training/validation split.
- Purpose: explicitly test, rather than assume, whether VI→EN creates meaningful interference.

### C2 — English style/domain specialization

- A: history/geography-heavy English Wikipedia articles.
- B: science/technology-heavy English Wikipedia articles.
- Article boundaries and train/validation membership come from the frozen English article manifest.
- A selection: at least 4 matches from the frozen history/geography keyword set and at most 1 technical-keyword match.
- B selection: at least 4 matches from the frozen technical keyword set and at most 3 history/geography-keyword matches.
- The two selectors are mutually checked for exact article overlap.

Frozen history/geography keyword set: `history, war, king, queen, empire, city, country, state, province, battle, dynasty, president, politic, geography, river, mountain`.

Frozen science/technology keyword set: `algorithm, computer, software, mathemat, physics, chemistry, biology, engineering, technology, network, data, programming, theorem, equation, system`.

### C3 — controlled lexical/knowledge conflict in natural language

- 128 deterministic entity identifiers are assigned in a balanced way to the ordinary Vietnamese labels `lam` and `đỏ` using SHA-256 parity.
- A and B use the same entities but exactly opposite label assignments.
- Training and validation use disjoint natural-language sentence templates; exact sentence overlap is prohibited.
- Each sentence repeats the entity-label relation several times in ordinary Vietnamese prose so the conflicting mapping is a meaningful fraction of the language-modeling target rather than an isolated arithmetic token transition.
- These labels are experimental conventions only and make no factual-world claim.

## Qualification protocol

- Dedicated qualification seeds: `404`, `505`. Final seeds are never used for domain selection.
- Context: 256.
- Micro-batch: 1.
- Gradient accumulation: 2.
- Effective batch: 2 contexts = 512 tokens/update.
- Qualification budget: 128 optimizer steps = 65,536 sampled training tokens per stage.
- Optimizer: AdamW, weight decay 0.1, gradient clip 1.0.
- Peak LR: `3e-4`.
- LR schedule: each stage starts a fresh 5% linear warmup then cosine decay to 10% of peak.
- Optimizer-state policy: load the frozen Baseline-0 optimizer state; continue optimizer moments from A into A2/B. Only the LR schedule restarts per stage.
- Evaluation: 16 deterministic evenly spaced held-out windows, fixed per candidate/domain and reused across seeds.

For every candidate and qualification seed, run:

1. Baseline checkpoint → A, measuring A learnability.
2. Baseline checkpoint → B, measuring B independent learnability.
3. The exact post-A checkpoint → A again for equal-budget A→A drift control.
4. The exact same post-A checkpoint → B for untreated sequential interference.

A and B are qualification-learnable only when each independent branch reduces its own held-out BPB by at least 5% for both qualification seeds and all metrics remain finite.

Qualification interference is considered usable when both qualification seeds have positive net interference, at least one of two seeds meets the final meaningful-forgetting threshold, and mean forgetting is positive.

Candidate selection rule is frozen before qualification outcomes: choose the first candidate in order `C1 → C2 → C3` satisfying both learnability and usable-interference qualification. This avoids selecting the numerically largest observed effect. If none qualifies, P0.9 is `STOP` and no final three-seed run is performed.

## Final frozen protocol template

After qualification chooses one candidate, its exact data hashes, sizes, and ID are appended below **before** running seeds 101/202/303. No domain, threshold, optimizer, LR, model-size, or compute-budget change is permitted after that append except an explicitly documented technical-correctness revision.

- Final seeds: `101`, `202`, `303`.
- Context: 256.
- Micro-batch: 1.
- Gradient accumulation: 2.
- Effective batch: 512 tokens/update.
- A training budget: 384 steps = 196,608 sampled tokens.
- B training budget: 384 steps = 196,608 sampled tokens.
- A→A control second-stage budget: 384 steps = 196,608 sampled tokens.
- Optimizer: AdamW, weight decay 0.1, gradient clip 1.0.
- LR: peak `3e-4`.
- LR schedule: each A/A2/B stage independently restarts 5% linear warmup then cosine decay to 10% peak.
- Optimizer-state policy: continue Baseline-0 optimizer state into A and continue the exact post-A optimizer state into either A2 or B.
- Evaluation windows: 16 deterministic windows selected from the frozen A_val/B_val streams; same windows across seeds.
- No anti-forgetting mechanism.

## Frozen metrics

Primary metric is BPB.

- `A_learning = A_initial - A_after_A`.
- `A_learning_fraction = A_learning / A_initial`.
- `B_acquisition = B_before_B - B_after_B`, where `B_before_B` is evaluated after A immediately before B.
- `B_acquisition_fraction = B_acquisition / B_before_B`.
- `forgetting = A_after_B - A_after_A`.
- `relative_forgetting = forgetting / A_after_A`.
- `control_drift = A_after_A2 - A_after_A`.
- `net_interference = A_after_B - A_after_A2`.

For reporting, `B_initial` from the common Baseline-0 checkpoint is also retained; the gate uses B-before-B so positive transfer from A cannot be miscounted as B acquisition.

## Frozen thresholds and final gate

For each seed:

- A learned: `A_learning_fraction >= 0.05`.
- B learned: `B_acquisition_fraction >= 0.05`.
- Meaningful forgetting threshold: `delta_A = max(0.10 BPB, 0.05 * A_after_A)`.
- Seed meets forgetting threshold when `forgetting >= delta_A`.

P0.9 is `PASS` only if all are true:

1. All three seeds learn A by at least 5% BPB.
2. All three seeds acquire B by at least 5% BPB after A.
3. Mean forgetting is at least the mean of the three frozen per-seed `delta_A` values.
4. At least 2/3 seeds individually meet their meaningful-forgetting threshold.
5. Mean net interference versus A→A is strictly greater than zero.
6. Every run remains finite and has no NaN/Inf/OOM/device failure.
7. The exact frozen protocol completes for all three seeds; no seed is selected or discarded by outcome.

If A/B learn but the forgetting gate fails, P0.9 is `REVISE`. If qualification cannot establish a usable pair within C1/C2/C3, P0.9 is `STOP`.

No significance test is claimed from three seeds. Aggregate mean, median, population standard deviation, min, and max are descriptive only.

## Final domain freeze

Qualification outcome: **STOP — no final domain selected**.

The bounded qualification run evaluated C1, C2, and C3 exactly once with seeds 404/505. No candidate satisfied the pre-registered qualification rule, so the final three-seed command is not authorized and this section intentionally has no `FINAL_SELECTED_CANDIDATE` marker. No threshold, LR, stage budget, model size, candidate definition, or selection rule was changed after observing qualification outcomes.

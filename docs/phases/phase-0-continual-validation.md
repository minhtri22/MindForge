# Phase 0 — Continual-Learning Validation

## 1. Executive result

**STOP**

MindForge did not establish a usable, reproducible real-language catastrophic-forgetting substrate within the pre-registered three-family bounded qualification search. No anti-forgetting treatment was run. The final seeds `101/202/303` were not authorized because no candidate passed qualification.

This is a falsification result, not evidence that catastrophic forgetting cannot exist in other tasks or budgets. It means the current Phase-0 bounded search did not produce a scientifically usable substrate without changing the frozen protocol after seeing outcomes.

## 2. Base commit

`0c0fb52ac5ce214fdaa0e577b499066606cb1b5b`

Starting P0.8 checkpoint SHA-256: `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`.

Dataset fingerprint: `c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696`.

## 3. Prior failed protocol

The older synthetic P0.9 used token-transition Domain A `+1` and Domain B `+2`. Mean A loss improved from `3.2091` before B to `2.8120` after B, giving forgetting `-0.3971`. That is positive transfer, not forgetting. Replay evidence from that experiment is therefore inconclusive and is not reused here.

The new increment uses only real-language or natural-language interference tasks and contains no replay, EWC, memory, regularization treatment, or Phase-1 work.

## 4. Qualification strategy

The protocol was written before qualification outcomes. Qualification used dedicated seeds `404/505`, context 256, micro-batch 1, gradient accumulation 2, 65,536 sampled tokens per stage, AdamW `3e-4`, weight decay 0.1, stage-local 5% warmup/cosine schedule, and continued optimizer state across A→A2/A→B branches.

Three and only three candidates were evaluated:

1. **C1** — Vietnamese Wikipedia → English Wikipedia language specialization.
2. **C2** — English history/geography-heavy Wikipedia → science/technology-heavy Wikipedia specialization.
3. **C3** — balanced contradictory entity-label mappings embedded in ordinary Vietnamese natural-language sentences, with disjoint train/eval templates.

Selection was pre-registered as the first `C1 → C2 → C3` candidate satisfying both-seed A/B independent learnability plus usable interference. No fourth candidate or post-outcome budget/LR change was allowed.

## 5. Rejected candidates

### C1 — VI → EN

Both qualification seeds showed small positive interference, but neither A nor B reached the frozen 5% independent learnability gate within the fixed budget.

| Seed | Independent A learning | Independent B learning | Sequential B acquisition | Forgetting BPB | Delta A | Net interference |
|---:|---:|---:|---:|---:|---:|---:|
| 404 | 2.568% | 1.984% | 4.261% | 0.1535 | 0.4095 | 0.2782 |
| 505 | 2.482% | 1.953% | 4.106% | 0.1631 | 0.4099 | 0.2974 |

Mean forgetting was `0.1583 BPB`, below the meaningful threshold on both seeds. C1 was rejected as insufficiently learned/insufficiently strong under the pre-registered thin-slice budget.

### C2 — history/geography → science/technology

C2 also failed the 5% independent learnability gate. In addition, A improved after B, so the observed forgetting metric was negative.

| Seed | Independent A learning | Independent B learning | Sequential B acquisition | Forgetting BPB | Delta A | Net interference |
|---:|---:|---:|---:|---:|---:|---:|
| 404 | 2.534% | 2.600% | 2.418% | -0.1168 | 0.4662 | 0.0497 |
| 505 | 2.473% | 2.600% | 2.284% | -0.1168 | 0.4665 | 0.0497 |

This is positive transfer on A, not catastrophic forgetting.

### C3 — controlled natural-language conflict

C3 was strongly learnable independently: A improved by `43.1–46.2%` and B by `43.6–44.4%`. It still failed as a valid continual-learning substrate. Training A transferred so strongly to B that `B_before_B` was already much better than Baseline-0; the subsequent B stage then worsened B rather than acquiring it.

| Seed | Independent A learning | Independent B learning | Sequential B acquisition | Forgetting BPB | Delta A | Net interference |
|---:|---:|---:|---:|---:|---:|---:|
| 404 | 43.126% | 43.607% | -0.166% | 0.0056 | 0.2964 | -0.0112 |
| 505 | 46.234% | 44.376% | -5.380% | 0.2973 | 0.2802 | 0.0070 |

Seed 505 alone crossed its A-forgetting delta, but the B stage failed the acquisition requirement and seed 404 had negative net interference. Counting this as catastrophic forgetting would violate the interpretation rule that degradation without successful B acquisition is a training/confounding failure rather than valid continual-learning interference.

## 6. Final frozen protocol

No final A/B pair was frozen. Qualification returned `STOP`, so the protocol intentionally contains no `FINAL_SELECTED_CANDIDATE` marker and the final `101/202/303` experiment was not run.

Had a candidate qualified, the already-pre-registered final configuration would have been 384 steps / 196,608 sampled tokens each for A, B, and A→A control, context 256, effective batch 512 tokens/update, AdamW `3e-4`, stage-local warmup/cosine, and continued exact post-A optimizer state. Those settings were not used to rescue qualification after observing results.

## 7. Data integrity

All candidates use the frozen MindForge BPE and frozen Wikimedia corpus provenance. C1 inherits the frozen article-level SHA-256 train/validation split. C2 selects disjoint articles only from those already-separated English train/validation collections. C3 has deterministic SHA-256-balanced opposite mappings and exact train/validation sentence overlap `0`.

| Candidate | Domain | Train bytes | Validation bytes | Train tokens | Validation tokens | Fingerprint |
|---|---|---:|---:|---:|---:|---|
| C1 | A / VI | 33,565,953 | 4,204,353 | 7,149,033 | 953,465 | `1b8c0c123f92aad7e7237202f55c7b2872b7b551ef7d15e6d60fd34f5e54bc75` |
| C1 | B / EN | 33,571,974 | 4,227,443 | 8,449,941 | 1,079,376 | `96af2b564edf7b5479cdfcf9d45e55880493e7c39643ae7c0e3cabd038c1d813` |
| C2 | A / history-geography | 7,030,308 | 1,026,323 | 1,819,187 | 274,198 | `373ab9658a087004d3791b5dbd032296497f9be800252477687dd21d5d431a45` |
| C2 | B / science-technology | 337,439 | 61,151 | 87,532 | 15,047 | `b7a03a6640fe0f91201605aa1ef1279fda00479083d425359aebf75f7f25182d` |
| C3 | A / conflict mapping | 115,774 | 40,170 | 27,854 | 10,015 | `ccd07f0da131136fe11c4aba2cdb4e08e78023cc1db22509819550aa0c20cb78` |
| C3 | B / opposite mapping | 115,902 | 40,210 | 27,854 | 10,015 | `a0860ca01ba193b95c3e294da74035de3dbe56195a155b46854b50cb2b265917` |

C2 contains 429/48 A train/validation articles and 47/7 B train/validation articles with A/B article overlap `0`.

## 8. Starting Baseline-0

- Checkpoint: P0.8 `baseline0-final.pt`.
- SHA-256: `795e23802ea07509285f3f63bf226678b955a360785f3f74a98f65ac6922f079`.
- Parameters: `10,339,200`.
- Architecture: frozen 4-layer, `d_model=320`, 8-head decoder-only Transformer with learned positions and tied LM head.
- Tokenizer: MindForge byte-level BPE, vocab 16,384.
- Corpus fingerprint: `c04d6f39c9fc1f47aa068c283e6b029ece1cd316611f64c9270d29453bfbc696`.
- Backend/dtype: Intel XPU / BF16.

## 9. Thresholds

Frozen before qualification/final outcomes:

- A independent learning: at least 5% BPB reduction.
- B independent qualification learning: at least 5% BPB reduction.
- Final B acquisition after A: at least 5% BPB reduction from `B_before_B` to `B_after_B`.
- Meaningful forgetting per seed: `max(0.10 BPB, 0.05 * A_after_A)`.
- Final seed criterion: mean forgetting at least mean delta and at least 2/3 seeds individually meeting delta.
- Mean net interference versus equal-budget A→A control: strictly greater than zero.

No threshold was relaxed after qualification.

## 10. Per-seed results

The final three-seed protocol was not authorized. Reporting invented or extrapolated `101/202/303` numbers would violate the protocol.

| Seed | A_initial | A_after_A | A_after_A2 | A_after_B | B_initial | B_after_B | A learning % | B learning % | Forgetting | Net interference | Result |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 101 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | N/A | N/A | N/A | N/A | NOT AUTHORIZED |
| 202 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | N/A | N/A | N/A | N/A | NOT AUTHORIZED |
| 303 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | N/A | N/A | N/A | N/A | NOT AUTHORIZED |

## 11. Aggregate results

No final aggregate exists because no final candidate qualified. Qualification aggregates are retained in `experiments/results/phase0_continual_qualification.json`; they are candidate-selection evidence, not a substitute for the required final three-seed gate.

## 12. Interpretation

The bounded search produced three different failure modes:

- C1: modest interference but insufficient domain learning under the frozen thin-slice budget.
- C2: insufficient learning plus positive transfer.
- C3: strong independent learnability, but sequential B acquisition fails after strong A→B transfer; one-seed A degradation is therefore not valid evidence of catastrophic forgetting.

MindForge therefore does **not** currently have a reproducible real-language forgetting signal suitable as a benchmark substrate. This does not mean MindForge solved continual learning, nor does it justify any anti-forgetting mechanism.

## 13. Failure/caveats

1. Qualification deliberately caps search at three families, so STOP is conditioned on this bounded design space and compute budget.
2. C1/C2 may become more learnable with more tokens, but increasing stage length after observing failure would violate the frozen qualification protocol and is not done here.
3. C3 demonstrates why independent learnability alone is insufficient: positive transfer can make B-before-B already easy, after which B-stage degradation is an invalid acquisition signal.
4. Three final seeds were never run; no statistical claim is made.
5. No anti-forgetting treatment was tested.

## 14. P0.9 gate

**P0.9 = STOP.**

None of the three pre-registered candidate task families satisfied the frozen qualification rule. Continuing to search or increasing compute until forgetting appears would benchmark-fit the substrate and is explicitly prohibited by this increment.

## 15. P0.10 consequence

**P0.10 remains BLOCKED / STOP.**

There is still no controlled, reproducible memory-value/forgetting signal on which to evaluate memory. P0.10 must not start from this result. Phase 1 remains **NOT AUTHORIZED**.

Overall Phase 0 status after this increment: **STOP** under the current evidence-gated roadmap.

## Reproduction

Qualification command:

```powershell
.\.venv\Scripts\python.exe experiments\phase0_continual_real.py qualification
```

An exit code of `2` with `status: STOP` is the expected canonical outcome for the frozen evidence. The final command is intentionally blocked by the absence of a final-domain freeze marker.

Machine-readable evidence:

- `experiments/results/phase0_continual_qualification.json`
- `experiments/results/phase0_continual_real.json`

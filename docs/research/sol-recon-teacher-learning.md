# MindForge-Mobile + sol_recon teacher-distillation proof

## Provenance

Source repository: `minhtri22/MindForge`
Observed `main` HEAD: `d0c4c33d17c2b36abc19411e946d3350786760f3`.
The Transformer implementation mirrors `mindforge/model.py` from that revision.

Direct `git clone` was blocked by sandbox DNS, so the kernel source was mirrored through the GitHub connector.

## Scope

This experiment intentionally excludes PPF. It adds only:

- a lightweight SQLite behavioral-lesson memory;
- a `sol_recon` teacher-feedback format;
- teacher-guided supervised updates of the MindForge Transformer kernel;
- held-out evaluation on unseen paraphrases.

The teacher feedback was authored by GPT-5.6 Sol at the observable answer/behavior level. No hidden chain-of-thought is stored.

## Sandbox adaptation

The production MindForge default kernel is about 10.34M parameters with a 16,384-token BPE vocabulary. The sandbox has PyTorch CPU but not the `tokenizers` package and CPU training of the full 10M/16K-output configuration exceeded the execution timeout.

Therefore the completed proof uses the SAME `TransformerLM` architecture but a sandbox-scale config:

- vocab: 512 (byte adapter uses 0-257)
- d_model: 128
- heads: 4
- layers: 2
- context: 256

This is a kernel-mechanism proof, not a benchmark of the validated 10.34M checkpoint.

## Teacher lessons

Ten behavioral families were taught: evidence discipline, ambiguity, permission, local routing, frontier escalation, calendar routing, message routing, latest correction, abstention, and concise exact-format output.

Lessons are persisted independently of model weights in SQLite and retrieved by lightweight keyword matching. Training cases contain the retrieved lesson plus an unseen-style task and target routing label.

## Result

Constrained router decoding (candidate LM likelihood):

- N0: 3/30 = 10.0%
- N5: 10/30 = 33.3%
- N10: 14/30 = 46.7%

Thus the same neural kernel improved +36.7 percentage points from N0 to N10 on held-out paraphrases.

Category results at N10:

- evidence: 0/3
- ambiguity: 1/3
- permission: 2/3
- local: 1/3
- frontier: 1/3
- calendar: 3/3
- message: 1/3
- latest correction: 2/3
- abstention: 2/3
- concise: 1/3

The result is not monotonic: some early abilities regressed after later teaching. This is evidence of interference / forgetting.

Free-form generation remained unstable and repetitive. The stronger result came from constrained routing-label likelihood, which fits the frozen MindForge-Mobile role (understand/route) better than chatbot-style generation.

## Verdict

`MECHANISM_PROOF_POSITIVE_BUT_WEAK`

What is proven:

1. MindForge's Transformer kernel can be used as the actual trainable student rather than a rule-based placeholder.
2. External Frontier-teacher lessons can be persisted outside weights and injected through `sol_recon`.
3. Teacher-supervised updates produced measurable held-out transfer on unseen paraphrases.
4. A tiny kernel benefits from constrained router decoding.

What is NOT proven:

1. The production 10.34M MindForge checkpoint improves by the same amount.
2. Long-term online learning is stable.
3. The memory retrieval scheme is sufficient.
4. PPF integration works; PPF was intentionally excluded.
5. The system approaches frontier-model capability.

## Next experiment

Run the identical protocol on the actual 10.34M MindForge kernel/checkpoint on the target Intel Arc 140V/XPU, preserving a frozen held-out set. Replay remains an ablation, not a promoted mechanism; see `sol-recon-replay-ablation.md`.

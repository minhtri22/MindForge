# sol_recon teacher-learning research experiment

Status: **research only / not promoted to MindForge core**.

This directory preserves the sandbox proof that combines the existing MindForge Transformer kernel with lightweight behavioral lesson memory and Frontier-teacher supervision. PPF is intentionally out of scope.

The sandbox reproducer uses the repository `TransformerLM` implementation with an explicit reduced configuration (`vocab_size=512`, `d_model=128`, `n_heads=4`, `n_layers=2`, `max_context=256`) and a byte adapter because the sandbox lacked the production tokenizer runtime and could not complete the full 10.34M/16K training loop within the execution limit.

`replay_ablation.py` is an ablation only. Replay is **not** a default architecture decision. Current evidence is `REPLAY_ONLY_INSUFFICIENT_FOR_ANTI_FORGETTING`.

Generated checkpoints, SQLite databases, and other runtime artifacts belong under `runs/` and should not be committed.

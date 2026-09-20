# 10 — Test Plan

## A. Schema/config tests

- every example validates experiment_config schema;
- unknown config vocabulary rejected;
- execution/data/evaluation/checkpoint/run/reasoning schemas have valid positive + negative fixtures;
- confirmatory lock rejects unresolved refs/auto precision.

## B. Unit

Canonical hashes, split determinism, freshness guard for seed/split/fixture, near-dedup/contamination parameter identity, reasoning parser modes, checkpoint selection tie-breaks, lineage chain/seal, Modelfile derivation.

## C. Integration

1. Qwen2.5-0.5B-Instruct pinned reference loads.
2. fixture data -> 2+ steps -> atomic checkpoint -> kill -> exact resume.
3. phase parent/child lineage.
4. HF canonical reload.
5. HF -> GGUF -> llama.cpp.
6. GGUF -> Ollama.
7. visible/hidden/off reasoning semantics where capability permits.
8. same InferenceGenerationContract across runtimes.
9. evidence payload -> ZIP -> external ZIP checksum.

## D. Failure injection

Corrupt shard/checksum, disk budget fail, process kill during checkpoint, stale lock, concurrent writer, wrong adapter base, synthetic unsupported architecture, tokenizer mismatch, malformed reasoning tags, missing sandbox/network isolation, Ollama unavailable, converter mismatch, required metric below threshold, secret detector hit.

## E. Reproducibility

Micro-run must preserve config/data hashes, selected step, logical consumed-token cursor, artifact inventory and metric tolerance according to declared determinism class.

## F. Security

Generated-code fixture attempts network/file/child-process escape and must be blocked by sandbox. Evidence redaction fixture injects fake token and confirms bundle does not leak it.

## G. Windows

Paths with spaces/Unicode, long-path handling, subprocess quoting, executable discovery, no-symlink fallback, atomic replace behavior, Job Object/process-tree kill, resume after interruption.

## H. Unsupported architecture fixture

Use deterministic synthetic/fake model config type that ModelAdapter registry intentionally marks unsupported; do not depend on an upstream architecture remaining unsupported forever.

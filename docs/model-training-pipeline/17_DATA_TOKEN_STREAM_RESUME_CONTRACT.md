# 17 — Data, Token Stream & Resume Contract

## 1. Source identity

Each source resolves immutable identity. Wikipedia includes project/language/dump date/artifact/URI/upstream checksum/local SHA-256/parser version. Code keeps repository/revision/path/language/license evidence/content hash when source supports it. Unknown license defaults deny for release.

## 2. Privacy/secret hygiene

Public text has pinned PII policy. Code has pinned secret scanner/ruleset. Raw sensitive values are not copied into evidence.

## 3. Normalization/dedup/contamination

Transforms are versioned/hashed. Exact dedup uses canonical bytes hash. Near-dedup freezes algorithm/tokenizer/ngram/signature/threshold/representative rule. Contamination freezes fixture hash, normalization, window/hash/threshold/action.

## 4. Split/freshness

Split identity is deterministic from algorithm version, seed and document identity. Freshness registry protects seed IDs, split IDs and fixture-set IDs.

## 5. Phase-scoped TokenStreamContract

Every training phase freezes its own stream contract:

- tokenizer hash after resolution;
- BOS/EOS/separator policy;
- sequence length/truncation;
- packing and cross-document behavior;
- sampling/shuffle/buffer/seed;
- worker count;
- mixture sampler if multiple datasets.

Reasoning/chat SFT may forbid cross-document packing even when CPT enables it.

Data manifest stores token_streams keyed by phase_id and a stream_hash for each.

## 6. ResumeCursor

Checkpoint persists dataset/shard, document/token offset, packed sequence index, consumed tokens, sampler cycle, shuffle buffer, global/per-worker RNG, mixture state and gradient-accumulation micro-step.

Backend unable to restore exact logical stream must declare best_effort; no silent downgrade.

## 7. Token accounting

consumed_tokens counts post-tokenization input tokens; effective_loss_tokens is separate after loss masking. Budget gates use frozen counter semantics.

## 8. Fingerprint

Data identity covers immutable sources, transform/quarantine decisions, dedup/contamination, exact splits, tokenizer identity and every phase stream hash; transient paths/mtime are excluded.

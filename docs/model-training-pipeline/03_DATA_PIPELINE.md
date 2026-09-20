# 03 — Data Pipeline

Canonical semantics ở 17_DATA_TOKEN_STREAM_RESUME_CONTRACT.md.

## 1. Stages

ACQUIRE -> VERIFY -> LICENSE/PRIVACY/SECRET -> NORMALIZE -> FILTER -> EXACT/NEAR DEDUP -> CONTAMINATION -> SPLIT -> TOKENIZE/PACK -> FINGERPRINT -> FREEZE.

## 2. Source identity

Không latest sau prepare. Wikipedia identity gồm project/language/dump date/artifact/URI/checksum/tool versions. Code identity giữ repo/file/revision/license evidence theo adapter capability.

Concrete references:
- examples/train_wikipedia_cpt.yaml: enwiki 20260301.
- examples/train_code_cpt.yaml: codeparrot/codeparrot-clean tại revision 35a59fb025bc0a102f7d96eac09d145b896d487b; development-only cho tới khi exact repository revision + license provenance được enrich.

## 3. Security/privacy/license

Unknown code license default deny for release; PII policy required cho public text; secret scanner required cho code; raw secrets/PII không đi vào evidence.

## 4. Dedup/contamination

Algorithm/version/normalization/parameters phải freeze. Near-dedup và contamination không được chỉ ghi configurable.

## 5. Split/freshness

Exact split identities lưu manifest. Freshness registry bảo vệ seeds, splits và fixture sets.

## 6. Token stream/resume

Training dùng frozen TokenStreamContract. Resume giữ shard/document/token/packed-sequence, shuffle buffer, worker RNG, mixture state và gradient-accumulation micro-step.

## 7. Reasoning data

Dataset giữ semantic fields messages/reasoning/answer/provenance/verifier. ModelAdapter serializer map sang tokens; data layer không giả định mọi model dùng think tags.

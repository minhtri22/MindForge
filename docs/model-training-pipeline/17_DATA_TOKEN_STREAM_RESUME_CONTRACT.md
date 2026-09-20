# 17 — Data, Token Stream & Resume Contract

## 1. Dataset identity

Mỗi dataset source phải resolve thành immutable `DatasetSourceIdentity`.

### Wikipedia

Bắt buộc:

- project/edition (ví dụ enwiki);
- language;
- dump date;
- dump artifact type;
- exact source URI;
- upstream checksum nếu có;
- downloaded file SHA-256;
- decompressor/parser name + version/hash.

`snapshot: latest` bị cấm sau prepare.

### Code

Reference adapter phải có manifest cụ thể. Production/release corpus bắt buộc giữ repository/file provenance ở mức nguồn hỗ trợ:

- repository URL/id;
- source revision;
- relative path;
- detected language;
- license evidence;
- content hash.

Unknown license mặc định `deny` cho release.

## 2. Privacy and secret hygiene

Trước tokenization:

- public text chạy PII policy: `report|quarantine|redact|deny` theo configured detector/version;
- code chạy secret/credential scanner pinned version/ruleset;
- hits phải vào quarantine report với content hash và reason;
- raw secrets/PII không được chép vào logs/evidence; evidence chỉ giữ hash/metadata cần audit.

## 3. Normalization contract

Mỗi transform có version/hash và parameters. Text Unicode normalization phải khai báo form. Code không được normalize whitespace/indentation trừ rule explicit.

Document identity được tính **sau canonical source extraction nhưng trước destructive filters**, và transform lineage nối input -> output hash.

## 4. Exact and near dedup

Exact dedup: SHA-256 canonical document bytes.

Near-dedup phải freeze:

```yaml
near_dedup:
  algorithm: minhash_lsh
  tokenizer: unicode_word_v1
  ngram_size: 5
  num_perm: 128
  bands: 32
  similarity_threshold: 0.85
  representative_rule: lowest_document_id
```

Các giá trị trên chỉ là reference defaults cho smoke; real execution contract có thể khác nhưng phải đầy đủ. Thay bất kỳ parameter nào -> data fingerprint mới.

## 5. Contamination contract

Detector phải freeze:

- fixture set ID/hash;
- text normalization;
- tokenization;
- n-gram/window size;
- hash algorithm;
- match threshold;
- handling action `remove|quarantine|fail`.

Fresh fixtures có `freshness_class` và không được inspect ở development/calibration.

## 6. Split identity and freshness registry

Split được quyết định bằng `split_seed + document_identity + algorithm_version`.

Manifest lưu exact IDs/hashes.

Freshness registry quản lý ba loại tài nguyên:

- seed IDs;
- split IDs;
- fixture-set IDs.

CLI guard kiểm cả ba; không chỉ seed. Access event được append vào lineage.

## 7. TokenStreamContract

Trước training phải freeze:

```yaml
token_stream:
  tokenizer_hash: ...
  add_bos: false
  add_eos: true
  separator_policy: eos
  sequence_length: 2048
  truncation: right
  packing:
    enabled: true
    cross_document: true
    remainder_policy: carry
  sampling:
    mode: without_replacement
    shuffle_algorithm: buffered_v1
    shuffle_buffer_size: 10000
    seed: 123
  workers: 4
```

Nếu `cross_document=true`, loss masking/document boundary behavior phải explicit.

Mixture sampling freeze theo target token fraction + sampling algorithm. Report actual token fraction/deviation.

## 8. ResumeCursor

Recoverable checkpoint phải giữ đủ trạng thái để replay chính xác stream logical:

- dataset/shard id;
- document identity/index;
- token offset trong document nếu cần;
- packed sequence index;
- consumed effective tokens;
- sampler epoch/cycle;
- shuffle algorithm + buffer contents/IDs;
- global sampler RNG;
- per-worker RNG/state;
- mixture sampler state;
- gradient accumulation micro-step.

Backend nào không thể restore chính xác phải khai `resume_fidelity=best_effort`; confirmatory run chỉ được dùng nếu execution contract cho phép và tolerance/restart policy đã freeze.

## 9. Token counting

`consumed_tokens` là tokens contributing to model input after tokenization/packing, không phải raw character count. `effective_loss_tokens` được report riêng sau loss mask.

Token budget gate dùng canonical counter đã freeze.

## 10. Data fingerprint

Data manifest hash bao phủ:

- source identities;
- transform versions/parameters;
- quarantine decisions;
- dedup/contamination config;
- exact split membership;
- tokenizer hash;
- TokenStreamContract excluding transient cache paths.

Cache path/mtime không được tham gia identity.

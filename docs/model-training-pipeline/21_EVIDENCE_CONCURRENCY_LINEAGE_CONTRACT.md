# 21 — Evidence, Concurrency & Lineage Contract

## 1. Two lineages

Software-development lineage tracks Git commits/tests/review. Training-run lineage tracks data lock, execution lock, phases, checkpoints, eval/export/runtime/promotion. Run provenance cross-references exact software SHA.

## 2. Hash chain and seal

Every run event has sequence, timestamp, type, payload hash, previous hash and event hash. Final chain head is sealed with frozen config, data manifest, adjudication and artifact inventory hashes.

## 3. Bundle order — no circular hash

Canonical order:

1. finalize evidence payload files;
2. create evidence/PAYLOAD_SHA256SUMS over payload files excluding ZIP/external bundle metadata;
3. verify payload manifest;
4. create evidence.zip from finalized payload;
5. compute evidence.zip.sha256 outside the ZIP;
6. create external bundle_manifest.json outside the ZIP referencing payload-manifest hash and ZIP hash;
7. hash bundle_manifest.json for release/promotion record.

No file is allowed to claim a checksum over itself.

## 4. One writer per run

Mutating a run requires exclusive lock with process/host/acquisition/software identity and stale-lock policy. A second writer is rejected.

## 5. Atomic metadata

Write temp in same filesystem, flush/fsync where supported, parse/hash verify, atomic replace, directory fsync where supported. Lineage append is locked and verifies previous head.

## 6. Atomic checkpoint

WRITING -> VERIFIED -> COMMITTED.

Write under .partial, fsync, generate hashes, reload/validate, create CHECKPOINT_COMPLETE.json, atomic rename, then append lineage. Partial checkpoint is never resumable/canonical.

## 7. Crash recovery

Detect stale lock/partial writes, recover last COMMITTED state, append recovery event. If exact scientific state cannot be proven, mark INVALID/new run rather than guess.

## 8. Specification checksum

Documentation SHA256SUMS is regenerated only after QA-driven patches settle. Mismatch is QA FAIL.

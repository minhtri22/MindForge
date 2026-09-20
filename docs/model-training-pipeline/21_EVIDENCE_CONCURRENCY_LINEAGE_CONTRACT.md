# 21 — Evidence, Concurrency & Lineage Contract

## 1. Two lineages

Never conflate:

### Software-development lineage
Tracks implementation milestones:
- Git commit SHA;
- tests;
- changed paths;
- review/QA result.

Stored in repository docs or Git history.

### Training-run lineage
Tracks experimental/runtime events for one run:
- data freeze;
- execution lock;
- phase transitions;
- checkpoints;
- evaluation;
- export/runtime verification;
- promotion.

Stored under `runs/<run_id>/lineage.jsonl`.

Cross-reference: run provenance records the exact software Git SHA.

## 2. Append-only hash chain

Every run lineage event has:
- monotonic sequence number;
- UTC timestamp;
- event type;
- payload hash;
- previous_event_hash;
- event_hash.

Chain head is sealed in final evidence manifest. Rewriting the chain changes the sealed head.

## 3. External seal

At adjudication/bundle:
```json
{
  "run_id":"...",
  "lineage_head_hash":"...",
  "frozen_config_hash":"...",
  "data_manifest_hash":"...",
  "adjudication_hash":"...",
  "artifact_inventory_hash":"..."
}
```

This manifest is hashed and recorded in:
- external `evidence.zip.sha256`;
- release/promotion record;
- optionally Git commit/signature for long-term anchoring.

Hash chain alone is not considered tamper-proof without this seal.

## 4. Evidence bundle order — no circular hash

Canonical order:

1. finalize run payload files;
2. generate `evidence/PAYLOAD_SHA256SUMS` covering payload files **excluding** ZIP and external ZIP checksum;
3. verify payload manifest;
4. create `evidence.zip` from the finalized evidence payload;
5. compute `evidence.zip.sha256` **outside** the ZIP;
6. write bundle manifest referencing both payload-manifest hash and ZIP hash.

Never include a checksum that claims to hash the file containing itself.

## 5. Workspace/run locks

One writer per run.

Before mutating `runs/<run_id>` acquire exclusive run lock with:
- owner PID/process identity;
- host;
- acquisition time;
- software SHA;
- stale-lock recovery rules.

Read-only status/eval inspection may use shared/read semantics only when files are finalized.

Two processes must never train/resume/write checkpoint for same run concurrently.

## 6. Atomic metadata writes

For JSON/YAML/JSONL state:
- write temp file in same filesystem;
- flush/fsync where supported;
- verify parse/hash;
- atomic rename/replace;
- directory fsync where supported.

Lineage append uses a locked append protocol and verifies previous head.

## 7. Atomic checkpoint commit protocol

Checkpoint state:

```text
WRITING -> VERIFIED -> COMMITTED
```

Protocol:
1. write to `.partial/<checkpoint_id>`;
2. write all weights/state;
3. fsync;
4. generate SHA256 manifest;
5. reload/validate required files;
6. create `CHECKPOINT_COMPLETE.json`;
7. atomic rename to final checkpoint directory;
8. append `CHECKPOINT_WRITTEN` lineage event.

Checkpoint without completeness marker is not resumable/canonical and is cleaned/quarantined according to recovery policy.

## 8. Crash recovery

At startup:
- detect stale writer lock;
- inspect partial writes;
- never promote a partial checkpoint;
- recover last committed state;
- append recovery event;
- if scientific state cannot be proven, mark run INVALID rather than guessing.

## 9. Evidence references

Every PASS/FAIL reason should point to stable relative artifact path + SHA-256. Reports are indexes over evidence, not source of truth.

## 10. SHA256SUMS for specification repository

Documentation-package `SHA256SUMS` is regenerated only after final remediation/QA docs settle. A mismatch is a QA FAIL.

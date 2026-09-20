# 06 — Checkpoint & Provenance

Canonical schema: schemas/checkpoint_manifest.schema.json. Atomic write/evidence/lineage: 21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md.

## 1. Recoverable checkpoint

Must include/hash weights, optimizer, scheduler, AMP scaler khi dùng, Python/NumPy/framework RNG, exact sampler/ResumeCursor, gradient accumulation micro-step, step/consumed tokens, config/data hashes, exact parent artifact hash, phase id và completeness status.

Folder không có committed completeness marker không resumable/canonical.

## 2. Canonical checkpoint

Được selected bởi phase-scoped rule và chứa HF config/tokenizer/template + weights + training/provenance/hash manifests.

## 3. Hash policy

SHA-256 files/artifacts; canonical serialized config/manifests; directory hash over sorted relative path + file hash; mtime/cache path excluded.

## 4. Lineage

Training-run lineage khác software-development lineage. Run chain có previous-event hash và final external seal.

## 5. Resume fidelity

Checkpoint declare exact hoặc best_effort. Confirmatory/release expectations freeze trước run; backend không được silently downgrade.

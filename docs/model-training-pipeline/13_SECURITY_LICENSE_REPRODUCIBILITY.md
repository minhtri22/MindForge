# 13 — Security, License, Reproducibility

Canonical security contract: 20_SECURITY_PRIVACY_SANDBOX_CONTRACT.md.
Canonical evidence/concurrency: 21_EVIDENCE_CONCURRENCY_LINEAGE_CONTRACT.md.

## 1. Secrets
Credentials only via env/keyring; redact logs/evidence; final bundle secret scan required.

## 2. Remote code
Denied by default. Allow only immutable pinned source + reviewed allowlist + restricted execution evidence.

## 3. Dataset
Text has license + privacy policy. Code release data requires provenance/license policy and secret scan; unknown license defaults deny.

## 4. Model rights
Record upstream license/restrictions; pipeline never infers redistribution rights.

## 5. Generated code
Unit/function benchmarks execute only under sandbox with no-network, no inherited secrets, quotas, timeout and restricted filesystem. If required isolation unavailable, release benchmark is BLOCKED.

## 6. Supply chain
Pin package/tool/model/data identities and checksums when authoritative source provides them.

## 7. Reproducibility
Bundle identifies software SHA, dependency/tool versions, exact model/data, transform/token-stream contract, seeds, resource class, export/runtime versions and declared determinism/tolerance.

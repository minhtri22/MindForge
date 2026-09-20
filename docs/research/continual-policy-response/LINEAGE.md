# CPRM Lineage

Status: **APPEND-ONLY**

This file is append-only. Existing entries must never be rewritten, reordered or
silently removed.

---

## 2026-09-20 — CPRM Branch Created

- Branch: `research/continual-policy-response`.
- Exact parent commit: `0700601f9196d3c5989fa8eb5169f28b1bb01799`.
- Parent decision: ACO formally converged and terminated; Option 2 selected.
- CPRM is a separately named program and is **not ACO-2**.
- Scientific execution: **NONE**.
- Fresh CPRM scientific seeds consumed: **NONE**.
- Model fitting: **NONE**.
- Controller: **CLOSED**.
- KCL-7: **CLOSED**.
- Protected KCL cohort: **UNTOUCHED**.

---

## 2026-09-20 — CPRM-0 Specification Foundation Frozen for QA

- Research object: policy-specific continuous responses + A-relative contrasts.
- Primary population: all prospectively eligible matched boundaries.
- Eligibility conditioned on post-action outcome/hard label: **FORBIDDEN**.
- ACO-1 40-seed cohort: **HISTORICAL / SPENT / EXCLUDED**.
- Protected KCL cohort: **EXCLUDED**.
- Mandatory baselines: action-global mean, action-by-stage mean, low-capacity linear state-response baseline.
- Finite roadmap frozen: CPRM-0 → CPRM-1 → CPRM-2 → conditional CPRM-3 → CPRM-4 → CPRM-5.
- CPRM-0 state: **PENDING ZERO-SCIENCE SPECIFICATION QA**.
- Scientific execution authorization: **NONE**.

---

## 2026-09-20 — CPRM-0 QA Attempt 1 Technical Failure

- Workflow run: `35516022578`.
- Failure point: QA test runner startup.
- Cause: `pytest` was not installed in the clean GitHub Actions Python environment.
- Specification assertion reached: **NO**.
- Scientific execution attempted: **NO**.
- Fresh scientific seed consumed: **NO**.
- Model fitting performed: **NO**.
- Classification: **TECHNICAL_QA_ENVIRONMENT_FAILURE**.
- Recovery allowed: install pinned QA-only dependency `pytest==8.4.2` and rerun the unchanged specification verifier.
- CPRM research object, target contract, population contract, baseline family, gates and roadmap: **UNCHANGED**.

---

## 2026-09-20 — CPRM-0 Zero-Science Specification QA Closed PASS

- CPRM-0 foundation commit: `a1d70d41a0a12ebb4fafbcbac0c059b0e502d40c`.
- QA environment repair commit: `341a13ee3da8b268ad31aad20d73a482666fe7dc`.
- Canonical QA workflow run: `35516092647`.
- Tests: **3/3 PASS**.
- Verdict: `CPRM0_ZERO_SCIENCE_SPEC_QA_PASS`.
- QA JSON SHA-256: `bcf7fa6b0b967bff932d3a7ae087f4fe450edc14d9aabc404ff42242eed62140`.
- Artifact ID: `10606658496`.
- Artifact ZIP SHA-256: `d4e3ecabd6ece4e9c0c2e0db7de5b846e5d453a3b0237e8a322f122f1c0e01c1`.
- Scientific execution attempted: **NO**.
- Fresh scientific seed consumed: **NO**.
- Model fitting performed: **NO**.
- CPRM execution workflow present: **NO**.
- CPRM scientific artifact present: **NO**.
- CPRM-0: **PASS / CLOSED**.
- CPRM-1 scientific execution: **NOT AUTHORIZED**.
- Next admissible action: design and preregister CPRM-1 Fresh Response Support & Geometry Qualification protocol only.

---

## 2026-09-20 — CPRM-1 Protocol Preregistered Before Scientific Execution

- Milestone: `CPRM-1 — Fresh Response Support & Geometry Qualification`.
- Predictor training: **FORBIDDEN / NONE**.
- Controller: **CLOSED**.
- Primary population: exactly `60 fresh seeds × 3 boundaries = 180 boundaries`.
- Policy responses: exactly `540`.
- Primary response vector: plasticity AUC, final current accuracy, mean prior retention, worst prior accuracy.
- Hard labels used for eligibility/adjudication: **NO**.
- Fresh seed manifest count: `60`.
- Seed manifest SHA-256: `d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3`.
- ACO-1 spent cohort reuse: **FORBIDDEN**.
- Protected KCL cohort use: **FORBIDDEN**.
- Reliability repeats: first six fresh seeds, exact deterministic repeat required.
- Support gate: complete `60/60` seeds and `180/180` boundaries only.
- Response non-degeneracy contract: frozen before outcomes.
- B-A/C-A contrast-support contract: frozen before outcomes.
- One-shot adjudicator: synthetic-only implementation authorized.
- Scientific fresh collection: **LOCKED / NOT AUTHORIZED**.
- Next: bind exact implementation/protocol/runtime in `CPRM1_EXECUTION_LOCK.json`, then run zero-science preflight only.

---

## 2026-09-20 — CPRM-1 Execution Lock v1 Frozen

- Implementation commit: `e955c4962846cda8cac633c4c9fd49b40a901750`.
- Protocol Git blob: `f61aabc5605400faea30e5d2af4349a2b32c792f`.
- Runner Git blob: `18774a9349adeb4a0e5d66ce46416564640f41aa`.
- Synthetic test Git blob: `dd54c5aaba63cf0fa649b5db445aec476e2a3847`.
- Zero-science workflow Git blob: `20968ba824194c6530b6a393d8aa5848b4fed79a`.
- Fresh manifest SHA-256: `d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3`.
- Runtime pinned: Python 3.12.14 / NumPy 2.3.3 / pytest 8.4.2 / PyTorch 2.10.0+cpu.
- Fresh scientific execution remains **BLOCKED** until both zero-science preflight and later independent lock verification PASS.
- No execution workflow exists.
- No fresh CPRM-1 scientific outcome exists.

---

## 2026-09-20 — CPRM-1 Zero-Science Preflight Closed PASS

- Canonical workflow run: `35517327267`.
- Focused synthetic/contract tests: **5/5 PASS**.
- Verdict: `CPRM1_ZERO_SCIENCE_PREFLIGHT_PASS`.
- Protocol SHA-256: `2663cb2b28f73e02bbac19c537e16632f978d2d754488932924bf37e7c8ea084`.
- Execution-lock SHA-256: `26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274`.
- Preflight JSON SHA-256: `0ef730573e70397bd45edc2b99ccc5b35d6f723e3e0156342189c40875a24f8f`.
- Artifact ID: `10606759798`.
- Artifact ZIP SHA-256: `7fceeb3b178ab6feddbf49b18c9f374998f9b4eff38c9cfa57662559bc194fd2`.
- Fresh manifest collision audit: **PASS**.
- Historical probe seed: `9595`; exact deterministic repeat: **PASS**.
- Fresh CPRM-1 seed execution attempted: **NO**.
- Scientific outcome generated: **NO**.
- Model fitting performed: **NO**.
- Fresh collection artifact: **NONE**.
- Formal result: **NONE**.
- Fresh execution remains blocked pending independent execution-lock verification.
- CPRM-2/controller/KCL-7: **CLOSED**.

---

## 2026-09-20 — CPRM-1 Independent Execution-Lock Verification Opened

- Exact lock SHA-256 to verify: `26c539a3be74f151e69863bc267268b1257e2715f707a436d44a45910d8af274`.
- Verification method: static independent verifier; CPRM-1 scientific runner is **NOT imported or called**.
- Required checks: protocol/source blobs, exact seed manifest, exact runtime, historical/protected/spent disjointness, support/geometry gates, retry policy, absence of collection/result, absence of fresh execution workflow.
- Fresh CPRM-1 seed execution during verification: **PROHIBITED**.
- Scientific outcome generation during verification: **PROHIBITED**.
- Model fitting during verification: **PROHIBITED**.
- Verification result at this entry: **PENDING**.

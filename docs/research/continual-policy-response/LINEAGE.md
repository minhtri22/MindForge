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

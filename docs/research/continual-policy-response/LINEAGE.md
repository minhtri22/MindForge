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

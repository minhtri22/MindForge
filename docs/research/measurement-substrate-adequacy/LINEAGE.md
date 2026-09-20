# MSA Lineage

Status: **APPEND-ONLY**

Existing entries must never be rewritten or silently removed.

---

## 2026-09-20 — MSA Program Created

- Program: **MSA — Measurement / Substrate Adequacy**.
- Branch: `research/measurement-substrate-adequacy`.
- Exact parent: `c1837438d944c0e11dcb961fa669cfef92bc3c2d`.
- MSA is **not CPRM-2** and **not predictor rescue**.
- Scientific execution: **NONE**.
- Fresh MSA seed manifest: **NONE**.
- Difficulty mutation: **NONE**.
- Predictor fitting: **NONE**.
- Controller/KCL-7: **CLOSED**.
- Protected KCL cohort: **UNTOUCHED**.

---

## 2026-09-20 — MSA-0 Specification Frozen for QA

- Mandatory endpoints: terminal accuracy + terminal cross-entropy loss.
- Terminal accuracy remains mandatory sentinel.
- Terminal-loss provenance: pre-CPRM KCL-1 `evaluate()`.
- MSA-1 substrate: **UNCHANGED**.
- MSA-1 difficulty manipulation: **FORBIDDEN**.
- Genuine endpoint saturation: **VALID SCIENTIFIC OUTCOME**.
- ACO-1 and CPRM-1 cohorts: **SPENT / EXCLUDED**.
- Finite roadmap: MSA-0 → MSA-1 → conditional MSA-2 → MSA-3 → MSA-4.
- MSA-0 state: **PENDING ZERO-SCIENCE QA**.

---

## 2026-09-20 — MSA-0 QA Attempt 1 Technical Predicate Mismatch

- Workflow run: `35519949524`.
- Scientific execution attempted: **NO**.
- Fresh MSA seed generated: **NO**.
- Difficulty mutation performed: **NO**.
- Predictor fitting performed: **NO**.
- Failure cause: verifier required literal phrase `before ACO/CPRM` while the frozen evidence document states the equivalent provenance phrase `predates ACO/CPRM`.
- Classification: **TECHNICAL_QA_STRING_PREDICATE_FAILURE**.
- Recovery: change verifier predicate only to match the frozen wording.
- Research question, endpoint candidates, substrate difficulty contract, freshness exclusions, falsification gates and roadmap: **UNCHANGED**.

---

## 2026-09-20 — MSA-0 QA Diagnostic Instrumentation

- Prior retries still failed only at aggregate specification assertion.
- Scientific execution attempted: **NO**.
- Contract changes: **NONE**.
- QA-only change: assertion now prints only false predicates so the exact verifier mismatch can be identified without altering scientific specification.

---

## 2026-09-20 — MSA-0 QA Saturation Predicate Newline Fix

- Diagnostic workflow: `35520136747`.
- Exact false predicate: `saturation_valid`.
- Frozen contract already states `CURRENT_SUBSTRATE_ENDPOINT_SATURATED` is a valid conclusion.
- Failure cause: verifier searched the contiguous string `valid conclusion`, while Markdown line wrapping inserted a newline.
- Scientific contract changes: **NONE**.
- Verifier-only recovery: semantic token checks within the same frozen document.
- Scientific execution / seed generation / difficulty mutation / predictor fitting: **NONE**.

# CLRM Lineage

Append-only.

## 2026-09-25 — CLRM Program Opened

- Program: **Continual Loss Response Modeling (CLRM)**.
- Branch: `research/continual-loss-response`.
- Exact parent: MSA formal convergence commit
  `64138ab9cb09dcb56a387d3b1f500063eff8302d`.
- Parent replicated finding:
  `ACCURACY_COARSE_LOSS_INFORMATIVE`.
- Program identity: **new program / not CPRM-2**.
- Primary response vector:
  `[L_current_end, L_prior_mean_end]` for each A/B/C policy.
- Direct channels: **6**.
- A-relative contrasts: B-A and C-A, each with two loss components.
- Terminal accuracy role: sentinel/diagnostic only.
- Primary population: all prospectively eligible T1→T2, T2→T3, T3→T4
  matched boundaries.
- Fresh-data roles: support-only → discovery train/sealed validation →
  independent replication.
- Spent exclusions: KCL, ACO-1, CPRM-1, MSA-1, MSA-3.
- Predictor fitting: **NOT AUTHORIZED**.
- Fresh scientific execution: **NOT AUTHORIZED**.
- Controller/KCL-7: **CLOSED**.
- Current milestone: **CLRM-0 Specification Foundation**.

---

## 2026-09-25 — CLRM-0 QA Attempt 1 Technical Infrastructure Failure

- Workflow: `36056186547`.
- Failure point: static specification tests before validator execution.
- Root cause: GitHub runner Python environment did not have `pytest` installed.
- Classification: **TECHNICAL_QA_INFRASTRUCTURE_FAILURE / ZERO-SCIENCE**.
- Scientific target changed: **NO**.
- Baseline/gate/partition contracts changed: **NO**.
- Fresh seed execution: **NO**.
- Scientific outcome generated: **NO**.
- Predictor fitting: **NO**.
- Controller execution: **NO**.
- QA recovery also narrows the CPRM anti-reuse assertion to the actual primary
  target-definition block, because the document intentionally names historical
  CPRM variables in a prohibition section.

---

## 2026-09-25 — CLRM-0 QA Checkout Optimization

- QA recovery run `36056366585` remained in repository checkout because
  `fetch-depth: 0` fetched full branch history.
- Classification: **QA_INFRASTRUCTURE_ONLY**.
- Checkout scope reduced to `fetch-depth: 4`, sufficient to retain the exact
  MSA closure ancestor and CLRM-0 commit chain required by static validation.
- Scientific target/baselines/gates/partitions/exclusions changed: **NO**.
- Fresh science/predictor/controller execution: **NO**.

---

## 2026-09-25 — CLRM-0 Independent Static Specification QA Closed PASS

- Audited branch head: `6c2c679bb90e9be8838503d346fed7ffd843310e`.
- Exact merge base / parent closure:
  `64138ab9cb09dcb56a387d3b1f500063eff8302d`.
- Git compare: **ahead 3 / behind 0 / 17 added CLRM files**.
- Inherited scientific implementation modified: **NO**.
- Exact two-axis CE-loss response vector: **FROZEN**.
- Accuracy role: **SENTINEL ONLY**.
- All-boundary population: **FROZEN**.
- B0/B1/B2 baselines: **FROZEN**.
- Role S / D-train / D-val / R separation: **FROZEN**.
- Baseline-superiority + point-calibration gates: **FROZEN**.
- KCL/ACO/CPRM/MSA freshness exclusions: **FROZEN**.
- Scientific runner/result: **ABSENT**.
- Fresh seed manifest: **ABSENT**.
- Predictor fitting: **NO**.
- Controller execution: **NO**.
- Verdict: `CLRM0_ZERO_SCIENCE_SPEC_QA_PASS`.
- CLRM-0: **PASS / CLOSED**.
- CLRM-1 protocol design: **AUTHORIZED**.
- CLRM-1 fresh science/predictor: **NOT AUTHORIZED**.

---

## 2026-09-25 — CLRM-0 Canonical Actions QA Confirmed PASS

- Workflow: `36057035870`.
- Workflow HEAD: `6c2c679bb90e9be8838503d346fed7ffd843310e`.
- Static tests: **4/4 PASS**.
- Verdict: `CLRM0_ZERO_SCIENCE_SPEC_QA_PASS`.
- QA JSON SHA-256:
  `74710fb9c8fe5422f33749664996ecc47f5e32c0a4f11d01c087f2e0e6d4d257`.
- Artifact ID: `10832548397`.
- Artifact ZIP SHA-256:
  `59776fe2373ead0fb9d3d1f790ec86643879fb7252cd38dd0f65b8f0e9af4659`.
- Fresh seed execution: **NO**.
- Scientific outcome: **NO**.
- Predictor fitting: **NO**.
- Controller execution: **NO**.
- This Actions PASS confirms the independent branch-tree audit already used to
  close CLRM-0.

---

## 2026-09-25 — CLRM-1 Preregistration Frozen

- Milestone: **CLRM-1 — Loss Response Support Qualification**.
- Predictor fitting: **PROHIBITED**.
- Exact Role-S cohort size: **72 seeds**.
- Population: **216 matched boundaries / 648 A-B-C response vectors**.
- Seed generation phrase: `MindForge|CLRM-1|role-s-loss-response-support|v1`.
- Role-S manifest SHA-256:
  `3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6`.
- Deterministic reliability repeats: first **6** frozen Role-S seeds.
- Primary direct channels: **6**, exactly
  A/B/C × {current CE loss, mean-prior CE loss}.
- Cell non-degeneracy:
  `unique_count >= 10 AND p90-p10 >= 0.02`.
- Channel qualification: cell PASS in **>=2/3 stages**.
- CLRM-1 PASS requires **all six direct channels**.
- Accuracy: **sentinel only / non-gating**.
- A-relative contrast geometry: **diagnostic only / non-gating**.
- Fresh execution: **BLOCKED** pending execution lock, zero-science preflight,
  and independent lock verification.
- Only `PASS_LOSS_RESPONSE_SUPPORT` may open **CLRM-2 design**.
- CLRM-2 predictor training: **NOT AUTHORIZED** by CLRM-1 design.

---

## 2026-09-25 — CLRM-1 Execution Lock v1 Frozen

- Preregistration/implementation commit:
  `2b8f29547b29a63bf3f4131a0cdd48cfb48c3e63`.
- Protocol Git blob:
  `6560f7ff12b98bfcdead97661c934b58abe3a437`.
- Role-S seed-manifest Git blob:
  `3060fe5f6d348390f3dbcdc1ceb7471084635318`.
- Scientific runner Git blob:
  `deb0c30af6a981705587637706e98ddc1cbc1ceb`.
- Synthetic/static test Git blob:
  `00333df9b8293409f6a40cada3dfa763e61035e8`.
- Role-S manifest SHA-256:
  `3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6`.
- Eight substrate blobs: frozen exact.
- ACO-1 / CPRM-1 / MSA-1 / MSA-3 spent manifest hashes: frozen exact.
- Six-channel geometry gate: frozen exact.
- Reliability / one-shot adjudication / retry policy: frozen exact.
- Predictor training: **NOT AUTHORIZED**.
- Fresh CLRM-1 execution: **BLOCKED** pending zero-science preflight and
  independent exact-lock verification.

---

## 2026-09-25 — CLRM-1 Zero-Science Preflight Closed PASS

- Canonical workflow: `36088425840`.
- Static/synthetic tests: **5/5 PASS**.
- Verdict: `CLRM1_ZERO_SCIENCE_PREFLIGHT_PASS`.
- Execution-lock SHA-256:
  `39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e`.
- Protocol SHA-256:
  `1841fb6ce65eb9d1f4ce93771797819fa68bc9216f5714322de645a874f59411`.
- Preflight JSON SHA-256:
  `d32e2efd209a8dcfd7ba6a1b2db9790536e65233817a3c476046c9758702976b`.
- Artifact ID: `10844344688`.
- Artifact ZIP SHA-256:
  `e9942ed848382117ae7df148c71b733d0e397c54dd2c968a8f4b0f954d6ccb57`.
- Historical extraction/repeat seed 9595: **PASS / EXACT**.
- KCL/ACO/CPRM/MSA collision audit: **ZERO**.
- Fresh Role-S seed execution: **NO**.
- Response geometry inspection: **NO**.
- Scientific outcome: **NO**.
- Predictor fitting: **NO**.
- Difficulty mutation: **NO**.
- Controller execution: **NO**.
- Independent execution-lock verification: **PENDING**.

---

## 2026-09-25 — CLRM-1 Independent Execution-Lock Verification Opened

- Exact lock SHA-256:
  `39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e`.
- Verifier is static and does **not** import/call the CLRM-1 scientific runner.
- Independent checks: source/protocol/manifest blobs, 8 substrate blobs,
  deterministic seed regeneration, KCL/ACO/CPRM/MSA collisions, six-channel
  geometry gate, reliability, one-shot adjudication, retry policy, exact
  runtime, preflight closure, and absence of execution workflow/collection/result.
- Fresh Role-S execution during verification: **PROHIBITED**.
- Response-geometry inspection: **PROHIBITED**.
- Predictor fitting / difficulty mutation / controller: **PROHIBITED**.
- Verification result at this entry: **PENDING**.

---

## 2026-09-25 — CLRM-1 Independent Execution-Lock Verification Closed PASS

- Canonical workflow: `36088745852`.
- Independent tests: **5/5 PASS**.
- Exact verified lock SHA-256:
  `39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e`.
- Verdict: `CLRM1_EXECUTION_LOCK_VERIFICATION_PASS`.
- Verification JSON SHA-256:
  `6153044c2cbde37ddbb631adc3bf386d4361da9bf593ca9ef25bd3bd87cabb01`.
- Artifact ID: `10844148728`.
- Artifact ZIP SHA-256:
  `cae8cdbed4bc485197da44a1d4d00aed72d1ea3c2d15c9a9ed49384c0250d3b3`.
- Deterministic 72-seed regeneration: **PASS**.
- Historical/protected/ACO/CPRM/MSA collisions: **ZERO**.
- Six-channel response contract: **PASS / EXACT**.
- Population / geometry / reliability / adjudication / retry contracts:
  **PASS / EXACT**.
- Fresh execution workflow: **ABSENT**.
- Fresh collection/result: **ABSENT**.
- Fresh scientific seed execution: **NO**.
- Response geometry inspection: **NO**.
- Predictor fitting: **NO**.
- Difficulty mutation: **NO**.
- Controller execution: **NO**.
- Exact CLRM-1 Role-S support collection is now **ELIGIBLE TO OPEN**, but has
  not started.
- CLRM-2 design remains **CLOSED UNTIL CLRM-1 PASS**.

---

## 2026-09-25 — CLRM-1 Canonical Role-S Scientific Execution Opened

- Exact verified CLRM-1 lock SHA-256:
  `39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e`.
- Independent verification:
  `CLRM1_EXECUTION_LOCK_VERIFICATION_PASS`, workflow `36088745852`.
- Authorized action: exactly one frozen 72-seed Role-S collection.
- Expected population: **216 boundaries / 648 A-B-C response vectors /
  1296 primary loss scalars**.
- Reliability repeats: exactly first **6** frozen Role-S seeds.
- Pre-adjudication validation: **integrity/support/reliability only**.
- Six-channel response geometry before preserve/adjudication: **PROHIBITED**.
- Contrast geometry before preserve/adjudication: **PROHIBITED**.
- Accuracy-distribution inspection before preserve/adjudication: **PROHIBITED**.
- Complete valid collection must be preserved before one-shot adjudication.
- Technical retry only before a complete valid collection and only under the
  same seed + same immutable lock.
- Complete valid collection rerun: **PROHIBITED**.
- Predictor fitting / difficulty mutation / controller: **PROHIBITED**.
- Result at this lineage entry: **UNOBSERVED**.

---

## 2026-09-25 — CLRM-1 Canonical Role-S Execution Closed PASS

- Canonical workflow: `36092039012`.
- Exact lock SHA-256:
  `39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e`.
- Role-S seeds: **72/72 COMPLETE**.
- Matched boundaries: **216/216 COMPLETE**.
- A/B/C response vectors: **648/648**.
- Primary loss scalars: **1296/1296**.
- Reliability repeats: **6/6 EXACT PASS**.
- Integrity/support/reliability: **PASS**.
- Collection SHA-256:
  `adc69007e98f036785427617b7109f0a93cc236e4ef605bfbdfcdf727748c7b4`.
- Collection evidence commit:
  `ff3d4d6b5c386c036e5e0de3286ff53f19cb18c4`.
- Pre-adjudication artifact ID: `10845952892`.
- Pre-adjudication artifact ZIP SHA-256:
  `b7530afd0e3ad748777518fad46d45311116da6fd881c46ac1dacbc7d4537155`.
- Intermediate six-channel/contrast/accuracy-distribution inspection: **NO**.
- Valid support-adjudicator calls: **1**.
- Observed status: **PASS**.
- Observed verdict: `PASS_LOSS_RESPONSE_SUPPORT`.
- Reason: `ALL_SIX_DIRECT_LOSS_CHANNELS_NONDEGENERATE`.
- Formal-result SHA-256:
  `1ed1ce672454c845445c0f87efb27df75cdc4842dea01c8a22b825a5ed76ff20`.
- Formal-result evidence commit:
  `aa35ad61f032b35303958edafd7b2c8e3ce7010d`.
- Complete evidence artifact ID: `10845703212`.
- Complete evidence ZIP SHA-256:
  `6cf2ff1afde9f2b41d540362720c8d9c4c481cfbf8212bd27e19dc8e1f3b70c8`.
- Predictor fitted: **NO**.
- Difficulty mutation: **NO**.
- Controller execution: **NO**.
- Role-S cohort: **HISTORICAL / SPENT SUPPORT EVIDENCE**.
- CLRM-1: **PASS / CLOSED**.
- CLRM-2 design: **AUTHORIZED**.
- CLRM-2 fresh science / predictor training: **NOT AUTHORIZED**.

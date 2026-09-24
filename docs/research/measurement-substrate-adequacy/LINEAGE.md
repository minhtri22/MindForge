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

---

## 2026-09-20 — MSA-0 Zero-Science Specification QA Closed PASS

- Canonical workflow run: `35520209506`.
- Tests: **3/3 PASS**.
- Verdict: `MSA0_ZERO_SCIENCE_SPEC_QA_PASS`.
- QA JSON SHA-256: `6996c313435b0886c5c8357633f7e6d492a0ab5cbdc3bcbc138e7253535c66e7`.
- Artifact ID: `10607299773`.
- Artifact ZIP SHA-256: `e00366bee0fdfc5114ddc6bf73a00b53ac38f96db9a4f6d3c506b5e391de19ce`.
- Scientific execution attempted: **NO**.
- Fresh MSA scientific seed generated: **NO**.
- Difficulty mutation performed: **NO**.
- Predictor fitting performed: **NO**.
- MSA scientific runner/artifact: **NONE**.
- Fresh MSA seed manifest: **NONE**.
- MSA execution workflow: **NONE**.
- MSA-0: **PASS / CLOSED**.
- MSA-1 scientific execution: **NOT AUTHORIZED**.
- Next admissible action: design and preregister MSA-1 Current-Substrate Endpoint Adequacy Qualification only.

---

## 2026-09-24 — MSA-1 Protocol Preregistered Before Fresh Science

- Milestone: `MSA-1 — Current-Substrate Endpoint Adequacy Qualification`.
- Current substrate difficulty mutation: **FORBIDDEN / NONE**.
- Predictor fitting: **FORBIDDEN / NONE**.
- Fresh cohort: exactly `72` seeds generated from frozen hash-based provenance.
- Seed manifest SHA-256: `e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347`.
- Population: `216` matched boundaries / `648` A/B/C endpoint pairs.
- Reliability repeats: first `6` seeds, exact deterministic equality required.
- Mandatory endpoint pair: terminal accuracy + terminal cross-entropy loss from the same canonical step-250 curve point.
- Accuracy saturation/informativeness gates: **FROZEN**.
- Loss saturation/informativeness gates: **FROZEN**.
- Joint four-way classification matrix: **FROZEN**.
- Scientific fresh execution: **LOCKED / NOT AUTHORIZED**.
- Next: bind exact protocol/runner/substrate/runtime in MSA-1 Execution Lock, then zero-science preflight only.

---

## 2026-09-24 — MSA-1 Execution Lock v1 Frozen

- Scientific implementation commit: `3dfb18c3704f4f8e91160b30514687fe7a1fbb00`.
- Protocol Git blob: `b4a68aee9db6a0698f70dbb1e1e4b33fbf7ffc4a`.
- Runner Git blob: `55d6686c6c1182b7706f4831cb8f49eec2ec032d`.
- Synthetic-test Git blob: `0cd1702ae2ecc64af270aa0e8843df3ea1f75fae`.
- Preflight-workflow Git blob: `a72ea5105e6dc306d7f214084b4160463f49f00d`.
- Eight exact substrate/model/replay/policy Git blobs are frozen in the lock.
- Fresh manifest SHA-256: `e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347`.
- Current substrate mutation permitted: **NO**.
- Fresh MSA-1 execution: **BLOCKED** pending zero-science preflight and later independent lock verification.
- Predictor/controller/KCL-7: **CLOSED**.

---

## 2026-09-24 — MSA-1 Zero-Science Preflight Closed PASS

- Canonical workflow run: `36023316869`.
- Synthetic/contract tests: **7/7 PASS**.
- Verdict: `MSA1_ZERO_SCIENCE_PREFLIGHT_PASS`.
- Protocol SHA-256: `4d9ce52b66192c3847d78883cb99fe21a767a6d719c4495149f1d43996b5ec48`.
- Execution-lock SHA-256: `c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657`.
- Preflight JSON SHA-256: `5d0d64bf1bb9382a76a1e08f0fd8374b43e14d9d207476e3cbcdcf7fb7320e14`.
- Artifact ID: `10818421146`.
- Artifact ZIP SHA-256: `41fb1920bfbcdc0a3c0d7ef1831fc863f0127f01a68aaa58a3f6961f42f0b3e8`.
- Fresh-seed collision audit: **PASS / ZERO COLLISIONS**.
- Frozen substrate/source identity: **PASS**.
- Historical probe seed: `9595`; exact repeat: **PASS**.
- Fresh MSA-1 seed execution: **NO**.
- Scientific outcome generated: **NO**.
- Difficulty mutation: **NO**.
- Predictor fitting: **NO**.
- Fresh collection: **NONE**.
- Formal result: **NONE**.
- Independent execution-lock verification: **PENDING**.
- MSA-2/predictor/controller/KCL-7: **CLOSED**.

---

## 2026-09-24 — MSA-1 Independent Execution-Lock Verification Opened

- Exact lock SHA-256: `c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657`.
- Verification implementation is static and independent; it does **not** import or call the MSA-1 scientific runner.
- Required checks: protocol/runner/test/preflight blobs, eight substrate blobs, exact 72-seed manifest + deterministic regeneration, exact runtime, KCL/protected/ACO/CPRM disjointness, accuracy gates, loss gates, classification matrix, retry policy, absence of collection/result/execution workflow.
- Fresh MSA-1 seed execution during verification: **PROHIBITED**.
- Difficulty mutation during verification: **PROHIBITED**.
- Predictor fitting during verification: **PROHIBITED**.
- Verification result at this entry: **PENDING**.

---

## 2026-09-24 — MSA-1 Verifier Attempt 1 Technical Parser Failure

- Workflow run: `36026522210`.
- Failure point: independent verifier tests, before canonical static verification.
- Root cause: verifier used `ast.literal_eval` for frozen numeric constants expressed as `2.0/24.0` and `-math.log(0.95)`; those expressions were not evaluated and produced missing values.
- Classification: **TECHNICAL_VERIFIER_PARSER_FAILURE / NON-SCIENTIFIC**.
- MSA-1 execution lock changed: **NO**.
- Protocol/runner/substrate/gates/seeds changed: **NO**.
- Fresh MSA-1 scientific seed execution: **NO**.
- Scientific outcome generated: **NO**.
- Difficulty mutation: **NO**.
- Predictor fitting: **NO**.
- Recovery scope: verifier-only safe static numeric-expression evaluator; no scientific runner import or execution.

---

## 2026-09-24 — MSA-1 Independent Execution-Lock Verification Closed PASS

- Canonical workflow: `36026801647`.
- Independent tests: **5/5 PASS**.
- Verified lock SHA-256: `c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657`.
- Verdict: `MSA1_EXECUTION_LOCK_VERIFICATION_PASS`.
- Verification JSON SHA-256: `cb8896c048576103f3ab0cddc2d41195d7c1e8525d06ce250d893a71c4322753`.
- Artifact ID: `10819766185`.
- Artifact ZIP SHA-256: `d23cca03803d37fa531f069951181076ed1f8a9dce8b3e19c98f7fbb97f71f11`.
- Protocol/runner/test/preflight blobs: **EXACT**.
- Eight substrate blobs: **EXACT**.
- 72-seed manifest + deterministic regeneration: **EXACT**.
- Runtime: **EXACT**.
- Historical/protected/ACO/CPRM collisions: **ZERO**.
- Accuracy gates: **EXACT**.
- Loss gates: **EXACT**.
- Classification matrix: **EXACT**.
- Retry policy: **EXACT**.
- Fresh execution workflow: **ABSENT**.
- Fresh collection: **ABSENT**.
- Formal result: **ABSENT**.
- Fresh scientific seed execution: **NO**.
- Scientific outcome generated: **NO**.
- Difficulty mutation: **NO**.
- Predictor fitting: **NO**.
- MSA-1 fresh collection is now **ELIGIBLE TO OPEN under exact verified lock**, but has not started.
- MSA-2/predictor/controller/KCL-7 remain **CLOSED**.

---

## 2026-09-25 — MSA-1 Locked Fresh Scientific Execution Opened

- Verified execution lock SHA-256: `c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657`.
- Independent verification: `MSA1_EXECUTION_LOCK_VERIFICATION_PASS`, workflow `36026801647`.
- Authorized action: exactly one frozen 72-seed current-substrate collection.
- Expected population: `72 seeds × 3 boundaries = 216 boundaries`.
- Expected A/B/C endpoint pairs: `648`.
- Reliability repeats: exactly first `6` preregistered fresh seeds.
- Pre-adjudication validation: **integrity/support/reliability only**.
- Accuracy/loss/joint classification inspection before adjudication: **PROHIBITED**.
- Complete collection must be preserved as artifact and branch evidence before adjudication.
- Adjudication: exactly one valid one-shot call on the preserved complete input.
- Technical collection retry: only before a complete valid collection exists, same seed + same lock, no seed substitution or difficulty change.
- Complete valid collection rerun: **PROHIBITED**.
- MSA-2 remains **CLOSED** regardless of MSA-1 verdict until a formal transition review.
- Predictor/controller/KCL-7 remain **CLOSED**.
- Scientific result at this lineage entry: **UNOBSERVED**.

---

## 2026-09-25 — MSA-1 Fresh Execution Closed PASS

- Workflow: `36033469789`.
- Fresh seeds: **72/72 COMPLETE**.
- Matched boundaries: **216/216 COMPLETE**.
- A/B/C endpoint pairs: **648**.
- Reliability repeats: **6/6 EXACT PASS**.
- Integrity/support: **PASS**.
- Collection SHA-256: `4b7269a5fb0ab6750e067cfd26d95913dabbe2181af4001a689a1cea85cdbcd4`.
- Collection evidence commit: `f5ec2e3a38813904a76290ff88f2df4fbc4b2167`.
- Collection-before-adjudication artifact ID: `10823599007`.
- Collection artifact ZIP SHA-256: `3ceb17a0add080d4fffd4c98e2b621c70021a56acc21baec6a9e3f7c21c87e08`.
- Intermediate endpoint-classification inspection: **NO**.
- One-shot adjudicator calls: **1**.
- Formal-result SHA-256: `359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637`.
- Formal-result evidence commit: `42a549601f44e80ebc35c446123ae8191eee5b53`.
- Complete execution artifact ID: `10823374088`.
- Complete execution artifact ZIP SHA-256: `465356e0d173978fd7f6aeef894f9ccb41d5402ed7317bde8f37f5bcacb91458`.
- Formal status: **PASS**.
- Formal verdict: `ACCURACY_COARSE_LOSS_INFORMATIVE`.
- Accuracy global state: saturated **TRUE**, informative **FALSE**.
- Loss global state: informative **TRUE**, saturated **FALSE**.
- Difficulty mutation: **NO**.
- Predictor fitting: **NO**.
- MSA-1 cohort: **HISTORICAL / SPENT**.

---

## 2026-09-25 — MSA-1 Formal Transition Review Closed

- Open MSA-2 to search for informative accuracy: **REJECTED**.
- Immediate structure-dependence MSA-2: **NOT AUTHORIZED / DEFERRED**.
- Selected next milestone: **MSA-3 — Independent Fresh Replication**.
- MSA-3 design/preregistration: **AUTHORIZED**.
- MSA-3 fresh execution: **NOT AUTHORIZED**.
- Replication must preserve exact MSA-1 substrate, endpoints, gates and classification matrix.
- Difficulty mutation/new endpoint metric/predictor fitting: **FORBIDDEN**.
- MSA-2/predictor/controller/KCL-7 remain **CLOSED**.

---

## 2026-09-25 — MSA-3 Independent Fresh Replication Preregistered

- Trigger: MSA-1 formal transition review selected exact fresh replication.
- Discovery claim: `ACCURACY_COARSE_LOSS_INFORMATIVE`.
- Discovery formal-result SHA-256: `359cdc7c505244e71a5122d0a1038f045d20af27782008afab9b1bbddbf51637`.
- MSA-1 scientific contract changes: **NONE**.
- Fresh cohort size: `72` seeds.
- Fresh manifest SHA-256: `5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8`.
- Population: `216` boundaries / `648` endpoint pairs.
- Reliability repeats: first `6` MSA-3 seeds, exact equality required.
- Replication criterion: exact underlying verdict `ACCURACY_COARSE_LOSS_INFORMATIVE` → `REPLICATION_CONFIRMED`; every other verdict → `REPLICATION_NOT_CONFIRMED`.
- Difficulty mutation: **FORBIDDEN / NONE**.
- New endpoint metric: **FORBIDDEN / NONE**.
- Predictor fitting: **FORBIDDEN / NONE**.
- Fresh MSA-3 execution: **LOCKED / NOT AUTHORIZED**.
- Next: freeze exact MSA-3 execution lock, run zero-science preflight, then independent lock verification.

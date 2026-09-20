# ACO Research Lineage

This file is **append-only**. Existing entries must never be rewritten, reordered, or deleted. Corrections are appended as new entries referencing the superseded entry.

---

## 2026-09-20 — ACO Program Opened After KCL Convergence

- Program: **Adaptive Continual Outcome Modeling (ACO)**
- Branch: `research/adaptive-continual-outcomes`
- Parent: `research/kernel-cl@a9159ae8f17693453e7b6378c92deb5effc4a56f`
- Initialization commit: `e5a394defccf84cc913c787f4c901d1b3fb84f88`
- Scientific trigger: KCL formal convergence established structural boundary-action heterogeneity but no qualified hard-target boundary controller.
- Origin-audit conclusion: KCL existed to establish evidence-backed continual-learning capability; optimizer-boundary action selection is a downstream subproblem, not the original objective.
- New research object: policy-specific continuous plasticity/retention/accuracy outcomes and action contrasts.
- First milestone: `ACO-1 — Target-Stability Qualification`.
- Controller status: **CLOSED / NOT AUTHORIZED**.
- KCL-7 status: **NOT AUTHORIZED**.
- Protected KCL confirmatory cohort: **UNTOUCHED / FORBIDDEN FOR ACO EXPLORATION**.
- Scientific execution performed in this entry: **NONE**.
- Next: implement ACO-1 runner + deterministic one-shot adjudicator + zero-science preflight; do not execute the fresh 40-seed cohort until all integrity gates pass.

---

## 2026-09-20 — ACO Initialization Zero-Science QA

- QA scope: branch/document integrity only; **no scientific outcome generated**.
- Compared against parent closure: `a9159ae8f17693453e7b6378c92deb5effc4a56f`.
- Initialization docs commit: `e5a394defccf84cc913c787f4c901d1b3fb84f88`.
- Lineage-opening commit: `6495062dd56da3a6a8ced9e40a678e740b0337bf`.
- Diff audit: exactly 9 files added under `docs/research/adaptive-continual-outcomes/`; no source, workflow, experiment result, or controller artifact added.
- ACO-1 seed collision audit against historical numeric seed records in root `Lineage.md`: **PASS — 0 collisions**.
- ACO-1 collision audit against protected KCL confirmatory cohort: **PASS — 0 collisions**.
- Protected KCL cohort consumption: **NO**.
- ACO-1 fresh execution authorization: **NO — remains blocked pending implementation + full zero-science preflight**.
- Next scientifically valid step: implement only the frozen ACO-1 measurement runner, identity tests, seed-manifest validator, and one-shot adjudicator; then run zero-science preflight before any fresh cohort execution.

---

## 2026-09-20 — ACO-1 Seed-Provenance Correction Before Execution

- Trigger: implementation preflight found that the sentence claiming deterministic generation from `SHA256("ACO1|i")` was not reproducible from the already-frozen 40-value seed list.
- Scientific execution before correction: **NONE**.
- Resolution: retain the exact 40 pre-registered seed values unchanged; remove the unsupported generation claim; freeze the explicit manifest as the source of truth.
- Frozen seed-manifest SHA-256 over the comma-joined decimal sequence: `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`.
- Seed values changed: **NO**.
- Thresholds/gates changed: **NO**.
- Outcome information used: **NO**.
- Interpretation: technical/provenance correction before execution, not a scientific protocol relaxation.

---

## 2026-09-20 — ACO-1 Pre-Implementation Protocol Clarification

- Scientific execution before clarification: **NONE**.
- Added diagnostic reference-accuracy margin `m_A_acc = A.final_accuracy - 0.95` because the frozen plasticity-repair predicate depends on whether A is below the same strict-current threshold.
- Added frozen whole-seed bootstrap RNG seed: `71001`.
- A/B/C policies changed: **NO**.
- Threshold values changed: **NO**.
- Near-margin bands changed: **NO**.
- Materiality gates changed: **NO**.
- Fresh cohort changed: **NO**.
- Purpose: remove implementation ambiguity before source code exists; no outcome-conditioned revision.

---

## 2026-09-20 — ACO-1 Zero-Science Preflight Closed PASS

- Implementation commit: `e4e8f27b164ca938e6efa910bfb1ec2fc056f1a2`.
- Workflow run: `35510372687`.
- Focused tests: **10/10 PASS**.
- Protocol SHA-256: `a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb`.
- Seed-manifest SHA-256: `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`.
- Historical matched-fork probe: seed `9595`, 3/3 boundary records integrity-valid, no ACO-1 fresh seed used.
- Preflight JSON SHA-256: `75b3b5351376246fe7efd97192633f84cf1305b42189f1bb6e363a1fade4a8b3`.
- Workflow artifact ID: `10605275966`.
- Artifact ZIP SHA-256: `f4f5825f652825bd76239d0b42bbaf08f17304f0bfcb058d9fdf771855ef8bbd`.
- Verdict: `ACO1_ZERO_SCIENCE_PREFLIGHT_PASS`.
- Fresh scientific execution: **NOT PERFORMED**.
- Scientific result: **NONE**.
- Execution lock: **ABSENT**.
- Controller: **CLOSED / NOT AUTHORIZED**.
- Next: create and independently verify ACO-1 execution lock; only then may the frozen 40-seed cohort execute.

---

## 2026-09-20 — ACO-1 Execution Lock Created, Verification Pending

- Scientific execution before lock creation: **NONE**.
- Lock schema: `ACO1-EXECUTION-LOCK-v1`.
- Scientific implementation bound to commit: `e4e8f27b164ca938e6efa910bfb1ec2fc056f1a2`.
- Runner Git blob bound: `117bd3f16d576bf6f683d83747b6c1723a7ae471`.
- Protocol SHA-256 bound: `a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb`.
- 40-seed manifest SHA-256 bound: `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`.
- Runtime locked to GitHub-hosted `ubuntu-24.04`, x86_64, Python `3.12.14`, pip `26.2.1`, NumPy `2.3.3`, pytest `8.4.2`, PyTorch `2.10.0+cpu`.
- Collection command and one-shot adjudication command frozen.
- Collection output: `experiments/aco/results/aco1_fresh_records.json`.
- Formal result output: `experiments/aco/results/FORMAL_RESULT.json`.
- Technical retry policy frozen: no outcome inspection before technical retry; no rerun after a complete valid collection; exactly one valid adjudication; any scientific source/protocol/seed/dependency change invalidates the lock and returns to zero-science preflight.
- Protected KCL confirmatory cohort explicitly prohibited.
- Independent lock verification: **REQUIRED / PENDING**.
- ACO-1 fresh execution: **STILL PROHIBITED**.
- Execution workflow: **ABSENT BY DESIGN** until independent verification closes PASS.

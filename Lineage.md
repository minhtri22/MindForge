# MindForge Kernel Research Lineage

This file is **append-only**. Existing entries must never be rewritten, reordered or deleted. Corrections are appended as new entries referencing the superseded entry.

---

## 2026-09-18 — KCL-0 Kernel Continual-Learning Track Opened

- Track: Kernel Continual Learning (KCL)
- Branch: `research/kernel-cl`
- Base: `main@924654c81c08832c23ff192fdcbf63d3f2680d3a`
- Scope decision: kernel-only research; PIT, OIR-PPV, PPF and non-kernel systems excluded.
- Existing `TransformerLM` remains unchanged for KCL-1.
- Historical P0.9 STOP remains valid and is not relabeled.
- KCL-1 protocol and qualification gates were frozen before result execution.
- Next: execute bounded KCL-1 forgetting-substrate qualification.


## 2026-09-18 — KCL-1 Valid Forgetting Substrate Established

- Status: **PASS**
- Verdict: `VALID_FORGETTING_SUBSTRATE_ESTABLISHED`
- Selected candidate: `C1_TASK_PREFIX_CYCLIC`
- Qualification seeds: `404`, `505`
- Independent A accuracy: `1.0 / 1.0`
- Independent B accuracy: `1.0 / 1.0`
- A-after-A accuracy: `1.0 / 1.0`
- B-after-B accuracy: `1.0 / 1.0`
- A-after-B accuracy: `0.0 / 0.0`
- Absolute forgetting: `1.0 / 1.0`
- Matched A→A control accuracy: `1.0 / 1.0`
- Control drift: `0.0 / 0.0`
- Model architecture changed: **NO**
- Scientific protocol hash: `3a4151f2c18a2f7f19f5396a07a61be49e9f5f84f0d2a76cc3484ba68be8087f`
- Canonical successful workflow run: `35317924719`
- Canonical source commit: `3e8deabf9cb4e0b77db42817978a553baa7a796b`
- Workflow artifact ID: `10536050915`
- Workflow artifact ZIP SHA-256: `23a78cc640928758539e1858f39cfde1af597edf8e5bdfaab08ff54c18ce3c9d`
- Machine-readable evidence: `experiments/kernel_cl/results/kcl1_summary.json`
- Paper: `docs/research/kernel-continual-learning/kcl1-paper.md`
- Interpretation: KCL-1 establishes a scientifically usable untreated-forgetting substrate only. It does **not** establish continual-learning capability.
- Integrity history: workflow runs `35317190484`, `35317414382`, `35317551678`, and `35317736356` failed before scientific training because of test-loader, dependency-command, or import-path defects. Scientific task definitions, gates, model settings, seeds, and candidate order were unchanged during those fixes.
- Next: freeze KCL-2 untreated-baseline characterization using final seeds disjoint from KCL-1 qualification seeds.


## 2026-09-18 — KCL-2 Untreated Forgetting Baseline Reproduced

- Status: **PASS**
- Verdict: `UNTREATED_FORGETTING_BASELINE_REPRODUCIBLE`
- Frozen substrate: `C1_TASK_PREFIX_CYCLIC`
- Final seeds: `101`, `202`, `303`, `707`, `909`; KCL-1 qualification seeds were not reused.
- Independent A accuracy mean: `1.0`
- Independent B accuracy mean: `1.0`
- B-after-B accuracy mean: `1.0`
- A-after-B accuracy mean: `0.0250`
- Absolute forgetting mean: `0.9750`
- Absolute forgetting range: `0.9167–1.0000`
- Forgetting population SD: `0.03333`
- Matched A→A control accuracy mean: `1.0`
- Control drift: `0.0` for all five seeds.
- Model architecture changed: **NO**
- Treatment present: **NO**
- Scientific protocol SHA-256: `e9fc806a5921757e0d0d6ceb2ccfe1703fc05e20f9f6b36330540f0600573d57`
- Canonical workflow run: `35318411840`
- Canonical source commit: `878b4d79a9084d88f0d3c6077fa440d0f9a519b4`
- Workflow artifact ID: `10535203983`
- Workflow artifact ZIP SHA-256: `ea4da768c6a5642d26107e215c8e11940e9c1bc768eaf6082fbbaf9d7d2ac963`
- Machine-readable evidence: `experiments/kernel_cl/results/kcl2_summary.json`
- Paper: `docs/research/kernel-continual-learning/kcl2-paper.md`
- Interpretation: the untreated sequential forgetting failure is reproducible outside the KCL-1 qualification seeds; this authorizes a causal mitigation experiment but still does **not** establish continual-learning capability.
- CI integrity note: two identical post-closure KCL-1 reruns were triggered unintentionally by the original broad workflow path filter; they were not used for candidate selection and KCL-1 was subsequently switched to manual-only dispatch.
- Next: freeze KCL-3 causal replay-treatment protocol before any replay execution.


## 2026-09-18 — KCL-3 Bounded Replay Causally Reduces Forgetting

- Status: **PASS**
- Verdict: `BOUNDED_REPLAY_CAUSALLY_REDUCES_FORGETTING`
- Treatment: bounded replay, frozen at `12.5%` of each B-stage batch (`14 B + 2 A replay`, batch size `16`).
- Seeds: `101`, `202`, `303`, `707`, `909`.
- CONTROL and TREATMENT were forked from the exact same post-A model and optimizer state for every seed.
- Equal budget: `250` B-stage optimizer updates and `4,000` processed examples per arm.
- CONTROL A-after-B mean: `0.0250`.
- TREATMENT A-after-B mean: `0.8750`.
- Mean retention gain: `0.8500`; minimum per-seed gain: `0.6667`.
- CONTROL forgetting mean: `0.9750`.
- TREATMENT forgetting mean: `0.1250`.
- CONTROL B-after-B mean: `1.0`.
- TREATMENT B-after-B mean: `1.0`.
- B accuracy delta: `0.0` for all five seeds.
- All frozen plasticity, retention, directional-consistency, aggregate-effect, and integrity gates: **PASS**.
- Replay-ratio search performed: **NO**.
- Model architecture changed: **NO**.
- Scientific protocol commit: `088102bb1080f550b3f3bb296abb214d00ef412d`.
- Scientific protocol SHA-256: `21b489dfdeb0914bd190c85a5489aa38d2a0e00026ef09ff180e78df6b9fca40`.
- Canonical workflow run: `35330552367`.
- Canonical source commit: `1f8ddc606895e4401d818dfb1ef2932f62438453`.
- Focused tests: `13 passed`.
- Workflow artifact ID: `10541022481`.
- Workflow artifact ZIP SHA-256: `b2e557583e67745f2b40cd766d4850bb7fcb4eb6812bd86c1c4926fff2bdf7c5`.
- Machine-readable evidence: `experiments/kernel_cl/results/kcl3_summary.json`.
- Paper: `docs/research/kernel-continual-learning/kcl3-paper.md`.
- Interpretation: bounded replay has a causal anti-forgetting effect on the frozen KCL substrate without measured plasticity loss. This is not yet evidence of generalized continual-learning capability.
- Next candidate milestone: KCL-4 minimal replay-boundary characterization under a separately frozen protocol. No alternative architecture or CL mechanism is authorized by KCL-3.


## 2026-09-18 — KCL-4 Minimum Effective Replay Boundary Established

- Status: **PASS**
- Verdict: `MINIMUM_EFFECTIVE_REPLAY_BOUNDARY_6_25_PERCENT`
- Frozen batch size: `16`.
- Minimum positive representable replay count: `1` prior-task sample per batch.
- Tested low dose: `1/16 = 6.25%`.
- Historical anchors: `0%` untreated KCL-2 baseline and `12.5%` KCL-3 proven replay treatment.
- Seeds: `101`, `202`, `303`, `707`, `909`.
- CONTROL A-after-B mean: `0.0250`.
- 6.25% replay A-after-B mean: `0.5750`.
- Mean retention gain: `0.5500`; minimum per-seed gain: `0.4583`.
- CONTROL forgetting mean: `0.9750`.
- 6.25% replay forgetting mean: `0.4250`.
- CONTROL B-after-B mean: `1.0`.
- 6.25% replay B-after-B mean: `0.99167`; minimum: `0.95833`.
- Mean B accuracy delta: `-0.00833`; the only non-zero measured plasticity cost was seed `101` at `-0.04167`, remaining above the frozen `0.95` B-acquisition gate.
- All frozen plasticity, per-seed retention, aggregate retention, aggregate forgetting, directional-consistency, paired-state, historical-anchor, and budget-integrity gates: **PASS**.
- Replay-ratio search performed: **NO**.
- Model architecture changed: **NO**.
- Scientific protocol commit: `be71a53dfe521729de76ddab83dfc416b8b426f4`.
- Scientific protocol SHA-256: `c186bd6e3b47b1c02f0b8b6ecbd7f5d96efb71605c5b55dfaba8fe8709740fb0`.
- Canonical workflow run: `35332116173`.
- Canonical source commit: `fb3a7466909f108f49d29a0bacf3fc9fbfa55fd4`.
- Focused tests: `19 passed`.
- Workflow artifact ID: `10542015732`.
- Workflow artifact ZIP SHA-256: `d41c7e58c48db87a3a8dc8484b45d4eab3a2159c4ab831c3601285b4ffba3ff3`.
- Machine-readable evidence: `experiments/kernel_cl/results/kcl4_summary.json`.
- Paper: `docs/research/kernel-continual-learning/kcl4-paper.md`.
- Interpretation: under the frozen batch size of 16, 6.25% is the minimum non-zero representable replay dose and it satisfies the KCL-3 effect contract. The result is substrate-specific and does not establish unseen-pair or scale generalization.
- KCL-5 status: **NOT STARTED / NOT AUTHORIZED BY THIS CLOSURE**.


## 2026-09-18 — KCL-5 Unseen Generalization Blocked by Substrate Qualification Failure

- Status: **FAIL**
- Verdict: `UNSEEN_FAMILY_SUBSTRATE_NOT_QUALIFIED`
- Frozen replay mechanism: `6.25%` replay (`15 B + 1 A replay`, batch size `16`).
- Unseen family U1: `U1_AFFINE_PREFIX`.
  - Qualification seed 606: PASS.
  - Qualification seed 808: PASS.
  - Independent A/B learning: `1.0 / 1.0` on both seeds.
  - Sequential B acquisition: `1.0 / 1.0`.
  - A forgetting: `0.875 / 0.875`.
  - Matched A→A drift: `0.0 / 0.0`.
  - U1 substrate status: **QUALIFIED**.
- Unseen family U2: `U2_STRIDE_SUFFIX`.
  - Qualification seed 606: PASS.
  - Qualification seed 808: **FAIL**.
  - Independent B learning at seed 808: `1.0`.
  - Sequential B acquisition at seed 808: `0.875`, below frozen `0.95` gate.
  - A forgetting at seed 808: `0.8333`.
  - Matched A→A drift: `0.0`.
  - U2 substrate status: **NOT QUALIFIED**.
- Final replay generalization seeds `111, 222, 333, 777, 999` were **not executed** because both unseen families were required to qualify first.
- Replay mechanism failure demonstrated: **NO**.
- Generalization claim tested to completion: **NO**.
- Model architecture changed: **NO**.
- Replay ratio changed/tuned: **NO**.
- Family-specific adaptation: **NO**.
- Scientific protocol commit: `d318b87a066ee122ee294e6001527914c65e3eee`.
- Scientific protocol SHA-256: `6a1d4e5dbcdc0393d1a1fbf4c71d2e2088ac01a36fc10f1be0996259fcb8baf1`.
- Canonical workflow run: `35333101201`.
- Canonical source commit: `83aa689485e8cb6fcf5e3b1382af59ac3bc319ed`.
- Focused tests: `25 passed`.
- Workflow artifact ID: `10541668631`.
- Workflow artifact ZIP SHA-256: `a2f94c38caadd8e4cef489adb0086b8643478f1a9d28340e5da817ea832d8e73`.
- Machine-readable evidence: `experiments/kernel_cl/results/kcl5_summary.json`.
- Paper: `docs/research/kernel-continual-learning/kcl5-paper.md`.
- Interpretation: KCL-5 failed at the prerequisite benchmark/substrate qualification stage. The result does not establish replay-generalization failure because treatment evaluation never began.
- KCL-6 long-horizon status: **BLOCKED / NOT STARTED**.
- Next scientific requirement: construct and pre-qualify an additional unseen task-pair substrate under a dedicated benchmark-reconstruction milestone, while keeping the 6.25% replay mechanism frozen and untouched.

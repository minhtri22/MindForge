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

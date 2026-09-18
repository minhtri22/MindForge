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

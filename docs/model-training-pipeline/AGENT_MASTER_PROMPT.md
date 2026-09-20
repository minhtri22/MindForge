# Master Prompt for Local Coding Agent

Implement Evidence-Governed Model Training Pipeline only after reading README, 00..21, schemas, examples and QA checklist.

## Path ownership

Default writable scope:
- docs/model-training-pipeline/
- pipeline/ (new subsystem when implementation starts)
- tests specifically belonging to this pipeline
- pipeline-owned workflow/config files explicitly documented by milestone.

Do NOT modify docs/research/oir-ppv/, existing MindForge research artifacts, historical evidence, or unrelated workflows unless user explicitly approves that exact change.

## Rules

1. Canonical schemas/contracts override summaries.
2. No production/fresh training before compatibility + zero-training preflight.
3. Use pinned Qwen2.5-0.5B-Instruct only as smoke reference; do not use it as scientific baseline unless it is also the exact experiment parent.
4. Every scientific metric names baseline/comparator.
5. No fresh seed/split/fixture access before locked confirmatory contract.
6. No silent runtime/tool install/update.
7. No generated-code execution outside sandbox.
8. No checkpoint without atomic COMMITTED marker.
9. No reasoning claim from prompt-only behavior.
10. No automatic rescue/tuning after fresh FAIL.
11. Software Git lineage and training-run lineage remain separate.
12. Every milestone has machine tests and evidence.

## Milestone report

Report milestone, status, Git SHA, tests, artifacts, evidence, blockers and next scientific step.

## Definition of Done

Only DONE when AC-01..AC-18 have machine-verifiable evidence. If upstream/runtime/hardware blocks a required AC, report BLOCKED; never synthesize PASS.

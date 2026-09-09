# QA_REPORT_HANDOFF_009_H1_v2 - Independent QA Re-Review

## Scope

Independent QA re-review of `DEV_TASK_009_FIX_01` and `HANDOFF_009_H1_v2.md` using `qa-core`, `qa-research`, and `qa-software`.

Reviewed evidence includes:

- `pipeline/run_h1_closure.py`
- `tests/test_h1_closure.py`
- frozen H1 protocol and matrix manifests
- original 140-cell H1 evidence
- `artifacts/h1_closure/EXP-H1-001/correction_v2/`
- `h1_comparison_v2.json`
- `H1_CLOSURE_REPORT_v2.md`

No scientific artifact, protocol, matrix, learner, or `PLAN.md` hypothesis state was modified by this QA review.

## Source of Truth / Frozen Identity

- Branch: `oir-ppv-research`
- HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- H1 protocol SHA256: `8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`
- H1 matrix SHA256: `55127d173e36028e069c841331b9807ee0dc4948241408c110b3a460be21823c`
- Conditions: `RAW, MEM, L0, L1, L2, L3, L4`
- Environments: `ENV-1..ENV-4`
- Seeds: `42, 123, 456, 789, 1011`
- H1 epsilon: `0.02`
- Primary complexity: `C_total = model_bytes + retained_state_bytes`

## Independent Evidence Replay

### Frozen evidence preservation

- protocol hash: PASS
- matrix hash: PASS
- original evidence manifest contains 140 cells
- 560/560 original required files hash-verified against the correction manifest
- original `h1_comparison.json` SHA256 remains `936905d6f94dce5cc1fcbed6e2d47c8e251268dac48e76b9c4e7910635a538de`
- original `H1_CLOSURE_REPORT.md` SHA256 remains `dfe0c4947902ae6254f0ce38fe75616dddde3b0a9acd76bf3cbd3d91abb749ac`
- no frozen 140-cell scientific matrix rerun or overwrite was required

### Corrected complexity evidence

- corrected learner cells: 100/100
- required `complexity_v2.json` + `provenance_v2.json`: present for 100/100
- `C_total == model_bytes + retained_state_bytes`: valid for 100/100
- failed correction cells: 0
- inapplicable correction cells: 0

Implementation inspection confirms the canonical inference-state payload now follows the actual `X -> I` path:

- L0: table encoder + PCA components/mean
- L1: table encoder + normalization + encoder; classifier excluded
- L2: table encoder + normalization + encoder body + posterior-mean head; decoder/logvar head excluded
- L3: table encoder + normalization + encoder; classifier excluded
- L4: table encoder + normalization + encoder; task/domain heads excluded

Canonical replay is verified to absolute tolerance `1e-12`.

### Reporting closure

`h1_comparison_v2.json` and `H1_CLOSURE_REPORT_v2.md` now include the required paired MEM/RAW analysis, including:

- wins/losses/ties
- mean/median/min/max
- complexity deltas/ratios vs MEM
- utility deltas and non-inferiority
- paired H1 criterion
- per-environment summaries
- RAW zero-denominator ratios encoded as JSON `null` with explicit reason
- machine-readable limitations

Verified v2 hashes:

- `h1_comparison_v2.json`: `55c2873aa613ec877af6967c4f8272c16c5f9c9c95d420aab67518c3ba9ec1da`
- `H1_CLOSURE_REPORT_v2.md`: `31e3c671b130aed29cb2ae66025a11aa7b2441b9532b326e8fd116eccbd24100`

### Independent test replay

- focused H1 suite: `18 passed`
- regression subset: `53 passed`
- known Windows pytest temporary-directory ACL warnings remain an environment limitation and did not invalidate these two successful replays

## Acceptance Matrix

| Criterion | QA result |
|---|---|
| Preserve frozen protocol/matrix | PASS |
| Preserve original 140-cell evidence | PASS |
| Canonical `X -> I` byte accounting | PASS |
| Exclude training-only learner state | PASS |
| Deterministic/replayable inference state | PASS |
| Preserve epsilon/seeds/ENV/MEM semantics | PASS |
| No learner tuning or scientific rerun | PASS |
| Complete MEM/RAW aggregate reporting | PASS |
| RAW divide-by-zero handling | PASS |
| Focused regression | PASS |
| `PLAN.md` remains PM-controlled | PASS |
| H2/MindForge remain unopened in this task | PASS |

## Scientific Assessment

Under the frozen MEM comparator:

- L0 PCA: 20/20 paired H1 successes
- L1 MLP: 19/20
- L2 VAE: 19/20
- L3 IRM-style surrogate: 20/20
- L4 DANN: 19/20

Therefore the frozen H1 operational prediction is supported within the tested benchmark scope because at least L0 and L3 satisfy the paired lower-complexity + utility-non-inferiority criterion across all 20 environment/seed pairs.

The conclusion remains materially limited by the controls:

1. MEM has zero test lookup hits across all 20 MEM cells, so its test utility is entirely the frozen global-majority fallback. This is a valid frozen control but a weak proxy for "memory" in general.
2. RAW has frozen `C_total = 0`, and learned representations do not establish superiority to RAW. For example, only 15/20 L0 cells are utility-non-inferior to RAW; L1/L3/L4 each have 1/20 and L2 has 2/20.
3. L3 remains an IRM-style surrogate and L4 an adapted DANN implementation, so the result must retain those fidelity labels.

Scientific conclusion:

`SUPPORTED_WITH_LIMITS`

Defensible claim boundary:

> Within ENV-1..ENV-4 and seeds 42, 123, 456, 789, 1011, at least the tested L0/PCA and L3/IRM-style representations require substantially less retained inference state than the frozen exact-row MEM control while maintaining utility within the frozen non-inferiority criterion. This does not establish superiority over RAW or memory systems generally.

## QA Verdict

Software / evidence integrity: `PASS`.

`DEV_TASK_009_FIX_01` acceptance: `PASS`.

H1 closure readiness: `PASS_WITH_LIMITS`.

Scientific H1 classification: `SUPPORTED_WITH_LIMITS`.

The two P1 blockers from `QA_REPORT_HANDOFF_009_H1.md` are closed. No new P0/P1 blocker was found.

PM may now record H1 as closed with the above claim boundary and proceed to the separately scoped H2 task. H2 must not reinterpret H1 as evidence of superiority to RAW or to memory architectures generally.

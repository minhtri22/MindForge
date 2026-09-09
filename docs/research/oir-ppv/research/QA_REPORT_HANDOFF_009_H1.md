# QA_REPORT_HANDOFF_009_H1 - Independent QA Review

## 1. Scope

Independent QA review of:

- `HANDOFF_009_H1.md`
- `pipeline/run_h1_closure.py`
- `experiments/OIR_PPV/H1_Closure/EXP-H1-001/H1_CLOSURE_REPORT.md`
- frozen H1 protocol / manifest
- final H1 artifacts under `artifacts/h1_closure/EXP-H1-001/full/`

No implementation code, frozen protocol, frozen manifest, final experiment artifact,
or `PLAN.md` hypothesis state was modified by this QA review.

## 2. Independent replay / audit evidence

Verified:

- H1 protocol freeze hash matches file contents:
  `8d055da087c9032f9d8e4ae310c07ee2d6eef99c4526e241222430f1d934f7d3`.
- matrix manifest hash matches file contents:
  `55127d173e36028e069c841331b9807ee0dc4948241408c110b3a460be21823c`.
- reference `EXP-LRN-001` manifest remains at:
  `f9dd3438006c6db2c0be555a86c1af0a8eeb96d097a516ef5d549f2880d86656`.
- 140 final cell directories exist.
- 140/140 contain `results.json`, `complexity.json`, `provenance.json`, and
  `condition_config.json`.
- 140/140 satisfy `c_total_bytes == model_bytes + retained_state_bytes`.
- 140/140 provenance records carry the frozen H1 protocol hash and matrix hash.
- focused H1 replay: `10 passed`.
- regression replay on the declared non-`tmp_path` subset: `53 passed`.
- `PLAN.md` currently still records H1 as `FORMALIZED`; its last-write time predates
  the H1 implementation/freeze by several hours, so the existing working-tree PLAN
  diff is treated as pre-existing coordination state rather than an H1-task edit.

## 3. Findings

### P1 - Canonical inference-state byte accounting is not protocol-faithful for all learners

The frozen rule states that learner `model_bytes` must represent the canonical
serialized inference state required to reproduce representation inference.

The implementation instead uses:

`pickle.dumps(extractor, protocol=5)`

for every L0-L4 learner.

For several learners this serializes training-only components that `encode()` does
not use at inference:

- L1 `MLPEncoderTrainable`: `classifier` is trained but `encode()` uses only `encoder`.
- L2 `VAEEncoder`: `decoder` and `logvar_head` are not required for posterior-mean
  representation inference; `encode()` uses `encoder_body` + `mu_head`.
- L3 `IRMStyleEncoderSurrogate`: `classifier` is not used by `encode()`.
- L4 `DANNSurrogateEncoder`: `task_head` and `domain_head` are not used by `encode()`.

Therefore L1-L4 `model_bytes` are conservative over-counts rather than the frozen
canonical inference-state measure.

This does not appear to manufacture the positive result; it penalizes those
learners. However, it is still a mismatch between frozen protocol semantics and
measurement implementation and must be corrected or explicitly amended/versioned
before final QA freeze.

### P1 - Aggregate H1 reporting is incomplete relative to the task contract

`h1_comparison.json` and `H1_CLOSURE_REPORT.md` contain paired per-seed/per-environment
evidence and several summary statistics, but they do not provide the full frozen
reporting contract for every learner vs MEM and RAW.

Missing/incomplete items include:

- explicit wins / losses / ties;
- mean, median, min, max for every required comparison metric;
- complete paired `C_total` delta/ratio and compression-ratio summaries vs RAW;
- explicit non-inferiority classification vs RAW;
- a complete aggregate limitations/failure/inapplicability section in the machine
  readable comparison object.

The raw per-pair evidence is present, so this is repairable without rerunning the
matrix if the byte-accounting issue is separately resolved.

### P2 - MEM is protocol-valid but empirically degenerate on these continuous observations

Across all 20 MEM environment/seed cells:

- `test_hits = 0`;
- every test prediction uses the frozen global-majority fallback.

Thus MEM test utility is effectively majority-class utility, not successful
memorized retrieval.

This does not violate the pre-frozen exact-row lookup semantics and therefore is
not a protocol breach. It is, however, a major interpretation limit: H1 vs MEM is a
low bar on this benchmark because exact raw-row matching never transfers to test.

The positive H1 result must not be generalized into a claim such as "learned
representations are inherently more efficient than memory".

### P2 - RAW control materially constrains interpretation

RAW has `C_total = 0` under the frozen accounting because raw input storage and the
common downstream task head are excluded.

Observed learner-vs-RAW utility deltas show that some learners are materially worse
than RAW even while passing H1 vs MEM. In particular, L3 has paired RAW utility
deltas as low as approximately `-0.74`.

Therefore the current result supports only the frozen MEM-comparator statement,
not superiority over RAW.

## 4. Acceptance-criteria assessment

1. Protocol frozen before final execution: PASS.
2. RAW/MEM controls without test-label leakage: PASS by implementation inspection.
3. L0-L4 learner semantics reused without H1-specific learner changes: PASS.
4. Complexity categories non-overlapping: PASS, but canonical inference-state byte
   implementation is PARTIAL due to P1 finding above.
5. Utility tolerance frozen before final execution: PASS.
6. Full seed list preserved: PASS.
7. Failed/inapplicable cells retained truthfully: PASS; final matrix has 0 failures.
8. Required per-cell artifacts/provenance exist: PASS.
9. Aggregate per-seed/per-environment evidence exists: PASS at raw-pair level, but
   required aggregate reporting contract is PARTIAL.
10. Focused/regression checks: PASS_WITH_LIMIT due to known Windows pytest temp ACL.
11. Historical EXP-LRN-001 manifest identity preserved: PASS.
12. H1 state remains PM-controlled in `PLAN.md`: PASS for this task based on file
    state/timestamps inspected during QA.

## 5. Scientific assessment

Under the frozen H1 rule against MEM:

- L0: 20/20 paired cells satisfy lower `C_total` + utility non-inferiority.
- L3: 20/20 paired cells satisfy the same rule using the currently reported bytes.
- L1/L2/L4: 19/20.

The developer candidate `SUPPORTED` is therefore directionally supported by the
retained evidence, especially because L0 alone satisfies all 20 MEM comparisons.

However, QA does not freeze that scientific label yet because the primary
complexity metric is not implemented exactly as frozen for all learner families.

QA scientific state:

`SUPPORTED_UNDER_FROZEN_MEM_COMPARATOR_WITH_LIMITS / NOT YET FROZEN`

The strongest defensible interpretation today is:

> Within ENV-1..ENV-4 and the five frozen seeds, at least PCA/L0 achieves much lower
> retained inference-state cost than the exact-row MEM control while maintaining
> non-inferior task utility. This does not establish superiority to RAW, and MEM
> generalization is degenerate because all test lookups miss.

## 6. QA verdict

Software / evidence integrity: `PASS_WITH_LIMITS`.

Task acceptance / closure readiness: `PARTIAL`.

Blocking findings before PM freeze:

1. Correct canonical inference-state serialization/accounting for L1-L4, or issue
   an explicit protocol amendment/version decision and rerun only the invalidated
   complexity scope as required by project governance.
2. Regenerate `h1_comparison.json` and `H1_CLOSURE_REPORT.md` with the complete
   required paired statistics and wins/losses/ties against both MEM and RAW.

Do not tune learners, change epsilon, alter MEM lookup semantics, replace seeds, or
modify the existing final evidence to make the result stronger.

## 7. Recommended next action

Open a narrow `DEV_TASK_009_FIX_01` limited to:

- inference-state accounting correction / protocol-consistency decision;
- aggregate reporting completion;
- focused regression and independent QA replay.

Do not start H2 until this H1 closure correction is independently accepted.

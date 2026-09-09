# H3R v1.1 G6 ADVERSARIAL REVIEW

Date: 2026-09-09
Role: Adversarial scientific reviewer

## Review objective

Attempt to invalidate the H3R v1.1 execution or its interpretation without changing the frozen protocol or rerunning the experiment.

## Challenges tested

1. **Wrong frozen identity?** Rejected. The decisive runner passed frozen protocol/test-manifest hash checks and pre-execution identity matched all 20 cells.
2. **Duplicate or hidden scientific access?** Rejected. The access log contains exactly one `H3R_V1_1_DECISIVE_ACCESS_001` event.
3. **Incomplete/selective matrix?** Rejected. 20/20 frozen environment-seed cells exist, are valid, and total 6039/6039 test rows.
4. **Noise violates mixed-schema contract?** Rejected. All realized-shift validators pass; categorical channels are preserved and normalized L_inf is bounded by 0.10.
5. **Statistics depend on result-dependent ordering?** Rejected. Independent recomputation using the frozen manifest seed order reproduces all estimates/CIs and the global verdict to floating-point tolerance.
6. **Verdict driven by an unstated criterion?** Rejected. All L1-L4 are falsified by the predeclared clean-utility lower-CI rule; support also fails the predeclared noise-improvement criterion.
7. **Cell observation-hash mismatch invalidates data identity?** Not supported as a P0/P1 challenge. The mismatch is a redundant post-check serialization field. Correct frozen observation identity was checked before metrics and is preserved in `pre_execution_identity.json`. Classified P2 and documented by erratum.
8. **Library FutureWarnings imply semantic drift?** Rejected. The warnings are deprecation notices; the runtime manifest records Python/Numpy/scikit-learn versions and source hashes, and execution completed deterministically under the frozen contract.
9. **Can the result be generalized to invariant learning or real-world robustness?** No. Any such generalization would exceed the claim boundary.

## Verdict

- ADVERSARIAL_REVIEW: `PASS_WITH_LIMITS`
- P0: none.
- P1: none.
- P2: decisive cell observation-hash metadata inconsistency; external validity remains intentionally unproven.
- Scientific classification survives adversarial review: `FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Rerun: `FORBIDDEN`.
- H4 remains unopened.

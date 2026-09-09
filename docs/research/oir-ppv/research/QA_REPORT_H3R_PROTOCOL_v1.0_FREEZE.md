# Independent Review — H3R Protocol v1.0 Freeze

Review target: `OIR-PPV-H3R v1.0`  
Branch: `oir-ppv-research`  
Source anchor HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`  
Review type: protocol/evidence-governance review only; decisive H3R experiment was not executed.

## Verdict

```text
INDEPENDENT_REVIEW: PASS_WITH_LIMITS
PROTOCOL_FREEZE: PASS
H3R_PROTOCOL_v1.0: FROZEN / NOT_EXECUTED
P0: 0
P1: 0
H4: NOT_OPENED / DEFERRED_BY_OWNER
```

## Material review findings

1. The draft could not be frozen as written because mandatory mechanism, split, noise, utility, candidate, statistical, and test-lock fields were unresolved.
2. Historical H3 `do(N)` cannot be reused as H3R observation noise. In particular, historical ENV-3 recomputed task-relevant values. H3R now perturbs only the post-generation observation channel, allowing ENV-3 without changing state or `Y`.
3. Reusing historical seeds would contaminate a revised decisive test because H1-H3 already exposed their test outcomes. H3R freezes a new disjoint seed set: `271828, 314159, 161803, 141421, 173205`.
4. Historical trained L0-L4 artifacts are not reused as scientific evidence. Learner definitions/hyperparameters are lineage; all five systems must be retrained from scratch on H3R clean train support.
5. Historical H3 used per-environment training, so Formal v1.0 lifecycle is correctly frozen as `ENVIRONMENT_CONDITIONED`, with zero test-time adaptation.
6. The primary estimand is now risk-oriented `E_noise = DeltaR_noise(candidate)-DeltaR_noise(L0)`, with a 0.01 practical improvement margin and 0.02 clean-utility noninferiority margin.
7. Four candidate-vs-L0 primary comparisons use Bonferroni familywise alpha 0.05 and deterministic stratified paired bootstrap; no result-dependent retry, pruning, or retuning is permitted.
8. Pareto and cost are disabled for H3R v1.0 acceptance, so they cannot become post-hoc rescue criteria.

## Test lock review

- Test identity: 4 environments x 5 new seeds = 20 cells.
- Frozen clean test rows: 6131.
- Four observation-noise replicates per test row.
- Test manifest SHA256: `4996c014aae5aba8aaaa72952e89692cb0f2fe439b2030a34ad72b271985349e`.
- Frozen protocol SHA256: `1cb444f9e5a48f8f3a69f866097611863d6177fbeb570aa5ceb78a2a7ee730e7`.
- Scientific test access count at freeze: `0`.

The sealing pass generated deterministic simulator rows only to record counts and SHA256 identities. It did not run any learner, compute predictions/metrics, summarize labels, compare candidates, or tune protocol values.

## Freeze limitations / P2 debt

The owner explicitly delegated commit/push to another agent working from the MindForge parent directory. Therefore the freeze artifacts are currently file-hash anchored to source HEAD `0521c575...` but are not yet contained in a new Git commit.

This is classified `P2 / PROVENANCE_PUBLICATION_DEBT`, not a scientific P0/P1 blocker, because protocol semantics, canonical file hashes, test identity, candidates, and thresholds are already frozen. **Decisive H3R execution must remain locked until the freeze package has been committed from the correct repository root and the resulting commit SHA is recorded without changing frozen scientific semantics.**

## Claim boundary

This review freezes a protocol; it provides no H3R scientific result. Historical H3 remains `CLOSED_WITH_LIMITS / NOT_SUPPORTED` and is not overwritten. H4 remains unopened.

# OIR-PPV Research Plan

## Source of truth

Canonical OIR-PPV research control path:

`docs/research/oir-ppv/research/PLAN.md`

The repository-root `PLAN.md` is the broader MindForge roadmap. OIR-PPV hypothesis state, evidence class, gate state, and next research action are controlled here.

Plans found under `.h3r2r_work/`, `h3r2r_work/`, `.qh3r_source/`, reconstruction clones, caches, and nested `targetrepo*` paths are snapshots only.

## Current control point

Reviewed head: `fa4a092bd5d3e4c5314e339561e1682c55e2dae4`

Current state: `REVIEW_COMPLETE__DEFER`

H4 scientific gate: `H4_ELIGIBLE`

H4 operational state: `NOT_OPENED / DEFERRED_BY_OWNER`

## Lineage

| Stage | Status | Evidence class |
|---|---|---|
| H3R | `FALSIFIED_UNDER_TESTED_CONDITIONS` | historical confirmatory adjudication |
| Q-H3R.1 | `PARTIAL_MECHANISM_DIAGNOSIS` | exploratory diagnostic |
| H3R2 | `INVALID_PROTOCOL_INPUT` | invalid prospective input |
| H3R reconstruction | `RECONSTRUCTION_CONFIRMED` | reconstruction fidelity |
| H3R2-R execution | `EXECUTION_INTEGRITY_PASS` | prospective execution |
| H3R2-R science | `PROTOCOL_DEVIATION` | descriptive scientific evidence |
| M6 | `EXPLORATORY_SUPPORTED / UNCONFIRMED` | exploratory |
| M7 | `EXPLORATORY_SUPPORTED / UNCONFIRMED` | exploratory |
| REVIEW_BEFORE_H4 | complete | independent QA gate |
| H4 | `NOT_OPENED / DEFERRED_BY_OWNER` | deferred future stage |

Reconstruction fidelity, execution integrity, exploratory diagnosis, descriptive evidence, and confirmatory adjudication remain separate evidence classes.

## Canonical research areas

- `q-h3r-1/`
- `h3r2-r/`
- `review-before-h4/`
- `PLAN.md`
- `REPO_LINEAGE.md`

## PM gate discipline

Before a future OIR-PPV stage begins:

1. read this plan and `review-before-h4/NEXT_GATE.md`;
2. verify branch and HEAD;
3. record the selected next stage here;
4. freeze hypothesis, evidence identity, protocol, decision rule, provenance, stopping rule, and failure rule before decisive evidence access when the work is confirmatory;
5. preserve historical evidence and record any authorized correction additively;
6. update this plan after closure before another stage begins.

Minimum decisive-evidence provenance: `source`, `config`, `seed`, `model_state`, `dataset_identity`, `artifact`, `hash`.

## Next action

The active PM state is `REVIEW_COMPLETE__DEFER`.

A future research stage starts only after the owner selects it and this canonical plan is updated to record that transition.

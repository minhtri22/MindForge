# OIR-PPV Research Plan

## Source of truth

Canonical OIR-PPV research control path:

`docs/research/oir-ppv/research/PLAN.md`

The repository-root `PLAN.md` is the broader MindForge roadmap. OIR-PPV hypothesis state, evidence class, gate state, and next research action are controlled here.

Plans found under `.h3r2r_work/`, `h3r2r_work/`, `.qh3r_source/`, reconstruction clones, caches, and nested `targetrepo*` paths are snapshots only.

## Current control point

Reviewed head before post-H3R frontier amendment: `4e26b203fbe991d073a65d659fdcd224ff699137`

Current state: `POST_H3R_FRONTIER_CLOSED`

H4 scientific gate: `H4_ELIGIBLE`

H4 operational state: `NOT_OPENED / DEFERRED_BY_OWNER`

H3R2-CONFIRMATORY-v2: `AUTHORIZED_FOR_PROTOCOL_REVIEW`

H3R2-CONFIRMATORY-v2 evidence access: `NOT_AUTHORIZED`

## Lineage

| Stage | Status | Evidence class |
|---|---|---|
| H3R | `FALSIFIED_UNDER_TESTED_CONDITIONS` | historical confirmatory adjudication |
| Q-H3R.1 | `PARTIAL_MECHANISM_DIAGNOSIS` | exploratory diagnostic |
| H3R2 | `INVALID_PROTOCOL_INPUT` | invalid prospective input |
| H3R reconstruction | `RECONSTRUCTION_CONFIRMED` | reconstruction fidelity |
| H3R2-R execution | `EXECUTION_INTEGRITY_PASS` | prospective execution |
| H3R2-R science | `PROTOCOL_DEVIATION` | descriptive scientific evidence |
| H3R2-R v1.1 | `BLOCKED_BY_GOVERNANCE / NOT_EXECUTED` | governance-blocked proposal |
| M6 | `EXPLORATORY_SUPPORTED / UNCONFIRMED` | exploratory |
| M7 | `EXPLORATORY_SUPPORTED / UNCONFIRMED` | exploratory |
| REVIEW_BEFORE_H4 | complete | independent QA gate |
| POST_H3R_FRONTIER | `CLOSED` | governance decision |
| H3R2-CONFIRMATORY-v2 | `AUTHORIZED_FOR_PROTOCOL_REVIEW` | protocol-review authorization only |
| H4 | `NOT_OPENED / DEFERRED_BY_OWNER` | deferred future stage |

Reconstruction fidelity, execution integrity, exploratory diagnosis, descriptive evidence, confirmatory adjudication, and governance authorization remain separate evidence classes.

## Canonical research areas

- `q-h3r-1/`
- `h3r2-r/`
- `review-before-h4/`
- `H3R2_CONFIRMATORY_v2_PROTOCOL_BRIEF.md`
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

Complete verdict and decision rules must be frozen before decisive evidence access.

## Post-H3R frontier governance — Amendment 001

A scientific closure does not automatically open the next hypothesis or experiment.

After closure, governance must explicitly assess mechanism status and evidence debt, then the owner must classify the next frontier as exactly one of:

1. confirmatory follow-up;
2. new hypothesis;
3. research stop/park.

Conceptual gate:

```text
Scientific Closure
        |
        v
Mechanism Status
        |
        v
Evidence Debt
        |
        v
Owner Frontier Decision
        |
  +-----+-----+
  |     |     |
  v     v     v
Confirmatory  New H  Stop/Park
```

This is a governance rule, not scientific evidence.

For the current frontier, the owner decision is:

- `DEFER_H4`;
- `AUTHORIZE_H3R2_CONFIRMATORY_V2_PROTOCOL_REVIEW`;
- `NOT_AUTHORIZE_H3R2_CONFIRMATORY_V2_EVIDENCE_ACCESS`.

H4 and H3R2-CONFIRMATORY-v2 are alternative post-H3R research directions. H3R2-CONFIRMATORY-v2 is not a prerequisite for H4. Future H4 opening remains a separate owner decision even if H3R2-CONFIRMATORY-v2 later closes successfully.

Protocol review for H3R2-CONFIRMATORY-v2 must remain preregistration-only until a future governance action authorizes execution. It must not generate fresh test identity, fresh seeds, decisive evidence, results, or a scientific verdict.

## Next action

The next authorized action is `H3R2_CONFIRMATORY_V2_PROTOCOL_REVIEW`.

This authorization covers protocol review/preregistration only. H4 remains closed and decisive evidence access remains unauthorized.

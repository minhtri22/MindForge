# Continual Loss Response Modeling (CLRM)

Status: **CLRM-0 PASS / CLOSED — CLRM-1 DESIGN ONLY AUTHORIZED**

Branch: `research/continual-loss-response`

Parent closure:

```text
research/measurement-substrate-adequacy
64138ab9cb09dcb56a387d3b1f500063eff8302d

MSA PROGRAM = FORMALLY CONVERGED / CLOSED
MSA-3 = REPLICATION_CONFIRMED
replicated finding = ACCURACY_COARSE_LOSS_INFORMATIVE
```

CLRM is a new response-modeling program opened after MSA convergence.

It is **not CPRM-2** and does not rescue the CPRM-1 frozen target.

CLRM-0 contains specification/governance only.

No fresh seed cohort, scientific collection, predictor fitting, feature
selection, hyperparameter tuning, controller, or KCL-7 execution is authorized.

Canonical CLRM-0 documents:

- `ORIGIN.md`
- `EVIDENCE_INHERITANCE.md`
- `RESEARCH_QUESTION.md`
- `RESPONSE_VECTOR_CONTRACT.md`
- `ACCURACY_SENTINEL_CONTRACT.md`
- `ELIGIBLE_POPULATION_CONTRACT.md`
- `BASELINE_CONTRACT.md`
- `PARTITION_CONTRACT.md`
- `QUALIFICATION_GATES.md`
- `FRESHNESS_EXCLUSIONS.md`
- `ROADMAP.md`
- `LINEAGE.md`

The next admissible transition after CLRM-0 PASS is design/preregistration of
CLRM-1 measurement-support qualification. CLRM-1 is still a no-predictor
milestone.


## CLRM-0 formal closure

Independent static zero-science specification QA is **PASS / CLOSED**.

Canonical closure: `CLRM0_SPEC_QA.md`.

```text
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS

CLRM-1 protocol design          AUTHORIZED
CLRM-1 fresh execution         NOT AUTHORIZED
predictor fitting              NOT AUTHORIZED
controller                     CLOSED
KCL-7                          CLOSED
```


Canonical zero-science Actions confirmation:

```text
workflow = 36057035870
4/4 tests PASS
CLRM0_ZERO_SCIENCE_SPEC_QA_PASS
```


## CLRM-1 preregistration status

CLRM-1 Loss Response Support Qualification is preregistered and its
zero-science preflight is **PASS / CLOSED**.

```text
Role-S seeds                   72 FROZEN
boundaries                     216 expected
policy response vectors        648 expected
direct loss channels           6 FROZEN
reliability repeats            6 FROZEN
Execution Lock SHA-256
39d4e22081c6cb6ac551c6ac5a77816747dd5dc9c477bd11b09c12de8f880d2e

CLRM1_ZERO_SCIENCE_PREFLIGHT_PASS
```

Fresh CLRM-1 science remains blocked pending independent exact-lock
verification. CLRM-2 design and predictor fitting remain closed.

# MSA — Measurement / Substrate Adequacy

Status: **MSA-0 PASS / CLOSED — SCIENTIFIC EXECUTION NOT YET AUTHORIZED**

Branch: `research/measurement-substrate-adequacy`

Exact parent:

```text
c1837438d944c0e11dcb961fa669cfef92bc3c2d
CPRM_FORMAL_CONVERGENCE_REVIEW = CLOSED
CPRM_PROGRAM = TERMINATED AS FORMULATED
NEXT_DIRECTION = RETURN UPSTREAM TO MEASUREMENT / SUBSTRATE ADEQUACY
```

MSA is an upstream measurement/substrate program. It is not CPRM-2 or predictor
rescue. Its purpose is to determine whether the current controlled
continual-learning substrate provides an adequate endpoint-performance
measurement regime before any future state-conditioned response model is
considered.

Authorized now: MSA-0 documentation, consistency checks, zero-science QA.

Not authorized: fresh MSA seeds, scientific collection, task/substrate
difficulty changes, training-budget changes, predictor fitting, controller
implementation, or MSA-1 execution.


## MSA-0 QA closure

Canonical QA: `MSA0_SPEC_QA.md`.

```text
MSA0_ZERO_SCIENCE_SPEC_QA_PASS
```

Authorized next: design and preregistration of MSA-1 only.

Still forbidden: fresh MSA execution, difficulty mutation, predictor fitting,
controller work, and reuse of protected/spent evidence.


## MSA-1 preregistration status

MSA-1 Current-Substrate Endpoint Adequacy Qualification is now preregistered,
implementation-frozen and zero-science preflight qualified.

```text
72-seed manifest             FROZEN
unchanged substrate identity FROZEN
endpoint pair                FROZEN
accuracy classification      FROZEN
loss classification          FROZEN
joint matrix                 FROZEN
execution lock v1            FROZEN
zero-science preflight       PASS

fresh MSA-1 science          NOT AUTHORIZED YET
MSA-2                        CLOSED
predictor                    CLOSED
```

Canonical closure: `MSA1_PREFLIGHT_QA.md`.

Next admissible step: independent execution-lock verification only.


## MSA-1 independent execution-lock verification

Independent verification is now **PASS / CLOSED**.

Canonical closure: `MSA1_EXECUTION_LOCK_VERIFICATION.md`.

```text
lock SHA-256
c42062b965a08f5e503f8307eaa27ffbede13511ed245dfdb80e0163d747f657

MSA1_EXECUTION_LOCK_VERIFICATION_PASS
```

No fresh MSA-1 seed was executed during verification.

The frozen 72-seed / 216-boundary current-substrate collection is now eligible
to be opened under the exact verified lock.

No fresh execution workflow has yet been created. MSA-2, predictor fitting,
controller work and KCL-7 remain closed.


## MSA-1 scientific result

MSA-1 completed under the verified frozen lock and returned:

```text
PASS
ACCURACY_COARSE_LOSS_INFORMATIVE
```

The frozen global classification is:

```text
terminal accuracy           SATURATED
terminal cross-entropy loss INFORMATIVE
```

Canonical scientific closure: `MSA1_FORMAL_CLOSURE.md`.

Formal transition review: `MSA1_FORMAL_TRANSITION_REVIEW.md`.

The transition review does **not** open MSA-2. The next authorized work is
MSA-3 independent-replication **design/preregistration only**, preserving the
exact MSA-1 substrate, endpoint definitions, gates and classification matrix.

MSA-3 fresh execution, MSA-2, predictor fitting, controller work and KCL-7
remain closed.


## MSA-3 replication status

MSA-3 Independent Fresh Replication is preregistered and zero-science
preflight qualified.

```text
discovery claim:
ACCURACY_COARSE_LOSS_INFORMATIVE

72-seed replication cohort    FROZEN
MSA-1 substrate/metrics/gates FROZEN / UNCHANGED
replication success criterion FROZEN
execution lock                FROZEN
zero-science preflight        PASS

fresh MSA-3 science           NOT AUTHORIZED YET
```

Canonical preflight closure: `MSA3_PREFLIGHT_QA.md`.

Next admissible step: independent exact-lock verification only.

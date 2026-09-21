# M5Q Q4_K_M — Bounded Implementation Authorization

## Status

```text
Q4_K_M implementation: AUTHORIZED
Q4 zero-outcome tests: AUTHORIZED
Q4 scientific execution: NOT AUTHORIZED
Q4 formal PASS claim: NOT AUTHORIZED

prior out-of-protocol outcome exposure: TRUE
future execution class:
FORMAL REPLICATION / QUALIFICATION
UNDER PRE-EXPOSURE PREREGISTERED CONTRACT

M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

Q4_K_M was preregistered before the accidental outcome exposure. The controlling
contract remains the pre-exposure `PREREGISTRATION.json` blob
`c7f6addf220f659276fd0035b272b235b12df22c`.

The accidental Q4 result is disclosed by `Q4_OUTCOME_EXPOSURE.json` and remains
exploratory only. Its SHA, manifest, size, output, parity result and combined-run
result MUST NOT be copied into Q4 code, tests, lock criteria, thresholds, or
expected-result assertions. No post-exposure gate may be added, including strict
Q4<Q8 compression ordering.

The Q4 contract remains exactly the preregistered one: target `Q4_K_M`, exact
F16 parent, exact model/revision, exact fixture/inference contract, exact
llama.cpp/converter lock, direct Q4↔F16 preservation comparator, and the same
13 per-target required gates.

Q8 PASS/CLOSED is sequence provenance only; Q4 does not inherit Q8 PASS.

Only these new target-specific files are authorized:

```text
pipeline/m5q_q4.py
tools/m5q_q4_qualification.py
tools/m5q_q4_preflight.py
tests/test_model_pipeline_m5q_q4.py
.github/workflows/model-pipeline-m5q-q4-preflight.yml
```

Existing general M5 and Q8 scientific surfaces are frozen. In particular,
`pipeline/m5.py` must remain blob
`0249be91acbe57fd20b8577a0cda3d6ea5acb048`; the accidental general-M5
fail-semantics change is not authorized.

The Q8 module may be used only as a structural reference for frozen-input
verification, exact F16 regeneration/identity checks, target-specific
quantization, direct F16 preservation, reasoning-runtime mapping, and terminal
adjudication.

The authorized sequence from this commit is:

```text
target-specific Q4 implementation
        ↓
unit/contract tests
        ↓
tests PASS
        ↓
exact implementation lock
        ↓
lock-present zero-science preflight
```

A separate execution authorization is mandatory after preflight PASS. This
document itself does not authorize Q4 quantization or scientific execution.

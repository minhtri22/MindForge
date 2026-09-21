# M5Q Lineage — Append Only

## 2026-09-21 — Program opened

Parent high-fidelity qualification:

```text
M5 F16 closure commit:
9ff987ebd95cd23fef4cd2a0511774d772b14400

qualified scientific commit:
2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719

authoritative workflow run:
35617920637

result hash:
0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57
```

Decision:

```text
OPEN M5Q AS A SEPARATE QUANTIZATION QUALIFICATION PROGRAM
TARGET 1: Q8_0
TARGET 2: Q4_K_M
EXECUTION: SEQUENTIAL / ONE TARGET AT A TIME
M6: REMAINS CLOSED
```

The F16 non-blocking observation
`M5_F16_PARITY_ABSOLUTE_CAPABILITY_CEILING` is inherited as a claim-scope
limitation, not as a reason to redesign the parent metric.

No scientific quantization execution has occurred on this branch at program
opening.

## 2026-09-21 — Q8_0 implementation tested and locked

Q8_0 implementation:

```text
68bbd071ba78f6325748159703a90232d69e4ade
```

Pre-lock test workflow:

```text
run: 35623958915
job: 106413584115
conclusion: success
existing M5 tests: 12/12 PASS
Q8_0 contract tests: 8/8 PASS
```

The implementation is target-specific. It regenerates and verifies the exact
qualified F16 parent before quantization, invokes only `Q8_0`, compares the
quantized runtime against the F16 parent rather than HF directly, carries the
known 0%-to-0% preservation limitation without changing the metric, and hard
blocks Q4 and M6.

At lock time:

```text
Q8_0 scientific execution: NOT YET RUN
Q4_K_M: NOT RUN / NOT AUTHORIZED
M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

The exact implementation/dependency blob set is frozen in
`Q8_0_IMPLEMENTATION_LOCK.json`.

The only next gate is zero-science preflight. No Q8_0 scientific execution is
authorized until that preflight passes.


## 2026-09-21 — Zero-science preflight helper invalidation and bounded repair

The first lock-present preflight invocation is terminally classified:

```text
run: 35624467187
job: 106415285615
artifact: 10651021689
classification: INVALID_ZERO_SCIENCE_PREFLIGHT_HELPER
scientific execution consumed: NO
```

The JSON itself reported `status=FAIL` because the helper attempted to prove it
did not import `pipeline.m5q` by searching its own source for a literal that was
necessarily present inside that check. The workflow nevertheless appeared green
because `python ... | tee` did not enable `pipefail`.

Bounded repair only:

```text
tools/m5q_q8_preflight.py:
literal self-scan -> AST import inspection

.github/workflows/model-pipeline-m5q-q8-preflight.yml:
enable set -o pipefail
```

The scientific Q8_0 implementation commit remains exactly:

```text
68bbd071ba78f6325748159703a90232d69e4ade
```

No model/config/fixture/inference/quantizer target/parity rule changed.
No quantization executed. Q4 and M6 remain closed.


## 2026-09-21 — Q8_0 zero-science preflight PASS

Authoritative requalification after the bounded helper repair:

```text
run: 35624821038
job: 106416489333
conclusion: success
artifact: 10651022297
artifact zip sha256:
f823a1041853a12e6513a63326e20d684ec455e4e817ce3c756b4f91d83e65a9
```

The emitted zero-science result is `PASS`.

All locked scientific/helper dependency blobs matched their expected Git blob
identities. Static checks proved that the Q8 implementation is target-specific,
does not enter the general M5 target loop, hard-codes Q4 as unexecuted, hard
blocks M6 and automatic M6 opening, and keeps the preflight itself detached from
the Q8 runtime implementation.

Regression evidence remained:

```text
existing M5 tests: 12/12 PASS
Q8_0 contract tests: 8/8 PASS
```

Execution boundary at preflight closure:

```text
quantization_executed: false
Q8_0 scientific execution: NOT RUN
Q4_K_M: NOT RUN / NOT AUTHORIZED
M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

Q8_0 is now `READY_FOR_ONE_SHOT_EXECUTION`. This lineage entry does not execute
or adjudicate Q8_0.

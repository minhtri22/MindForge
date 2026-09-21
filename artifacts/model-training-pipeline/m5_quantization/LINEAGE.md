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


## 2026-09-21 — Q8_0 one-shot scientific qualification PASS / CLOSED

The first orchestration attempt stopped before scientific execution:

```text
run: 35628522807
job: 106428724201
classification: INVALID_EXECUTION_ORCHESTRATION
scientific execution started: NO
quantization executed: NO
one-shot scientific authorization consumed: NO
```

The defect was restricted to the execution authorization lookup and was repaired
without changing the scientific Q8 implementation, config, fixture, inference
contract, quantizer target, or preservation rule.

Authoritative one-shot execution:

```text
run: 35628720499
job: 106429375737
head: b74f30553c648b9951719b2001ba9f253af5bb5c
artifact: 10653802062
artifact zip sha256:
f05934d02eeb25a21cc51e9d6160866d0966b8c5fa7590857d18c76d71ae4b91
```

Scientific result:

```text
status: PASS
result_hash:
16b3ce2f4522481ab086068c4a0ce625f9c0a2759d9d946a3deffc7bcf44c1c8

failed_required_gates: []
```

Q8_0 artifact:

```text
file: model-q8_0.gguf
quantizer type: Q8_0
size: 531067744 bytes
sha256:
35e1d06149ea36b2021f02369db0910cc6e02e691666cdbde0488210172e0146

aggregate manifest hash:
2b7133017c74b3d5a1775b1620eed65a8fccaa70f35009038d88fde2daaf9e0b
```

The exact frozen F16 parent identity was regenerated and matched before Q8
quantization. All 13 preregistered Q8 gates passed, including real llama-cli
load/inference, task-vector and accuracy identity versus F16, format
preservation, reasoning runtime mapping, and artifact-size reduction.

The inherited F16 benchmark limitation remains non-blocking and unchanged:

```text
F16 task vector: [false, false]
Q8 task vector:  [false, false]
F16 accuracy:    0.0
Q8 accuracy:     0.0
preservation:    PASS
absolute capability claim: NO
```

Terminal state:

```text
Q8_0: PASS / CLOSED
Q8 rerun: NOT AUTHORIZED

Q4_K_M: NOT EXECUTED
Q4 does not inherit Q8 PASS

M6: CLOSED / NOT AUTHORIZED
M6 auto-open: FALSE
bulk training: CLOSED / NOT AUTHORIZED
```

The next permitted governance action is a separate Q4_K_M implementation
authorization/opening under the already-preregistered M5Q sequence. This entry
does not open or execute Q4_K_M.


## 2026-09-22 — Accidental-agent drift quarantined; Q4 outcome exposure recorded

An accidental agent advanced `docs/evidence-model-training-pipeline` by 15
commits and created a parallel combined Q8+Q4 program.

Audit found that the authoritative M5Q branch itself had not drifted:

```text
authoritative M5Q head:
997e555b53f957268da1ec19ebc10ebb4a0873e9
```

The full accidental chain was preserved at:

```text
quarantine/m5-quantization-agent-drift-20260921
ddb0a080ae06c99b6f72ffa633d34f255989b485
```

Then the F16 evidence branch was restored to:

```text
docs/evidence-model-training-pipeline
9ff987ebd95cd23fef4cd2a0511774d772b14400
```

No accidental history was deleted.

The audit rejected the combined Q8+Q4 execution semantics as authoritative for
M5Q because the locked M5Q program is sequential and target-specific.

Useful technical findings were retained as quarantine/reference knowledge:
exact F16 parent identity checking, order-independent post-serialization target
membership, and compression/distinct-hash observations. None was cherry-picked
into active scientific code during this audit.

The accidental Q8 result independently reproduced the authoritative Q8 artifact
identity. This is corroborative only; Q8 remains closed under its original
authoritative result.

Q4 scientific work was executed outside the authoritative sequence in run
`35632404520`, and a later accidental replay `35634940378` exposed a Q4
artifact and PASS under the accidental protocol. Therefore:

```text
Q4_K_M formal status:
NOT FORMALLY QUALIFIED

prior out-of-protocol outcome exposure:
TRUE
```

The exposed Q4 outcome is retained as exploratory evidence and is forbidden from
driving thresholds, tuning, fixture/runtime changes, or a formal PASS claim.

Because Q4_K_M had already been preregistered before exposure, the next Q4 step
may proceed only as a **formal replication/qualification under the pre-exposure
preregistered contract**, with a fresh target-specific implementation lock and
zero-science preflight.

M6 and bulk training remain closed.


## 2026-09-22 — Q4_K_M bounded implementation authorization opened

Q4_K_M remains `NOT FORMALLY QUALIFIED` with prior out-of-protocol outcome
exposure explicitly disclosed.

The controlling contract is still the pre-exposure preregistration blob:

```text
c7f6addf220f659276fd0035b272b235b12df22c
```

The accidental Q4 outcome is forbidden from influencing code, tests, thresholds,
lock criteria, or expected results. Q4 will proceed as a formal
replication/qualification under that pre-exposure contract.

Only target-specific Q4 implementation/test/preflight files may be added.
`pipeline/m5.py`, Q8 scientific code/evidence, and the preregistration remain
frozen.

Current boundary:

```text
Q4 implementation: AUTHORIZED
Q4 tests: AUTHORIZED
Q4 scientific execution: NOT AUTHORIZED
M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

Next valid action: implement the target-specific Q4 path and run zero-outcome
tests. Exact implementation lock may be created only after tests PASS.


## 2026-09-22 — Q4_K_M implementation tests PASS; exact implementation locked

Target-specific Q4 implementation:

```text
97d7dad329aa0196ead9005e631eebbeb8aa2163
```

Zero-outcome test workflow:

```text
run: 35640617420
job: 106468748043
conclusion: success

M5 regression: 12/12 PASS
Q8 regression: 8/8 PASS
Q4 contract tests: 10/10 PASS
```

The workflow explicitly proved:

```text
quantization_executed=false
q4_scientific_execution_executed=false
m6_authorized=false
```

The implementation is now frozen in
`Q4_K_M_IMPLEMENTATION_LOCK.json`, including the target-specific code and all
transitive scientific/provenance dependencies required to regenerate and verify
the frozen F16 comparator.

The lock records prior out-of-protocol outcome exposure but does not embed the
exposed Q4 artifact SHA, manifest, size, or accidental PASS as an expected value
or threshold.

Current boundary:

```text
Q4 implementation: LOCKED
Q4 zero-outcome tests: PASS
Q4 scientific execution: NOT AUTHORIZED
M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

The only next gate is lock-present zero-science preflight.

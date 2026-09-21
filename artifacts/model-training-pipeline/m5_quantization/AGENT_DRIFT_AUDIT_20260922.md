# M5Q Agent-Drift Audit and Selective Salvage Decision

## Audit status

```text
AUDIT: COMPLETE
AUTHORITATIVE_BRANCH:
research/model-pipeline-m5-quantization-qualification

AUTHORITATIVE_HEAD_BEFORE_AUDIT:
997e555b53f957268da1ec19ebc10ebb4a0873e9

DRIFTED_BRANCH:
docs/evidence-model-training-pipeline

DRIFTED_HEAD:
ddb0a080ae06c99b6f72ffa633d34f255989b485

QUARANTINE_BRANCH:
quarantine/m5-quantization-agent-drift-20260921

RESTORED_DOCS_HEAD:
9ff987ebd95cd23fef4cd2a0511774d772b14400
```

The authoritative M5Q branch was not modified by the accidental agent. Its HEAD
remained exactly the Q8 PASS closure commit throughout the incident.

The accidental work occurred on `docs/evidence-model-training-pipeline`, which
advanced 15 commits beyond the F16 closure and introduced a parallel Q8+Q4
quantization program.

## Preservation and restoration action

The accidental 15-commit chain is preserved intact at:

```text
quarantine/m5-quantization-agent-drift-20260921
→ ddb0a080ae06c99b6f72ffa633d34f255989b485
```

After preservation, `docs/evidence-model-training-pipeline` was restored to:

```text
9ff987ebd95cd23fef4cd2a0511774d772b14400
```

No accidental commit was deleted from repository history.

## Drift classification

### Rejected as authoritative scientific lineage

The following changes are not admitted into the authoritative M5Q scientific
chain:

1. replacing the preregistered sequential program
   `Q8 → freeze/adjudicate → Q4` with a combined Q8+Q4 one-shot program;
2. changing general `pipeline/m5.py` semantics so a failed quantized target no
   longer fails immediately before later targets run;
3. treating Q8 and Q4 as one aggregate qualification whose overall result is
   emitted only after both targets execute;
4. using the accidental combined-run replay as the formal Q4 qualification;
5. treating the replay as a clean first-look one-shot after Q4 had already been
   executed in the prior failed wrapper invocation.

These are protocol changes, not merely refactors.

## Selective salvage — retained as valuable technical knowledge

The quarantine work contains useful engineering ideas. They are retained for
later bounded review, but are not automatically cherry-picked into the current
scientific implementation.

### S1 — Exact F16 parent identity helper

The accidental branch added helpers equivalent in intent to:

```text
single_file_gguf_identity()
high_fidelity_identity_matches()
```

They check exact parent filename, size, SHA-256, and aggregate manifest before
quantization.

Decision:

```text
VALUE: KEEP AS REFERENCE
CURRENT SCIENTIFIC CODE CHANGE: NO
```

Reason: the authoritative M5Q Q8 implementation already enforces exact F16
parent SHA/manifest identity before quantization. A shared helper refactor may
be considered only after the active Q4 qualification is closed, so refactoring
cannot perturb the current confirmatory/replication sequence.

### S2 — Order-independent post-serialization target membership

The accidental wrapper exposed a real technical property:
canonical JSON serialization sorts mapping keys. Therefore serialized mapping
key order is not evidence of scientific execution order.

The bounded repair:

```text
exact target membership
instead of serialized key iteration order
```

is technically correct for a future multi-target wrapper.

Decision:

```text
VALUE: KEEP AS REFERENCE
CURRENT Q8/Q4 TARGET-SPECIFIC PATH CHANGE: NO
```

The current authoritative target-specific path does not need this helper.

### S3 — Compression ordering and distinct artifact identities

The accidental program checked:

```text
Q4_K_M size < Q8_0 size < F16 size
and all artifact hashes distinct
```

This is useful descriptive/post-quantization evidence.

Decision:

```text
VALUE: KEEP AS POST-QUANTIZATION OBSERVATION CANDIDATE
ADD AS CURRENT Q4 REQUIRED GATE: NO
```

Because Q4 size has already been exposed, strict Q4<Q8 ordering must not now be
introduced retroactively as a required Q4 gate. The preregistered Q4 gate set
must remain independent of the observed accidental outcome.

## Q8 consequence

The authoritative Q8 result remains unchanged and valid:

```text
Q8_0: PASS / CLOSED

authoritative run:
35628720499

result hash:
16b3ce2f4522481ab086068c4a0ce625f9c0a2759d9d946a3deffc7bcf44c1c8

artifact SHA256:
35e1d06149ea36b2021f02369db0910cc6e02e691666cdbde0488210172e0146

size:
531067744
```

The accidental combined replay independently regenerated the same Q8 artifact
SHA-256 and size. This is useful reproducibility evidence, but it does not
replace or reopen the authoritative Q8 adjudication.

## Q4 outcome exposure

Q4_K_M was executed outside the authoritative sequential governance.

First accidental execution:

```text
run: 35632404520
job: 106441521839

execution reached:
run_m5_qualification() completed

wrapper failure:
post-serialization target-key order guard

classification for authoritative M5Q:
OUT_OF_PROTOCOL / OUTCOME_EXPOSED
```

The failure occurred after Q8 and Q4 quantization/runtime work had already been
performed. Therefore the later replay cannot be treated as an unexposed
first-look invocation.

Accidental replay:

```text
run: 35634940378
job: 106449940536
status reported by accidental protocol: PASS

combined result hash:
08d4f3f92ff1422a505d0c87239644f9e4cbff0f6994a879b61fb9e328f232ba
```

Observed Q4 artifact:

```text
name:
model-q4_k_m.gguf

sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977

aggregate manifest:
e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b

size:
397807456

accidental protocol parity:
PASS
```

These values are retained strictly as **out-of-protocol exploratory
observations**.

They are forbidden from being used to:

- tune Q4 parameters;
- create or relax acceptance thresholds;
- add a new required compression threshold;
- change fixture, prompts, inference values, llama.cpp revision, converter,
  quantizer type, or comparator;
- claim Q4 formal PASS.

## Correct Q4 path after exposure

The original M5Q program preregistered Q4_K_M before the accidental Q4 outcome
was exposed. Therefore Q4 may still proceed, provided the pre-exposure contract
is preserved without tuning.

The scientific status is now:

```text
Q4_K_M:
NOT FORMALLY QUALIFIED
PRIOR OUT-OF-PROTOCOL OUTCOME EXPOSURE = TRUE
```

The next Q4 execution must be described as:

```text
FORMAL REPLICATION / QUALIFICATION
UNDER PRE-EXPOSURE PREREGISTERED CONTRACT
```

and not as a blind first-look confirmatory run.

Required safeguards:

1. derive Q4 implementation from the authoritative M5Q preregistration and Q8
   closure, not from the quarantine implementation;
2. preserve the preregistered Q4 target `Q4_K_M`;
3. preserve exact F16 parent, model/revision, fixture, inference contract,
   llama.cpp/converter lock, and preservation comparator;
4. do not use the exposed Q4 SHA, size, parity, or output text as an acceptance
   threshold;
5. implement Q4 target-specific code/tests/lock/preflight independently;
6. execute one formal replication under that locked pre-exposure contract;
7. adjudicate its result as-is;
8. keep M6 and bulk training closed throughout.

## Authoritative state after audit

```text
M5 F16:
PASS / CLOSED

Q8_0:
PASS / CLOSED
rerun not authorized

Q4_K_M:
NOT FORMALLY QUALIFIED
prior out-of-protocol outcome exposure recorded
next state requires separate implementation authorization

M6:
CLOSED / NOT AUTHORIZED

bulk training:
CLOSED / NOT AUTHORIZED
```

## Next valid action

The next permitted action is a bounded **Q4_K_M implementation authorization**
that explicitly cites this outcome-exposure audit and preserves the
pre-exposure preregistered contract.

No Q4 execution is authorized by this audit document itself.

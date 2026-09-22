# M6 Ollama Qualification — Lineage

## ORIGIN

M6 opens only after the M5/M5Q post-quantization governance review adjudicated:

```text
M5 = PASS / CLOSED
M5Q = PASS / CLOSED
basis to open M6 = YES
```

Origin commit:

```text
7bcacfa8fb291a9a55e2acf19077c8e61f33c329
```

M6 does not reopen F16, Q8_0 or Q4_K_M and does not inherit their PASS as an
Ollama PASS.

## 2026-09-22 — Bounded M6 specification + implementation authorization opened

A new M6 branch is opened:

```text
research/model-pipeline-m6-ollama
```

Authorized scope:

```text
specification
implementation
zero-runtime unit/contract tests
exact implementation lock after tests PASS
lock-present zero-science/zero-runtime preflight
```

Forbidden during this stage:

```text
all Ollama executable invocation
ollama create
ollama run/chat
ollama pull/rm/serve
Ollama installation/update
M6 scientific qualification
M6 PASS claim
M7 opening
bulk training
```

The canonical smoke packaging parent is the exact formal Q4_K_M artifact from
M5Q, selected because the frozen canonical config already declares q4_k_m.
This does not establish a production-target preference.

M6 must create and freeze an exact Ollama lock, deterministic Modelfile contract,
ephemeral ownership/cleanup semantics, reasoning mapping, parity comparator and
adjudication contract before any runtime execution.

Next valid action:

```text
implement M6 specification/code + zero-runtime tests
```


## 2026-09-22 — M6 zero-runtime implementation tests PASS; exact implementation locked

Authoritative zero-runtime test run:

```text
run: 35672110940
job: 106570655074
conclusion: success
tests: 13/13 PASS
```

The run proved:

```text
ollama_executable_invoked=false
ollama_runtime_execution_executed=false
m6_scientific_execution_executed=false
m7_authorized=false
```

M6 now has a deterministic zero-runtime implementation for:

```text
exact Ollama release lock
frozen Q4 source identity verification
deterministic Modelfile generation
ephemeral namespace construction
ownership-gated cleanup planning
reasoning/think request mapping
frozen llama.cpp-parent parity comparison
hard downstream boundaries
```

The Ollama release lock is pinned to official release `v0.34.2` and retains
authoritative asset digests for Windows amd64 and Linux amd64. No Ollama binary
was downloaded, installed, probed or executed.

The implementation and its transitive governance/runtime-contract dependencies
are frozen in `IMPLEMENTATION_LOCK.json`.

Current boundary:

```text
M6 implementation: LOCKED
zero-runtime tests: PASS
Ollama runtime execution: NOT AUTHORIZED
M6 scientific execution: NOT AUTHORIZED
M7: CLOSED
bulk training: CLOSED
```

Next valid gate: lock-present zero-science / zero-runtime preflight.


## 2026-09-22 — M6 lock-present zero-science / zero-runtime preflight PASS

Authoritative preflight:

```text
run: 35672245794
job: 106571075062
conclusion: success
artifact: 10671841332
artifact zip sha256:
1e936fc0512d1758353ce05e23c8261aae8b1110df78b3709eafa2bbecaa646b
```

The emitted preflight result is `PASS`.

All locked blobs matched. Static checks confirmed:

```text
exact Ollama release lock = PASS
no Ollama subprocess execution = PASS
no runtime import from preflight = PASS
deterministic Modelfile contract = PASS
ownership-gated cleanup = PASS
task/format parity rather than exact-text parity = PASS
M7 hard-closed = PASS
bulk training hard-closed = PASS
```

The same lock-present run also retained 13/13 zero-runtime contract tests PASS.

Execution boundary:

```text
ollama_executable_invoked=false
ollama_runtime_execution_executed=false
m6_scientific_execution_executed=false
M6 PASS claim: NOT AUTHORIZED
M7: CLOSED
bulk training: CLOSED
```

M6 is now ready only for a **separate runtime execution authorization** that
must choose an exact pinned venue/asset and explicitly authorize the minimum
Ollama commands needed for qualification. This preflight itself does not
authorize or execute Ollama.


## 2026-09-22 — M6 runtime authorization opened; Windows amd64 venue selected

The runtime venue is frozen as:

```text
GitHub Actions windows-2025 / x64
Ollama v0.34.2
ollama-windows-amd64.zip
sha256:
8f3fd071a2a2f9497b562f43502c77c2b701a99d1ee5dfda28da8c786373063b
```

The authorization permits only a bounded isolated runtime sequence:
asset verification, version probe, isolated server, owned create, frozen chat
parity, and owned cleanup.

A provenance gap was identified before runtime execution: the exact formal Q4
GGUF bytes were not persisted in the repo or any authoritative/accidental
Actions artifact. Only its frozen identity/evidence remains.

Therefore a hard parent-artifact admission gate is added:

```text
ollama create is forbidden until an existing materialized Q4 parent verifies:

size:
397807456

sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977
```

Silent Q4 requantization is explicitly forbidden because Q4 scientific rerun is
closed.

If exact parent bytes cannot be supplied, the correct state is
`INVALID_PROVENANCE_PARENT_ARTIFACT_UNAVAILABLE`, not scientific FAIL.

No Ollama command has been executed by this authorization commit.

Next valid action: create the bounded Windows venue orchestration. Venue/asset
qualification may run, but create/chat must remain gated on exact Q4 parent
artifact admission.


## 2026-09-22 — Windows amd64 M6 venue qualified; parent artifact admission blocked

Runtime authorization:

```text
5eb195bb78136be1d26f1acb7308d3f698c69d31
```

Bounded venue orchestration:

```text
ace26397115fba8dcdf3aac1e771d2ea042491ca
```

Authoritative venue run:

```text
run: 35673229900
job: 106574150869
conclusion: success
artifact: 10672072418
artifact zip sha256:
e21a20fe75c8630ab5a1665d6a5879627b70041fed91ffa2c2c7eb926a20921b
```

Venue evidence:

```text
requested runner: windows-2025 / x64
actual ImageOS: win25-vs2026
actual ImageVersion: 20260907.229.1
PowerShell: 7.6.5

Ollama asset SHA256:
PASS

Ollama client version:
0.34.2 / PASS

isolated server health:
PASS
```

The parent-artifact gate correctly blocked scientific packaging:

```text
required:
model-q4_k_m.gguf

size:
397807456

sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977

observed:
PARENT_ARTIFACT_UNAVAILABLE
```

Therefore the run is classified:

```text
INVALID_PROVENANCE_PARENT_ARTIFACT_UNAVAILABLE
```

This is **not** an M6 scientific FAIL.

The orchestration did not attempt to rescue the missing parent by requantizing
Q4:

```text
ollama create executed = false
ollama chat executed = false
owned cleanup executed = false
Q4 requantization executed = false
M6 scientific result = null
```

The Windows Ollama venue itself is now qualified at the asset/version/isolated
server layer. Full M6 packaging/parity remains blocked solely on admission of the
exact frozen Q4 parent bytes.

M7 and bulk training remain closed.

Next valid action: open a bounded parent-artifact materialization/provenance
program for M6. It must produce or recover a byte-identical Q4 parent without
reopening or re-adjudicating Q4 science; only after exact SHA/size admission may
a separate create/chat/owned-cleanup scientific runtime authorization be used.


## 2026-09-22 — Bounded parent-artifact materialization program opened

A separate M6 sub-program now owns recovery/materialization of the missing
frozen Q4 parent bytes.

It may recover an existing copy or, only after recovery is exhausted,
deterministically reconstruct the artifact under exact frozen identities.

This does not reopen Q4 science:

```text
Q4_K_M = PASS / CLOSED
Q4 scientific rerun = NOT AUTHORIZED
M6 create/chat = NOT AUTHORIZED
```

Admission is byte-identity only. A match or mismatch does not alter the closed
Q4 scientific verdict.


## 2026-09-22 — Parent-artifact materialization tooling zero-science PASS

The bounded parent-artifact sub-program completed its implementation/test gate:

```text
implementation:
a6f9d4341894cf59cab853d4ae6912e060c10599

zero-science run:
35674627035

tests:
12/12 PASS
```

No Q4/F16 bytes were materialized and no quantizer, model inference, scientific
adjudication, Ollama create, or Ollama chat execution occurred.

A separate execution authorization remains mandatory before any real
recovery-copy or deterministic reconstruction.


## 2026-09-22 — Parent-artifact recovery execution authorized, reconstruction still closed

The M6 parent-artifact sub-program is authorized for one recovery-only attempt
bound to implementation `a6f9d434...` and zero-science closure
`94c9300f...`.

This authorization cannot execute the Q4_K_M quantizer. A real
`NOT_FOUND_RECOVERY_EXHAUSTED` result must be frozen before deterministic
reconstruction can receive a separate authorization.

M6 scientific execution remains closed.


## 2026-09-22 — Existing-byte recovery exhausted

The bounded parent-artifact recovery attempt completed with:

```text
NOT_FOUND_RECOVERY_EXHAUSTED
candidate_count = 0
```

The recovery authorization is consumed. No quantizer, model inference, Q4
scientific adjudication, or Ollama create/chat path executed.

The exact Q4 parent remains unavailable. Deterministic reconstruction remains
closed until a separate authorization is opened against the frozen F16 and Q4
identities.


## 2026-09-22 — Parent-artifact deterministic reconstruction authorized

Existing-byte recovery is exhausted and frozen. The parent-artifact sub-program
now authorizes exactly one deterministic reconstruction attempt after exact F16
parent admission.

This is artifact materialization only:

```text
F16 exact bytes
→ exact llama.cpp ce8caa6e...
→ Q4_K_M
→ compare exact frozen Q4 byte identity
```

It is not a Q4 scientific rerun. M6 create/chat and all downstream scientific
execution remain closed until reconstructed Q4 bytes are admitted and frozen.


## 2026-09-22 — Q4 reconstruction blocked before build by missing frozen F16 bytes

The deterministic reconstruction orchestration reached the mandatory F16
parent-admission gate and terminated as:

```text
INVALID_PROVENANCE_F16_PARENT_UNAVAILABLE
```

No llama.cpp build, quantizer execution, Q4 reconstruction, scientific
evaluation, or Ollama execution occurred.

The deterministic reconstruction authorization remains unconsumed because the
quantizer never started. M6 scientific execution remains closed.


## 2026-09-22 — Bounded F16 parent-artifact recovery/materialization program opened

The Q4 reconstruction attempt remains blocked before build because the frozen
F16 binary was not persisted.

A separate F16 sub-program is opened for byte-preserving recovery/materialization
only. F16 regeneration and scientific re-adjudication remain forbidden.

The still-unconsumed Q4 reconstruction authorization `9506e5fc...` is
protected and may receive a new orchestration only after exact F16 bytes are
admitted.


## 2026-09-22 — F16 parent recovery/materialization zero-science PASS

The bounded F16 parent sub-program is implemented and locked after 14/14
zero-science tests PASS.

No F16 recovery/materialization, F16 regeneration, Q4 reconstruction, or Ollama
scientific execution occurred.

The still-unconsumed Q4 reconstruction authorization `9506e5fc...` remains
protected. A separate F16 materialization execution authorization is required
before exact F16 bytes may be admitted.


## 2026-09-22 — F16 existing-byte materialization execution authorized

A one-attempt F16 parent materialization authorization is opened after exact implementation lock and zero-science PASS.

It is strictly byte-preserving and cannot regenerate F16 or execute Q4 reconstruction.

The Q4 reconstruction authorization `9506e5fc...` remains untouched and unconsumed. M6 scientific execution remains closed.


## 2026-09-22 — F16 parent existing-byte attempt terminal / no source found

The bounded F16 parent attempt completed successfully at the orchestration layer
but found no exact serialized F16 bytes in the provenance-safe sources examined.

```text
classification:
F16_EXISTING_BYTES_NOT_FOUND

F16 parent admitted:
false

Q4 reconstruction executed:
false
```

The Q4 reconstruction authorization `9506e5fc...` remains unconsumed, but no
new reconstruction orchestration is admissible until exact frozen F16 bytes are
admitted.

M6 scientific execution remains closed.


## 2026-09-22 — Venue-independence amendment: GitHub persistence is not a research blocker

The previous GitHub-hosted recovery results remain valid for the exact source
sets inspected, but their downstream interpretation is amended.

```text
NOT FOUND IN GITHUB != GLOBALLY UNAVAILABLE
GITHUB ACTIONS != REQUIRED SCIENTIFIC VENUE
```

A qualified local Windows machine is an admissible authoritative M6 execution
venue.

M6 may proceed locally by first admitting an exact local Q4 or F16 binary. If
neither binary exists locally, a separate pre-outcome deterministic artifact
regeneration program may recreate F16/Q4 under the already frozen identities
without running model-quality fixtures or re-adjudicating F16/Q4 science.

Cross-OS executable hashes are venue-specific; exact source commit/build
contract/input/output identities remain the cross-venue invariants.

This amendment does not change any previous run result, hash, or scientific
verdict.

Next valid action: local-Windows M6 venue qualification / pre-outcome execution
package.

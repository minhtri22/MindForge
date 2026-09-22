# M6 F16 Parent Artifact Recovery / Materialization — Lineage

## 2026-09-22 — Program opened

Origin:

```text
blocked reconstruction closure:
9b2098e36275f7eecf44f9e3974d3afc5fb4e682

classification:
INVALID_PROVENANCE_F16_PARENT_UNAVAILABLE

reconstruction authorization:
9506e5fc205e641aba942a0bc9ff2fbaa7d881a5

reconstruction authorization consumed:
false
```

The program is bounded to acquiring an already-existing serialized F16 byte
object with the exact frozen identity.

It may later copy/download/extract/reassemble bytes, but may not execute the
HF-to-GGUF converter or otherwise regenerate F16.

F16 scientific state remains:

```text
PASS / CLOSED
```

The Q4 deterministic reconstruction authorization remains untouched and
unconsumed.

Next gate: implement recovery/materialization tooling and zero-science tests.


## 2026-09-22 — F16 existing-byte tooling zero-science PASS / implementation locked

Authoritative zero-science gate:

```text
implementation:
24768d87f9f22b820ac02e7428d40ea3df015bf7

run:
35678265391

job:
106589294845

tests:
14/14 PASS

planning artifact:
10673403827

artifact zip sha256:
cbb746488ff00c127911022c62dec6abd0d37dc7ea36ae967fe621332f1fabd9
```

The locked tooling supports only byte-preserving recovery/materialization modes:
existing-file copy, existing-object download, archive-member extraction, and
ordered chunk reassembly.

The zero-science gate proved:

```text
existing F16 bytes materialized = false
F16 regeneration executed = false
HF-to-GGUF conversion executed = false
llama-cli evaluation executed = false
fixture/model inference executed = false
scientific adjudication executed = false
Q4 reconstruction executed = false
Ollama create/chat executed = false
```

The deterministic Q4 reconstruction authorization
`9506e5fc205e641aba942a0bc9ff2fbaa7d881a5` remains byte-identical and
unconsumed.

F16 recovery/materialization execution is still not authorized. The next valid
gate is a separate one-attempt existing-byte materialization authorization.


## 2026-09-22 — One-attempt F16 existing-byte materialization authorized

The locked implementation and zero-science evidence are now bound into a separate execution authorization.

```text
implementation:
24768d87f9f22b820ac02e7428d40ea3df015bf7

lock / zero-science closure:
8055fdb382a0f6006ecd78ae0f4321e8e1516b8d

tests:
14/14 PASS
```

Exactly one future byte-preserving materialization attempt is authorized using copy, existing-object download, archive extraction, or ordered chunk reassembly.

F16 regeneration and HF-to-GGUF conversion remain forbidden. The deterministic Q4 reconstruction authorization `9506e5fc...` remains unconsumed and cannot execute inside the F16 materialization workflow.

No materialization is executed by this authorization commit.

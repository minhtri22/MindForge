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

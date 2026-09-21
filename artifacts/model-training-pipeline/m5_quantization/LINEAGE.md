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

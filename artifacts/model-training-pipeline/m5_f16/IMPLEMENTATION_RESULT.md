# M5 F16 Formal Closure — High-Fidelity llama.cpp Requalification

## Verdict

```text
M5_F16_STATUS: PASS / CLOSED
SCIENTIFIC_SHA: 2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719
AUTHORITATIVE_RUN: 35617920637
AUTHORITATIVE_JOB: 106393309234
RESULT_HASH: 0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57

F16_CONVERSION: PASS
REAL_LLAMA_CPP_INFERENCE: PASS
HF↔LLAMA_FROZEN_PARITY: PASS
REASONING_RUNTIME_MAPPING: PASS
QUANTIZATION_EXECUTED: NO
QUANTIZATION_QUALIFICATION_AUTHORIZED_TO_OPEN: YES
M6_AUTHORIZED: NO
BULK_TRAINING_AUTHORIZED: NO
```

This document formally closes only the high-fidelity F16 portion of M5.

## Qualified lineage

The frozen M5.1 decomposition identified the canonical tokenizer export fidelity
defect. M2 was repaired and requalified before F16 requalification.

The first local fallback lineage later exposed two infrastructure/runtime-invocation
defects without producing a scientific F16 outcome:

1. the HF prefetch helper was launched by script path and could not import the
   repository package;
2. the pinned llama.cpp CLI remained in its interactive loop after one generated
   response because the runtime invocation did not include `--single-turn`.

The latter was formally authorized as an INVALID_RUN_REPAIR and changed exactly
the process-exit contract of the llama.cpp runtime probe. No model, weight,
tokenizer, fixture, prompt, seed, inference parameter, threshold, parity rule,
llama.cpp revision, converter revision, or F16 dtype was changed.

Authorized repair:

```text
authorization:
aa8bac30448078490e563ae73bf08ee749245cb8

qualified scientific implementation:
2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719

runtime change:
+ --single-turn
```

## Authoritative execution

```text
workflow:
Model Pipeline M5 F16 Repair Requalification

run:
35617920637

job:
106393309234

conclusion:
success

evidence artifact:
m5-f16-repair-requalification
artifact id: 10647342952
artifact ZIP sha256:
0f5bab6b69361ef88c4fdefaf3608a1876d7033722e618ae702a36b4678029a5
```

The workflow passed foundation regressions, exact pinned llama.cpp checkout,
converter import verification, exact llama.cpp build, real F16 conversion,
real llama.cpp inference, the frozen HF↔llama task/format parity gate, and the
F16-only governance boundary.

## Frozen identities

```text
model:
Qwen/Qwen2.5-0.5B-Instruct

model revision:
7ae557604adf67be50417f59c2c2f167def9a775

llama.cpp:
ce8caa6e60a03093351d6016a818720e0d46f0fb

converter git blob:
e09616b190cf124e818d8a740468d4e84086015c

M2 canonical directory hash:
8be9a4984f89da07f2f9b23250a342edb1fa4d8dc07d6985579613026304b04c

M2 tokenizer manifest:
1567e178abe4f245846c6bd59e7e6f3b7e842fde92200ddfc74851559a402023
```

## F16 artifact

```text
topology:
single_file

file:
model-f16.gguf

size:
994156384 bytes

sha256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b

aggregate manifest hash:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8
```

## Required gates

All required F16 gates passed:

- M5.1 mechanism authorizes the bounded M2 repair;
- M2 PASS;
- canonical tokenizer source fidelity PASS;
- M2 tokenizer manifest equals the successful M5.1 pinned-source arm;
- exact llama.cpp lock PASS;
- Qwen2 converter capability PASS;
- real llama-cli binary PASS;
- F16 conversion PASS;
- real F16 inference PASS;
- frozen HF↔llama task/format parity PASS;
- reasoning runtime mapping PASS;
- quantization not executed;
- public bulk training not started.

There are no failed required gates.

## Non-blocking observation — parity ceiling / semantic limitation

The authoritative result contains:

```text
HF accuracy:        0.0
llama.cpp accuracy: 0.0

HF task vector:        [false, false]
llama.cpp task vector: [false, false]

format parity: true
parity gate:   PASS
```

This is **not** a contradiction and is **not** grounds to reopen or rewrite M5 F16.

The frozen M5 parity gate answers the preservation question:

> Did the high-fidelity llama.cpp runtime preserve the HF task/format behavior
> under the frozen fixture and inference contract?

It does not answer the absolute-capability question:

> Is the model sufficiently capable on this task set?

The gate can therefore PASS at `0% ↔ 0%`. In this execution, llama.cpp emitted
non-empty natural-language answers whose semantics include the expected answers,
while the fixture's strict exact-answer task rule still scored them false. The HF
baseline also produced the same false task vector, so preservation parity passed.

This limitation is recorded as:

```text
M5_F16_PARITY_ABSOLUTE_CAPABILITY_CEILING
severity: NON_BLOCKING
```

Scientific interpretation:

- M5 F16 PASS proves high-fidelity runtime preservation under the frozen contract.
- M5 F16 PASS does **not** prove absolute task capability.
- The observed ceiling must not be used to relax or retroactively change the M5
  adjudication rule.
- Any future absolute-capability benchmark redesign is a separate preregistered
  study, not an M5 rescue.

## Boundary after closure

M5 F16 closure changes exactly one downstream permission:

```text
Q8/Q4 qualification may now be opened.
```

It does **not** mean Q8 or Q4 has passed, and Q4 may not inherit F16 PASS.

The following remain closed:

```text
M6: CLOSED / NOT AUTHORIZED
bulk training: CLOSED / NOT AUTHORIZED
```

No automatic transition from M5 F16 PASS to M6 is allowed.

## Next program

Open a separately governed Q8_0 / Q4_K_M quantization qualification from this
closed F16 parent. Each quantized target requires its own artifact identity,
load/infer evidence, preservation/quality gate, and adjudication.

M6 may be considered only after a separate post-quantization governance decision.

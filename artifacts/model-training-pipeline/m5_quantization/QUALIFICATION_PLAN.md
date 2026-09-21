# M5Q — Quantized GGUF Qualification Plan

## Status

```text
PROGRAM: M5Q
STATE: OPEN / SPECIFICATION-ONLY
PARENT: M5 F16 PASS / CLOSED
PARENT RESULT HASH:
0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57

Q8_0: NOT EXECUTED
Q4_K_M: NOT EXECUTED

M6: CLOSED / NOT AUTHORIZED
BULK TRAINING: CLOSED / NOT AUTHORIZED
```

This program is opened only because the high-fidelity F16 parent is formally
closed PASS. It is a separate qualification program; no quantized target inherits
F16 PASS.

## Scientific question

For each frozen target, independently:

> Does quantizing the exact qualified F16 GGUF to the specified llama.cpp target
> preserve the qualified F16 runtime behavior under the same fixture and
> inference contract?

Targets:

```text
1. Q8_0
2. Q4_K_M
```

The program does not ask whether quantization improves model quality, and it
does not select a production target.

## Frozen parent

```text
model:
Qwen/Qwen2.5-0.5B-Instruct

revision:
7ae557604adf67be50417f59c2c2f167def9a775

scientific implementation:
2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719

M5 F16 closure:
9ff987ebd95cd23fef4cd2a0511774d772b14400

llama.cpp:
ce8caa6e60a03093351d6016a818720e0d46f0fb

F16 SHA256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b

F16 aggregate manifest:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8
```

A qualification run must regenerate or materialize an F16 source whose identity
matches the frozen parent before quantization begins. A mismatch is
`INVALID_PROVENANCE`; the target is not allowed to run.

## One-target-at-a-time execution

The qualification is intentionally sequential for traceability:

```text
frozen F16 parent
        ↓
Q8_0 implementation lock
        ↓
Q8_0 one-shot execution
        ↓
freeze Q8_0 evidence + adjudication
        ↓
Q4_K_M implementation lock
        ↓
Q4_K_M one-shot execution
        ↓
freeze Q4_K_M evidence + adjudication
        ↓
post-quantization governance review
```

No Q4 configuration may be changed after looking at Q8 outcome. The only
target-specific difference is the preregistered quantizer target.

A scientific Q8 FAIL does not authorize repair/tuning. Q4 may still execute
because it is an independent preregistered target, but it cannot be described as
a rescue for Q8.

## Frozen inference contract

```text
fixture:
tests/fixtures/eval_v1

max_new_tokens: 128
context_length: 2048
temperature: 0.0
top_p: 1.0
top_k: 0
seed: 42
threads: 2
llama-cli process mode: --single-turn
```

No target may receive target-specific prompting or generation parameters.

## Required gate set per target

Every target must independently prove:

1. exact F16 parent identity;
2. exact pinned llama.cpp identity;
3. exact quantizer target identity;
4. quantizer exit code 0;
5. non-empty quantized GGUF;
6. frozen artifact manifest/hash;
7. real llama-cli load and inference;
8. non-empty / format-valid runtime outputs;
9. task-vector equality to the frozen F16 parent;
10. accuracy equality to the frozen F16 parent;
11. format parity to the frozen F16 parent;
12. artifact-specific reasoning runtime mapping PASS;
13. artifact size smaller than the F16 parent.

No target can inherit another target's gate.

## Carried non-blocking observation

The F16 parent has:

```text
HF task vector:    [false, false]
F16 task vector:   [false, false]
HF accuracy:       0.0
F16 accuracy:      0.0
preservation gate: PASS
```

Therefore the current frozen fixture has a known semantic/ceiling limitation:
preservation can PASS at `0% ↔ 0%`.

This remains non-blocking because changing the parent metric after seeing the F16
outcome would be a retroactive redesign. M5Q must therefore preserve the parent
contract exactly and restrict its claim:

```text
allowed claim:
quantized runtime preserved the frozen F16 behavior

forbidden claim:
quantized runtime demonstrated useful absolute task capability
```

A future absolute-capability benchmark improvement must be a separate
preregistered study.

## Adjudication

Per target:

```text
PASS
FAIL_QUANTIZATION
FAIL_RUNTIME
FAIL_PRESERVATION
FAIL_REASONING_MAPPING
INVALID_PROVENANCE
INVALID_INFRASTRUCTURE
```

Scientific FAIL is terminal for that target. It may not be rerun with changed
settings to seek PASS.

Infrastructure-invalid runs may be repaired only at the infrastructure layer,
with unchanged scientific identity and a documented superseding run.

## Hard downstream boundary

Even if both Q8_0 and Q4_K_M PASS:

```text
M6_AUTHORIZED = FALSE
M6_AUTO_OPEN = FALSE
BULK_TRAINING_AUTHORIZED = FALSE
```

After both targets reach terminal adjudication, the only permitted next step is a
separate post-quantization governance review. That review may decide whether an
M6 qualification should be opened; M5Q itself cannot open or execute M6.

## Immediate next step

No quantization run is authorized by this specification alone.

The next valid action is:

```text
Q8_0 implementation
        ↓
tests
        ↓
exact implementation lock
        ↓
zero-science preflight
        ↓
one-shot Q8_0 execution
```

Q4_K_M remains unopened for execution until Q8_0 evidence is frozen.

# M5Q Q4_K_M — Formal Replication Execution Authorization

## Decision

```text
TARGET: Q4_K_M
EXECUTION CLASS:
FORMAL_REPLICATION_QUALIFICATION_UNDER_PRE_EXPOSURE_PREREGISTERED_CONTRACT

AUTHORIZATION:
EXACTLY ONE FORMAL SCIENTIFIC REPLICATION

SCIENTIFIC IMPLEMENTATION:
97d7dad329aa0196ead9005e631eebbeb8aa2163

IMPLEMENTATION LOCK:
87bc09f479c5fd6ba3e3ec3725d859ed5ad9feb1

ZERO-SCIENCE PREFLIGHT:
PASS
run 35641025835
```

This authorization permits exactly one target-specific Q4_K_M scientific
invocation under the already-frozen pre-exposure contract.

It does not itself execute Q4 and does not introduce an execution workflow.

## Why execution is now admissible

All required pre-execution gates are complete:

```text
implementation authorization: COMPLETE
target-specific implementation: COMPLETE
zero-outcome tests: PASS
exact implementation lock: LOCKED
lock-present zero-science preflight: PASS
```

The preflight proved all locked blobs match and dynamically verified that the
accidentally exposed Q4 outcome values are absent from the active Q4
implementation.

## Mandatory exposure disclosure

Prior out-of-protocol Q4 outcome exposure remains TRUE.

The future run therefore is not a blind first-look experiment. It is:

```text
FORMAL REPLICATION / QUALIFICATION
UNDER PRE-EXPOSURE PREREGISTERED CONTRACT
```

The accidental artifact hash, manifest, size, parity, outputs and PASS status
must not influence:

- code or configuration;
- thresholds;
- expected hash or size;
- expected PASS/FAIL;
- gate definitions;
- rerun decisions.

No strict Q4<Q8 gate may be introduced.

## Frozen execution identity

The run must use exactly:

```text
implementation:
97d7dad329aa0196ead9005e631eebbeb8aa2163

Q4 target:
Q4_K_M

model:
Qwen/Qwen2.5-0.5B-Instruct

model revision:
7ae557604adf67be50417f59c2c2f167def9a775

F16 parent SHA256:
437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b

F16 parent manifest:
eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8

llama.cpp:
ce8caa6e60a03093351d6016a818720e0d46f0fb

converter blob:
e09616b190cf124e818d8a740468d4e84086015c

fixture:
tests/fixtures/eval_v1

max_new_tokens: 128
temperature: 0
top_p: 1
top_k: 0
seed: 42
context_length: 2048
threads: 2
llama-cli: --single-turn
```

Comparator remains the qualified F16 parent and all 13 preregistered gates
remain unchanged.

## One-run rule

Only one formal Q4 scientific invocation is authorized.

Once the target-specific scientific invocation begins, the authorization is
consumed for scientific purposes. Its emitted result must be adjudicated as-is.

A scientific FAIL is terminal and must not be rerun to seek PASS.

An infrastructure/orchestration failure that occurs before scientific invocation
starts does not constitute a Q4 scientific result. If failure occurs after the
scientific invocation starts, evidence must establish whether an adjudication
artifact exists before any further governance decision.

## Downstream boundary

Even a Q4 PASS does not authorize M6.

```text
Q8 rerun = NOT AUTHORIZED
M6 = CLOSED / NOT AUTHORIZED
M6 auto-open = FALSE
bulk training = CLOSED / NOT AUTHORIZED
```

After Q4 terminates, its evidence must first be frozen and formally adjudicated.
Only then may a separate post-quantization governance review be opened.

## Next action

This commit contains no execution workflow and starts no scientific run.

The next valid action is to create bounded Q4 execution orchestration that is
cryptographically/provenance-bound to this authorization and the exact locked
implementation, then perform the single authorized formal replication.

# M6 Parent Artifact — Recovery-Only Execution Authorization

## Decision

```text
PROGRAM:
M6_PARENT_ARTIFACT_MATERIALIZATION

IMPLEMENTATION:
a6f9d4341894cf59cab853d4ae6912e060c10599

ZERO-SCIENCE CLOSURE:
94c9300fa6c9c7df38b271a8295a69ef40572a6a

AUTHORIZATION:
ONE RECOVERY ATTEMPT ONLY
```

This authorization permits execution of the **recovery-first** stage only.

It does not authorize deterministic reconstruction and does not authorize the
Q4 quantizer.

## Frozen Q4 target

```text
file:
model-q4_k_m.gguf

size:
397807456

sha256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977

aggregate manifest:
e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b

Q4 scientific status:
PASS / CLOSED
```

Admission requires exact byte identity before and after persistence.

## Authorized recovery sources

One bounded recovery attempt may inspect/materialize an already-existing copy
from an explicit provenance-safe source, including:

- a user-supplied/local file made available to the execution venue;
- an existing persistent binary store;
- an existing repository/workflow binary artifact if one is subsequently
  located.

Every candidate requires an explicit source reference and exact identity
verification.

## Recovery outcomes

Valid terminal outcomes for this authorization are:

```text
ADMITTED_EXISTING_BYTES
NOT_FOUND_RECOVERY_EXHAUSTED
INVALID_PROVENANCE
INVALID_INFRASTRUCTURE
```

None of these outcomes changes the closed Q4 scientific verdict.

## Reconstruction remains closed

The frozen F16 identity and Q4_K_M reconstruction contract are recorded only so
a future authorization can bind to them.

This authorization explicitly sets:

```text
reconstruction execution = NOT AUTHORIZED
llama-quantize execution  = NOT AUTHORIZED
```

If the actual recovery execution terminates as
`NOT_FOUND_RECOVERY_EXHAUSTED`, that result must first be frozen as evidence.

Only after that evidence exists may a **separate deterministic reconstruction
authorization** be opened.

Recovery exhaustion must never implicitly fall through to quantization in the
same workflow.

## Scientific boundary

Still forbidden:

```text
Q4 scientific rerun
Q4 fixture evaluation
llama-cli evaluation
model inference
new Q4 scientific result
Q4 re-adjudication
M5Q reopening
ollama create/chat
M6 scientific execution
M6 PASS claim
M7
bulk training
```

## Next action

Create a recovery-only orchestration cryptographically bound to this
authorization, execute exactly one recovery attempt, and freeze its outcome.

Do not add deterministic reconstruction to that orchestration.

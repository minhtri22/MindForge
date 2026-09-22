# M6 — Bounded Specification + Implementation Authorization

## Status

```text
M5 / M5Q: PASS / CLOSED

M6:
SPECIFICATION = AUTHORIZED
IMPLEMENTATION = AUTHORIZED
ZERO-RUNTIME TESTS = AUTHORIZED

OLLAMA EXECUTABLE INVOCATION = NOT AUTHORIZED
OLLAMA CREATE = NOT AUTHORIZED
OLLAMA RUN/CHAT = NOT AUTHORIZED
OLLAMA PULL/RM/SERVE = NOT AUTHORIZED
OLLAMA INSTALL/UPDATE = NOT AUTHORIZED

M6 SCIENTIFIC QUALIFICATION = NOT AUTHORIZED
M6 PASS CLAIM = NOT AUTHORIZED
M7 = CLOSED
BULK TRAINING = CLOSED
```

This program starts from the post-quantization governance review commit:

```text
7bcacfa8fb291a9a55e2acf19077c8e61f33c329
```

and is a new milestone branch:

```text
research/model-pipeline-m6-ollama
```

## Purpose

M6 owns the Ollama work that M5 intentionally did not claim:

- deterministic Modelfile generation;
- exact Ollama runtime pinning;
- safe ephemeral model ownership/cleanup;
- real Ollama chat qualification;
- reasoning/think mapping;
- completion of the Ollama leg of cross-runtime parity.

This authorization opens only specification, implementation and zero-runtime
testing. It does not authorize runtime execution.

## Parent artifact

The canonical smoke packaging target is Q4_K_M because the frozen
`end_to_end_small.yaml` already declares `q4_k_m` as its quantized smoke
target.

This is configuration continuity, **not** a claim that Q4_K_M is the preferred
production quantization.

Frozen Q4 identity:

```text
result hash:
da5e1bcb6b542c0dbecbabfb26f79cd1f986d49546181bede2779693426570ef

artifact SHA256:
ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977

aggregate manifest:
e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b
```

M5Q PASS does not become M6 PASS.

## Ollama lock

M6 must create:

```text
docs/model-training-pipeline/runtime/ollama.lock.json
```

before any runtime execution.

The lock must freeze an exact Ollama version/release identity and checksum or
equivalent authoritative release identity when available.

During the current stage the implementation is forbidden from:

```text
ollama --version
ollama create
ollama run
ollama chat
ollama pull
ollama rm
ollama serve
installation/update
```

The exact lock is a specification artifact first; runtime verification belongs
to a later separately authorized execution stage.

## Modelfile contract

Generated Modelfile content must be deterministic and derived from the frozen
inference contract.

It may not silently introduce independent temperature/top_p or other generation
defaults.

The generated Modelfile hash must be frozen before runtime execution.

## Namespace and cleanup

The canonical ephemeral name pattern is:

```text
pipeline-test-<run_id>-<artifact_hash_prefix>
```

Before future model creation the runtime path must prove either that the name is
absent or that it is already owned by the current run.

Implementation must make it impossible for cleanup to delete an unrelated user
model.

Ownership and cleanup decisions must be represented in a runtime manifest.

## Reasoning mapping

M6 may implement Ollama-specific reasoning/think mapping, but the mapping must be
deterministic and preregistered before runtime.

Raw transport/parser evidence remains required.

No generated-reasoning quality claim is opened by this milestone.

## Parity contract

Future M6 runtime qualification must complete the missing Ollama leg of the
existing normalized inference contract.

Comparator semantics remain task/format behavior, not exact output text.

The inherited limitation remains:

```text
frozen parent task vector = [false, false]
frozen parent accuracy = 0.0
```

Therefore an eventual Ollama parity PASS is not proof of useful absolute task
capability.

## Authorized implementation surface

M6 may create:

```text
artifacts/model-training-pipeline/m6/**
docs/model-training-pipeline/runtime/ollama.lock.json
pipeline/m6.py
tools/m6_ollama_preflight.py
tools/m6_ollama_qualification.py
tests/test_model_pipeline_m6.py
.github/workflows/model-pipeline-m6-preflight.yml
```

M5/M5Q scientific code and evidence remain protected.

## Zero-runtime tests

Tests may exercise pure functions, filesystem fixtures, deterministic Modelfile
rendering, command construction, namespace ownership logic, parity comparison
and mocked subprocess boundaries.

They may **not** invoke an Ollama executable.

Required tests include:

- exact lock contract;
- deterministic Modelfile bytes;
- frozen inference parameter mapping;
- frozen Q4 identity verification;
- namespace determinism/collision safety;
- cleanup refusal for unowned names;
- no pull/install/update command in qualification path;
- reasoning mapping determinism;
- frozen parity comparator;
- hard M7/bulk boundary;
- zero-runtime preflight isolation.

## Gate sequence

```text
M6 specification
        ↓
M6 implementation
        ↓
zero-runtime tests
        ↓
tests PASS
        ↓
exact implementation lock
        ↓
lock-present zero-science / zero-runtime preflight
        ↓
SEPARATE runtime execution authorization
        ↓
only then may Ollama commands run
```

No runtime command is authorized by this document.

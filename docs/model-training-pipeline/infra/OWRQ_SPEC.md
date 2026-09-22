# OWRQ — Ollama Windows Runtime Qualification

**Program type:** NON-SCIENTIFIC INFRASTRUCTURE QUALIFICATION  
**Status:** SPECIFICATION ONLY  
**Parent governance:** `750d6358a88e738cfaf971b3a5db3192f7622889`

## 1. Purpose

OWRQ qualifies a reusable Ollama runtime-adapter/substrate scope for future MindForge studies.

It does not test model quality, parity, reasoning quality, or any research hypothesis.

Its first qualification target is the runtime-launch conflict identified by M6R RFD-C1:

```
--cache-type-v q4_0
+
--flash-attn off
→ llama_init_from_model abort
```

The qualification target is the repaired runtime configuration, not the M6R outcome.

## 2. Reuse objective

A successful OWRQ result produces one reusable artifact:

`QUALIFIED_RUNTIME_SCOPE`

Future studies do not repeat OWRQ while the scope tuple remains exact-equal. They perform one cheap `INFRA_BINDING_CHECK`.

## 3. Scientific firewall

OWRQ must not:
- read or execute `tests/fixtures/eval_v1`;
- compare against llama.cpp task vector/accuracy/format;
- evaluate model answer quality;
- evaluate reasoning semantics;
- use M6R scientific outcomes as a PASS criterion;
- change or reinterpret M6/M6R/RFD verdicts;
- authorize M6R2 science;
- open M7 or bulk training.

A runtime fixture may exercise model load and one plumbing response, but its output is only a liveness/transport signal and must not be scored for scientific content.

## 4. Exact runtime family

Primary target:
- OS: target local Windows research machine;
- installed Ollama family: `0.34.2`;
- executable must come from the installed Ollama path;
- system/user Ollama configuration must not be mutated globally;
- existing service on `127.0.0.1:11434` must not be stopped, restarted, replaced, or reconfigured.

OWRQ uses a dedicated process-scoped qualification server on:

`127.0.0.1:11468`

using the exact installed `ollama.exe`.

## 5. Process-scoped repair

Qualification server environment:

```
OLLAMA_HOST=127.0.0.1:11468
OLLAMA_KV_CACHE_TYPE=f16
```

OWRQ must **not** set `OLLAMA_FLASH_ATTENTION`.

Therefore the repair is exactly:
- remove quantized KV-cache from the incompatible launch state;
- use the documented/default fidelity class `f16`;
- leave flash-attention resolution to the runtime/backend.

No global/user/machine environment mutation is allowed.

## 6. Fixture rule

OWRQ uses an already-local, non-study model fixture.

Preferred first fixture if present:

`llama3.2:1b`

Rules:
- no `ollama pull`;
- no model create;
- no model delete;
- fixture must already exist before qualification;
- its exact local model identity/digest is captured into the qualification evidence;
- if absent, OWRQ returns `UNRESOLVED_INFRA_FIXTURE`; it does not fetch a replacement automatically.

The fixture exists only to force llama-server launch under the qualification environment.

## 7. Required evidence

Evidence creation begins before runtime invocation.

Required durable records:

1. repository HEAD + adapter blob identity;
2. OS build + machine fingerprint scope;
3. installed Ollama version + executable SHA256;
4. preexisting service state on port 11434;
5. qualification port 11468 availability;
6. process-scoped environment;
7. fixture name + resolved local digest/manifest identity;
8. qualification server stdout/stderr;
9. exact llama-server child launch line or equivalent authoritative runtime evidence;
10. evidence that V-cache is `f16` or non-quantized;
11. evidence that `--cache-type-v q4_0` is absent;
12. observed flash-attention resolution, without forcing it;
13. model-load/liveness result;
14. process cleanup;
15. proof that port 11434 service and user model set were not mutated;
16. evidence manifest hashes.

## 8. Qualification gates

OWRQ uses one consolidated qualification result rather than a chain of micro-gates.

`QUALIFIED_RUNTIME_SCOPE` requires all of:

- exact installed Ollama 0.34.2 identity PASS;
- dedicated qualification server starts on 11468;
- process-scoped `OLLAMA_KV_CACHE_TYPE=f16` is effective;
- child llama-server command/evidence contains no quantized V-cache conflict;
- model fixture loads;
- one non-study plumbing request completes;
- no global config mutation;
- no port-11434 service mutation;
- no user model mutation;
- evidence completeness/integrity PASS.

Otherwise:
- valid infra defect → `FAIL_INFRA`;
- missing fixture/capability/evidence → `UNRESOLVED_INFRA`.

Neither result changes a scientific verdict.

## 9. Retry / repair semantics

OWRQ is infrastructure, not science.

A failed qualification package may be repaired and versioned when:
- the repair changes only infrastructure implementation/configuration;
- no scientific artifact/fixture/threshold/endpoint is introduced;
- the repaired package gets static QA;
- every local qualification attempt has a unique evidence directory.

There is no retry-until-scientific-PASS issue because no scientific endpoint is measured.

A valid `FAIL_INFRA` is terminal for that exact OWRQ package version.

## 10. Scope tuple

A successful qualification freezes:

```
OS build / machine scope
installed Ollama version
ollama.exe SHA256
runtime-adapter blob
qualification environment contract
observed backend/flash-attention resolution
fixture identity
API contract
```

Future studies may bind only if required scope keys match.

## 11. M6R2 relationship

OWRQ does not block M6R2 specification, static implementation, or QA.

It blocks only M6R2 runtime execution.

M6R2 later consumes OWRQ through one `INFRA_BINDING_CHECK`; it does not rerun OWRQ.

## 12. Next step

After spec QA:
- implement one evidence-first OWRQ runner;
- static/failure-injection QA;
- perform local non-scientific qualification;
- formal-close with `QUALIFIED_RUNTIME_SCOPE`, `FAIL_INFRA`, or `UNRESOLVED_INFRA`.

No M6R2 inference is authorized here.

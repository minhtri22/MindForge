# M6R2 — Fresh Ollama Parity Replication

**Program:** M6R2_PARITY_REPLICATION  
**Status:** SPECIFICATION / PREREGISTRATION ONLY  
**Scientific execution:** NOT AUTHORIZED  
**Parent governance:** `750d6358a88e738cfaf971b3a5db3192f7622889`

## 1. Reframed question

M6R2 is not a test of Ollama installation, PowerShell process capture, KV-cache configuration, or Windows service management.

Those belong to the separate OWRQ infrastructure lane.

M6R2 asks only:

> Given the exact admitted Q4 artifact and a runtime that is already bound to a qualified Ollama infrastructure scope, does the Ollama packaged target reproduce the frozen llama.cpp parent behavior under the frozen parity and reasoning contracts?

This is a fresh parity replication.

## 2. Historical evidence retained

Historical outcomes are immutable:

```
M6   = FAIL_PACKAGE / CLOSED
M6R  = FAIL_RUNTIME / CLOSED
RFD-C1 = ROOT_CAUSE_IDENTIFIED / CLOSED
```

RFD-C1 established that M6R failed because the runtime launched llama-server with an incompatible quantized V-cache / flash-attention configuration.

That finding motivates infrastructure repair in OWRQ. It is **not** an M6R2 scientific treatment.

## 3. No-treatment replication

M6R2 contains no scientific intervention relative to the intended M6R parity question.

Frozen study identity:

- Q4 filename: `model-q4_k_m.gguf`
- Q4 bytes: `397807456`
- Q4 SHA256: `ca9ac3104fa025619f34eaf941f4bac95787cc4aba2818d3e972766bc02cb977`
- aggregate manifest: `e47700cab51bcf82174aa437ed767032f7ff29e3e1594690f5b9ff91e4762e0b`
- Modelfile SHA256: `5db25cbceaaa6b359b73f7edde1f54acb6a95f27a4803f5d28ad1b65012e1946`
- fixture set: `tests/fixtures/eval_v1`
- fixture manifest blob: `450d83d38130765fe4a74fb18bab90177328218f`
- reference profile blob: `1214e551c250e73b7a8cbbde71201fdd17e49ae1`
- reasoning implementation blob: `3813ae3ff00a49f2f97ccbda7833e0bf299ff1e4`

Frozen generation contract:

```
num_ctx       2048
num_predict   128
temperature   0
top_p         1
top_k         0
seed          42
stream        false
```

Frozen llama.cpp parent:

```
task vector   [false, false]
accuracy      0
```

Exact text equality is not required.

## 4. Infrastructure boundary

M6R2 does not qualify Ollama.

Before runtime execution it performs exactly one consolidated `INFRA_BINDING_CHECK`.

The binding must point to a formally qualified OWRQ artifact and verify only the required scope keys:

```
OWRQ qualification identity
local-machine scope
Ollama version
ollama.exe hash
runtime-adapter blob
runtime environment contract
backend/flash-attention resolution scope
API contract
```

If binding fails:
- M6R2 execution is unavailable;
- no scientific FAIL is recorded;
- no M6R2 scientific attempt is consumed;
- work returns to OWRQ.

No repeated OWRQ qualification is allowed when the exact qualified scope still matches.

## 5. Setup is not science

The following are infrastructure/setup operations:

- system-runtime health check;
- exact infra binding;
- ephemeral namespace collision check;
- package directory creation;
- exact Q4 copy/hash verification;
- frozen Modelfile materialization;
- `ollama create`;
- `/api/show` metadata check;
- owned-artifact cleanup;
- evidence capture for those operations.

Failure in these stages is:

`BLOCKED_OR_INVALID_INFRA_PREOUTCOME`

It is not `FAIL_PARITY`.

It does not consume the M6R2 scientific attempt.

## 6. Scientific outcome boundary

The scientific/evidence boundary begins only when the first frozen `eval_v1` task is submitted to the bound Ollama runtime.

Attempt accounting is based on **outcome exposure**, not merely process startup.

### No scientific outcome exposed

If the first eval request produces no valid model response and positive evidence identifies an infrastructure invariant failure:

- classify `INVALID_INFRA_PREOUTCOME`;
- scientific attempts consumed = 0;
- exact-unchanged M6R2 may execute later after infrastructure is independently repaired/requalified.

No science parameter may change.

### Scientific outcome exposed

The first valid response content from an `eval_v1` task consumes the one M6R2 scientific attempt.

After that point:
- no selective rerun;
- no fixture/parameter/comparator change;
- no threshold change;
- no retry to seek parity PASS.

If infrastructure fails after partial outcome exposure, classify `INVALID_INFRA_POSTOUTCOME`; the attempt remains consumed and M6R2 is terminal without a new fresh program.

## 7. Scientific endpoints

Required evidence endpoints:

1. all frozen eval outputs are non-empty;
2. task vector equals frozen llama.cpp parent;
3. runtime accuracy equals frozen llama.cpp parent;
4. format parity equals frozen llama.cpp parent;
5. reasoning runtime mapping passes the frozen contract;
6. unexpected non-empty native Ollama `thinking` field is failure.

These are the only M6R2 parity/reasoning outcome gates.

## 8. Verdict classes

Scientific/evidence verdicts:

- `PASS_PARITY`
- `FAIL_PARITY`
- `FAIL_REASONING_MAPPING`

Infrastructure states:

- `BLOCKED_INFRA_BINDING`
- `INVALID_INFRA_PREOUTCOME`
- `INVALID_INFRA_POSTOUTCOME`
- `INVALID_PROVENANCE`

Infrastructure states do not count as scientific FAIL.

## 9. Gate consolidation

M6R2 uses four governance stages only:

```
S0  specification + adversarial QA
S1  static implementation + zero-science QA
S2  one consolidated OWRQ binding check
S3  one fresh outcome execution + adjudication
```

No separate user-facing gate is required for package/create/chat plumbing steps inside the already-qualified infrastructure scope.

S2 is performed immediately before S3 and can be part of the same one-click local package.

## 10. OWRQ independence

Current OWRQ specification lineage may evolve independently on:

`infra/ollama-windows-runtime-qualification`

M6R2 design and static implementation are not blocked while OWRQ is unfinished.

Only S3 runtime execution waits for a qualified OWRQ binding.

## 11. Anti-rescue invariants

Forbidden after M6R2 outcome exposure:

- changing Q4 bytes;
- rebuilding/requantizing Q4;
- changing Modelfile semantics;
- changing eval_v1;
- changing generation parameters;
- changing parent comparator;
- changing parity criteria;
- changing reasoning mapping;
- enabling flash-attention to rescue an observed outcome;
- changing KV-cache policy as a study treatment;
- selective task rerun;
- resetting outcome-exposure state.

## 12. Downstream

M6R2 PASS does not rewrite M6 or M6R.

M6R2 PASS may satisfy the Ollama parity evidence dependency for later product/release work, subject to normal downstream contracts.

This specification does not authorize:
- M6R2 implementation;
- M6R2 execution;
- M7;
- bulk training.

## 13. Next step

After this specification passes adversarial QA:

`M6R2 S1 — static implementation + zero-science QA`

Implementation may be completed before OWRQ local qualification finishes.

Runtime execution remains blocked only at S2.

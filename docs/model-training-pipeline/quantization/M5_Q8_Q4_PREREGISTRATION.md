# M5-Q — Q8_0 / Q4_K_M Quantization Qualification Preregistration

## Status

OPEN — specification and zero-outcome implementation authorization only.

Parent M5 F16 is formally closed PASS. This program is a separate qualification
of two quantized GGUF targets. It does not reopen M5 F16, authorize M6, or
authorize bulk training.

## Frozen parent

- F16 closure evidence: `artifacts/model-training-pipeline/m5_f16/M5_F16_QUALIFICATION_EVIDENCE.json`
- qualified F16 scientific commit: `2cb3cb6d1fbaa2230bc8b8d8bdf6dcdc51f4c719`
- F16 result hash: `0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57`
- F16 GGUF SHA256: `437c300945705b9a255322366eab3017e890ac6d997716eb7d1351b2e76f4d4b`
- F16 aggregate manifest hash: `eb1113def8177252743eb462aa06d24925387f6c5544f27a115850bc6f0efbb8`
- M2 canonical directory hash: `8be9a4984f89da07f2f9b23250a342edb1fa4d8dc07d6985579613026304b04c`
- tokenizer manifest hash: `1567e178abe4f245846c6bd59e7e6f3b7e842fde92200ddfc74851559a402023`

No quantizer may run until the regenerated F16 artifact matches the frozen
parent identity exactly.

## Frozen targets

Targets are independent children of the same F16 parent:

1. `q8_0` using llama.cpp mode `Q8_0`
2. `q4_k_m` using llama.cpp mode `Q4_K_M`

Q4 is never derived from Q8. Both are quantized directly from the same verified
F16 file.

The order is an execution order only and is not a ranking.

## Runtime lock

The existing llama.cpp lock remains frozen:

- llama.cpp commit: `ce8caa6e60a03093351d6016a818720e0d46f0fb`
- converter git blob: `e09616b190cf124e818d8a740468d4e84086015c`
- high-fidelity parent: F16
- real `llama-cli` inference required
- real `llama-quantize` invocation required

No runtime revision, model revision, fixture, prompt, seed, inference parameter,
task-success rule, or parity rule may change inside this qualification.

## Required gates

The one-shot adjudicator MUST require all of the following:

1. parent F16 closure is PASS and explicitly permits quantization to open;
2. M6 and bulk training remain unauthorized at parent entry;
3. exact llama.cpp / converter lock PASS;
4. regenerated M2 canonical directory hash equals the frozen F16 parent;
5. regenerated tokenizer manifest equals the frozen F16 parent;
6. regenerated F16 file SHA256, size, and aggregate manifest hash equal the
   frozen F16 parent BEFORE any quantizer invocation;
7. real F16 llama.cpp inference remains non-empty and frozen HF↔llama parity
   remains PASS;
8. Q8_0 quantizer invocation succeeds and emits a non-empty artifact;
9. Q8_0 real llama.cpp inference is non-empty;
10. Q8_0 preserves the frozen HF task/format parity contract;
11. Q4_K_M quantizer invocation succeeds and emits a non-empty artifact;
12. Q4_K_M real llama.cpp inference is non-empty;
13. Q4_K_M preserves the frozen HF task/format parity contract;
14. compression ordering is strict: `Q4_K_M size < Q8_0 size < F16 size`;
15. Q8_0 and Q4_K_M artifact hashes are distinct from each other and from F16;
16. public bulk training is not started;
17. M6 remains unauthorized in the result.

Any failed required gate makes the overall qualification FAIL. A genuine FAIL
must not be retried with changed modes, thresholds, prompts, fixtures, seeds, or
runtime revisions.

## Explicit parity limitation

The frozen F16 parent recorded `HF accuracy = 0` and `llama.cpp accuracy = 0`
while preservation parity passed. This program inherits that limitation.

Therefore a PASS here means only:

- exact parent identity was preserved before quantization;
- the requested quantization mode produced a loadable artifact;
- real llama.cpp inference executed;
- the frozen task/format preservation contract did not drift;
- the artifact achieved the required compression ordering.

A PASS MUST NOT be cited as proof of useful absolute task capability, semantic
quality, or benchmark superiority of Q8_0 or Q4_K_M.

Any future absolute-capability or quality-loss study requires a separate
preregistered benchmark with independently justified metrics.

## Falsification / no-rescue rules

- Parent F16 mismatch => STOP before quantization.
- A target quantizer/runtime/parity failure => record FAIL as-is.
- No post-hoc threshold creation.
- No target substitution.
- No fallback to another llama.cpp revision.
- No model change.
- No Q4-from-Q8 chain.
- No automatic M6 transition.

## Boundary after adjudication

If both Q8_0 and Q4_K_M PASS, the only newly permitted action is a separate
post-quantization governance decision selecting which artifact(s), if any, may
enter later integration work.

M6 remains CLOSED until that separate decision.

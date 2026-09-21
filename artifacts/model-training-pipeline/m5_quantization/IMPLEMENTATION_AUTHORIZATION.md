# M5-Q — Q8_0 / Q4_K_M Implementation Authorization

## Status

AUTHORIZED — one frozen execution only.

This authorization opens exactly one Q8_0 / Q4_K_M quantization qualification
from the already closed M5 F16 parent. It does not authorize M6 or bulk training.

## Frozen implementation package

- package candidate: `f3b6aaf030cb3c935ade7be878363266b4bd7ea1`
- scientific core: `8cf9147b7cfa83e15b9a72efc9a0aa95f280ab1f`
- preregistration: `0d1de0f5dac97eeaea0312254db03d7a42c8c0e3`
- frozen target config: `8ba2cb856b4f133a548deec24f63c49f1efd5bca`

The package contains:

- frozen Q8_0 / Q4_K_M preregistration and lock;
- a config differing from the closed F16 config only by
  `quantize: [q8_0, q4_k_m]`;
- a parent-identity guard executed before any quantizer invocation;
- independent Q8_0 and Q4_K_M children of the same F16 parent;
- one-shot quantization harness;
- zero-outcome contract tests;
- a marker-gated GitHub Actions workflow.

## Zero-outcome QA

PASS.

Static and provenance checks established:

- base model revision unchanged;
- llama.cpp lock unchanged;
- converter lock unchanged;
- M5.1 evidence unchanged;
- closed M5 F16 evidence unchanged;
- dependency lock unchanged;
- quantization config differs from base config at exactly one line;
- after the core commit, only harness/test/workflow files changed;
- M6 remains closed;
- bulk training remains closed.

Exact-core F16 regression:

- workflow: `Model Pipeline M5 F16 Repair Requalification`
- run: `35631247719`
- job: `106437702569`
- head: `8cf9147b7cfa83e15b9a72efc9a0aa95f280ab1f`
- conclusion: `success`

All F16 regression steps passed, including the real F16 llama.cpp requalification
and the F16-only governance boundary.

## Execution authorization

Exactly one marker-triggered execution is authorized with:

- parent F16 result hash:
  `0f76c8b2a420a629927f758fc6bc21b4c92c08b052ee7b76e49eef9161dd3e57`
- targets in order: `q8_0`, `q4_k_m`
- source for both targets: the same exact regenerated F16 parent;
- llama.cpp commit:
  `ce8caa6e60a03093351d6016a818720e0d46f0fb`

The workflow MUST stop before quantization if the regenerated F16 artifact does
not exactly match the frozen parent size, SHA256, and aggregate manifest hash.

A genuine PASS or FAIL is terminal for this frozen execution. No threshold,
prompt, seed, target, runtime revision, or model change is allowed as rescue.

## Boundary

Even if both quantized targets PASS:

- M6 remains CLOSED;
- bulk training remains CLOSED;
- no absolute-capability claim is authorized;
- only a separate post-quantization governance decision may open next work.


## Bounded adjudicator repair and exact replay authorization

Prior execution:

- run: `35632404520`
- job: `106441521839`
- head: `58ba71b22140ef8b89e28d38804e268feecbf347`
- classification: `INVALID_ADJUDICATOR / SCIENTIFIC_OUTCOME_UNADJUDICATED`
- failure point: wrapper post-serialization target-key ordering guard
- observed keys: `q4_k_m, q8_0`
- frozen execution order: `q8_0, q4_k_m`

Mechanism:

`pipeline.io.atomic_write_json()` canonicalizes JSON with `sort_keys=True`.
The wrapper incorrectly treated serialized mapping key order as scientific target
order. The pre-execution config-order guard remains unchanged and still enforces
`q8_0 -> q4_k_m`.

Repair authorization:

- repair-governance commit:
  `3e9167e48977566ed2e40985fe4f4567215f9f64`
- repaired scientific candidate:
  `72d71edc87703bada5e7f766d62a1bfd59eb7923`
- allowed semantic change: post-serialization exact target membership only;
- regression coverage: canonical sorted order accepted; missing, extra and
  non-mapping forms rejected.

Exactly one exact replay is authorized from this repaired candidate. All frozen
model, parent, target, threshold, seed, prompt, llama.cpp, converter and runtime
contracts remain unchanged. A genuine PASS or FAIL from the repaired
adjudicator is terminal.

M6 remains CLOSED. Bulk training remains CLOSED.

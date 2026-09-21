# M5-Q Adjudicator Repair Authorization

## Status

AUTHORIZED — bounded technical repair only.

Run `35632404520` is classified **INVALID_ADJUDICATOR / SCIENTIFIC_OUTCOME_UNADJUDICATED**.

The frozen Q8_0 / Q4_K_M execution reached and returned from
`run_m5_qualification()`. The wrapper then rejected the serialized
`quantized_targets` mapping because it compared JSON key iteration order to the
frozen execution order. Canonical JSON serialization uses `sort_keys=True`, so
the mapping is serialized as `q4_k_m, q8_0` although the frozen execution order
remains `q8_0, q4_k_m`.

## Allowed repair

Exactly these semantic changes are authorized:

- keep the pre-execution config-order guard unchanged and order-sensitive;
- change only the post-serialization adjudicated-target guard to require exact
  membership: both `q8_0` and `q4_k_m`, with no missing or extra target;
- add regression tests proving canonical key sorting cannot create false drift;
- preserve every model, revision, F16 parent identity, quantization target,
  threshold, prompt, seed, llama.cpp lock, converter lock, runtime contract and
  governance boundary.

## Replay rule

After the bounded repair passes zero-outcome QA, exactly one replay of the same
frozen Q8_0 / Q4_K_M program is authorized solely because the prior invocation
failed in the wrapper after scientific execution and did not emit the required
qualification result artifact.

A genuine PASS or FAIL from the repaired adjudicator is terminal. No rescue
tuning is authorized.

M6 and bulk training remain CLOSED.

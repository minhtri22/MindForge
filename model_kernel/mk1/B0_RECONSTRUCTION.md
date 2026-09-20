# MK-1 B0 Reconstruction v0.1

Status: **PASS**

Date: **2026-09-21**

Formal verdict:

`B0_RECONSTRUCTION_PASS`

## 1. Scope

This is a zero-science compatibility gate. It does not train MK-1, materialize MK-1 data, or produce a scientific outcome.

The reconstruction validates the exact B0 model/runtime/checkpoint compatibility on the active `research/model_core` branch before any MK-1 implementation lock.

## 2. Execution

Canonical valid workflow run:

`35526336632`

Execution head:

`6f54872d0825f07a3394747576c537ca447c999b`

Workflow:

`.github/workflows/mk1-b0-reconstruction.yml`

Artifact:

- name: `mk1-b0-reconstruction`
- id: `10609797460`
- ZIP SHA-256: `e2a87f0871c8b8c6a55493f8b186221d0dd41705aac4eb70be1bf2a5e82ca632`

## 3. Execution repair record

First workflow run:

`35526242084`

ended before reconstruction because pytest could not import the local `mindforge` package in the GitHub Actions environment.

Failure:

`ModuleNotFoundError: No module named 'mindforge'`

No B0 reconstruction result, checkpoint replay, artifact, or scientific output was produced by that run.

Repair commit:

`6f54872d0825f07a3394747576c537ca447c999b`

Repair:

`PYTHONPATH=.`

No model code, checkpoint, target, metric, threshold, seed, or scientific contract changed.

## 4. Exact B0 source identity at canonical execution

Git blobs already frozen in BASELINE_CONTRACT.md remain unchanged for the model definition:

- `mindforge/config.py`: `91a3f92ea2449a82fb2d03e0442cbf6e72980caf`
- `mindforge/model.py`: `98b4368c2b594082f0b84cd010e2bcc3548ab3fc`

Canonical execution SHA-256 values:

- `mindforge/config.py`: `95e784b83bab57e0618aa52e0c826204609c1ae2d80a6ab47f4cf2b4c4d96169`
- `mindforge/model.py`: `438dbe1f4438ac211655eb6bcbb042f7413e94edcd50d94b526115783918397b`
- `mindforge/model_contract.py`: `d651b304366dcc9c6e512e9e77cb6881a0e8613c861e532997bcda99aa919545`
- `mindforge/checkpoint.py`: `730eea9e68a32a3ad68ada88f8fecc2ca3c3a07b90b3c002362a64658709fd36`
- `mindforge/evaluate.py`: `412c904af2f1c0865e87d4e25ff9dfd70769a41430a161aa949c26a921c45095`
- `mindforge/generate.py`: `14744409ed200820e2afa81e9fdb83cd66bb9208f12c0746490fe02e944529d7`
- `tests/test_mks_model_kernel.py`: `9b075dcc9ef5e6fe9717de4278d3eecf1e482e203d317b9a094c3cce16178de9`

## 5. B0 configuration and parameter count

Reconstructed default configuration:

- vocab_size = 16,384
- d_model = 320
- n_heads = 8
- n_layers = 4
- max_context = 512
- ff_mult = 4
- dropout = 0.0

Observed parameter count:

`10,339,200`

Expected:

`10,339,200`

Result:

**PASS**

The parameter count is independently consistent with:

- token embedding: 5,242,880;
- position embedding: 163,840;
- four Transformer layers: 4 × 1,232,960 = 4,931,840;
- final LayerNorm: 640;
- LM head adds no independent parameters because its weight is tied to token embeddings.

## 6. Runtime contract

Focused MKS tests:

**PASS**

Runtime reconstruction confirms:

- `TokenModel` structural conformance: PASS;
- context_limit = 512;
- concrete vocab_size metadata = 16,384;
- model construction: PASS.

Runtime:

- Python 3.12.14
- PyTorch 2.12.1+cpu
- NumPy 2.5.2
- CPU / float32

The historical MKS XPU closure remains separate evidence; this run establishes current-HEAD CPU compatibility.

## 7. Historical checkpoint reconstruction

Checkpoint:

`runs/phase2-lr-sweep-v1/baseline/seed-101/checkpoint-step-200.pt`

Expected SHA-256:

`6561fa2b354b317cf173faaa5a5cc236a4584cb047df3afdb2871dabae01778e`

Observed SHA-256:

`6561fa2b354b317cf173faaa5a5cc236a4584cb047df3afdb2871dabae01778e`

Bytes:

`62,115,779`

Checkpoint contract:

- format_version = 1;
- step = 200;
- model config = exact B0 default config;
- parameter count after restore = 10,339,200;
- model state restore = PASS;
- optimizer state restore = PASS;
- tokenizer fingerprint = `66a81f01511a62896089e8e2a510c95dad61b567cec12f0dbc5752529b11fb3e`;
- dataset fingerprint = `6fbf6b28c072c6fccb5385992d457ddaee7c63b3a54ae9c5bc93a346d54d5bee`.

## 8. Deterministic compatibility replay

Because the historical Phase-2 tokenizer and token-array files referenced by the run metadata are not present in the current Git tree, this gate does **not** claim a new historical Phase-2 metric parity replay.

Instead, the restored real checkpoint was evaluated twice on a deterministic synthetic token compatibility fixture.

Observed repeat deltas:

- cross entropy delta = 0.0;
- bits-per-byte delta = 0.0.

Greedy generation on the same restored checkpoint and zero-science tokenizer fixture:

- token output exact across repeated runs: PASS;
- text output exact across repeated runs: PASS.

This reproduces current deterministic evaluation/generation semantics without fabricating historical dataset availability.

## 9. Boundary and limitation

Supported claim:

> The exact B0 architecture, parameter count, runtime contract, historical checkpoint format/state, and deterministic current evaluation/generation behavior remain compatible on the active Model Core branch.

Not supported:

> The original Phase-2 BPB value was re-derived on the original tokenizer/data in this run.

The historical Phase-2 metrics remain inherited provenance only because their tokenizer/data files are not repository-contained at this checkpoint.

## 10. Gate decision

`B0_RECONSTRUCTION_PASS`

This authorizes the next **non-scientific** gate only:

`B0_DIRECT_M1_Z_MATCHING_FEASIBILITY`

It does not authorize MK-1 data materialization or training.

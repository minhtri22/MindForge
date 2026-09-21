# MK-1 Implementation Lock Specification v0.1

Status: **FROZEN BEFORE MK-1 CODE / HASH MANIFEST PENDING**

Date: **2026-09-21**

Parent Model Core HEAD:

`1f7dfbb353b68617e1522cd3ee47bb0ca83d950f`

## 1. Authorization boundary

This lock authorizes implementation and zero-fresh synthetic preflight only.

It does **not** authorize:

- materializing any scene in namespaces `7101000..7104599`;
- fitting the scientific tokenizer;
- using model seeds `71001..71005` for training;
- neural scientific training;
- validation outcome inspection;
- pristine-confirmatory inference.

## 2. Scientific contract bound

The implementation must conform exactly to the current blobs:

- HYPOTHESES_AND_PREREGISTRATION.md — `b0c976aaf2f99af7c5e80633d56cad4575c914ff` plus Amendment 002 status update lineage;
- PREREGISTRATION_AMENDMENT_001.md — `0ec12864118e1b95d579318edab0dc8c00552656`;
- PREREGISTRATION_AMENDMENT_002.md — `1a7015cab1df40eb9467b42b1b9992e30a18d911`;
- ZERO_SCIENCE_QA_AMENDMENT_001.md — `dd67636b08afea8b38d491e3081e8b60c054270e`;
- ZERO_SCIENCE_QA_AMENDMENT_002.md — `4e01488fea59087507dd08a442dfec95bead9fbf`;
- TARGET_ONTOLOGY.md — `65b152f54b7f2bb7ea45e97a433443e0956a7d11`;
- TARGET_STABILITY_AUDIT.md — `e4dfd62eb4aeb14595d03e299a753ac6711d9547`;
- OBSERVABLE_IDENTIFIABILITY_CONTRACT.md — `53e37771fd3244df7f4c461305963afc7ff12221`;
- STRUCTURED_Z_SCHEMA.md — `045cafa9a8cc6bc9b207da9915f47f982152fbaa`;
- BASELINES_AND_MATCHING.md — `4bca66437bbfe91b45a7762a61d213982f99da3f`;
- DATA_SPLIT_AND_EVALUATION.md — `5192a273e36911d5c9598f2de19884b71525c083`;
- B0_RECONSTRUCTION.md — `173dd942fd703755dd253d785ca5f3993cbd5c38`.

Before final hash binding, the manifest must replace any descriptive reference above with the then-current exact blob and prove no scientific clause changed during implementation.

## 3. Allowed repository changes

Only the following implementation surfaces are authorized:

### Existing model source

`mindforge/model.py`

Allowed change only:

- factor existing B0 hidden computation into a method that returns post-final-LayerNorm hidden states;
- `forward(input_ids)` must still return exactly the existing tied-LM-head logits;
- no parameter, mask, layer, activation, normalization, or initialization change.

### New research implementation package

`experiments/model_core/mk1/`

Allowed files:

- `__init__.py`
- `contracts.py`
- `modeling.py`
- `losses.py`
- `recompose.py`
- `data_contract.py`
- `trainer.py`
- `metrics.py`
- `preflight.py`

### Tests / workflow

- `tests/test_model_core_mk1_preflight.py`
- `.github/workflows/mk1-zero-fresh-preflight.yml`

No other production/runtime file may change without a new pre-outcome lock amendment.

## 4. B0 hidden-state refactor

Required API:

`TransformerLM.hidden_states(input_ids) -> [batch, time, 320]`

It must contain exactly the pre-existing sequence:

1. token embedding;
2. positional embedding;
3. causal mask;
4. Transformer encoder;
5. final LayerNorm.

`forward` becomes semantically:

`lm_head(hidden_states(input_ids))`

Zero-fresh gate:

for fixed float32 CPU weights/tokens, logits before and after refactor are exactly equal.

B0 parameter count must remain:

`10,339,200`

## 5. Neural arms

### B0-DIRECT

- exact B0 backbone;
- final non-padding token hidden state;
- one `Linear(320,34,bias=True)`;
- zero initialization for readout weight and bias;
- C-only loss.

Expected trainable total:

`10,350,114`

### M1-Z

- exact B0 backbone;
- same pooling;
- one `Linear(320,70,bias=True)`;
- zero initialization for readout weight and bias;
- Z-only factor-family loss;
- parameter-free R for canonical C.

Expected trainable total:

`10,361,670`

Zero readout initialization is frozen for both arms to remove an avoidable arm-specific random-head initialization confound.

The first optimizer step therefore updates readouts while backbone gradient through the zero readout is initially zero in both arms. This symmetry is accepted and frozen.

## 6. Tensor slices

The implementation must expose named immutable slices.

M1-Z:

- Z1: `[0:32]`;
- Z2 comparator: `[32:36]`;
- Z2 temporal precision: `[36:39]`;
- Z2 scalars: `[39:43]`;
- Z3 evidence scope: `[43:51]`;
- Z3 asserted scope: `[51:59]`;
- Z3 scope relation: `[59:63]`;
- Z4: `[63:70]`.

B0-DIRECT:

- C1: `[0:8]`;
- C2: `[8:16]`;
- C3: `[16:24]`;
- C4: `[24:28]`;
- C5: `[28:34]`.

Any different layout invalidates the lock.

## 7. Frozen recomposer implementation

R must implement only Amendment 001 identities.

Binary decode:

`logit >= 0`

Categorical decode:

`argmax`, ties to lowest class index.

R must be pure, deterministic, and parameter-free.

Synthetic unit tests must cover every R identity and prove:

`gold_fixture_C == R(gold_fixture_Z)`

for all zero-fresh fixtures.

## 8. Scientific data generator contract

No scientific data is generated during implementation/preflight.

Later materialization must use the already reserved scene namespaces.

Each admitted scene contains:

- one assertion object;
- one current evidence object;
- exact Z gold;
- exact C = R(Z) gold;
- exactly two text surfaces.

Renderer families are frozen as:

- `A` — training-visible canonical renderer;
- `B` — training-visible paraphrastic renderer;
- `C` — held-out renderer family.

Split surface policy:

- TRAIN: A + B;
- VALIDATION: A + B;
- PRISTINE_CONFIRMATORY: A + C.

Renderer C templates/lexical tables may exist in source before materialization but may not be used for tokenizer fitting or training.

Generation must be deterministic from scene ID and frozen code only.

No external model/API/teacher is used to author gold or render surfaces in MK-1 v0.1.

## 9. Coverage-by-construction requirements

The generator code must be written so that, before model outcomes:

- all 32 Z1 classes can reach the frozen support-count gates;
- every Z3 scope class and all four scope relations can reach support gates;
- every Z4 field has positive and negative examples where logically admissible;
- at least 30% of scenes contain >=2 independently scorable mechanisms;
- numeric/ordinal/temporal scalar-present and scalar-absent cases both exist;
- no target uses future/counterfactual data.

Actual support is adjudicated only after authorized materialization.

If the materialized data fail support/stability/identifiability gates, training remains blocked.

## 10. Tokenizer implementation boundary

Use unchanged `mindforge.tokenizer.train_tokenizer`.

Later scientific fitting:

- TRAIN surfaces only;
- requested maximum vocab 16,384;
- freeze one artifact/hash;
- actual vocab 258..16,384;
- all IDs <16,384;
- identical artifact for both arms/seeds.

Zero-fresh preflight may train a tiny disposable tokenizer on synthetic fixture text only to test the plumbing. It must not use any reserved scientific scene ID or surface.

## 11. Input contract

- UTF-8 text;
- tokenizer output must contain at least one token;
- maximum allowed encoded length = 512;
- no scientific sample is truncated.

If a materialized scientific surface exceeds 512 tokens:

`INPUT_LENGTH_CONTRACT_FAIL`

and training is blocked pending a pre-outcome data-contract amendment.

Micro-batch = 1; therefore no PAD token is introduced.

## 12. Frozen scientific training schedule

This schedule is implemented but not executed until later authorization.

For each arm and each seed:

- optimizer: AdamW;
- learning rate: `3e-4`;
- weight decay: `0.1`;
- gradient clip: `1.0`;
- total optimizer steps: `5,000`;
- micro-batch: `1`;
- gradient accumulation: `8`;
- effective examples per optimizer step: `8`;
- warmup fraction: `0.05`;
- cosine decay;
- minimum LR fraction: `0.1`;
- validation interval: `250` steps;
- latest-resume checkpoint: overwritten every `250` steps;
- no early stopping;
- dtype: `float32`;
- device: `auto`.

The learning-rate multiplier must reuse the existing `mindforge.train.learning_rate_multiplier` behavior rather than inventing a new schedule.

## 13. Deterministic sample schedule

Let the admitted TRAIN surface list be sorted by:

`(scene_id, renderer_family)`.

There are no stochastic text augmentations during training.

For each paired seed, both arms use an identical deterministic infinite schedule:

1. cycle index starts at 0;
2. create `numpy.random.default_rng(seed + cycle_index * 1_000_003)`;
3. permute all admitted TRAIN surface indices once;
4. consume the permutation sequentially;
5. increment cycle and repeat.

A step consumes the next eight samples because accumulation = 8.

The exact sample-ID sequence must match between paired arms byte-for-byte.

No failed run/seed is replaced.

## 14. Paired initialization

Scientific seeds remain exactly:

`71001..71005`.

For each seed:

1. set Python/NumPy/PyTorch seed;
2. instantiate exact default B0 once;
3. serialize/hash that B0 state as the paired initialization;
4. load the identical B0 state into B0-DIRECT and M1-Z;
5. zero-initialize each readout.

The Phase-2 checkpoint is never substituted here.

Zero-fresh preflight uses only non-scientific fixture seeds and never creates these five states.

## 15. Validation and checkpoint selection

Both arms always train all 5,000 steps.

At steps:

`250, 500, ..., 5000`

evaluate the full admitted VALIDATION surfaces.

Common checkpoint-selection metric:

canonical C balanced score from DATA_SPLIT_AND_EVALUATION.md.

For M1-Z use `R(Z)`.

For B0-DIRECT use direct C.

Best checkpoint:

- strictly greater score replaces prior best;
- exact tie keeps the earliest checkpoint.

No arm-specific loss is used for checkpoint selection.

PRISTINE_CONFIRMATORY is never inspected during training or selection.

## 16. Metrics and bootstrap

`metrics.py` must implement the preregistered H1a/H1b/H1c metrics without threshold search.

H1b bootstrap:

- unit = canonical scene;
- 10,000 paired resamples;
- bootstrap RNG seed = `71101`;
- each sampled scene retains predictions from all five paired model seeds;
- recompute each arm's complete canonical-C balanced score within each resample;
- report percentile 2.5% / 97.5%;
- no row/surface-level bootstrap.

The confirmatory H1b point estimate is the mean of the five seed-specific canonical-C balanced scores, with the same scene set in both arms.

## 17. D-PIT freeze

D-PIT remains the exact PIT-19 Representation V3 implementation.

Frozen aggregate historical runtime SHA-256:

`b09e284cfd8316140d202e43be216e7fb4ff1743ed4e4900589fb5a0bb5ca1e9`

H1c implementation may materialize/copy that exact historical runtime later, but no modified deterministic rule is admissible.

The common-field mapping must be frozen in code before scientific model outcomes are inspected.

## 17A. Frozen H1c common-field mapping

Before any scientific model outcome, H1c uses only exact semantic correspondences with frozen PIT-v3.

Common fields:

- all 32 Z1 primitive types, using the union of PIT evidence and teaching-signal primitive `type` values;
- Z3 evidence scope;
- Z3 asserted scope;
- Z3 scope relation;
- Z4 `conflict_present` from PIT evidence conflict state;
- Z4 `supersession_supported`;
- Z4 `scope_supported`;
- Z4 `temporal_rule_supported`;
- Z4 `fallback_policy_supported`;
- Z4 `operational_signal_supported`;
- all eight canonical C1 booleans.

Excluded from H1c common fields:

- Z2;
- Z4 `numeric_value_supported`, because PIT-v3 exposes `numeric_threshold_supported`, which is not semantically identical for ordinal/vague-count cases;
- C2/C3/C4/C5 when they duplicate already-counted Z3/Z4 fields in the pooled error.

Pooled H1c representation error is the total binary/categorical field-error rate across this fixed common set.

Primitive precision degradation is computed on the 32 Z1 primitive types only.

H1c whole-scene paired bootstrap:

- 10,000 resamples;
- RNG seed `71102`;
- unit = canonical scene;
- recompute relative pooled-error reduction in every resample;
- report percentile 2.5% / 97.5%.

The neural raw input and D-PIT structured input must be generated from the same canonical scene text. D-PIT may receive its historical `evidence` / `teaching_signal` object shape, but it may not receive semantic information absent from the neural serialization.

## 18. Zero-fresh preflight

Preflight must use only synthetic fixture scenes/text and non-scientific fixture RNG seeds.

It must not:

- enumerate or generate any reserved 7101xxx/7103xxx/7104xxx scene;
- fit a tokenizer on scientific surfaces;
- instantiate paired scientific seeds 71001..71005;
- perform multi-step scientific training.

Required checks:

1. full legacy MKS focused tests PASS;
2. B0 parameter count unchanged;
3. hidden-state refactor exact-logit parity;
4. B0-DIRECT total parameters exact;
5. M1-Z total parameters exact;
6. parameter gap <=1%;
7. tensor slices exact;
8. zero readout initialization exact;
9. all R identities pass;
10. fixture gold C == R(gold Z);
11. one synthetic forward/loss/backward step finite for each arm;
12. paired synthetic input schedule identity;
13. synthetic tokenizer metadata/ID bounds valid;
14. no reserved scientific ID/seed appears in produced preflight artifacts;
15. no scientific data directory is created.

## 19. Hash-binding rule

After code and tests are implemented, create:

`model_kernel/mk1/IMPLEMENTATION_LOCK_MANIFEST.md`

It must list exact Git blobs/SHA-256 for every allowed implementation file and confirm no unauthorized file changed.

Only when that manifest passes static review is the implementation lock complete.

Then, and only then, run the zero-fresh workflow.

## 20. Stop rule

Any implementation need that requires changing:

- target semantics;
- Z/C dimensions;
- loss family;
- pooling;
- model architecture;
- scientific seed policy;
- metric/threshold;
- split namespaces;
- renderer-family isolation;
- training schedule;

must stop and return to a new preregistration/lock amendment before scientific data or outcomes exist.


## 21. Amendment 003 pre-materialization correction

Amendment 003 was frozen after the canonical v0.1 zero-fresh PASS but before any scientific data materialization.

Binding:

`model_kernel/mk1/PREREGISTRATION_AMENDMENT_003.md`

Amendment 003 authorizes changes only to already-allowed implementation surfaces:

- `experiments/model_core/mk1/data_contract.py`;
- `experiments/model_core/mk1/metrics.py`;
- `experiments/model_core/mk1/preflight.py`;
- `tests/test_model_core_mk1_preflight.py`;
- `.github/workflows/mk1-zero-fresh-preflight.yml`.

Purpose:

- remove split-local canonical-scene duplication before first materialization;
- restore prospective support for all primary target classes;
- make `C1.resolves_conflict` reachable;
- project support/integrity gates with fixture ordinals only;
- exclude contextual scope-relation cases from H1c relation scoring because frozen PIT-v3 uses a non-identical `CONTEXTUAL` relation.

The original implementation manifest and zero-fresh result remain historical evidence for implementation v0.1.

After Amendment 003 implementation, a new implementation manifest V2 and a new canonical zero-fresh v0.2 execution are mandatory before scientific materialization.

No scientific scene ID may be generated before both V2 gates PASS.

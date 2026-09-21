# MK-1 Paired Initialization and Exact Sample/Token Budget Audit Specification v0.1

Status: **FROZEN BEFORE SCIENTIFIC SEED INSTANTIATION**

Date: **2026-09-21**

## 1. Authorization basis

Required prior PASS:

- `SCIENTIFIC_MATERIALIZATION_AND_DATA_AUDIT_PASS`
- `TOKENIZER_FREEZE_PASS`

Canonical tokenizer artifact:

- source run: `35562370974`
- artifact id: `10622602143`
- artifact ZIP SHA-256: `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Frozen tokenizer SHA-256:

`e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`

Frozen TRAIN tokenized-manifest SHA-256:

`7be5c48156329e2239ac7345845f705a9b934d7bcc7e940e7dd128c0603a934e`

Frozen TRAIN source SHA-256:

`5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`

Frozen TRAIN totals:

- surfaces: `4000`
- tokens across one complete surface pass: `645726`

Scientific training remains blocked during this audit.

## 2. Scientific seeds

Exactly and only:

`71001, 71002, 71003, 71004, 71005`

No seed may be replaced.

The audit is the first authorized instantiation of these seeds for model weights.

No optimizer may be constructed.

No model forward/backward may be executed.

## 3. Paired base initialization

For each seed:

1. use existing `prepare_paired_initialization(seed,...)`;
2. instantiate exact default B0 once through the frozen helper;
3. save one paired base-state file;
4. freeze:
   - file SHA-256;
   - canonical `state_dict_sha256`;
   - exact model config;
5. reload through existing `load_paired_initialization`;
6. build both arms from that same state using existing `build_arm`;
7. require:
   - DIRECT backbone state digest == paired base digest;
   - M1-Z backbone state digest == paired base digest;
   - DIRECT readout all zeros;
   - M1-Z readout all zeros;
   - DIRECT total parameters = `10,350,114`;
   - M1-Z total parameters = `10,361,670`.

No arm-specific random initialization is admissible beyond the already-frozen zero readout.

## 4. Exact TRAIN-order alignment

Download the exact frozen materialization artifact and tokenizer artifact.

Load TRAIN source using existing:

`load_surface_records`

which sorts by:

`(str(scene_id), str(renderer_family))`.

Load `tokenized_train.jsonl`.

Require exact row-for-row equality of:

- scene_id;
- renderer_family;
- input_text SHA-256;
- exact token IDs obtained by re-encoding source input_text with frozen tokenizer;
- token count.

This proves the tokenized manifest and the actual trainer input list have the same index semantics.

## 5. Frozen scientific sample schedule

Reuse existing:

`deterministic_sample_indices(count=4000, seed)`.

Do not reimplement the RNG schedule independently.

Frozen training consumption:

- optimizer steps: `5000`;
- accumulation: `8`;
- micro-batch: `1`;
- consumed surfaces per arm/seed: `40000`.

For each seed, materialize an exact schedule manifest with 5,000 rows.

Each row records:

- optimizer step 1..5000;
- eight ordered sample keys `scene_id:renderer_family`;
- eight ordered token counts;
- step input-token total;
- cumulative input-token total.

Freeze each schedule manifest SHA-256.

## 6. Schedule identities

Because 40,000 = 10 × 4,000 and each schedule cycle is a full permutation, require for every seed:

- exactly 10 complete permutation cycles consumed;
- every TRAIN surface occurs exactly 10 times;
- no surface outside frozen TRAIN appears;
- total scheduled samples = `40000`.

For paired arms:

- DIRECT schedule bytes == M1-Z schedule bytes;
- DIRECT schedule SHA-256 == M1-Z schedule SHA-256.

The implementation may store one canonical per-seed schedule file if it independently derives both arm schedules and proves exact byte equality before collapsing them to the shared artifact.

## 7. Exact token-budget gate

For every seed:

Expected exact total:

`10 × 645726 = 6457260`

Require:

- DIRECT processed input tokens = `6457260`;
- M1-Z processed input tokens = `6457260`;
- absolute difference = `0`;
- relative difference = `0.0`.

This is stricter than the previously frozen <=1% matching bound and therefore does not relax the preregistration.

No padding/truncation token cost exists because micro-batch is 1 and all sequences already satisfy <=512.

## 8. Deterministic schedule diversity diagnostic

Across the five seeds, report schedule SHA-256 values.

Require:

- same-seed paired-arm hashes equal;
- distinct seeds are not required by the hypothesis to have distinct hashes, but collisions must be reported;
- no collision may be silently repaired by changing a seed.

This is diagnostic only.

## 9. Output evidence

Canonical pre-training audit artifact must contain:

- five paired initialization `.pt` files;
- five schedule JSONL files;
- `PAIRED_INIT_AND_TOKEN_BUDGET_RESULT.json`.

Result JSON freezes for every seed:

- paired-init file SHA-256;
- B0 state_dict SHA-256;
- DIRECT backbone SHA-256;
- M1-Z backbone SHA-256;
- parameter counts;
- readout-zero checks;
- schedule SHA-256;
- sample count;
- per-surface multiplicity min/max;
- total tokens;
- paired-arm token gap;
- source/tokenizer provenance.

## 10. PASS gates

All must hold:

1. exact source materialization artifact identity;
2. exact tokenizer artifact/tokenizer SHA identity;
3. exact TRAIN source and tokenized-manifest hashes;
4. row-for-row source/tokenized alignment;
5. five and only five frozen scientific seeds;
6. paired backbone identity for every seed;
7. zero readouts for both arms;
8. exact parameter counts;
9. 40,000 scheduled samples per seed;
10. every TRAIN surface appears exactly 10 times per seed;
11. paired-arm schedule SHA equality;
12. exact token total `6457260` per arm/seed;
13. token-budget gap = zero;
14. no optimizer construction;
15. no model forward/backward;
16. no validation/pristine model outcome.

Failure of an implementation/execution prerequisite before scientific seed instantiation may be repaired only without changing this scientific contract.

A valid scientific gate failure after seed instantiation is preserved and does not authorize seed replacement or schedule changes.

## 11. Authorization after PASS

A PASS does not itself run training.

It authorizes a separate explicit:

`MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK`

which must bind:

- these exact five paired initialization files/state hashes;
- these exact schedule hashes;
- the frozen tokenizer artifact;
- the frozen TRAIN and VALIDATION data;
- the already-locked trainer implementation;
- the no-confirmatory-before-selection rule.

Only after that final execution lock passes may optimizer step 1 be run.


## 12. Implementation allowlist

Before any scientific seed is instantiated, this gate may add exactly:

- `experiments/model_core/mk1/pretraining_audit.py`;
- `tests/test_model_core_mk1_pretraining_audit.py`;
- `.github/workflows/mk1-pretraining-audit.yml`;
- `model_kernel/mk1/PRETRAINING_AUDIT_IMPLEMENTATION_LOCK.md`;
- `model_kernel/mk1/PRETRAINING_AUDIT_TRIGGER_v0.1.md` only after lock PASS.

Existing scientific implementation files are read-only dependencies for this gate:

- `experiments/model_core/mk1/contracts.py`;
- `experiments/model_core/mk1/modeling.py`;
- `experiments/model_core/mk1/trainer.py`;
- `mindforge/config.py`;
- `mindforge/model.py`;
- `mindforge/tokenizer.py`.

No change to those dependencies is authorized by this gate.

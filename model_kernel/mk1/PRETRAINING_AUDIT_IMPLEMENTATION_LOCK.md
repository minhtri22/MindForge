# MK-1 Pretraining Audit Implementation Lock v0.1

Status: **PASS / PRETRAINING AUDIT HASH LOCKED / ONE SCIENTIFIC AUDIT AUTHORIZED**

Date: **2026-09-21**

Source HEAD before this lock:

`c0ebba1aa786e8646f9347875a28f551ead9e085`

Candidate state:

`PRETRAINING_AUDIT_IMPLEMENTATION_LOCK_PASS`

## 1. New gate implementation bindings

| Path | Git blob | SHA-256 |
|---|---|---|
| `model_kernel/mk1/PAIRED_INIT_AND_TOKEN_BUDGET_SPEC.md` | `d903a09df0e32f084d995f3825d5c3055127f08f` | `d1214e449698bacabbf7cb6af95acfac581c9916fe8fcf7e13b0dd14300ad12e` |
| `experiments/model_core/mk1/pretraining_audit.py` | `df6d2de20f575d0314335abaa25674ae55be93ab` | `a934b73b46fb3902fa0c4e070623abb4c44525e3ce100f4eea68a7a9c9e9189c` |
| `tests/test_model_core_mk1_pretraining_audit.py` | `599c9e3e4e25d5d972ff97847e60d4a7bd5c3df3` | `4b43fb181d5a21a13e1de6cd97fa984da1a6efdfcfb0304191e651e20bc52f42` |
| `.github/workflows/mk1-pretraining-audit.yml` | `d5abfb2770f784a714534dce608f549c76f0cea5` | `89875efb2b355448942482faa3a4fa01c4db72e27859c0ba8335a526554da915` |

## 2. Frozen read-only scientific dependencies

| Path | Git blob | SHA-256 |
|---|---|---|
| `experiments/model_core/mk1/contracts.py` | `cb9d8c067586dfc52b8b23cac7b88868b7498a9f` | `4ece6dd85d2fea2a5c46d6e6058f71ca7ffeaebadaee1a5bf462fae1f1816e7c` |
| `experiments/model_core/mk1/modeling.py` | `f6f79e044a7787d604b46b41a0c68b423cc600ab` | `37f27824b29167b1320fa363ff035a7b4637253c20d0caedff9381c0aea073a7` |
| `experiments/model_core/mk1/trainer.py` | `195cbecef37e091e61e20a2020ba9a90ed7ce2a0` | `5c705878efbc1604d4faaa10242aab32833196dcb7f2e35dd95abc07aedd7f1b` |
| `mindforge/config.py` | `91a3f92ea2449a82fb2d03e0442cbf6e72980caf` | `95e784b83bab57e0618aa52e0c826204609c1ae2d80a6ab47f4cf2b4c4d96169` |
| `mindforge/model.py` | `b585945631a027fb1f124c780fc5f7fd330c0287` | `7562951b9a62e99ecc2c275061662911e339c95b9913c627b9f74dfcc2974a22` |
| `mindforge/tokenizer.py` | `68c7d687c684c800c98344e26be7c75425ea528f` | `3315abd29e7ff086df1a67db5f15f2ae161a2f7d7e9b58913f14572fcc2c8c6e` |
| `model_kernel/mk1/TOKENIZER_FREEZE_RESULT.md` | `ba302d650f8fdef7429f3b047ffb6e8d2d134775` | `be474027ee86dfc605e9f48dc39227adffad785aeeb30921dbbd8f5d53f63ad0` |

## 3. Frozen artifact inputs

Scientific materialization:

- run: `35553551910`
- artifact id: `10619711251`
- ZIP SHA-256: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`

Scientific tokenizer/tokenized inputs:

- run: `35562370974`
- artifact id: `10622602143`
- ZIP SHA-256: `3dc96112fb76f84df9cbd983c046af9b9a98f20b51abbe24c5ea67b15da405c6`

Frozen internal identities:

- TRAIN source SHA-256: `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`
- tokenizer SHA-256: `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`
- tokenized TRAIN manifest SHA-256: `7be5c48156329e2239ac7345845f705a9b934d7bcc7e940e7dd128c0603a934e`
- TRAIN one-pass tokens: `645726`.

## 4. Frozen scientific execution contract

Seeds:

`71001, 71002, 71003, 71004, 71005`

Schedule:

- steps = `5000`
- accumulation = `8`
- surfaces consumed = `40000`
- complete TRAIN cycles = `10`
- exact expected input tokens = `6457260` per seed/arm.

The runner reuses the existing schedule generator and paired-initialization helpers. It does not define replacement scientific RNG or initialization semantics.

## 5. Explicitly forbidden execution

The gate may instantiate model weights and construct the two arm modules only to inspect state identity/readout initialization.

It may not:

- construct `torch.optim` or any optimizer;
- invoke DIRECT or M1-Z forward;
- call `train_arm`;
- execute backward;
- update parameters;
- inspect validation model outcomes;
- execute pristine-confirmatory inference.

The runner result must explicitly record all such actions as false.

## 6. Fixture-only implementation QA

Before scientific seed execution, workflow must run:

`tests/test_model_core_mk1_pretraining_audit.py`

The test uses only fixture seeds `12345` and `12346`.

It must prove:

- same fixture seed -> byte-identical schedule;
- different fixture seed -> different schedule hash.

No scientific seed is used in fixture QA.

## 7. Output evidence

A valid scientific audit produces:

- five `paired_init_seed_*.pt` files;
- five `schedule_seed_*.jsonl` files;
- `PAIRED_INIT_AND_TOKEN_BUDGET_RESULT.json`.

The canonical artifact may be large because it intentionally preserves the exact five base-state files needed by the later training execution lock.

## 8. Independent review gates

Before PASS:

1. all bindings in sections 1–2 match HEAD;
2. trigger file does not yet exist;
3. workflow listens only to `PRETRAINING_AUDIT_TRIGGER_v0.1.md`;
4. runner contains no optimizer construction and no `train_arm` call;
5. runner never calls a model/arm forward;
6. scientific dependencies in section 2 are unchanged;
7. exact prior artifact identities match their formal closures.

Only then may status become:

`PRETRAINING_AUDIT_IMPLEMENTATION_LOCK_PASS`

and one canonical scientific pretraining audit may be triggered.

Scientific optimizer training remains forbidden regardless of this lock.


## 9. Independent review closure

Independent review after candidate-lock creation established:

- candidate-lock commit changed only this lock document;
- trigger did not exist during review;
- all section-1 implementation Git blobs and SHA-256 values re-matched exactly;
- all section-2 scientific dependency Git blobs and SHA-256 values re-matched exactly;
- workflow references the pretraining-audit trigger path exactly twice: push watch and authorization guard;
- runner source contains zero `torch.optim` construction;
- runner source contains zero `train_arm` call;
- runner source contains zero explicit `.forward(...)` call;
- runner source contains zero explicit `.backward(...)` call;
- tokenizer/data artifact identities match the formal prior closures.

Formal verdict:

`PRETRAINING_AUDIT_IMPLEMENTATION_LOCK_PASS`

Exactly one canonical paired-initialization/token-budget audit is now authorized.

Scientific optimizer training remains forbidden.

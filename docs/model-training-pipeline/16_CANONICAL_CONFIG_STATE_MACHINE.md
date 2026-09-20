# 16 — Canonical Config & State-Machine Contract

## 1. Single source of truth

schemas/experiment_config.schema.json is the canonical authoring vocabulary. Each phase owns its parent_ref, datasets, TokenStreamContract, stop rule, optimizer/scheduler transition, checkpoint-selection rule and training settings.

Before side effects: parse -> schema validate -> resolve refs/device/precision/datasets/tools -> semantic validate -> canonical serialize -> hash -> freeze.

Confirmatory/release cannot lock unresolved refs, placeholders, main/latest or precision auto.

## 2. Semantic graph validation

Schema validation is necessary but not sufficient. Resolver must also prove:

- phase IDs unique;
- every phase dataset ref exists;
- parent_ref=model only for a valid root phase;
- parent_ref=phase:X points to an earlier phase, never forward/cycle;
- every phase gets exactly one parent;
- checkpoint-selection metric exists for that phase when rule needs it;
- every metric baseline_id resolves;
- phase_parent baseline points to an existing phase and means the artifact immediately before that phase;
- no fresh resource is referenced by smoke/development/calibration;
- token-stream tokenizer hash after resolution matches model tokenizer used for that phase.

Failure is config semantic INVALID before training.

## 3. Run classes

smoke, development, calibration, confirmatory, release.

## 4. Run state machine

DRAFT -> PREPARED -> PREFLIGHT_PASS -> EXECUTION_LOCKED -> RUNNING -> EVALUATED -> ADJUDICATED_PASS/ADJUDICATED_FAIL/INVALID -> EXPORTED -> RUNTIME_VERIFIED -> REPRO_VERIFIED -> PROMOTED.

Required export/runtime/repro failure after a valid scientific adjudication transitions to QUALIFICATION_FAIL. INVALID means evidence/execution invalidity, not an ordinary negative result.

## 5. Phase state machine

PLANNED -> INPUT_READY -> TRAINING -> TRAINED -> CHECKPOINT_SELECTED -> PHASE_EVALUATED -> PHASE_PASS/PHASE_FAIL/PHASE_INVALID.

A downstream phase may consume only the COMMITTED checkpoint selected by its parent phase's own frozen checkpoint-selection rule.

## 6. Phase transition

Default CPT -> SFT/reasoning: carry selected weights; reset optimizer/scheduler/scaler/sampler; derive phase RNG from frozen phase seed. Carry requires explicit compatibility proof.

## 7. Phase-scoped TokenStreamContract

Token stream is phase-scoped because CPT and chat/reasoning SFT may require different packing, boundaries and sequence length. No global stream config may silently override a phase.

## 8. Stop/warmup/precision

Exactly one stop kind. Warmup has unit/value and is resolved before lock. Precision auto is authoring-only and must resolve before locked execution.

## 9. PEFT identity

base, adapter, merged HF, canonical training and canonical export artifacts are distinct identities.

## 10. Dirty code

Confirmatory/release requires exact software SHA and dirty=false.

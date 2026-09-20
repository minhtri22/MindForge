# 16 — Canonical Config & State-Machine Contract

## 1. Single source of truth

schemas/experiment_config.schema.json is the canonical authoring vocabulary. It requires datasets, token_stream, phases with training config, baselines, evaluation metrics/inference, reasoning and export.

Before any side effect: parse -> schema validate -> resolve refs/device/precision/datasets/tools -> semantic validate -> canonical serialize -> hash -> freeze.

Confirmatory/release cannot lock unresolved refs, placeholders, main/latest or precision auto. Smoke/development may author mutable refs only if resolver freezes an immutable SHA before train.

## 2. Run classes

smoke, development, calibration, confirmatory, release.

Fresh seed/split/fixture resources are forbidden before locked confirmatory access.

## 3. Run state machine

DRAFT -> PREPARED -> PREFLIGHT_PASS -> EXECUTION_LOCKED -> RUNNING -> EVALUATED -> ADJUDICATED_PASS/ADJUDICATED_FAIL/INVALID -> EXPORTED -> RUNTIME_VERIFIED -> REPRO_VERIFIED -> PROMOTED.

Any required export/runtime/repro gate failure after scientific adjudication transitions to QUALIFICATION_FAIL. INVALID is reserved for evidence/execution invalidity rather than a valid negative scientific result.

Smoke may terminate at RUNTIME_VERIFIED and cannot PROMOTE.

## 4. Phase state machine

PLANNED -> INPUT_READY -> TRAINING -> TRAINED -> CHECKPOINT_SELECTED -> PHASE_EVALUATED -> PHASE_PASS/PHASE_FAIL/PHASE_INVALID.

Phase manifest stores exact parent, datasets/fingerprints, stop rule, transition policy, checkpoint-selection rule, selected hash, metrics and child artifact.

## 5. Phase transition

Default CPT -> SFT/reasoning: carry weights; reset optimizer/scheduler/scaler/sampler; derive phase RNG from frozen phase seed. Carry requires explicit contract + compatibility proof.

## 6. Stop rule

Exactly one stop object: max_steps, max_tokens or max_epochs. No implicit precedence.

## 7. Warmup

Warmup always includes unit + value; resolved count/unit is frozen before lock.

## 8. Precision/device

Before lock freeze framework/backend, device class/count, resolved precision, mixed-precision/scaler policy, determinism flags and known nondeterministic kernels.

## 9. PEFT identity

base_artifact, adapter_artifact, merged_hf_artifact, canonical_training_artifact and canonical_export_artifact are distinct identities. Standalone GGUF release uses merged artifact unless pinned runtime path explicitly supports adapter mode.

## 10. Dirty code

Confirmatory/release requires exact source SHA and dirty=false. Development dirty state records patch hash and is not promotable as confirmatory evidence.

# QA Round 2 Report — Evidence-Governed Model Training Pipeline

## 1. Scope

Independent re-review of the remediated specification on branch `docs/evidence-model-training-pipeline`.

- original reviewed state: `48c6cb3adca69d44142ad231e555f2cf77d652b1`
- pre-remediation checklist: `c8c5f6196127d04da08f40030017c667ada95b66`
- main remediation: `3048a781bad312d4be0abde112fae1ad2bc7913f`
- latest QA-reviewed candidate before this report: `886d47d69c70faffbb1281b39666130f4236f435`

This QA reviews specification consistency and implementation-readiness. It is not a claim that the future training software or model has already passed runtime/training acceptance.

## 2. Original findings

- BLOCKER: 17/17 remediated.
- HIGH: 32/32 remediated.
- No original BLOCKER remains open.

The detailed proof index is `QA_REMEDIATION_CHECKLIST.md`.

## 3. New defects found by round 2

Round 2 did not merely confirm the first remediation. It found and forced additional fixes:

1. canonical config schema still needed stronger required fields and metric/baseline binding;
2. evidence bundle manifest location had a residual checksum-order ambiguity;
3. token stream/checkpoint selection needed phase scope, not run scope;
4. downstream phase parent linkage needed an explicit acyclic parent graph;
5. R0 Qwen reasoning serialization was underspecified;
6. execution lock needed hashes for model profile, baseline registry, evaluator/inference and phase resource identity;
7. old CodeSearchNet S3 reference is no longer usable and was replaced;
8. Wikipedia/code reference configs had missing dev evaluation fixtures;
9. YAML `off` portability issue was fixed by quoting enum values.

All are resolved in the current candidate state.

## 4. Machine/static verification

### Schema syntax
PASS — all 8 current JSON Schema documents parse as JSON:
- experiment config
- execution contract
- data manifest
- evaluation contract
- checkpoint manifest
- reasoning response
- run manifest
- model profile

### Example validation
PASS — all 4 shipped YAML examples validate against the canonical ExperimentConfig JSON Schema using PyYAML + Draft 2020-12 JSON Schema validation:
- `examples/end_to_end_small.yaml`
- `examples/reasoning_sft.yaml`
- `examples/train_wikipedia_cpt.yaml`
- `examples/train_code_cpt.yaml`

PASS — `profiles/qwen2.5-0.5b-instruct-r0.yaml` validates against `schemas/model_profile.schema.json`.

### Semantic graph checks
PASS:
- phase IDs are unique in shipped examples;
- all phase dataset refs exist;
- each phase has parent_ref, phase-scoped token stream, checkpoint-selection and training contract;
- downstream parent refs point backward to an earlier phase;
- all metric baseline IDs resolve.

### Stale-definition scan
PASS:
- no active CodeSearchNet source remains;
- no hardcoded Modelfile temperature 0.7 remains;
- no placeholder model pin remains in shipped examples;
- no evaluation-level global checkpoint-selection remains;
- no unquoted `mode: off` remains.

## 5. External-source verification

Verified during QA:
- Qwen/Qwen2.5-0.5B-Instruct revision `7ae557604adf67be50417f59c2c2f167def9a775` exists and the model page identifies Apache-2.0.
- Wikimedia `enwiki/20260301` dump is complete and exposes the configured multistream artifact/checksum manifests.
- CodeSearchNet's historic S3 distribution is no longer reliable; the reference was replaced by `codeparrot/codeparrot-clean` pinned at `35a59fb025bc0a102f7d96eac09d145b896d487b`.
- CodeParrot remains development-only in this spec until repository-revision/license provenance is enriched.

## 6. Residual limitations that are not specification BLOCKERs

These are intentionally deferred to implementation/real execution:

- exact backend determinism tolerance cannot be empirically proven until M2 runs;
- llama.cpp/Ollama compatibility must be re-probed against the exact pinned runtime versions selected during implementation;
- real-data privacy/license scanner effectiveness requires implementation evidence;
- actual GGUF quality/parity and reasoning-quality gates require trained artifacts;
- public dataset availability can change, so source acquisition must verify immutable identity/checksum at prepare time.

These limitations do not justify inventing PASS; the spec explicitly makes them runtime gates.

## 7. QA verdict

```text
ORIGINAL BLOCKERS:              0 unresolved
ORIGINAL HIGH FINDINGS:         0 unresolved
ROUND-2 NEW BLOCKERS:           0 unresolved
SCHEMA SYNTAX:                  PASS
SHIPPED CONFIG SCHEMA VALIDATE: PASS
PHASE/BASELINE GRAPH:           PASS
REFERENCE SOURCE CHECK:         PASS_WITH_RELEASE_RESTRICTIONS
DOCUMENT CONSISTENCY:           PASS
IMPLEMENTATION-READY SPEC:      YES
TRAINING/RUNTIME VERIFIED:      NO (implementation not started)
```

The specification may proceed to M0 implementation only after the final documentation `SHA256SUMS` is regenerated and verified. That checksum regeneration is a mechanical closure step and must be the last content-changing operation in this documentation QA sequence.

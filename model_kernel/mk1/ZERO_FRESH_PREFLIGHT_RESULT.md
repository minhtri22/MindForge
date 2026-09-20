# MK-1 Canonical Zero-Fresh Preflight Result v0.1

Status: **PASS**

Date: **2026-09-21**

Formal verdict:

`ZERO_FRESH_PREFLIGHT_PASS`

## 1. Canonical execution identity

Workflow:

`.github/workflows/mk1-zero-fresh-preflight.yml`

Canonical workflow run:

`35529006429`

Canonical execution head:

`22d8c7cf813f114a3573adad5a358e4a926fb0d9`

Trigger commit:

`22d8c7cf813f114a3573adad5a358e4a926fb0d9`

Authorization basis:

- implementation manifest final PASS: `9f68e1e9175c48731d59b41bdd09294789ed1f9a`;
- one-shot trigger guard: PASS;
- no scientific data existed before execution.

## 2. Canonical artifact

Artifact:

- name: `mk1-zero-fresh-preflight`
- artifact id: `10610537857`
- artifact ZIP SHA-256: `2ca801ce739f4aa16ac267c0ab8acee5c915dc5058050e435d0542e4bf952708`
- size: 509 bytes

Artifact schema:

`MK1-ZERO-FRESH-PREFLIGHT-v0.1`

Artifact status:

`PASS`

## 3. Legacy and contract tests

Combined focused test command:

`pytest -q tests/test_mks_model_kernel.py tests/test_model_core_mk1_preflight.py`

Observed:

`14 passed in 2.73s`

Result:

**PASS**

This includes the legacy MKS compatibility tests plus MK-1 zero-fresh contract tests.

## 4. B0 compatibility gates

Observed B0 parameter count:

`10,339,200`

Expected:

`10,339,200`

Result:

**PASS**

Hidden-state refactor exact-logit parity:

`true`

Result:

**PASS**

The implementation-level hidden-state exposure did not alter B0 language-model logits in the frozen float32 CPU parity fixture.

## 5. Neural-arm parameter gates

B0-DIRECT observed:

`10,350,114`

Expected:

`10,350,114`

M1-Z observed:

`10,361,670`

Expected:

`10,361,670`

Absolute difference:

`11,556`

Observed relative gap:

`0.001115264238293634`

approximately:

`0.111526%`

Frozen maximum:

`1.0%`

Result:

**PASS**

## 6. Tensor and initialization gates

Observed:

- tensor slices: PASS;
- zero readout initialization: PASS.

Frozen dimensions remain:

- B0-DIRECT C output = 34;
- M1-Z Z output = 70.

Result:

**PASS**

## 7. Recomposer and target-integrity fixture gates

Observed:

- recomposer identities: PASS;
- fixture gold recomposition: PASS.

The synthetic fixture confirms:

`gold_fixture_C == R(gold_fixture_Z)`

for the zero-fresh contract fixtures.

Result:

**PASS**

This is implementation-contract evidence only. It is not the later materialized scientific target-stability audit.

## 8. Synthetic forward/loss/backward gates

Observed:

- B0-DIRECT synthetic loss finite: true;
- M1-Z synthetic loss finite: true;
- backward gradients finite for all produced gradients.

Result:

**PASS**

No multi-step scientific training was executed.

## 9. Paired sample schedule

Observed:

`paired_synthetic_schedule = true`

Result:

**PASS**

This confirms deterministic schedule identity on the synthetic fixture.

It does not instantiate the frozen scientific model seeds.

## 10. Synthetic tokenizer plumbing

Observed:

`synthetic_tokenizer_contract = PASS`

The preflight used disposable fixture text only.

It did not fit the scientific tokenizer.

Result:

**PASS**

## 11. Zero-fresh boundary

Artifact explicitly records:

- `scientific_namespace_touched = false`
- `scientific_seed_touched = false`
- `scientific_data_created = false`

Result:

**PASS**

No reserved scientific scene namespace was materialized.

No scientific model-training seed was used.

No scientific dataset directory was created.

## 12. Invalid pre-lock runs

Earlier automatically triggered workflow runs are excluded from evidence, including:

- `35528445838`
- `35528568383`
- `35528581759`
- `35528608614`
- `35528655281`
- `35528657593`

Their conclusions do not contribute to this verdict.

Only post-manifest canonical run `35529006429` is admissible.

## 13. Scientific interpretation

Supported:

- the exact B0 implementation remains compatible after hidden-state exposure;
- B0-DIRECT and M1-Z satisfy the frozen parameter-matching bound;
- tensor layouts and deterministic recomposition are implemented consistently;
- both neural arms can execute one finite synthetic forward/loss/backward step;
- paired scheduling and tokenizer plumbing are mechanically viable;
- the implementation can proceed to the separately gated scientific-data contract.

Not supported:

- learnability of Z;
- superiority of M1-Z over B0-DIRECT;
- improvement over D-PIT;
- target stability on materialized scientific data;
- observable identifiability on materialized scientific data;
- tokenizer quality on scientific TRAIN text;
- any training or confirmatory result.

## 14. Authorization after PASS

The following gate is now eligible:

`SCIENTIFIC_DATA_MATERIALIZATION_AND_PRETRAINING_AUDIT`

This means the program may next materialize the prospectively reserved scene namespaces only for:

1. split/integrity audit;
2. target-stability/margin audit;
3. observable-identifiability audit;
4. renderer/coverage/support audit;
5. TRAIN-only scientific tokenizer fitting and hash freeze;
6. token-length/input-contract audit.

Neural training remains **BLOCKED** until all of those pre-training gates PASS.

The PASS here does not authorize direct transition from zero-fresh preflight to training.

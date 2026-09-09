# H3R v1.1 Freeze Erratum 001

Status: `P2_METADATA_CLARIFICATION / NON_SCIENTIFIC / CLOSED`

## Scope

The frozen H3R v1.1 artifacts contain the phrases:

- `scientific_semantics: UNCHANGED_FROM_H3R_v1.0`
- `semantic_delta_from_v1_0: NONE`

These phrases refer only to the retained scientific core: estimand, baseline/candidate set, probe contract, noise magnitude/family, metrics, utility margin, bootstrap/multiplicity rules, acceptance logic, aggregation, and stopping rule.

They do **not** mean that the protocol identity or test lock is unchanged.

H3R v1.1 intentionally changes the protocol/test identity by using a fresh versioned test lock and fresh seeds after the H3R v1.0 one-shot access was consumed. `governance/protocol_versioning.md` explicitly lists `test lock` as a version-bump trigger. The v1.0 -> v1.1 version bump therefore satisfies the versioning policy.

## Scientific impact

None. This erratum does not alter frozen H3R v1.1 bytes, test identities, seeds, metrics, thresholds, model definitions, noise parameters, or evidence. Scientific test access remains `0` for v1.1.

## Governance interpretation

Read the frozen wording as:

```text
scientific_core_delta_from_v1_0 = NONE
protocol_identity_delta_from_v1_0 = NEW_VERSION_AND_FRESH_TEST_LOCK
```

No amendment, refreeze, or test-lock regeneration is required for this metadata clarification.

# MK-1 Target Stability / Margin Audit v0.1

Status: **FROZEN / CONSISTENCY-EXTENDED UNDER AMENDMENT 001 / NOT EXECUTED**

Date: **2026-09-21**

Original pre-extension blob:

`9cfe8ad74a821b09135366c010ece962787a4ab9`

## 1. Purpose

KCL showed that a real structural target can still be a poor prediction target when hard labels collapse heterogeneous continuous mechanisms or sit near decision margins.

MK-1 therefore audits target stability before representation training.

This audit evaluates the **gold target contract**, not model performance.

## 2. Audit unit

The unit is a semantic scene / canonical gold object plus all surface realizations assigned to that scene.

All variants of the same semantic scene belong to one split only.

## 3. Categorical-target stability

For categorical Z1/Z3/Z4 fields and every categorical/binary canonical C field, require all:

- deterministic derivation from the canonical gold object;
- 100% repeatability under serialization/order changes of the gold object;
- no dependence on final policy/action labels;
- no dependence on future or counterfactual outcome;
- invariant target under surface paraphrases explicitly declared semantics-preserving.

Any target with ambiguous gold derivation is removed **before training** or causes protocol revision before any scientific outcome.

No post-training relabeling is allowed.

## 4. Continuous / threshold-derived target stability

For Z2 quantities and any discrete target derived from them:

- store the underlying continuous quantity whenever observable;
- store the frozen threshold/comparator separately;
- compute distance-to-threshold margin before training;
- report the fraction of records within 1%, 5%, and 10% of the applicable normalized threshold span.

If a hard label is derived from a continuous quantity, the audit must identify whether prediction error could be dominated by near-threshold instability.

## 5. Admission gates

Target stability PASS requires:

1. zero Z or C target fields using forbidden future/counterfactual information;
2. stored/derived gold C equals the frozen deterministic recomposition R(gold Z) for 100% of scenes;
3. 100% deterministic gold re-derivation on an independent implementation check;
4. 100% split-local invariance for declared semantics-preserving variants;
5. every threshold-derived hard target retains its generating continuous quantity;
6. no primary target family has more than 20% of records inside the frozen 5% margin band unless that family is modeled/evaluated continuously rather than as a primary hard classification target;
7. no target class required for primary adjudication has fewer than 100 training examples or 40 pristine-confirmatory examples.

The support-count rules are checked after data materialization and before model training.

## 6. Failure consequences

- If (1)-(5) fail: **TARGET_CONTRACT_INVALID**. Training is forbidden.
- If (6) fails: **HARD_TARGET_UNSTABLE**. The hard label cannot be a primary MK-1 endpoint; use the generating quantity or redesign prospectively.
- If (7) fails: **TARGET_SUPPORT_INSUFFICIENT**. Data materialization may be expanded only under a pre-outcome amendment that preserves the seed/split-generation rule.

No model result may rescue a failed target-stability audit.

## 7. KCL transfer boundary

This audit imports KCL's methodological lesson, not its thresholds, labels, optimizer state, or controller semantics.

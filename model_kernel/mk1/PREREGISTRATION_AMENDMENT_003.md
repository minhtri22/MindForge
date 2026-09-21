# MK-1 Preregistration Amendment 003 — Pre-Materialization Generator Integrity

Status: **PRE-MATERIALIZATION / PRE-OUTCOME / REQUIRED BEFORE SCIENTIFIC DATA**

Date: **2026-09-21**

No scientific MK-1 scene in namespaces 7101000..7104599 had been materialized when this amendment was frozen.

No scientific tokenizer had been fitted.

No scientific training had occurred.

## 1. Trigger

Static generator review after canonical zero-fresh PASS identified deterministic defects that would make the first scientific materialization invalid if executed unchanged.

### F1 — split-local ordinal reset

The v0.1 generator maps each split to an index beginning at zero.

Consequences if executed unchanged:

- TRAIN, VALIDATION, and PRISTINE_CONFIRMATORY would repeat early canonical scenes;
- raw-text/canonical duplicate gates would fail;
- the single-use materialization opportunity would be wasted on a known-invalid dataset.

### F2 — quantifier schedule has incomplete support

The v0.1 expression:

`index * 3 + 1 mod 6`

has gcd(3,6)=3 and reaches only two of six quantifier slots.

Consequences:

- multiple Z1 quantifier classes have zero support;
- multiple Z2 comparator/scalar targets have zero support;
- target-support gates would fail before training.

### F3 — scope-relation schedule omits EQUAL

The v0.1 scope arithmetic produces no `EQUAL` scope relation.

Consequence:

- a primary Z3/C4 class has zero support.

### F4 — conflict and resolution are mutually exclusive

The v0.1 relation generator selects only one relation primitive.

Because canonical C defines:

`resolves_conflict = conflict_present AND resolution_primitive`

the positive class for `C1.resolves_conflict` is unreachable.

### F5 — H1c contextual scope-relation mismatch

Frozen PIT-v3 scope lattice returns relation `CONTEXTUAL` whenever either side has contextual scope.

MK-1 v0.1 uses `INCOMPARABLE` for a contextual/non-contextual pair.

Therefore those relation values are not exact semantic correspondences and must not be scored as the same H1c field.

## 2. Corrected global scientific ordinal

The scientific generator must use one non-overlapping ordinal `u`:

- TRAIN 7101000..7102999 -> `u=0..1999`;
- VALIDATION 7103000..7103399 -> `u=2000..2399`;
- PRISTINE_CONFIRMATORY 7104000..7104599 -> `u=2400..2999`.

No split resets to zero.

Fixture generation uses explicitly supplied non-scientific ordinals and never invokes a reserved scientific scene ID.

## 3. Corrected relation schedule

For every ordinal `u`:

`conflict_present = (u mod 2 == 0)`

A second relation modifier uses:

`modifier_slot = floor(u / 2) mod 6`

with exact order:

1. EXPLICIT_SUPERSESSION
2. IMPLICIT_SELECTION
3. CORRECTION
4. CONTEXT_SPLIT
5. EXCEPTS
6. NONE

Z1 relation labels contain:

- CONFLICT_EXISTS iff `conflict_present`;
- the selected non-NONE modifier.

This explicitly permits conflict + resolution to coexist.

## 4. Corrected quantifier and temporal schedules

Quantifier slot:

`u mod 6`

over:

1. EXACT_THRESHOLD
2. LOWER_BOUND_THRESHOLD
3. UPPER_BOUND_THRESHOLD
4. ORDINAL_TRIGGER
5. VAGUE_COUNT_POLICY
6. NONE

Temporal slot:

`(u + 2) mod 6`

over:

1. EXACT_DURATION
2. APPROX_DURATION
3. PERIODIC_RULE
4. EXPIRY_RULE
5. RECENCY_RELATION
6. NONE

This pairing guarantees that every scene has at least one present continuous Z2 scalar:

- when quantifier is VAGUE_COUNT_POLICY, temporal is EXACT_DURATION;
- when quantifier is NONE, temporal is APPROX_DURATION.

## 5. Unique scalar schedule without split-range extrapolation

Define:

`v(u) = ((7919 * u + 1237) mod 10007) + 1`

10007 is prime and 7919 is non-zero modulo 10007.

For `u=0..2999`, `v(u)` is injective.

Whenever a scalar slot is present:

- numeric_value = `v(u)`;
- ordinal_index = `v(u)`;
- duration_seconds = `v(u)`;
- period_seconds = `v(u)`.

Because the affine permutation wraps through a common bounded range, split identity is not encoded as a monotonic scalar range.

At least one present scalar plus injective `v(u)` makes the canonical Z object unique across all 3,000 scientific scenes.

## 6. Corrected scope schedule

Let:

`mode = u mod 4`

and:

`k = floor(u / 4)`.

### mode 0 — EQUAL

`evidence_scope = asserted_scope = k mod 8`.

### mode 1 — NARROWER

`evidence_scope = 1 + (k mod 6)`

`asserted_scope = evidence_scope - 1`.

### mode 2 — BROADER

`evidence_scope = k mod 6`

`asserted_scope = evidence_scope + 1`.

### mode 3 — INCOMPARABLE

If `k mod 2 == 0`:

- evidence_scope = CONTEXTUAL;
- asserted_scope = `floor(k/2) mod 7`.

Else:

- evidence_scope = `floor(k/2) mod 7`;
- asserted_scope = CONTEXTUAL.

This gives all four MK-1 relation classes prospective support and preserves all eight scope labels.

## 7. Other primitive schedules

Fallback:

`slot = (u + 1) mod 4`

over the three frozen fallback primitives plus NONE.

Uncertainty:

`slot = (u + 2) mod 5`

over the four frozen uncertainty primitives plus NONE.

Operational signal:

`claim_operational = (floor(u/2) mod 2 == 0)`.

## 8. Z4 semantics

Define the deterministic support bit:

`support_bit(u,s) = ((u + 3*s) mod 4) < 2`.

Then:

- conflict_present = relation conflict bit;
- supersession_supported = resolution primitive present AND support_bit(u,1);
- scope_supported = frozen scope-support rule below;
- numeric_value_supported = true when no numeric_value is asserted, otherwise support_bit(u,2);
- temporal_rule_supported = true when no primary temporal rule is asserted, otherwise support_bit(u,3);
- fallback_policy_supported = true when no fallback policy is asserted, otherwise support_bit(u,4);
- operational_signal_supported = true when no operational signal is asserted, otherwise support_bit(u,5).

Primary temporal rule means one of:

- EXACT_DURATION
- APPROX_DURATION
- PERIODIC_RULE
- EXPIRY_RULE

RECENCY_RELATION alone is not an asserted temporal policy for C1.

### Scope-support rule

Use the same support semantics as the frozen PIT-v3 lattice where semantically applicable:

- asserted CONTEXTUAL -> supported;
- evidence CONTEXTUAL -> supported only for asserted OBSERVATION/TURN/SESSION/CONTEXTUAL;
- otherwise supported iff asserted scope rank <= evidence scope rank.

This changes no target vocabulary.

## 9. Target-margin interpretation

MK-1 v0.1 has continuous Z2 values, but no primary hard class is created by thresholding a continuous observed scalar.

EXACT/LOWER_BOUND/UPPER_BOUND are explicit rule/comparator semantics serialized in the current input; they are not labels obtained by comparing `v(u)` against a decision threshold.

Therefore target-stability gate 6 is recorded as:

`NO_THRESHOLD_DERIVED_PRIMARY_HARD_TARGETS / NOT_APPLICABLE`

rather than inventing an arbitrary numeric margin.

Continuous Z2 values remain evaluated continuously under the already frozen nAE gates.

## 10. H1c contextual scope relation

H1c common-field comparison is amended prospectively:

- evidence scope remains comparable;
- asserted scope remains comparable;
- scope relation is included only when neither scope is CONTEXTUAL;
- contextual/non-contextual relation scenes report scope-relation coverage exclusion;
- no mapping `PIT CONTEXTUAL -> MK INCOMPARABLE` is allowed.

All other frozen H1c common-field mappings remain unchanged.

## 11. Required pre-materialization QA

Before scientific materialization, fixture-only QA must prove over prospective ordinal schedules without reserved scientific IDs:

1. every Z1 primary class reaches projected support >=100 TRAIN and >=40 confirmatory;
2. every Z2 categorical class reaches the same support threshold where primary;
3. each Z2 scalar has projected presence >=100 TRAIN and >=40 confirmatory;
4. every Z3/C2/C3/C4 categorical class reaches support threshold;
5. every primary binary Z4/C1/C5 field has both positive and negative support >=100 TRAIN and >=40 confirmatory, where logically admissible;
6. projected canonical Z signatures are unique across all 3,000 ordinals;
7. every projected scene has at least one scalar;
8. projected multi-factor confirmatory fraction >=30%;
9. H1c contextual relation exclusion is deterministic;
10. no scientific namespace/file is materialized.

Only PASS authorizes updating the implementation hash lock and rerunning zero-fresh.

## 12. Authorization

This amendment authorizes only:

- generator implementation correction;
- H1c scorer correction;
- fixture-only pre-materialization QA;
- implementation re-lock;
- zero-fresh rerun.

Scientific data materialization remains blocked until those gates PASS.

Scientific tokenizer fitting and all neural training remain blocked.

# PPF-L3 E1 Generator Hardening + Small Smoke Benchmark Validation

Status: **PASS — SMALL-SCALE GENERATOR FOUNDATION VALIDATED / FULL GENERATOR NOT FROZEN**

Starting commit: `7b7856aa1dbc31cf331064e37349da335f881d1b`

Scope: research tooling only. No recognizer, no L4, no canonical DEV/VALIDATION/FINAL generation, and no Model/Kernel changes.

## 1. Ordered execution

E1 was executed in the frozen order:

1. E1-G0A — full shared L2 semantic-validation bridge.
2. E1-G0B — structural/path-based counterfactual diff.
3. E0 regression.
4. Only after G0A/G0B/E0 were green, E1-B smoke expansion.

The first G0B run returned `REVISE`: the path contract omitted a real permission-loss difference. The pair declaration/normalization was tightened; the gate was not bypassed. E1-B was treated as evidence only after G0B passed.

## 2. E1-G0A — full L2 semantic bridge

The reduced `semerr()` implementation in `ppf_l3/e0.py` was removed. Frozen L2 validation is centralized in `tools/research/ppf_l2_validation.py`, and both the L2 proof validator and L3 generator call the same semantic implementation.

Shared checks include:

- duplicate `event_id`;
- observable non-occurrence requires explicit opportunity;
- missing-like observability requires `missingness_reason`;
- invalid phenomenon intervals;
- derived-observation procedure requirements;
- unresolved `input_event_refs`;
- unresolved relation targets;
- pattern-level event/payload leakage;
- capture-policy provenance;
- duplicate source identity without valid lineage.

Sandbox execution proved:

- E0: 33/33 visible events pass shared schema + semantic validation;
- E1: 218/218 visible events pass shared schema + semantic validation;
- L2 negative tests: 8/8 PASS on the shared validator;
- E1 semantic mutations reject unresolved input refs, unlineaged duplicate sources, forbidden pattern payload fields, and malformed derived provenance.

### Frozen 60-fixture regression provenance

The sandbox cannot resolve `github.com`, so the complete 60-file frozen L2 fixture corpus could not be cloned/materialized into the container. The starting repository already freezes the 60/60 L2 result; E1 extracts the existing `semantic_errors()` implementation without changing its rules and leaves the schema unchanged. Therefore G0A is accepted as a semantic-preserving refactor, while this environmental limitation is recorded explicitly rather than represented as a fresh 60-file sandbox rerun.

A future environment with a normal clone should rerun `python tools/research/ppf_l2_validate.py` as a cheap regression check; this is not a semantic blocker for the E1 smoke proof.

## 3. E1-G0B — strong counterfactual diff

E1 replaces tuple-index exceptions with declarative `PairContract` objects and recursive changed-path reports across normalized semantic layers:

- truth;
- opportunities;
- hidden behavior;
- observation policy;
- visible records;
- lifecycle/control state;
- expected answers / identifiability.

Six E1 pair instances pass:

- CF-A full observation vs permission loss;
- CF-B single evidence vs same-origin replica;
- CF-C no correction vs correction;
- CF-D meaningful alternatives vs constrained availability;
- CF-E known vs hidden critical context;
- CF-F raw-only vs raw+derived evidence.

Mutation QA proves an undeclared hidden-behavior change fails the pair contract and a missing required controlled difference also fails.

## 4. E0 regression

All E0 gates remain PASS after the shared-validator refactor. The original E0 deterministic seed hashes remain stable.

Focused E0 tests: **13/13 PASS**.

## 5. E1 smoke scale

Namespace: `ppf-l3-e1-smoke/1`

```text
synthetic persons:              6
scenario structures:           10
registered variants:           15
histories/cases:               30
checkpoints:                  120
visible L2 events:            218
L2-valid visible events:      218 / 218
counterfactual pair instances: 6
future-leak violations:         0
truth-leak violations:          0
```

E1 smoke is plumbing/QA evidence only and is not part of the canonical 30-person / 32-config / 188-history benchmark.

## 6. Structure coverage

- S1 observable routine;
- S2 sparse coincidence / NO_PATTERN;
- S3 permission-loss fake-drift trap;
- S4 correction/rejection;
- S5 deletion;
- S6 same-origin replication;
- S7 preference with meaningful alternatives;
- S8 constrained availability with superficially repeated choice;
- S9 known vs hidden critical context;
- S10 raw vs raw+derived lineage.

## 7. New semantic evidence

### Preference vs availability

S7 and S8 share controlled behavior realization but differ in the preregistered opportunity set. S7 exposes meaningful alternatives and latent `PREFERENCE`; S8 constrains availability and remains `INSUFFICIENT_TRUE_SUPPORT`. No frequency detector or admission threshold is used.

### Unknown context

The hidden-context side preregisters identifiability `NO`; after the early checkpoint its expected semantic answer is `UNKNOWN_CONTEXT`. The oracle does not guess the missing scope.

### Raw/derived non-inflation

S10 raw+derived adds a valid `DERIVED_OBSERVATION` with `DERIVED_FROM`, `input_event_refs`, and a known procedure. Hidden behavioral occurrence count remains one.

## 8. Seed isolation

Seed hierarchy remains deterministic and SHA-256 based. No Python built-in `hash()` or global RNG is used.

Changing S7's behavior replica changes S7 realization while preserving its truth/opportunity process, and does not alter S8's truth/opportunities. Observation streams remain independently derived.

## 9. Checkpoint semantics

Checkpoint prefixes use `ingested_time`. The smoke surface includes delayed ingestion, lifecycle controls, and derived evidence arriving after its raw input. Future-leak violations: **0**.

## 10. Oracle boundary

Expected answers are declared in scenario specifications. The oracle only associates those declarations with method-visible prefixes.

Static review finds no generic count/frequency/ratio/score/confidence threshold, classifier, or pattern detector.

## 11. Test execution

Sandbox focused suite:

```text
29 / 29 PASS
```

Breakdown:

- E0 regression tests: 13;
- E1/hardening tests: 16;
- L2 shared negative tests: 8/8 PASS (additional direct execution).

`py_compile` passes for the changed research modules.

## 12. E1 gates

```text
E1-G0A full L2 semantic bridge:          PASS
E1-G0B strong counterfactual diff:       PASS
E1-G1 full L2 validation:                PASS
E1-G2 strong counterfactual isolation:   PASS
E1-G3 E0 regression:                     PASS
E1-G4 multi-structure seed isolation:    PASS
E1-G5 preference/opportunity distinction:PASS
E1-G6 unknown-context abstention:         PASS
E1-G7 raw/derived non-inflation:          PASS
E1-G8 checkpoint correctness:            PASS
E1-G9 truth leakage:                     PASS
E1-G10 no cherry-picking:                PASS
E1-G11 oracle boundary:                  PASS
E1-G12 scope integrity:                   PASS
```

## 13. Scientific recommendation

E1 demonstrates that the generator foundation survives a modest increase in semantic/event surface after closing both E0 review findings. The foundation is **small-scale validated**, not fully frozen for the canonical benchmark.

Candidate next action after independent review: **L3-E2 — Full DEV Generation** using the already frozen DEV allocation (6 persons / 7 truth configs / 38 histories).

E2 is not authorized by this artifact.

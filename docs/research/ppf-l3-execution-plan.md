# PPF-L3 Benchmark Execution Plan

Status: **PASS / FROZEN EXECUTION PLAN ONLY**

Execution status: **GENERATOR NOT IMPLEMENTED / BENCHMARK NOT GENERATED / RECOGNIZER NOT IMPLEMENTED**

Frozen authorities:

- `ppf-recognize-me-contract.md` — L1 semantic authority;
- `ppf-personal-event-contract.md` and `data/ppf-l2/schema.json` — L2 evidence authority;
- `ppf-l3-benchmark-protocol.md` — L3 benchmark protocol;
- `ppf-l3-ground-truth-contract.md` — two-level truth and identifiability contract;
- `ppf-l3-benchmark-qa.md` — frozen protocol QA;
- `mindforge-architecture-invariants.md` — architecture authority. PPF remains an optional plugin research track; this plan does not authorize kernel/model changes.

## 1. Primary planning question

> What is the smallest rigorous L3 benchmark execution that is large and diverse enough to falsify weak recognition methods, while remaining reproducible, inspectable, and cheap enough to iterate locally?

**Plan answer: YES.**

The initial Tier-S execution is frozen at **30 synthetic persons, 32 base truth configurations, and 188 generated histories/cases**. It uses two replication classes, person-disjoint protected splits, multiple temporal checkpoints, 14 counterfactual pair templates, three structural holdouts, evaluator-only final-test truth, and generator/oracle QA frozen before implementation.

The plan deliberately favors semantic/adversarial coverage over population realism or large scale.

## 2. Hard scope

This artifact freezes execution planning only.

Allowed:

```text
dataset allocation
person/scenario allocation
seed allocation
split/holdout policy
counterfactual suite
checkpoint policy
generator component boundaries
generator/oracle QA
artifact layout
version/freeze policy
resource envelope
```

Not authorized:

```text
generator implementation
history generation
recognizer/baseline implementation
pattern scoring
training
threshold tuning
method evaluation
L4/L5
production PPF
kernel/model changes
mobile integration
```

## 3. Architecture acknowledgement

This plan follows the frozen architecture decision:

```text
Model != Kernel.
The Model owns learned representations/capabilities.
The Kernel owns only proven universal primitives.
Plugins own feature-specific mechanisms and semantics.
Hosts own composition.
PPF is an optional MindForge extension/plugin.
PPF research cannot self-authorize kernel or model changes.
```

The benchmark generator/oracle are research tooling, not kernel primitives and not the PPF production runtime.

## 4. Benchmark unit hierarchy

The following terms are distinct and must not be used interchangeably.

| Unit | Definition |
|---|---|
| benchmark version | Immutable semantic/execution version, initially `ppf-l3-benchmark/v1`. |
| split | `DEV`, `VALIDATION`, or protected `FINAL_TEST`. |
| scenario family | Semantic/adversarial family defined by the frozen L3 protocol. |
| scenario template | Method-independent generative structure implementing one or more families. |
| synthetic person | Stable synthetic identity with a structural mixture of truths; not a demographic persona. |
| truth configuration | Evaluator-only bundle of latent truths, scopes, opportunities, lifecycle transitions, and expected checkpoint semantics. |
| behavior seed | Random stream controlling behavioral realization while truth remains fixed. |
| observation seed | Independent random stream controlling observation/corruption while truth and behavioral realization remain fixed. |
| history/case | One visible L2-compliant longitudinal history produced from one truth configuration + behavior seed + observation seed. |
| evaluation checkpoint | Evaluator-registered temporal cut at which only history up to that point is method-visible. |
| evaluation unit | One preregistered semantic question at one checkpoint with expected positive claim or abstention/lifecycle state. |

A person may own multiple truth configurations and each history may exercise multiple scenario families.

## 5. Frozen initial scale

### 5.1 Canonical totals

```text
synthetic persons:                 30
base truth configurations:         32
STANDARD configurations:           20
HIGH-RISK configurations:          12
STANDARD replication:              2 behavior x 2 observation = 4 histories/config
HIGH-RISK replication:             3 behavior x 3 observation = 9 histories/config
STANDARD histories:                80
HIGH-RISK histories:              108
total histories/cases:            188
counterfactual pair templates:     14
minimum instantiated pairs:        42
estimated checkpoints:          ~1,004
estimated evaluation units:    ~2,000-2,800
estimated visible L2 events:   ~18,000-28,000
```

Formula:

```text
20 * 4 + 12 * 9 = 188 histories
```

Family rows in the dataset matrix are **coverage views and intentionally overlap**. They must not be summed to derive the canonical case total.

### 5.2 Why 30 persons

Thirty persons are the smallest frozen scale judged sufficient to support:

- ten structural archetype dimensions with overlap rather than one-person/one-scenario coupling;
- person-disjoint `6 / 6 / 18` split allocation;
- multiple persons per major semantic family;
- three protected structural holdout combinations;
- repeated high-risk adversarial configurations without allowing one synthetic person to dominate evidence.

The first scientific execution must not be enlarged merely to improve apparent robustness. Expansion requires a documented coverage or variance failure.

## 6. Synthetic-person structural coverage

Persons are structural mixtures, not demographic personas. Every person receives 3-5 structural tags; counts below overlap.

| Archetype dimension | Minimum persons |
|---|---:|
| P-A stable/simple | 10 |
| P-B context-dependent | 12 |
| P-C relationship-conditioned | 8 |
| P-D exception-heavy | 8 |
| P-E drift/reversal-heavy | 8 |
| P-F poor-observability | 10 |
| P-G multi-device-heavy | 8 |
| P-H correction/deletion-heavy | 8 |
| P-I overlapping-pattern-heavy | 10 |
| P-J mostly-no-pattern/sparse | 10 |

No synthetic person may own more than 20% of the evaluation units for any major metric family.

## 7. Positive / negative / abstention balance

The canonical denominator is **all registered evaluation units**, not histories or raw observations.

Frozen target mix for v1:

```text
active-positive/current-support units:  60% +/- 3%
pure negative/no-pattern units:          22% +/- 3%
required abstention/lifecycle units:     23% +/- 3%
negative+abstention overlap:              5% +/- 2%
```

Therefore the target fraction with **no correct active positive claim** is approximately 40%, within the L3 falsification target and never below 35%.

The mix is a benchmark falsification design, not an estimate of real-world prevalence.

## 8. Identifiability balance

Target across registered evaluation units:

```text
YES:      60% +/- 5%
PARTIAL:  20% +/- 5%
NO:       20% +/- 5%
```

Every major positive pattern family must have identifiable `YES` cases. Families involving missing context, degraded observation, coverage change, or cold start must additionally contain `PARTIAL` and/or `NO` cases where semantically appropriate.

Identifiability is preregistered from scenario construction and observation provenance, never from recognizer success.

## 9. History-length regimes

Ranges are generator construction ranges, not recognizer admission thresholds.

```text
SHORT:   4-10 relevant opportunities
MEDIUM: 16-32 relevant opportunities
LONG:   48-96 relevant opportunities
```

Target history allocation:

```text
SHORT:   48 histories
MEDIUM:  84 histories
LONG:    56 histories
TOTAL:  188 histories
```

Long histories carry most lifecycle transitions; short histories carry disproportionate cold-start, sparse coincidence, and insufficient-evidence controls.

## 10. Checkpoint policy

Standard longitudinal checkpoints:

```text
C0 cold start
C1 early
C2 mid
C3 mature
```

Medium/long histories add `C4` for late/currentness evaluation. Lifecycle histories add evaluator-only named checkpoints:

```text
pre-change
immediate-post-change
later-post-change
pre-control
immediate-post-control
later-post-control
post-observation-loss
stale-currentness
```

Frozen checkpoint budget estimate:

```text
48 SHORT  x 4 checkpoints = 192
84 MEDIUM x 5 checkpoints = 420
56 LONG   x 7 checkpoints = 392
TOTAL                        1,004
```

A lifecycle checkpoint can coincide with a numbered checkpoint when timestamps are identical; it is not duplicated in the count.

## 11. Seed hierarchy

Every generated case records evaluator-only seed provenance:

```text
master_seed
scenario_seed
person_seed
behavior_seed
observation_seed
```

Conceptual deterministic derivation:

```text
master_seed
  -> hash(version, split, scenario_template_id)
  -> hash(..., person_id)
  -> hash(..., behavior_replica_index)
  -> hash(..., observation_replica_index)
```

Exact hashing/serialization is implementation work, but requirements are frozen:

- full seed tuple must produce canonical-JSON semantic stability;
- changing `observation_seed` only must preserve truth, opportunities, and realized behavior;
- changing `behavior_seed` only may change realized behavior while preserving latent truth and observation policy;
- public IDs must not encode seeds/families/truth status.

## 12. Replication classes

### STANDARD

```text
2 behavior seeds x 2 observation seeds = 4 histories/configuration
```

Used for ordinary semantic coverage where failure does not hinge on rare stochastic coincidence.

### HIGH-RISK

```text
3 behavior seeds x 3 observation seeds = 9 histories/configuration
```

Mandatory high-risk coverage includes:

```text
sparse coincidence
confounding
Simpson-like aggregation
coverage-induced fake drift
true drift vs observation-only change
multi-device replication
correction/rejection
deletion/reset
unidentifiable truth
```

High-risk conclusions must never rely on one seed.

## 13. Counterfactual suite

Freeze 14 pair templates. Each must have at least one instantiated pair in DEV, one in VALIDATION, and one in FINAL_TEST: minimum **42 instantiated pairs / 84 paired histories**, all included within the canonical 188 histories.

| Pair | Controlled change | Held constant | Expected semantic effect | Primary metric |
|---|---|---|---|---|
| CF-01 | full observability -> permission loss | truth, opportunities, behavior | identifiability/status may change; latent behavior unchanged | abstention, false drift |
| CF-02 | normal -> degraded quality | truth, opportunities, behavior | support may weaken/abstain; truth unchanged | abstention/staleness |
| CF-03 | single evidence -> same-origin replicas | behavioral episode | behavioral occurrence unchanged | replica inflation |
| CF-04 | true routine -> chance-matching NO_PATTERN | observation policy/count shape | positive truth changes | false promotion |
| CF-05 | stable coverage -> fake drift coverage collapse | behavior/truth | no behavioral drift | false drift |
| CF-06 | true drift -> observation-only change | pre-T history shape | only true-drift side changes latent behavior | drift correctness |
| CF-07 | meaningful alternatives -> constrained availability | visible option frequency where possible | preference identifiability/truth relation differs | preference/scope correctness |
| CF-08 | contextual slices -> misleading aggregate | aggregate count shape | conditional truth must not collapse globally | scope correctness |
| CF-09 | scoped exception -> random deviation | parent pattern | exception relation differs | exception correctness |
| CF-10 | no correction -> correction applied | underlying prior history | active semantic state changes | correction correctness |
| CF-11 | no deletion -> deletion applied | pre-delete history | active state becomes DELETED | deletion correctness |
| CF-12 | known relationship -> hidden relationship identity | behavior | relationship-specific claim becomes UNKNOWN_CONTEXT | abstention/scope |
| CF-13 | raw only -> raw+derived lineage | behavioral episode | recurrence truth unchanged | raw/derived inflation |
| CF-14 | independent corroboration -> same-origin replication | visible source count | evidentiary relation changes; behavioral episode does not multiply | corroboration/replica correctness |

A pair must fail QA if any undeclared truth, opportunity, behavior, or observation variable differs.

## 14. Protected split discipline

Person-disjoint allocation is frozen:

```text
DEV:         6 persons (20%)
VALIDATION:  6 persons (20%)
FINAL_TEST: 18 persons (60%)
TOTAL:      30 persons
```

Target history allocation, reconciled to 188:

```text
DEV:         38 histories
VALIDATION:  38 histories
FINAL_TEST: 112 histories
TOTAL:      188 histories
```

A history, truth configuration, or synthetic person may not cross protected split boundaries. Split assignment happens before method evaluation.

DEV may expose truth for generator/evaluator debugging. VALIDATION truth is available for method selection only after generator/oracle freeze. FINAL_TEST truth/seeds remain evaluator-only and uncommitted to the public repository before final evaluation.

## 15. Structural holdouts

Final test must include at least these three unseen combinations of otherwise known axes:

```text
SH-1 relationship-conditioned + missingness + correction
SH-2 exception + multi-device replication + raw/derived lineage
SH-3 drift/reversal + partial observability + derived evidence
```

Families may be known during development; the specific combined structure and final parameterization are protected.

## 16. Adversarial parameter holdout

At minimum, FINAL_TEST includes evaluator-secret parameterizations for:

```text
extreme availability skew
coverage collapse aligned with an apparent behavior change
replica bursts with mixed source timing
context imbalance producing misleading aggregate reversal
correction followed by similar passive behavior
delete/reset with unrelated concurrent truth
```

Method designers may know these attack classes exist but not their final seed/parameter values.

## 17. Case/evaluation-unit registration

Before any method output is inspected, evaluator manifests freeze:

```text
case_id
person_id
split
scenario_template/family refs
truth_configuration_ref
behavior_seed
observation_seed
checkpoint IDs
evaluation-unit IDs
counterfactual pair ID if any
difficulty axes
```

Method-visible case IDs are opaque (for example `case-a91f72`) and contain no truth/family/seed hints.

Each evaluation unit contains evaluator-only:

```text
unit_id
case/checkpoint
semantic question
pattern family
scope/context
target/action/outcome
expected active answer
forbidden overgeneralizations
identifiability
lifecycle/parent relation where relevant
```

## 18. False-promotion denominator

The negative-unit denominator is the finite preregistered set of evaluation units with no correct active positive claim.

The execution must include explicit units for:

```text
NO_PATTERN
sparse coincidence / insufficient true support
required abstention
wrong-scope negatives
coverage-induced fake drift
replica-inflation negatives
raw/derived duplication negatives
deleted-state active-return negatives
correction-resurrection negatives
```

False discovery among emitted positives remains a separate output-denominator metric.

## 19. Generator component plan

No component is implemented by this task.

| Component | Input | Output | Forbidden responsibility |
|---|---|---|---|
| `truth_spec` | scenario/person specification | latent truth configuration | infer truth from generated history or method output |
| `opportunity_generator` | truth + scenario/person seed | hidden opportunity/context sequence | use observation loss to redefine opportunity truth |
| `behavior_realizer` | truth + opportunities + behavior seed | hidden realized behavior | apply observation corruption |
| `observation_renderer` | hidden behavior/opportunities + observation seed | visible L2 records + evaluator corruption provenance | change latent behavioral truth |
| `l2_validator` | visible records | schema/semantic validation report | infer patterns |
| `checkpoint_oracle` | frozen truth + visible prefix + control provenance | evaluator-only expected answers/identifiability | emulate recognizer or choose thresholds |
| `manifest_writer` | registered specs/seeds/splits | deterministic manifests | expose evaluator-only labels to methods |
| `benchmark_qa` | generated artifacts/manifests | QA reports | tune cases based on recognizer success |

Truth flow is one-way:

```text
truth -> opportunities -> behavior -> observation -> visible history
```

Never `history -> redefine truth`.

## 20. Oracle boundary

The oracle is a **semantic judge**, not a reference detector.

It may know latent truth, scenario specification, observation-corruption provenance, correction/deletion timing, and visible history up to checkpoint T. It must derive expected answers from frozen L1 semantics and preregistered scenario construction, without introducing a count/probability/confidence admission threshold.

Expected states include:

```text
SUPPORTED
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
UNKNOWN_CONTEXT
NOT_OBSERVABLE
STALE
USER_REJECTED
SUPERSEDED
DELETED
```

Identifiability `YES/PARTIAL/NO` is assigned before method output.

## 21. Metric coverage

The execution preserves a metric vector plus separate hard-violation counts. No weighted composite score is allowed.

| Family/failure | Primary metric |
|---|---|
| sparse coincidence / NO_PATTERN | false promotion, false discovery |
| preference availability skew | pattern/scope correctness |
| confounding / Simpson-like aggregation | scope correctness |
| random counterexample | counterexample sensitivity |
| stable scoped exception | exception correctness |
| real drift / reversal | drift/reversal correctness, change latency |
| coverage-induced fake drift | false drift |
| correction/rejection | correction correctness, resurrection violations |
| deletion/reset | deletion correctness, deleted-active-return violations |
| missingness/unobservable | abstention correctness |
| multi-device/raw-derived duplication | replica-inflation violations |
| staleness | staleness correctness |
| unknown relationship/context | abstention subtype + scope correctness |

Hard violations remain individually visible at minimum:

```text
deleted-active-return
false drift
correction resurrection
missingness-as-negative
same-origin replica inflation
raw-derived inflation
scope collapse
```

## 22. Resource envelope

Planning envelope for 188 Tier-S histories:

```text
visible events/case:       ~95-150 average, regime-dependent
total visible L2 events:   ~18,000-28,000
canonical JSON footprint:  ~20-50 MB including evaluator manifests/reports
generator runtime target:  seconds to low minutes on ordinary local CPU
validator/oracle target:   bounded local CPU/RAM; no accelerator required
```

These are engineering envelopes, not performance promises. If initial implementation exceeds ~100 MB of benchmark artifacts or requires accelerator-scale compute without semantic justification, execution must REVISE before expansion.

## 23. Final-test secrecy in a public repository

Chosen operational strategy:

**Public generator + public DEV artifacts/policy; evaluator-secret FINAL_TEST seed/spec/truth package generated and retained outside the public Git repository.**

Public repository may contain:

```text
protocols
execution plan
generator source after separate authorization
public schemas/interfaces
DEV scenario examples/data after freeze
validation policy
artifact contracts
```

The public repository must not contain before confirmatory evaluation:

```text
FINAL_TEST truth
FINAL_TEST expected answers
FINAL_TEST identifiability labels
FINAL_TEST seed manifest
protected structural-holdout parameterization
family-revealing final case paths/IDs
```

A local evaluator-only package records commit/version provenance and hashes. Publishing it retires that final set as held-out evidence.

## 24. Benchmark versioning and freeze stages

Initial version:

```text
ppf-l3-benchmark/v1
```

Freeze stages:

```text
1. PLAN FROZEN
2. GENERATOR FROZEN
3. DEV DATASET FROZEN
4. VALIDATION DATASET FROZEN
5. FINAL TEST FROZEN
```

Each later stage must record repository commit and artifact hashes.

After final-test exposure, any change to truth semantics, scenario/evaluation-unit semantics, metric definitions, oracle logic, or final cases requires a new benchmark version. Bugs may be documented, but v1 cannot be silently rewritten around recognizer outcomes.

## 25. Execution phases

```text
E0 generator skeleton validation
   -> truth-to-history plumbing, L2 validity, seed reproducibility

E1 smoke benchmark
   -> 4-6 persons, selected families; plumbing evidence only

E2 full DEV generation
   -> family/metric/checkpoint coverage

E3 VALIDATION generation
   -> frozen method-tuning set

E4 FINAL_TEST generation
   -> only after generator/oracle freeze, using protected evaluator inputs
```

This plan does not authorize E0 implementation. Separate approval is required.

## 26. Execution-plan gate

### L3EP-G1 — totals frozen
PASS: 30 persons / 32 configs / 188 histories / ~1,004 checkpoints.

### L3EP-G2 — family allocation frozen
PASS: canonical matrix covers all protocol families; family rows may overlap.

### L3EP-G3 — replication frozen
PASS: STANDARD `2x2`, HIGH-RISK `3x3`.

### L3EP-G4 — counterfactual suite frozen
PASS: 14 templates, minimum 42 instantiated pairs.

### L3EP-G5 — protected split frozen
PASS: person-disjoint `6/6/18`, target histories `38/38/112`.

### L3EP-G6 — structural/adversarial holdout frozen
PASS: three structural combinations plus protected parameter sets.

### L3EP-G7 — generator QA frozen
PASS: see `ppf-l3-generator-qa-plan.md`.

### L3EP-G8 — oracle semantics frozen
PASS: two-level truth, method-independent semantic judge, no recognition thresholds.

### L3EP-G9 — artifact visibility/layout frozen
PASS: see `ppf-l3-artifact-layout.md`.

### L3EP-G10 — public/private boundary frozen
PASS: final truth/seeds remain outside public repo until evaluation is retired.

### L3EP-G11 — resource envelope bounded
PASS: 188 cases and tens of thousands of L2 events remain local-friendly.

### L3EP-G12 — no method coupling
PASS: no recognizer/baseline/model feature defines truth, cases, oracle, or metrics.

**L3 EXECUTION PLAN GATE: PASS / FROZEN.**

## 27. Scientific recommendation

Freeze this plan before generator implementation. The next possible action is a separately authorized **L3 E0 Generator Skeleton Validation** task. It must prove generator/oracle correctness before producing the full benchmark and must still contain no recognizer or L4 work.

Current status:

```text
PPF-L1: PASS / FROZEN
PPF-L2: PASS / FROZEN
PPF-L3 Benchmark Protocol: PASS / FROZEN
PPF-L3 Execution Plan: PASS / FROZEN
PPF-L3 Generator: NOT IMPLEMENTED
PPF-L3 Benchmark Execution: NOT STARTED
PPF-L4: BLOCKED
PPF-L5: BLOCKED
```

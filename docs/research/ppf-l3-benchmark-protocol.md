# PPF-L3 Ground-Truth Personal Pattern Benchmark Protocol

Status: **L3 BENCHMARK PROTOCOL / PROTOCOL DESIGN ONLY**

Frozen inputs:

- PPF-L1 — **PASS / FROZEN**;
- PPF-L2 — **PASS / FROZEN**;
- `ppf-l3-ground-truth-contract.md` — hidden-truth and checkpoint-answer contract.

Execution status: **BENCHMARK NOT GENERATED / NOT RUN**

Implementation status: **NO PATTERN ALGORITHM / NO GENERATOR IMPLEMENTATION**

## 1. Primary research question

> Can PPF define a benchmark where personal-pattern truth is known independently of the method under test, so that later pattern methods can be falsified rather than merely demonstrated?

**Protocol answer: YES, provided the rules in this document are frozen before benchmark execution.**

The benchmark is designed to distinguish actual recognition from frequency fitting, telemetry-artifact fitting, benchmark leakage, overclaiming, failure to abstain, and failure to respect correction/deletion semantics.

## 2. Scientific success criterion

The protocol succeeds only if a future benchmark can:

> Generate a personal history from hidden truth, corrupt observability independently, reveal only the L2-compliant visible history, and still know exactly what a correct recognizer is allowed to claim or must abstain from claiming at each evaluation checkpoint, without reference to the method being tested.

This requires two independent standards of correctness:

1. **latent behavioral correctness** — what is actually true in the synthetic person;
2. **observation-bound semantic correctness** — what is justified by the visible evidence at the checkpoint.

The second standard is the primary target of method evaluation. A method is not rewarded for guessing hidden truth that the visible history cannot justify.

## 3. Hard scope

Allowed in this protocol:

```text
benchmark semantics
ground-truth specification
synthetic/semi-synthetic design
scenario families
generator contract
split/seed policy
evaluation units
semantic matching rules
metric definitions
adversarial design
leakage controls
benchmark QA requirements
future artifact formats
```

Forbidden:

```text
pattern detector
pattern scoring implementation
baseline implementation
training or model selection
threshold tuning
hyperparameter search
production pattern engine
live telemetry collection
L4/L5 work
mobile integration
```

No recognition method is evaluated in this task.

## 4. Central truth-independence principle

The benchmark generator conceptually executes:

```text
Layer A — hidden personal truth
        ↓
Layer B — opportunity/context process
        ↓
Layer C — behavioral realization
        ↓
Layer D — observation process
        ↓
Layer E — visible L2-compliant history
```

The method sees only Layer E up to the current evaluation checkpoint.

The method must not see:

```text
latent truth
truth status
identifiability labels
expected semantic answers
future events
change points not yet visible
generator latent variables
secret evaluation seeds
truth-only relation labels
```

Method output can never alter truth, identifiability, evaluation units, or expected answers.

## 5. Generative layers

### 5.1 Layer A — hidden personal truth

Defines the synthetic person's facts, behavioral patterns, negative/no-pattern states, lifecycle changes, correction state, and deletion state using `ppf-l3-ground-truth-contract.md`.

Required positive pattern families:

```text
ROUTINE
PREFERENCE
CONDITIONAL_PREFERENCE
RELATIONSHIP_CONDITIONED
TEMPORAL_SEQUENCE
CONTEXT_ACTION_ASSOCIATION
EXCEPTION
DRIFT
REVERSAL
```

Required negative/control states:

```text
NO_PATTERN
INSUFFICIENT_TRUE_SUPPORT
CONFLICTING_STRUCTURE
```

Facts remain independent from behavioral pattern truth.

### 5.2 Layer B — opportunity/context process

Defines when a relevant opportunity exists, which context dimensions apply, and which alternatives are available.

Examples:

```text
commute opportunity
meal choice opportunity
weekday/weekend
social or relationship context
location context
calendar/event context
choice-set availability
```

The hidden opportunity process knows opportunities that the observation process may later hide.

### 5.3 Layer C — behavioral realization

Realizes the person's behavior from hidden truth and opportunities while allowing:

```text
pattern-consistent action
meaningful alternative choice
observable behavioral non-occurrence
stable exception
ordinary random deviation
counterexample
```

Behavioral randomness is independently seeded from observation corruption.

### 5.4 Layer D — observation process

Transforms realized behavior/opportunities into visible L2 evidence while independently varying:

```text
source/platform class
observability
missingness mechanism
capture policy/history window
delay/batching/out-of-order ingestion
observation quality/coverage
raw/derived representation
multi-device replication/corroboration/unknown relation
correction/deletion/control evidence
```

Layer D must emit only records compliant with the frozen L2 event contract/schema for the benchmark version under execution.

### 5.5 Layer E — visible history

The method receives only the visible event history that exists at the evaluation checkpoint.

Behavioral stochasticity and observation stochasticity must remain separately replayable and auditable.

## 6. No universal pattern-admission threshold

L3 does not define truth by applying a threshold to generated or visible counts.

Forbidden truth definitions include:

```text
pattern exists iff count >= N
pattern exists iff observed fraction > X
pattern exists iff confidence > Y
```

Ground truth is generated from the hidden rule before visible observation corruption.

Therefore both cases are valid:

```text
latent pattern exists
visible history is sparse due observation loss
```

and:

```text
latent NO_PATTERN
short visible realization happens to be 3/3 or 4/4 identical
```

No single `pattern_probability` controls benchmark difficulty. Opportunity count, behavioral consistency, alternatives, context specificity, exceptions, coverage, missingness, noise, history length, and change timing are independent axes.

## 7. Benchmark tiers

### Tier S — fully synthetic

All truth, opportunities, behavior, and observation corruption are generated from protocol-controlled specifications.

Tier S is sufficient for initial L3 execution because it provides exact hidden truth, exact corruption provenance, reproducibility, and deliberate adversarial cases.

### Tier SS — semi-synthetic

Realistic event templates or non-private distributions may be derived from public datasets or manually authored traces, while personal truth, pattern structure, perturbations, correction/deletion state, and evaluation answers remain benchmark-controlled.

Tier SS is optional until Tier S reveals a realism limitation worth testing.

Private user telemetry is not required for either tier.

## 8. Scenario families

Every future L3 execution must instantiate positive, negative, and adversarial histories. Scenario families are semantic structures, not methods.

### 8.1 Routine/opportunity family

Generate explicit opportunity processes with true routine, weak/non-pattern controls, observable non-occurrence, and hidden outcomes under telemetry loss.

The hidden benchmark knows all behavioral opportunities; the visible history may expose only a subset.

### 8.2 Preference/availability family

Meaningful alternatives are explicit at every evaluable choice opportunity.

Required adversarial cases include skewed availability where the most frequently observed option is not the latent preference, so consumption frequency cannot define preference truth.

### 8.3 Conditional and relationship-conditioned family

Generate different valid behavior structures under contexts such as alone/family or known relationship presence. Include unknown relationship identity cases whose expected answer is `UNKNOWN_CONTEXT` for relationship-specific claims.

### 8.4 Temporal sequence family

Generate recurring ordered behavior, same events in inconsistent order, missing middle events, and sparse coincidental order.

No causal truth is implied.

### 8.5 Context-action/confounding family

Generate co-occurring contexts where only one scope dimension defines the latent association.

Example:

```text
meeting_end + Monday_discount + app_open
```

Truth may scope the association to `Monday_discount`. A method that assigns the pattern to `meeting_end` commits a scope/context-assignment error. This is not a causal-inference test.

### 8.6 Simpson-like aggregation family

Mandatory adversarial family.

Generate coherent conditional patterns whose aggregate counts favor a misleading global conclusion, for example:

```text
alone -> A
with family -> B
```

with unequal context/opportunity frequencies. Correct evaluation rewards the scoped patterns and penalizes global collapse.

### 8.7 Exception family

Truth explicitly contains a parent pattern plus stable exception scope/outcome. Also generate random deviations and temporal replacement controls.

The evaluator checks whether the parent is preserved, the exception is found, scope is correct, and the exception is not collapsed into global contradiction or noise.

### 8.8 Real drift family

Truth contains explicit change points and valid intervals. Observation gaps may occur independently.

Evaluation checkpoints occur before and after the true change so premature drift, delayed transition, and stale old-pattern surfacing are separately measurable.

### 8.9 Coverage-induced fake drift family

Mandatory adversarial family.

Latent behavior remains unchanged while permission, source coverage, non-wear, or device availability changes at time T.

Correct behavior is no behavioral drift claim. Depending on visible evidence, expected state may be `NOT_OBSERVABLE`, `STALE`, or another L1 abstention state.

### 8.10 Reversal family

Earlier regime supports A; later comparable opportunities support incompatible B. Truth encodes valid intervals/change point and distinguishes reversal from temporary exception, weakening, and missingness.

### 8.11 Correction/rejection family

Required cases include:

```text
user rejects inferred preference
user corrects source observation
user edits scope
user declares exception
source correction/supersession
```

The benchmark defines the correct downstream active semantic state, target scope, and historical lineage.

User rejection and behavioral latent process remain separate. Continued passive X-like behavior does not silently clear `USER_REJECTED`.

### 8.12 Deletion/reset family

Mandatory cases include user delete, source deletion, and reset request.

Truth distinguishes historical pre-deletion truth from allowed active post-deletion state. Physical storage deletion is outside L3.

### 8.13 Multi-device duplication/corroboration family

Mandatory adversarial cases include one underlying workout rendered as watch observation, repository sync copy, and phone-visible copy. Ground-truth behavioral occurrence count remains one.

Paired controls include independently observed corroborating sources without treating evidence records as multiple behavioral episodes.

### 8.14 Raw/derived evidence family

Required variants:

```text
raw only
derived only
raw + derived lineage
derived with known procedure
derived with unknown procedure
```

Behavioral truth is independent of evidence representation. Raw plus derived copies must not inflate recurrence.

### 8.15 Missingness family

Explicitly vary:

```text
missing by design
sampling gap
permission loss
device disconnected
wearable non-wear
background restriction
sync delay
history truncation
unknown missingness
```

The benchmark knows underlying behavior while visible evidence may not.

### 8.16 Observation-quality family

Hold latent behavior fixed while changing quality/coverage. This isolates whether a method incorrectly converts telemetry quality into pattern truth or numeric confidence.

### 8.17 Cold-start/new-context/new-relationship family

Include almost no history, first few opportunities, newly introduced context, and new relationship scope. Correct output often requires abstention.

### 8.18 Pattern interaction/overlap family

Generate persons with multiple simultaneously true patterns and events that support more than one truth item. Include interacting and apparently conflicting contextual slices.

The benchmark must not assume one active pattern or one event-to-one-label mapping.

### 8.19 Unidentifiable-truth family

Generate latent truth that the visible history intentionally cannot recover. `identifiable_from_visible_history=NO` makes abstention the expected outcome.

This family is mandatory because recognition quality must not be conflated with omniscience.

## 9. Negative controls

Future benchmark execution must contain substantial cases requiring no positive pattern claim.

Minimum negative categories:

```text
NO_PATTERN
random behavior
sparse coincidence
conflicting structure
insufficient opportunity
unknown critical context
unobservable history
```

At least **30% of registered evaluation units** in a standard L3 execution must require no positive pattern claim; the target band is **30–40%**, and an explicitly adversarial suite may exceed 40%.

This is a falsification balance target, not an estimate of real-world pattern prevalence.

## 10. History-length regimes

Do not freeze product durations. Use benchmark-relative regimes:

```text
few opportunities
moderate opportunities
many opportunities
```

Each regime contains both positive truth and no-pattern/abstention controls to measure premature promotion and late recognition separately.

## 11. Synthetic-person diversity

Persons vary structurally rather than demographically:

```text
few strong routines
many weak contextual structures
relationship-heavy behavior
high stable-exception rate
frequent genuine change
stable behavior with poor observability
multiple overlapping patterns
```

Demographic personas are excluded unless a later research question independently requires them.

## 12. Seed policy and reproducibility

Future execution records a master seed and deterministically derives separate streams at minimum for:

```text
scenario structure
synthetic person
behavioral realization
observation process
```

The key invariant is independent control of behavior randomness and observation randomness.

This enables paired experiments such as:

```text
same truth + same behavior realization + different telemetry corruption
different behavior realization + same observation policy
```

Seeds and seed-derived identifiers in held-out evaluation are evaluator-only and must not leak semantic labels into filenames, event payloads, IDs, or method-visible metadata.

One seed is never sufficient evidence for an adversarial-family conclusion. Future L3 execution planning must freeze repeated seeds per family, multiple persons, and multiple observation corruptions before running methods. This protocol deliberately does not freeze an arbitrary huge dataset size.

## 13. Counterfactual/adversarial pairs

Future execution requires at least **10 controlled counterfactual/adversarial pairs**.

Each pair changes one intended factor while holding relevant hidden structure constant, or changes hidden structure while holding observation conditions constant.

Required pair templates include:

1. same latent behavior: full observability vs permission loss;
2. same latent behavior: high vs degraded observation quality;
3. same behavioral episode: one evidence record vs replicated multi-device copies;
4. same observation policy: true routine vs no-pattern realization;
5. stable behavior: normal coverage vs coverage-induced fake drift;
6. identical visible counts: meaningful alternatives vs constrained availability;
7. identical aggregate counts: coherent contextual slices vs global no-split structure;
8. stable parent pattern: scoped exception vs random deviation;
9. same pre-T history: true behavior change vs observation-only change;
10. same historical pattern: no delete vs effective delete/correction transition.

Additional pairs are encouraged where they isolate generator or evaluator bugs.

## 14. Dataset split discipline

Split discipline applies even when a method is not trained.

### Development split

Published/inspectable scenario templates and development seeds may be used to debug method output format and evaluator compatibility.

### Validation split

Separate seeds and parameter combinations may be used for method selection or tuning. Any tuning decisions must be considered contaminated with respect to those combinations.

### Final held-out test

The final test contains evaluator-secret seeds plus at least one **structural holdout**, such as unseen combinations of familiar difficulty axes, held-out adversarial parameter combinations, or a held-out scenario variant within a known semantic family.

The final test cannot be repeatedly used for threshold selection or method iteration. Once exposed, it is no longer final-held-out evidence and a new held-out set is required for confirmatory claims.

No final test label, latent variable, truth ID, family label, or seed hint may appear in method-visible history paths or payloads.

## 15. Truth/history artifact separation

Future benchmark cases conceptually produce:

```text
history.json   # method-visible L2 event history
truth.json     # evaluator-only latent truth + checkpoint answers
manifest.json  # evaluator/run provenance and split assignment
```

The method receives only `history.json` and the public output contract.

Truth leakage is prohibited through:

```text
event names
fixture/case IDs
file paths
directory names
generator seed names
source/provider names
payload fields
context labels not otherwise observable
ordering of cases
manifest metadata
```

Public case identifiers must be opaque with respect to truth/family/status.

## 16. Evaluation checkpoints

Every longitudinal case registers one or more evaluator-only checkpoints.

Required checkpoint classes across the benchmark suite include:

```text
cold start
early/few opportunities
moderate history
late/many opportunities
immediately before true change
after true change
after observation loss
after correction/rejection
after deletion/reset
stale-currentness checkpoint
```

The same case may have different expected answers over time.

Initial L3 execution prioritizes incremental/online evaluation. Optional full-history batch evaluation may be reported separately and cannot replace temporal checkpoints.

## 17. Evaluation-unit contract

Before method output is inspected, the evaluator registers a finite set of semantic evaluation units from scenario truth.

Each unit specifies:

```text
person/case
checkpoint
semantic question/pattern family
scope/context
target/action/outcome
valid-time relation
exception/parent relation when relevant
expected positive pattern(s) or expected abstention/lifecycle state
```

Evaluation units solve two scientific problems:

1. the benchmark has a finite method-independent denominator for negative/abstention scoring;
2. the evaluator does not need to pretend the open universe of all imaginable patterns is enumerable.

Evaluation units are evaluator-only. Their labels must not leak into `history.json`.

## 18. Prediction-to-truth semantic matching

A future method output contract must make predictions comparable on these dimensions:

```text
pattern type
scope/context
target/action/outcome
valid time/currentness
exception/parent relation where relevant
semantic status/abstention state
```

A **full positive match** requires semantic agreement on all dimensions required by the truth item at the checkpoint.

Examples of non-full matches:

```text
correct action + wrong global scope
correct pattern type + wrong relationship identity
correct current action + stale time interval
exception outcome found but parent destroyed
```

Such predictions are not counted as full true positives. They are recorded in the relevant error dimensions, especially scope/exception/staleness.

When multiple truth patterns and predictions overlap, evaluation uses one-to-one semantic matching within an evaluation unit so duplicate predictions cannot create multiple true positives for one truth item. The exact future evaluator implementation may use deterministic maximum matching, but this protocol freezes the semantics rather than implementation code.

## 19. Metric principle

Metrics prioritize semantic correctness over positive recall.

A method that emits many patterns must not score well simply because it catches positives.

L3 freezes a **metric vector plus hard failure visibility**. It does not define a weighted aggregate `PPF_SCORE`.

## 20. Pattern precision and recall

At each checkpoint/evaluation unit:

```text
TP = method positive claims with a full semantic match
FP = method positive claims without a full semantic match
FN = expected positive truth items with no full semantic match

pattern_precision = TP / (TP + FP)
pattern_recall    = TP / (TP + FN)
```

Report micro and macro pattern precision/recall, plus by-pattern-type breakdown.

Wrong-scope or wrong-valid-time claims do not receive full positive credit even if the action/outcome matches.

## 21. False discovery and false promotion

Two complementary false-claim metrics are mandatory.

### 21.1 False discovery rate among emitted positives

```text
false_discovery_rate
= false positive active pattern claims
  / all active positive pattern claims emitted by the method
```

This denominator is method-output based and directly penalizes a recognizer that floods evaluation with speculative patterns.

If a method emits no positive claims, false-discovery rate is reported as not applicable for that slice; recall and abstention metrics still reveal whether the method simply abstained everywhere.

### 21.2 Negative-unit false promotion rate

```text
false_promotion_rate
= negative/abstention evaluation units receiving any unjustified positive pattern claim
  / all registered evaluation units whose expected visible semantic answer contains no positive active pattern claim
```

This denominator is finite, preregistered, and independent of method output.

False promotion must be reported separately for at least:

```text
NO_PATTERN
sparse coincidence
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
UNKNOWN_CONTEXT
NOT_OBSERVABLE
STALE-only currentness questions
USER_REJECTED active-state questions
DELETED active-state questions
```

These two metrics replace vague references to false positives over an undefined open universe of possible patterns.

## 22. Abstention correctness

Required abstention states include at least:

```text
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
UNKNOWN_CONTEXT
NOT_OBSERVABLE
STALE
```

Report:

```text
exact abstention correctness
wrong-positive-on-abstention rate
abstention subtype confusion matrix
unnecessary abstention on identifiable positive units
```

Numeric confidence is not required.

## 23. Scope correctness

Scope error is first-class.

Report at least:

```text
exact scope match rate
overgeneralization rate
underspecified/incorrect-context rate
relationship-scope error rate where applicable
```

Truth `with family -> mild food` does not fully match prediction `always prefers mild food`. Likewise, a Friday-evening truth does not fully match a global routine claim.

## 24. Counterexample sensitivity

The benchmark identifies evaluator-known counterevidence and controlled counterexample mutations/pairs.

Report whether method output remains semantically compatible with visible counterexamples. Examples of failure include claiming `always home` despite visible non-home outcomes, or preserving a global pattern when visible contextual slices contradict it.

At minimum report:

```text
counterexample-respected rate
overabsolute-claim rate
pairwise response correctness after counterevidence injection
```

## 25. Exception correctness

Report a vector rather than forcing one scalar:

```text
parent preserved
exception detected when identifiable
exception scope correct
exception outcome correct
random deviation not promoted as stable exception
exception not collapsed into global contradiction
temporal replacement not left as permanent exception
```

## 26. Drift and reversal metrics

Freeze these metrics:

```text
drift state correctness
reversal state correctness
false drift rate on stable-behavior controls
false drift rate on observation-loss controls
change-point latency in opportunities after true change
premature-change rate before true change
old-pattern retirement/currentness correctness
```

Change-point latency is reported as a raw number or distribution of opportunities between the true change point and the first checkpoint with the correct observable transition. No universal acceptable latency threshold is frozen here.

When post-change evidence is not yet identifiable, abstention is expected and latency is not treated as a false negative until the checkpoint answer becomes recoverable.

## 27. Correction correctness

Required dimensions:

```text
correction respected
target scope correct
old assertion no longer active when invalidated/superseded/rejected
historical provenance not confused with current truth
unrelated evidence/personalization preserved
no silent resurrection from later passive evidence while user rejection remains active
```

Report correctness rates and violation counts by correction type.

## 28. Deletion and reset correctness

Hard metric:

```text
deleted_active_return_violations
```

After deletion is effective, every active return of the deleted personalization is a failure.

Also report:

```text
deletion target/scope correctness
reset scope correctness
over-deletion rate for unrelated active personalization
post-delete stale resurrection count
```

Physical byte deletion is not evaluated by L3.

## 29. Staleness correctness

Report separately:

```text
STALE classification correctness
stale-as-current violation rate
stale-vs-reversal confusion
stale-vs-never-supported confusion
```

Staleness is not automatically drift or reversal.

## 30. Optional confidence calibration

Numeric confidence is not required for L3 benchmark compatibility.

If a tested method emits numeric confidence, future execution reports must add calibration analysis such as Brier score, expected calibration error, and reliability curves where semantically applicable. Calibration remains supplementary to semantic correctness and cannot rescue hard correction, deletion, or false-promotion failures.

## 31. Resource metrics

Future runs may record runtime, memory, retained state size, and update cost because PPF seeks minimal machinery.

Resource efficiency is secondary in L3 and cannot compensate for semantic failure.

## 32. Hard benchmark failure classes

The following must be exposed individually and may never be hidden by an aggregate score:

```text
high false promotion on negative controls
systematically treating missingness as behavioral negative evidence
systematically counting same-origin replicas as repeated independent behavior
globalizing context-specific truth
false drift under observation loss
ignoring explicit correction/rejection
returning deleted personalization as active
systematic failure to abstain when truth is unidentifiable
```

This protocol does not freeze production accept/reject thresholds. Future L3 execution planning must preregister any threshold or decision rule used to claim that a method passes a benchmark gate before final held-out results are examined.

## 33. Anti-self-confirmation rules

Mandatory benchmark design rules:

```text
truth semantics derive from frozen L1
visible event semantics derive from frozen L2
truth is generated before method output
generator does not encode expected algorithm features
no method-specific threshold defines truth
no method-specific representation defines truth
no method feature appears as hidden label in visible payload
negative controls are substantial
adversarial families deliberately attack naive success modes
structural holdout exists
final test is not iteratively tuned against
metric vector exposes failure modes separately
```

Benchmark authors must document generator choices before seeing final method results. If a scenario is added specifically because a tested method failed on it, that scenario belongs to development or a next benchmark version, not retroactively to the same confirmatory test.

## 34. Generator/method separation

Future benchmark implementation must keep these concepts separately reviewable:

```text
truth generator
behavior/opportunity generator
history renderer
observation corruptor
evaluator
external method-under-test interface
```

This protocol defines interfaces and semantics only. It does not implement those modules.

## 35. Benchmark mutation QA

Before method evaluation, future benchmark QA must perform controlled mutations and verify oracle expectations.

| Mutation | Expected latent truth | Expected visible-answer effect |
|---|---|---|
| remove a fraction of observations while leaving behavior unchanged | unchanged | may reduce identifiability/support; must not invent drift |
| add same-origin replicated evidence | unchanged | recurrence truth unchanged |
| change only platform/source provenance | unchanged | semantic truth unchanged |
| change hidden preference | changed | behavior regime/answers must change when observable |
| degrade observation quality | unchanged | may change identifiability, not latent behavior |
| apply permission loss | unchanged | may become `NOT_OBSERVABLE` or `STALE` |
| apply correction | behavioral truth may remain; active semantic state changes by correction scope | targeted expected answer changes |
| apply delete/reset | historical truth may remain; active semantic state changes | deleted/reset target must not remain active |

The mutation suite is benchmark QA, not recognition-method testing.

## 36. Oracle sanity checks

Future generator/evaluator QA must verify at least:

```text
truth -> generated opportunity/behavior is internally consistent
behavior -> visible history corruption matches observation specification
all visible records validate against the frozen L2 schema/version
visible history contains no hidden truth labels
behavior and observation random streams can be varied independently
change points align with generated behavioral regimes
exception parent/scope relations are coherent
correction/deletion timing and targets are coherent
evaluation units and expected answers are fixed before method output
counterfactual pairs differ only in declared factors
```

## 37. Difficulty axes

Future evaluation reports performance by:

```text
history length/opportunity count
opportunity density
behavioral consistency
alternative availability
context dimensionality
exception frequency
observation coverage
missingness mechanism/severity
observation quality
multi-device duplication
noise/deviation level
change frequency/timing
identifiability
```

Difficulty axes must not be collapsed into one scalar parameter.

## 38. Reporting requirements

Future L3 reports must include the complete metric vector overall and sliced at least by:

```text
pattern type
adversarial family
negative-control category
observability/coverage level
history-length regime
drift/reversal regime
correction/deletion regime
identifiability
counterfactual pair type
```

Reports must also disclose:

```text
benchmark version
split policy
seed policy
number of persons/cases/checkpoints
number and proportion of negative evaluation units
held-out structural dimensions
any tuning exposure
all hard-failure counts
```

No single average may substitute for these breakdowns.

## 39. L1 -> L2 -> L3 traceability

| Frozen L1 requirement | Frozen L2 evidence capability | L3 benchmark family | Required L3 metric/check |
|---|---|---|---|
| Routine needs comparable opportunities | explicit opportunity + observability | routine, sparse coincidence, missing-opportunity histories | routine recall, false promotion, abstention |
| Preference needs meaningful alternatives | opportunity alternatives + context | preference with skewed availability | preference precision/recall, scope correctness, false promotion |
| Context is compositional | multi-dimension known/unknown/conflicting context | conditional preference, confounder, Simpson-like slices | scope correctness, global-collapse errors, abstention |
| Relationship-conditioned claims require identity scope | entities + relationship status | known vs unknown relationship histories | relationship-scope correctness, `UNKNOWN_CONTEXT` correctness |
| Sequence requires observable order | three-time + missingness | stable order, inconsistent order, missing middle | sequence precision/recall, abstention |
| Exception preserves parent under scoped deviation | context + temporal evidence | stable exception vs random deviation vs replacement | exception correctness vector |
| Drift must differ from coverage change | observability/capture policy + three-time | real drift vs coverage-induced fake drift | drift correctness, false drift, latency |
| Reversal is temporal incompatible replacement | opportunity/context + time | A-to-B comparable-choice histories | reversal correctness, old-pattern retirement |
| Observation quality != pattern confidence | quality/coverage fields | same behavior under different quality | paired invariance, false promotion/abstention slices |
| Multi-device copies are not independent behavior | replica/corroboration relations | replicated workout vs independent-source pair | replica-inflation failure, pattern precision |
| Raw/derived are distinct evidence | evidence kind + derivation lineage | raw/derived-copy histories | duplicate-evidence sensitivity, false promotion |
| User correction/rejection is provenance-bearing | feedback/control + target/correction relations | reject/correct/edit-scope histories | correction correctness, no resurrection |
| Delete/reset differ from other lifecycle states | deletion/target lineage | delete/reset histories | deleted-active-return violations, over-deletion |
| Abstention is first-class | missingness/context/quality states | cold start, unknown context, unidentifiable truth | abstention correctness/subtype confusion |
| Stale differs from never-supported/reversed | time + observability + lineage | prior support then no recent evidence | staleness correctness |
| Facts are not manufactured by behavior | user assertion/entity provenance | repeated companion behavior with/without relationship fact | fact/pattern boundary check, relationship scope error |

## 40. Frozen L3 protocol gates

L3 benchmark protocol = PASS only if all gates are satisfied.

```text
L3P-G1  truth exists independently of method output
L3P-G2  latent behavioral truth and expected visible semantic answer are distinct
L3P-G3  behavioral realization and observation process are separately controlled
L3P-G4  opportunity/context generation is explicit where pattern semantics require it
L3P-G5  substantial negative/no-pattern controls are mandatory
L3P-G6  sparse-coincidence adversarial family is defined
L3P-G7  confounding/context-split and Simpson-like families are defined
L3P-G8  exception, drift, and reversal truth/lifecycle are explicit
L3P-G9  coverage-induced fake drift is a mandatory adversarial family
L3P-G10 correction/rejection/deletion/reset truth transitions are defined
L3P-G11 multi-device replication/corroboration attacks are defined
L3P-G12 abstention evaluation is first-class and subtype-aware
L3P-G13 false discovery and false promotion are first-class with precise denominators
L3P-G14 scope/context correctness is evaluated separately from action match
L3P-G15 drift/reversal/correction/deletion/staleness metrics are defined
L3P-G16 truth leakage controls are explicit across content, IDs, paths, seeds, and metadata
L3P-G17 development/validation/final held-out discipline includes structural holdout
L3P-G18 anti-self-confirmation and benchmark mutation/oracle defenses are explicit
L3P-G19 identifiability is represented independently of method success
L3P-G20 multiple incremental evaluation checkpoints are required
L3P-G21 no recognition algorithm, model representation, admission threshold, or generator implementation leaks into the protocol
```

## 41. Protocol STOP / REVISE conditions

### REVISE

Return `REVISE` before benchmark execution if any of these remain ambiguous:

```text
latent truth depends on visible counts after generation
identifiability depends on method success
expected semantic answer cannot be fixed before method output
negative evaluation denominator is undefined
scope matching can reward global overclaim as fully correct
user rejection/deletion active state is ambiguous
held-out split can leak family/truth labels
counterfactual mutations alter multiple uncontrolled factors
one method representation is privileged by generator/evaluator design
```

### STOP

Return `STOP` if meaningful personal-pattern truth cannot be specified independently of the recognition method, or if the benchmark cannot distinguish hidden behavioral truth from observation corruption using the frozen L2 evidence semantics.

## 42. Protocol decision

Against the frozen L1/L2 contracts and the requirements above:

```text
PPF-L3 Benchmark Protocol: PASS / FROZEN
PPF-L3 Benchmark Execution: NOT STARTED
```

Reason: method-independent latent truth, observation-bound semantic answers, explicit identifiability, opportunity-grounded generation, adversarial/negative families, leakage controls, split discipline, precise false-claim denominators, and lifecycle metrics can all be defined without selecting a recognizer.

This decision does not prove a benchmark generator is correct until a later separately authorized execution creates and QA-validates it. It does not authorize L4 or any pattern algorithm.

## 43. Next boundary

The next action after external review is **none unless separately authorized**.

Do not implement the benchmark generator in this task. Do not run benchmark cases. Do not implement or evaluate a pattern method. Do not begin L4.

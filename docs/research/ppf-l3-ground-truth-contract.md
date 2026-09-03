# PPF-L3 Ground-Truth Personal Pattern Contract

Status: **L3 BENCHMARK PROTOCOL ARTIFACT / NO GENERATOR IMPLEMENTATION**

Frozen dependencies:

- `ppf-recognize-me-contract.md` — L1 semantic authority;
- `ppf-personal-event-contract.md` and `data/ppf-l2/schema.json` — L2 visible-evidence authority.

Scope: define the minimum method-independent hidden truth and checkpoint answer needed to generate and evaluate future PPF benchmark histories. This contract does not define a detector, score, admission threshold, baseline, model, training procedure, or production representation.

## 1. Hard rule

Benchmark truth exists before and independently of any recognition method.

```text
method output
must never define
latent truth or expected semantic answer
```

Future benchmark generation follows this conceptual order:

```text
hidden personal truth
        ↓
opportunity + context process
        ↓
behavioral realization
        ↓
observation process
        ↓
missingness / delay / quality / replication / correction artifacts
        ↓
visible L2-compliant event history
```

The method receives only the visible L2 history available at an evaluation checkpoint. The evaluator receives the hidden truth contract and checkpoint answer.

## 2. Two-level ground truth

PPF-L3 freezes two distinct truth levels.

### Level 1 — latent behavioral truth

What is actually true in the synthetic person's hidden behavioral process, including patterns that may be partially or completely hidden by the observation process.

Examples:

```text
routine exists
preference exists under context C
stable scoped exception exists
behavior reverses at change point T
no pattern exists
```

### Level 2 — expected visible semantic answer

What a correct PPF recognizer is allowed to claim at a specific checkpoint from the visible L2-compliant evidence then available.

Examples:

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

Level 2 prevents the evaluator from rewarding omniscience. A latent routine can exist while the correct visible answer is `NOT_OBSERVABLE`, `STALE`, or `INSUFFICIENT_EVIDENCE`.

## 3. Truth domains

The truth manifest separates three domains that must never be inferred from one another by benchmark construction.

### 3.1 Fact truth

Directly established personal facts, such as a relationship identity, are represented independently from behavioral recurrence.

Example:

```text
relationship(child, entity-7)
```

Repeated behavior with `entity-7` must not manufacture the `child` fact label.

### 3.2 Behavioral pattern truth

The latent personal behavior structures being evaluated.

Required pattern types:

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

### 3.3 Explicit negative/control truth

Required negative states include:

```text
NO_PATTERN
INSUFFICIENT_TRUE_SUPPORT
CONFLICTING_STRUCTURE
```

These are generator/evaluator truth states. They do not introduce a universal numeric pattern-admission threshold.

`INSUFFICIENT_TRUE_SUPPORT` means the benchmark intentionally defines a history regime in which a positive stable pattern is not part of the latent truth, even if a short realization happens to look regular. It is not computed by applying a count threshold to visible observations.

## 4. Minimum conceptual truth record

A future machine-readable representation may use different field names, but each evaluable latent pattern needs the following semantics.

| Concept | Required meaning |
|---|---|
| truth/person identity | Which synthetic person/scenario owns the truth; never exposed as a semantic hint. |
| `pattern_id` | Stable benchmark-local identity for one latent truth item. |
| `pattern_type` | One required L1-compatible behavioral pattern shape. |
| `truth_status` | Positive truth, negative/control truth, or lifecycle state. |
| scope/context | The dimensions under which the truth applies. |
| target/action/outcome | What behavior, choice, ordered relation, or association the truth asserts. |
| valid time | Start/end or regime interval in which the latent truth applies. |
| opportunity definition | What constitutes a comparable opportunity and, for preference, the meaningful choice set. |
| behavioral outcome rule | Generator-side rule that realizes behavior; method-independent and hidden. |
| exceptions/counterexamples | Stable scoped exception relations and ordinary deviations/counterevidence. |
| parent/interaction relations | Parent pattern, overlap, or interaction with other true patterns where relevant. |
| change points | Explicit latent regime transitions for drift/reversal. |
| correction state | User/source correction/rejection state and effective time/scope. |
| deletion/reset state | Active-state deletion/reset semantics and effective time/scope. |
| identifiability | Whether Level-1 truth is recoverable from visible evidence at the checkpoint. |
| expected semantic answer | Level-2 answer the evaluator should expect from visible evidence. |

The truth representation must not contain future method features such as a detector score, embedding, learned state, method confidence, threshold, cluster ID, or model-specific hypothesis object.

## 5. Scope representation

Truth scope is compositional and platform-neutral, following L1/L2 semantics.

Examples:

```text
weekday = true
time_band = after_work
social = alone
relationship = child_present
location_category = work_exit
```

Scopes may overlap. One event can support multiple true patterns. Two apparently conflicting patterns may both be true under distinct scopes.

The truth contract therefore forbids a one-event-to-one-label assumption.

## 6. Opportunity truth

Any truth whose meaning depends on opportunities must define the opportunity process independently of visible observation.

For a routine, the hidden benchmark knows every relevant opportunity and behavioral outcome, including opportunities later hidden by telemetry loss.

For a preference, the hidden benchmark additionally knows the meaningful alternatives available on each choice opportunity.

Example hidden opportunity sequence:

```text
30 commute opportunities
18 realized home
7 realized other destination
2 realized observable non-action
3 realized outcomes later hidden by observation corruption
```

The visible history may expose fewer than 30 opportunities or outcomes. The latent denominator must not be reconstructed from visible event count.

## 7. Behavioral realization is distinct from observation stochasticity

Pattern strength is not a single `pattern_probability` parameter.

The hidden behavioral process may independently vary:

```text
opportunity count
behavioral consistency
alternative availability
context specificity
exception rate
ordinary random deviation
history length
change timing
```

The observation process separately varies:

```text
coverage
missingness mechanism
source quality
delay / batching
history truncation
multi-device replication/corroboration
raw/derived representation
```

Independent random streams must permit the same latent truth/behavior realization to be rendered under different telemetry corruption, and vice versa.

## 8. Exceptions and counterexamples

An `EXCEPTION` truth item requires:

```text
parent_pattern_id
exception_scope
exception_outcome
valid_time
```

The parent remains valid in its complementary scope. Ordinary random deviations are recorded as behavioral realizations/counterexamples but do not automatically become exception truth.

The benchmark must be able to distinguish:

```text
stable scoped exception
random deviation
unresolved conflict
temporal replacement/drift
```

## 9. Drift and reversal truth

Behavioral change uses explicit latent regime boundaries.

Minimum change semantics:

```text
prior_pattern_id / prior regime
change_point
new regime or changed scope
valid intervals
```

`DRIFT` indicates a time-scoped change in form, scope, or applicability. `REVERSAL` is a directional replacement by an incompatible alternative under comparable opportunities/context.

Observation coverage changes do not modify latent behavioral truth. A coverage drop with unchanged behavior is a separate adversarial truth condition whose Level-2 answer may become `NOT_OBSERVABLE` or `STALE`, not drift.

## 10. Correction and rejection truth

The truth contract keeps two states separate:

```text
behavioral latent process
user/source correction state
```

A user rejection can make an active personalization claim `USER_REJECTED` while later passive behavior continues to resemble the rejected behavior.

The benchmark must not silently allow passive evidence to resurrect the same active claim. Re-activation requires an explicit truth transition defined by the benchmark scenario, such as a new user confirmation or a separately specified post-correction semantic state. Merely continuing the same passive behavior is insufficient to clear `USER_REJECTED`.

Correction records must identify:

```text
correction type
target
scope
effective checkpoint/time
resulting active semantic state
```

Historical source evidence remains distinguishable from the current active interpretation.

## 11. Deletion and reset truth

Deletion truth separates:

```text
historical latent truth before deletion
active semantic state after deletion takes effect
```

The benchmark scores semantic active-state behavior only. It does not define physical storage deletion.

After effective deletion, the expected active answer for the deleted personalization is `DELETED`; returning the deleted personalization as active is a hard violation.

A reset can target a broader personalization scope. Unrelated truth outside that scope must remain independently evaluable so over-deletion can be detected.

## 12. Identifiability

Each evaluation checkpoint labels how recoverable the relevant latent truth is from visible evidence:

```text
YES
PARTIAL
NO
```

Interpretation:

- `YES`: visible evidence is deliberately sufficient in semantic ingredients for the benchmark's expected positive/current answer;
- `PARTIAL`: some truth dimensions are recoverable but at least one required scope/status dimension is not fully justified;
- `NO`: the visible history intentionally cannot justify the latent truth; the correct result is generally an L1 abstention state.

Identifiability is an evaluator truth label. It is not exposed to the method.

It must be derived from the scenario specification and observation process, not from whether a particular method happened to succeed.

## 13. Expected visible semantic answer

At every registered evaluation checkpoint, the evaluator defines a finite set of evaluation units before method output is inspected.

An evaluation unit identifies the semantic question being judged, for example:

```text
person/checkpoint
pattern type or abstention question
scope/context
target/action/outcome
active-time relation
parent/exception relation if applicable
```

Its expected answer contains:

```text
positive supported pattern(s), if justified
or
required abstention/lifecycle state

plus allowed scope
plus forbidden overgeneralizations
plus applicable counterevidence/exception relations
```

Evaluation units are registered from benchmark truth/scenario design before method output and are evaluator-only. This gives false-promotion metrics a finite method-independent denominator without pretending that the universe of all possible patterns is enumerable.

## 14. Evaluation time

Truth is checkpointed. The same longitudinal history can have different expected answers at:

```text
cold start
after a few opportunities
after moderate history
before change
after true change
after coverage loss
after correction/rejection
after deletion/reset
late/stale period
```

The benchmark must prioritize incremental/online checkpoints. Full-history batch evaluation may be supported later, but cannot replace checkpoint evaluation for drift, stale state, correction, and deletion.

## 15. Tiny illustrative examples

These are truth-contract examples only, not generated datasets and not admission thresholds.

### Example 1 — true routine, visible support

```text
latent_truth:
  type = ROUTINE
  scope = weekday_after_work
  outcome = home

checkpoint answer:
  identifiable = YES
  expected = SUPPORTED scoped routine
```

### Example 2 — sparse coincidence control

```text
latent_truth:
  NO_PATTERN

behavior realization:
  first 3 opportunities happen to select A

checkpoint answer:
  identifiable = YES
  expected = INSUFFICIENT_EVIDENCE / no stable positive pattern
```

### Example 3 — latent preference hidden by availability

```text
latent_truth:
  PREFERENCE for A when A/B/C are meaningfully available

history regime:
  B is much more frequently available

checkpoint answer:
  evaluate preference using observed choice sets, not raw consumption frequency
```

### Example 4 — same behavior, lost observability

```text
latent_truth:
  ROUTINE unchanged

observation process:
  permission revoked at T

checkpoint answer after T:
  identifiable = NO or PARTIAL
  expected = NOT_OBSERVABLE or STALE
  forbidden = DRIFT claim from disappearance alone
```

### Example 5 — scoped exception

```text
parent:
  weekdays -> home

exception:
  Wednesday -> child pickup first

expected:
  preserve parent + recognize Wednesday exception
```

### Example 6 — reversal

```text
before T:
  comparable choices -> A

after T:
  comparable choices -> B

expected after observable transition:
  prior A historical/superseded in current scope
  B current
  reversal state recognized
```

### Example 7 — user rejection with similar later behavior

```text
behavioral latent process:
  X-like choices continue

user semantic state:
  USER_REJECTED X at T

expected after T:
  do not surface X as active merely from passive recurrence
```

### Example 8 — deletion

```text
before T:
  routine X historically valid

at T:
  delete X becomes effective

expected after T:
  DELETED active state
  returning active X = violation
```

### Example 9 — overlapping truth

```text
one Friday gym event may support:
  Friday routine
  context-action association
  temporal sequence endpoint

truth representation:
  multiple pattern_ids may reference overlapping behavioral events
```

## 16. What this contract does not decide

This contract does not decide:

```text
how many observations are enough in production
which statistical test recognizes a pattern
which threshold admits a pattern
which model representation is used
how confidence is calculated
how state is stored or indexed
how deleted bytes are physically removed
how mobile telemetry is collected
```

Those decisions cannot be used to define L3 benchmark truth.

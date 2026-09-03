# PPF-L1 Recognize-Me Contract

Status: **L1 SEMANTIC PROOF ARTIFACT**

Protocol basis: `ppf-l1-l2-foundation-protocol.md` v2 at `d9bab4cf0bcd68dc9f2a3ad4084b7e6cfa97d3a3`

Scope: define what PPF may claim about one person from bounded personal-history evidence without selecting an algorithm, threshold, confidence model, storage system, or platform implementation.

## 1. Contract rule

For any bounded scenario, a reviewer must be able to determine:

1. what kind of semantic claim the evidence can support;
2. what context/opportunity scope applies;
3. whether PPF must abstain;
4. what the evidence does **not** justify;
5. which user correction/deletion state changes the active claim.

The contract is deliberately non-probabilistic. Numeric pattern confidence and admission thresholds are outside L1 and require later proof.

The semantic universe is **not a mutually exclusive taxonomy**. `PATTERN` is an umbrella claim; routine, preference, sequence, relationship-conditioned behavior, and context-action association are claim shapes that may overlap. Exception and change/drift qualify relationships among claims over context or time. Explicit user correction is a provenance-bearing semantic operation, not a behavioral pattern type.

## 2. Semantic universe

### FACT

**Definition.** A personal datum asserted or established as a datum rather than inferred from recurring behavior.

**Required semantic evidence.** An explicit assertion or other evidence whose meaning directly establishes the datum. Provenance must remain knowable conceptually.

**Positive example.** User states, “Alice is my spouse.” The asserted relationship may be represented as a fact with user provenance.

**Negative example.** The user messages Alice after work on many occasions. That does not establish that Alice is the spouse.

**Not.** Not an observation merely because it was observed; not a recurring behavioral pattern; not a preference.

**Boundary.** An observation is evidence that something was observed/asserted. A fact is the datum the evidence directly establishes. A pattern is a recurring relation inferred across evidence.

### OBSERVATION

**Definition.** A provenance-bearing record that a source observed, derived, or explicitly reported an occurrence, state, choice, or assertion.

**Required semantic evidence.** A source and an observed/derived/asserted content item. L1 requires provenance conceptually but does not define its L2 representation.

**Positive example.** “At dinner, the user selected a Japanese restaurant from the displayed alternatives.”

**Negative example.** “The user prefers Japanese food.” That is a higher-level claim, not a single observation.

**Not.** Not automatically a fact, pattern, preference, or causal explanation.

**Boundary.** Multiple observations can support one or several pattern claims. One observation can also be relevant to several candidate patterns without itself becoming any of them.

### CURRENT CONTEXT

**Definition.** The set of presently relevant contextual dimensions under which an observation or pattern claim is interpreted.

**Required semantic evidence.** One or more context dimensions whose values and observability are known well enough for the claim being evaluated.

**Positive example.** Friday + 17:40 + leaving office + alone + walking + phone available.

**Negative example.** “Commute” as a forced single label when social context and day-of-week materially change the behavior.

**Not.** Not a universal ontology and not a causal explanation.

**Boundary.** Context is compositional. A missing required dimension can make a context-conditioned claim `UNKNOWN_CONTEXT` even when other dimensions are known.

### PATTERN

**Definition.** A recurring, scoped relation supported across multiple relevant evidence instances/opportunities, rather than an isolated occurrence.

**Required semantic evidence.** Repetition or recurrence plus the semantic ingredients required by the specific pattern shape: opportunities for routines, alternatives for preferences, order for sequences, context for associations, and so on.

**Positive example.** Across comparable observable after-work opportunities, a recurring home-commute behavior is present.

**Negative example.** Three isolated matching events with no basis for stability are not automatically a stable pattern.

**Not.** Not a single observation, fact, causal law, or statistical score.

**Boundary.** `PATTERN` is an umbrella semantic layer. Specific claims should carry the more precise shape when available.

### ROUTINE

**Definition.** A recurring behavior under comparable context and **observable opportunities**.

**Required semantic evidence.** Recurring behavior + comparable context + a knowable set of opportunities whose outcomes were observable or explicitly unknown. The opportunity denominator may be qualitative or counted in a scenario; L1 sets no admission threshold.

**Positive example.** 18 home trips out of 21 comparable observable after-work commute opportunities, with the remaining observable outcomes known.

**Negative example.** 18 home trips with an unknown number of commute opportunities.

**Not.** Not frequency alone and not preference merely because the action recurs.

**Boundary.** Routine asks “what recurs when the opportunity/context arises?” Preference asks “what is selected when meaningful alternatives exist?” A routine can coexist with a preference but neither implies the other.

### PREFERENCE

**Definition.** A choice tendency under meaningful choice opportunities where meaningful alternatives existed, or an explicit self-reported preference preserved as such.

**Required semantic evidence.** For behavioral inference: choice opportunity + meaningful alternatives + observed selection tendency. For explicit preference: a user assertion with provenance and scope. Explicit and behaviorally inferred preference must remain distinguishable.

**Positive example.** Across dining opportunities with several reasonable cuisines available, Japanese is repeatedly selected; or the user explicitly states “I prefer Japanese food.”

**Negative example.** Japanese is eaten 20 times because it is the only practical option.

**Not.** Not consumption frequency, availability, habit, or causal motivation.

**Boundary.** An explicit preference is a user-sourced preference assertion; it does not rewrite passive history. A behavioral preference requires alternatives, unlike a routine.

### RELATIONSHIP-CONDITIONED BEHAVIOR

**Definition.** A pattern whose scope or form differs under a person/entity relationship or social context.

**Required semantic evidence.** A relationship/social context that is itself sufficiently identified, plus behavior observed across comparable opportunities within that scope.

**Positive example.** Alone the user repeatedly selects spicy food; with the child the user repeatedly selects non-spicy food.

**Negative example.** One non-spicy meal with the child.

**Not.** Not proof that the person caused the behavior.

**Boundary.** This is a named specialization of context-conditioned pattern semantics because person identity/relationship is a materially reviewable scope. It is not a separate causal primitive.

### TEMPORAL SEQUENCE

**Definition.** A recurring ordered relation among observations/actions where order is part of the claim.

**Required semantic evidence.** Repeated occurrence of the relevant ordered relation with sufficient temporal observability to distinguish order from missing events.

**Positive example.** Leaves work → opens Maps → messages spouse recurs in that order.

**Negative example.** The same three actions occur frequently but in inconsistent orders.

**Not.** Not a routine solely because events recur; not causal dependence.

**Boundary.** Routine concerns recurring behavior under opportunities; sequence concerns recurring order. A sequence can itself be routine-like, but the order relation remains independently necessary.

### CONTEXT→ACTION ASSOCIATION

**Definition.** A recurring association between a compositional context and an action/outcome.

**Required semantic evidence.** Repeated action/outcome observations under a sufficiently known context, with relevant comparison/counterevidence available where needed to avoid collapsing conflicting contextual slices.

**Positive example.** Under Friday-evening + leaving-office + alone context, navigation to the gym recurs.

**Negative example.** Gym navigation happened once after a Friday meeting.

**Not.** Not causality. The context is not claimed to produce the action.

**Boundary.** Relationship-conditioned behavior is a specialization where the contextual dimension is a person/relationship. Sequence is about order, not merely co-occurrence under context.

### EXCEPTION

**Definition.** A repeatable or semantically declared scoped deviation from a broader pattern that leaves the broader pattern valid in its remaining scope.

**Required semantic evidence.** A parent pattern plus a distinguishable condition/scope under which the deviation is coherent. A user may also explicitly declare an exception.

**Positive example.** General weekday commute → home; Wednesdays → child pickup first.

**Negative example.** One unexplained detour in an otherwise stable commute history.

**Not.** Not automatically random noise, counterevidence to the entire parent, or temporal replacement of the parent.

**Boundary.** Exception is context-scoped. Drift/reversal is time-scoped change in the pattern itself. Contradictory evidence without a coherent scope is `CONFLICTING_EVIDENCE`, not automatically an exception.

### CHANGE / DRIFT

**Definition.** A temporal change in a previously supported pattern’s form, scope, or applicability across comparable observable opportunities.

**Required semantic evidence.** A prior supported pattern; later comparable opportunities; adequate observability in both periods; evidence that the behavior relation changed rather than only telemetry coverage.

**Positive example.** A formerly stable morning coffee choice moves to afternoon across later comparable, fully observable days.

**Negative example.** Morning coffee records disappear on the same date a permission is revoked.

**Not.** Not missingness, one-off exception, or stale evidence by itself.

**Boundary.** `WEAKENING` means the prior relation is less consistently supported but not clearly replaced; `DRIFT` is changed behavior/scope; `REVERSAL` is a directional replacement by an incompatible alternative; `STALE` means current applicability cannot be supported because evidence freshness is inadequate, not that behavior is known to have changed.

### EXPLICIT USER CORRECTION

**Definition.** A provenance-bearing user operation that changes how an assertion/observation is semantically treated without silently rewriting historical evidence.

**Required semantic evidence.** User source, target of correction, operation type, scope, and temporal applicability sufficient to interpret the correction. Exact storage/lineage representation belongs to L2.

**Positive example.** User says, “No, that location event was wrong; I was not at the gym.” The targeted observation can be corrected/invalidated as evidence while the original record remains historical provenance.

**Negative example.** Silently editing a stored pattern from “gym” to “home” with no record of what changed or why.

**Not.** Not proof that all passive observations are false; not the same as delete.

**Boundary.** Correction changes semantic validity/scope. Deletion requests removal from active/retrievable PPF state. Rejection targets an assertion; correction may target an observation; reset has broader scope.

## 3. Abstention/status contract

| State | When it applies | PPF may claim | PPF must not claim | Example |
|---|---|---|---|---|
| `SUPPORTED` | Required semantic ingredients are present and the bounded scenario provides coherent supporting evidence | The scoped claim described by the evidence | Universal truth, causality, or unscoped generalization | Repeated home commute across comparable observable opportunities |
| `INSUFFICIENT_EVIDENCE` | A required ingredient or enough semantic evidence for recurrence/choice/order is absent | That evidence exists, and what is missing | Stable pattern | 3/3 matching events with only three sparse opportunities |
| `CONFLICTING_EVIDENCE` | Material evidence supports incompatible claims and no coherent context/time split resolves it | The conflict and known slices | One collapsed global pattern | Similar comparable contexts support opposite destinations with no known splitter |
| `STALE` | A formerly supported claim lacks evidence current enough for the requested present-time scope | Historical pattern existed; current applicability is stale | That the old pattern still applies now or that it reversed | Old commute pattern, no recent observable period |
| `UNKNOWN_CONTEXT` | A context dimension required to scope the claim is unknown/ambiguous | Known evidence plus missing context requirement | Context-specific claim | Restaurant choices known but companion identity unknown for a relationship-conditioned claim |
| `NOT_OBSERVABLE` | The relevant opportunity/outcome could not be observed | Observability failure/unknown outcome | Non-occurrence or behavioral negative | Permission absent during commute window |
| `USER_REJECTED` | User explicitly rejects an active inferred/asserted personalization claim within a defined scope | That the claim was rejected and underlying evidence remains historical unless separately corrected/deleted | Continue surfacing the rejected claim as active personalization | “Stop assuming I prefer X.” |
| `SUPERSEDED` | A newer assertion/correction replaces an older assertion for the same semantic scope | Historical lineage and the newer active assertion | Treat both as simultaneously current for the same scope | User edits “weekday gym” to “Tue/Thu gym” |
| `DELETED` | User/source deletion semantics remove information from active/retrievable PPF state | Only deletion state/lineage as permitted by later design | Return the deleted information as active personal state | User requests deletion of a personal pattern |

Numeric pattern confidence is outside L1. If introduced later, it requires independent calibration proof. L1 uncertainty is semantic, not probabilistic.

## 4. Observation quality vs pattern support

Hard invariant:

```text
observation quality != pattern support/confidence
```

A single high-quality observation can remain insufficient to establish a pattern. A degraded observation source can coexist with a supported pattern if other valid evidence supports it. Observation quality describes evidence quality/coverage; pattern support describes whether the semantic claim is justified by the evidence set.

## 5. User-correction operations

| Operation | Semantic effect | Does not mean |
|---|---|---|
| `CONFIRM` | User explicitly affirms the targeted claim in the stated scope | Passive history is rewritten or future behavior is guaranteed |
| `REJECT` | Targeted personalization claim becomes `USER_REJECTED` in scope | Underlying observations are deleted |
| `EDIT_SCOPE` | Earlier assertion is superseded by a scope-corrected assertion | Historical assertion vanishes |
| `DECLARE_EXCEPTION` | Adds/affirms a scoped exception relation to a broader claim | Parent pattern is globally invalidated |
| `CORRECT_OBSERVATION` | Marks a targeted observation/derived assertion as corrected/invalid for relevant evidence use, preserving provenance | Silent overwrite or automatic deletion |
| `REQUEST_DELETE` | Requests deletion semantics for targeted information and affected active derived state | Mere hiding or rejection |
| `RESET_PERSONALIZATION` | Requests broad removal/deactivation of personalization state in the defined reset scope | Erasing unrelated host/app data outside PPF |

If later passive evidence conflicts with a user rejection/correction, L1 does not let that evidence silently resurrect the same active claim. The correction’s scope/time and the new evidence must be represented and reviewed. Whether a genuinely new post-correction pattern is later admitted is a future benchmark/policy question, not an algorithm chosen here.

## 6. Deletion/replacement semantics

| Operation/state | Semantic effect |
|---|---|
| `HIDE` | Do not surface the information, while its semantic validity may remain unchanged. |
| `DEACTIVATE` | Do not use the assertion as active personalization until reactivated/re-established; historical validity may remain. |
| `INVALIDATE` | The assertion/observation is no longer valid evidence for the targeted interpretation. |
| `SUPERSEDE` | A newer assertion replaces an older one for the same scope; old provenance remains historical. |
| `DELETE` | Targeted information must not remain active/retrievable from PPF merely through stale derived state/cache/index. Physical mechanics are deferred. |
| `RESET PERSONALIZATION` | Broad user-directed clearing/deactivation of PPF personalization state in the reset scope; exact physical mechanics are deferred. |

`USER_REJECTED != DELETE`, `INVALIDATE != DELETE`, and `SUPERSEDE != DELETE`.

## 7. Category interaction matrix

| Concept A | Concept B | Same? | Key distinction |
|---|---|---|---|
| Observation | Fact | No | evidence item vs directly established datum |
| Observation | Pattern | No | single evidence item vs recurring scoped relation |
| Routine | Preference | No | recurring behavior under opportunities vs selection among meaningful alternatives |
| Routine | Sequence | No | recurring behavior under opportunity vs recurring ordered relation |
| Preference | Frequency | No | meaningful alternatives/choice are required |
| Relationship-conditioned behavior | Context-action association | Subtype | person/relationship is a specific compositional context dimension |
| Exception | Counterevidence | Not necessarily | coherent scoped deviation may preserve parent pattern; unscoped contradiction is counterevidence |
| Exception | Drift | No | context-scoped deviation vs temporal change to the pattern |
| Drift | Missingness | No | behavioral change vs evidence-coverage change |
| Sequence | Causality | No | recurring order vs causal mechanism |
| Context association | Causality | No | co-occurrence/conditioning vs causal mechanism |
| User rejection | Invalidation | No | user rejects personalization claim vs evidence/assertion becomes semantically invalid |
| Invalidation | Delete | No | invalid for inference vs removed from active/retrievable PPF state |
| Supersede | Delete | No | replacement with lineage vs deletion |
| Stale | Insufficient evidence | No | formerly supported but not current vs never sufficiently supported for requested claim |
| Observation quality | Pattern support | No | evidence quality/coverage vs semantic support across evidence |

## 8. Minimality review

| Semantic concept | Decision | Reason |
|---|---|---|
| FACT | KEEP | required to prevent behavioral evidence from inventing personal facts |
| OBSERVATION | KEEP | preserves evidence vs conclusion boundary |
| CURRENT CONTEXT | KEEP | required for scope, opportunity, exceptions, and compositional conditioning |
| PATTERN | KEEP as umbrella | necessary boundary between evidence and recurring personal claim; not a peer leaf taxonomy |
| ROUTINE | KEEP | opportunity denominator is an independently necessary semantic distinction |
| PREFERENCE | KEEP | meaningful alternatives/choice distinguish it from recurrence |
| RELATIONSHIP-CONDITIONED BEHAVIOR | KEEP as named specialization | semantically a context-association subtype, but retaining the named specialization exposes relationship identity/scope uncertainty explicitly without adding a new primitive |
| TEMPORAL SEQUENCE | KEEP | order is independent from frequency/context co-occurrence |
| CONTEXT→ACTION ASSOCIATION | KEEP | captures non-causal context-conditioned recurrence beyond routine/choice/sequence |
| EXCEPTION | KEEP as qualifier | needed to preserve scoped deviations without collapsing parent pattern |
| CHANGE/DRIFT | KEEP as lifecycle relation | distinguishes temporal behavioral change from static pattern and missingness |
| EXPLICIT USER CORRECTION | KEEP as operation/evidence role | user control, rejection, correction, deletion, and scope edits cannot be represented as ordinary passive pattern evidence |

No semantic distinction is removed. The minimality constraint is satisfied by treating several listed concepts as **roles/specializations**, not by creating independent ontology entities for each label.

## 9. L1 → L2 semantic dependencies

L1 requires L2 later to make the following evidence properties representable; L1 does not define how:

- observable opportunity and observable non-occurrence information;
- observability/missingness state and coverage limitations;
- compositional context dimensions and whether required dimensions are known;
- occurrence/result/ingestion time semantics sufficient to establish order and freshness;
- source/provenance and observation-quality information;
- relationship/entity identity references sufficient to scope relationship-conditioned claims;
- explicit user feedback provenance, target, scope, and time;
- correction/supersession/deletion lineage;
- raw/derived evidence distinction when it affects interpretation.

If these inputs are unavailable, the appropriate L1 result is often abstention (`UNKNOWN_CONTEXT`, `NOT_OBSERVABLE`, `INSUFFICIENT_EVIDENCE`, or `CONFLICTING_EVIDENCE`), not a fabricated negative.

## 10. Authority boundary

PPF may recognize, retrieve, report supporting/counterevidence, and report uncertainty. It has no authority to execute actions.

```text
PPF                 -> recognize / retrieve / report evidence and uncertainty
MindForge-Mobile    -> understand / reason / route
Host / OS / app     -> authorize / execute
```

This contract selects no algorithm, numeric threshold, confidence model, database, storage architecture, model family, or mobile framework.

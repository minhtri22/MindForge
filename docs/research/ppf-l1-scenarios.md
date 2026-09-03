# PPF-L1 Semantic Scenario Set

Status: **L1 PROOF SCENARIOS / NO IMPLEMENTATION**

Protocol basis: PPF-L1/L2 Foundation Protocol v2.

Scenario count: **41**. `[ADV]` marks an explicit adversarial/falsification scenario. Numbers are evidence descriptions, never admission thresholds.

For recurring claims marked `SUPPORTED`, the scenario itself stipulates that recurrence is established within the bounded history; any counts illustrate opportunity/context structure rather than define a general admission rule. Borderline quantitative sufficiency is intentionally not solved in L1.

## S01 — Explicit relationship fact

- **Evidence:** User states, “Alice is my spouse.”
- **Opportunity/context:** Direct user assertion; no behavioral opportunity is needed.
- **Observability limitations:** None relevant to the assertion itself.
- **Explicit feedback:** The assertion is the user input.
- **Question:** What may PPF claim?
- **Expected classification:** `FACT` (user-asserted relationship datum) plus an `OBSERVATION` of the assertion.
- **Expected status:** `SUPPORTED` for the scoped asserted fact.
- **Allowed claim:** Alice is asserted by the user to be the spouse.
- **Forbidden claim:** Messaging frequency proves the relationship or that the relationship is externally verified.
- **Reason:** Direct assertion establishes the datum semantically; behavior is not needed to infer it.
- **Relevant gates:** L1-G1, G2, G9.

## S02 — One restaurant choice is only an observation

- **Evidence:** User selects Japanese from Japanese, Vietnamese, and Korean once.
- **Opportunity/context:** One real dining choice opportunity with alternatives.
- **Observability limitations:** Choice is fully observed.
- **Explicit feedback:** None.
- **Question:** May PPF claim a Japanese preference?
- **Expected classification:** `OBSERVATION`; candidate preference evidence only.
- **Expected status:** `INSUFFICIENT_EVIDENCE` for behavioral preference.
- **Allowed claim:** One Japanese choice was observed among alternatives.
- **Forbidden claim:** User prefers Japanese food.
- **Reason:** Alternatives exist, but one choice does not establish a recurring selection tendency.
- **Relevant gates:** L1-G2, G4, G8.

## S03 — Opportunity-aware commute routine

- **Evidence:** 18 home trips among 21 comparable observable after-work commute opportunities; remaining outcomes are known alternatives.
- **Opportunity/context:** Weekday, workday ended, commute opportunity, comparable location/context.
- **Observability limitations:** All 21 opportunities are observable.
- **Explicit feedback:** None.
- **Question:** What pattern shape is semantically permitted?
- **Expected classification:** `ROUTINE` scoped to the stated commute context.
- **Expected status:** `SUPPORTED` within this bounded history.
- **Allowed claim:** Going home recurs under comparable observable after-work opportunities.
- **Forbidden claim:** The user always goes home, prefers home, or work ending causes the trip.
- **Reason:** Recurrence, comparable context, and opportunity denominator are all present.
- **Relevant gates:** L1-G3, G11.

## S04 — Occurrences with unknown denominator

- **Evidence:** 18 observed home trips; number of after-work commute opportunities is unknown.
- **Opportunity/context:** Some after-work contexts are known, total comparable opportunities are not.
- **Observability limitations:** Coverage/opportunity denominator unknown.
- **Explicit feedback:** None.
- **Question:** May PPF claim a routine?
- **Expected classification:** `OBSERVATION` set relevant to a possible routine.
- **Expected status:** `INSUFFICIENT_EVIDENCE` for routine.
- **Allowed claim:** Home trips recurred in observed data.
- **Forbidden claim:** Home is the user's routine after work.
- **Reason:** Occurrence count without observable opportunities cannot characterize recurrence under opportunity.
- **Relevant gates:** L1-G3, G8.

## S05 — [ADV] Three-of-three sparse coincidence

- **Evidence:** Three observed Monday commutes all go home.
- **Opportunity/context:** Only three comparable observable opportunities exist in the bounded history.
- **Observability limitations:** Those three are observable; longitudinal stability is absent.
- **Explicit feedback:** None.
- **Question:** Is a stable Monday routine permitted?
- **Expected classification:** Sparse recurring observations, not an admitted stable routine.
- **Expected status:** `INSUFFICIENT_EVIDENCE`.
- **Allowed claim:** All three observed Monday opportunities ended at home.
- **Forbidden claim:** Stable Monday-home routine.
- **Reason:** Protocol explicitly requires sparse-coincidence falsification; matching sparse cases cannot automatically become stable patterns.
- **Relevant gates:** L1-G3, G8, G13.

## S06 — Explicit stated preference

- **Evidence:** User says, “I prefer Japanese food when choosing dinner for myself.”
- **Opportunity/context:** Scope explicitly says self-choice dinner.
- **Observability limitations:** Passive behavior is not needed to represent the assertion.
- **Explicit feedback:** Direct preference assertion.
- **Question:** What preference may PPF represent?
- **Expected classification:** `PREFERENCE`, subtype explicit/user-stated; also an observation of user assertion.
- **Expected status:** `SUPPORTED` as an explicit preference assertion.
- **Allowed claim:** User explicitly states the scoped preference.
- **Forbidden claim:** Passive behavior independently confirms it or it applies when dining with family.
- **Reason:** Contract allows explicit preference while preserving provenance and scope separately from behavioral inference.
- **Relevant gates:** L1-G2, G4, G9.

## S07 — Behavioral preference with alternatives

- **Evidence:** Across recurring dinner choices, several reasonable cuisines are available and Japanese is repeatedly selected; counterchoices are also observed.
- **Opportunity/context:** Comparable self-choice dinners with meaningful alternatives.
- **Observability limitations:** Choice sets and selected outcomes are observable.
- **Explicit feedback:** None.
- **Question:** What may PPF claim?
- **Expected classification:** Behaviorally inferred `PREFERENCE` scoped to these dinners.
- **Expected status:** `SUPPORTED` in the bounded evidence summary.
- **Allowed claim:** Japanese is a recurring selection tendency when meaningful alternatives are available in this scope.
- **Forbidden claim:** Japanese is universally preferred or selection is caused by an observed context.
- **Reason:** Choice opportunity, alternatives, and recurring selection tendency are all stipulated.
- **Relevant gates:** L1-G4, G11.

## S08 — [ADV] Frequency without choice

- **Evidence:** User eats Japanese food 20 times; it is the only practical food option on all 20 occasions.
- **Opportunity/context:** Meal opportunities exist, but no meaningful alternative choice set exists.
- **Observability limitations:** Meals are observed completely.
- **Explicit feedback:** None.
- **Question:** Is Japanese preference supported?
- **Expected classification:** Recurring behavior, not behavioral preference.
- **Expected status:** `INSUFFICIENT_EVIDENCE` for preference.
- **Allowed claim:** Japanese food was repeatedly consumed under constrained availability.
- **Forbidden claim:** User prefers Japanese food.
- **Reason:** Frequency cannot substitute for meaningful alternatives.
- **Relevant gates:** L1-G4, G13.

## S09 — Conditional preference by social context

- **Evidence:** When alone, repeated choices among alternatives favor spicy cuisine; with family, repeated choices among alternatives favor mild cuisine.
- **Opportunity/context:** Same meal type, social context differs and is known.
- **Observability limitations:** Choice opportunities and social context are observable.
- **Explicit feedback:** None.
- **Question:** What preference is permitted?
- **Expected classification:** Two scoped/conditional `PREFERENCE` claims; also relationship/social-context conditioned behavior.
- **Expected status:** `SUPPORTED` for each scope.
- **Allowed claim:** Selection tendency differs by social context.
- **Forbidden claim:** One global cuisine preference that erases the context split.
- **Reason:** Context conditioning resolves the apparent aggregate contradiction.
- **Relevant gates:** L1-G4, G5.

## S10 — Relationship-conditioned behavior

- **Evidence:** Alone, spicy meals recur; with the user's child, non-spicy choices recur across comparable opportunities.
- **Opportunity/context:** Person identity and relationship are known for the child-present slice.
- **Observability limitations:** Relevant opportunities observable.
- **Explicit feedback:** None.
- **Question:** What may PPF claim?
- **Expected classification:** `RELATIONSHIP-CONDITIONED BEHAVIOR` and scoped context-action association.
- **Expected status:** `SUPPORTED`.
- **Allowed claim:** Food choice pattern differs when the child is present.
- **Forbidden claim:** The child causes non-spicy choices.
- **Reason:** Person/social context conditions the association without causal evidence.
- **Relevant gates:** L1-G5, G11.

## S11 — [ADV] Relationship identity uncertainty

- **Evidence:** Non-spicy choices recur when “companion-7” is present, but evidence cannot establish whether companion-7 is the child or another person.
- **Opportunity/context:** Meal opportunities observable; relationship identity required for the proposed child-conditioned claim is unknown.
- **Observability limitations:** Identity/relationship dimension unavailable.
- **Explicit feedback:** None.
- **Question:** May PPF claim child-conditioned behavior?
- **Expected classification:** Context-action evidence with unresolved relationship scope.
- **Expected status:** `UNKNOWN_CONTEXT` for child-conditioned claim.
- **Allowed claim:** Behavior is associated with presence of companion-7 if that entity reference is stable.
- **Forbidden claim:** Behavior is conditioned on the child relationship.
- **Reason:** Relationship-conditioned semantics require sufficiently identified relationship context.
- **Relevant gates:** L1-G5, G8.

## S12 — Recurring temporal sequence

- **Evidence:** Across comparable after-work episodes: leave work → open Maps → message spouse recurs in that order.
- **Opportunity/context:** After-work episodes are comparable and observable through the sequence window.
- **Observability limitations:** No relevant sequence gaps.
- **Explicit feedback:** None.
- **Question:** What may PPF claim?
- **Expected classification:** `TEMPORAL SEQUENCE`.
- **Expected status:** `SUPPORTED`.
- **Allowed claim:** The ordered sequence recurs under the stated context.
- **Forbidden claim:** Opening Maps causes the message or the sequence is obligatory.
- **Reason:** Recurring order, not mere event frequency, is supported.
- **Relevant gates:** L1-G1, G11.

## S13 — [ADV] Same events, inconsistent order

- **Evidence:** Leave work, Maps, and spouse-message all recur, but their order varies materially across episodes.
- **Opportunity/context:** Comparable after-work episodes.
- **Observability limitations:** Order is fully observable.
- **Explicit feedback:** None.
- **Question:** Is the specific sequence supported?
- **Expected classification:** Recurring event observations; no specific temporal-sequence pattern.
- **Expected status:** `CONFLICTING_EVIDENCE` for the proposed ordered sequence.
- **Allowed claim:** The events commonly occur in the after-work context.
- **Forbidden claim:** A fixed leave→Maps→message sequence.
- **Reason:** Frequency of components does not establish recurring order.
- **Relevant gates:** L1-G1, G8, G11.

## S14 — [ADV] Missing middle event

- **Evidence:** Leave-work and spouse-message are observed; Maps telemetry is unavailable in the middle of multiple sequence windows.
- **Opportunity/context:** After-work sequence opportunities exist.
- **Observability limitations:** Maps source not observable during the critical interval.
- **Explicit feedback:** None.
- **Question:** May PPF infer the three-step sequence or its absence?
- **Expected classification:** Partial sequence evidence.
- **Expected status:** `NOT_OBSERVABLE` for the middle-step question; `INSUFFICIENT_EVIDENCE` for full sequence.
- **Allowed claim:** Start/end observations occurred; middle outcome is unknown.
- **Forbidden claim:** Maps did or did not occur.
- **Reason:** Missing telemetry cannot become sequence evidence or negative evidence.
- **Relevant gates:** L1-G8, G11.

## S15 — [ADV] Coincidental ordered pair

- **Evidence:** On three observed Mondays, a meeting ends before a food-delivery app opens.
- **Opportunity/context:** Only sparse Monday instances; other possible contexts not yet examined.
- **Observability limitations:** Observed instances are complete.
- **Explicit feedback:** None.
- **Question:** May PPF claim a stable sequence or causal relation?
- **Expected classification:** Ordered observations relevant to a candidate sequence.
- **Expected status:** `INSUFFICIENT_EVIDENCE`.
- **Allowed claim:** In observed cases, meeting-end preceded app-open.
- **Forbidden claim:** Stable sequence or meeting caused app use.
- **Reason:** Sparse coincidence and causality are both unproven.
- **Relevant gates:** L1-G8, G11, G13.

## S16 — Multi-label Friday gym association

- **Evidence:** Gym navigation recurs under Friday + 17:40-ish + leaving-office + alone + walking context.
- **Opportunity/context:** All listed dimensions are available and relevant; comparable Friday-exit opportunities observable.
- **Observability limitations:** None material.
- **Explicit feedback:** None.
- **Question:** What may PPF claim?
- **Expected classification:** `CONTEXT→ACTION ASSOCIATION` using compositional context.
- **Expected status:** `SUPPORTED`.
- **Allowed claim:** Gym navigation is associated with the stated multi-label context.
- **Forbidden claim:** A single “Friday” label fully explains the pattern or Friday causes gym navigation.
- **Reason:** Multiple dimensions jointly scope the recurring association.
- **Relevant gates:** L1-G5, G11.

## S17 — [ADV] Required context dimension missing

- **Evidence:** Gym and home destinations both recur Friday after work; social context is unavailable.
- **Opportunity/context:** Friday/work-exit known; alone-vs-with-family unknown and suspected material.
- **Observability limitations:** Social context not observable.
- **Explicit feedback:** None.
- **Question:** May PPF select one Friday-after-work pattern?
- **Expected classification:** Context-conditioned evidence with incomplete scope.
- **Expected status:** `UNKNOWN_CONTEXT`.
- **Allowed claim:** Destination outcomes conflict under the currently known context.
- **Forbidden claim:** A single Friday destination pattern or a fabricated social-context split.
- **Reason:** Required contextual discriminator is absent.
- **Relevant gates:** L1-G5, G8.

## S18 — [ADV] Confounder: meeting vs recurring discount

- **Evidence:** Every observed Monday, a meeting ends and then the food-delivery app opens; Mondays also have a recurring discount notification before app use.
- **Opportunity/context:** Monday, meeting, and discount contexts co-occur.
- **Observability limitations:** All listed events observable; no causal intervention evidence.
- **Explicit feedback:** None.
- **Question:** What causal/context claim is allowed?
- **Expected classification:** Context/action and temporal associations with confounded context.
- **Expected status:** `SUPPORTED` only for co-occurrence/order; causal explanation unsupported.
- **Allowed claim:** App use recurs in a context containing meeting-end and Monday discount.
- **Forbidden claim:** Meeting causes food-delivery use or discount causes it.
- **Reason:** Association cannot identify causal driver among co-occurring context dimensions.
- **Relevant gates:** L1-G5, G11, G13.

## S19 — [ADV] Simpson-like aggregate reversal

- **Evidence:** Aggregate choices make A appear more common than B. Conditioned data show: alone, A is repeatedly selected among alternatives; with family, B is repeatedly selected among alternatives. Opportunity mix differs across the two contexts.
- **Opportunity/context:** Choice sets are meaningful; social context and opportunity counts are known.
- **Observability limitations:** None material.
- **Explicit feedback:** None.
- **Question:** What preference claim is allowed?
- **Expected classification:** Context-specific `PREFERENCE` claims; aggregate claim is not the faithful semantic summary.
- **Expected status:** `SUPPORTED` for scoped preferences; global A-vs-B claim `CONFLICTING_EVIDENCE`/mis-scoped.
- **Allowed claim:** Alone→A tendency; family→B tendency.
- **Forbidden claim:** “User globally prefers A” solely from aggregate frequency.
- **Reason:** Context composition and opportunity distribution explain the aggregate reversal.
- **Relevant gates:** L1-G4, G5, G13.

## S20 — Rare consistent Wednesday exception

- **Evidence:** Broad weekday pattern is commute home; every observed Wednesday comparable opportunity includes child pickup first.
- **Opportunity/context:** Weekday commute opportunities observable; Wednesday + child-pickup context coherent.
- **Observability limitations:** None material.
- **Explicit feedback:** None.
- **Question:** Is Wednesday counterevidence or exception?
- **Expected classification:** Parent `ROUTINE` plus scoped `EXCEPTION`.
- **Expected status:** `SUPPORTED` for both scoped claims.
- **Allowed claim:** Home-after-work remains general pattern with a Wednesday pickup exception.
- **Forbidden claim:** Wednesday is random noise or globally invalidates the weekday pattern.
- **Reason:** Deviation is coherent and repeatable under a distinguishable condition.
- **Relevant gates:** L1-G3, G6.

## S21 — [ADV] One random detour

- **Evidence:** One airport detour occurs among an otherwise coherent commute history; no repeating condition is identified.
- **Opportunity/context:** Comparable commute opportunity; detour context has no known reusable scope.
- **Observability limitations:** Fully observed.
- **Explicit feedback:** None.
- **Question:** Is this an exception pattern?
- **Expected classification:** `OBSERVATION` / counterexample to perfect regularity, not a semantic exception pattern.
- **Expected status:** Parent routine may remain `SUPPORTED`; exception claim `INSUFFICIENT_EVIDENCE`.
- **Allowed claim:** A deviation occurred.
- **Forbidden claim:** Stable airport exception.
- **Reason:** Exception requires coherent scope or explicit declaration, not any isolated deviation.
- **Relevant gates:** L1-G6, G8.

## S22 — [ADV] Unsplit contradictory destinations

- **Evidence:** Under apparently comparable observable after-work contexts, home and gym are both repeatedly observed with no known context/time splitter.
- **Opportunity/context:** Available context dimensions are the same.
- **Observability limitations:** None known; a hidden context variable may exist but is not observed.
- **Explicit feedback:** None.
- **Question:** May PPF declare one as an exception to the other?
- **Expected classification:** Conflicting pattern evidence.
- **Expected status:** `CONFLICTING_EVIDENCE`.
- **Allowed claim:** Evidence supports incompatible outcomes under currently known scope.
- **Forbidden claim:** Arbitrarily choose a parent pattern and label the other an exception.
- **Reason:** No coherent exception condition is established.
- **Relevant gates:** L1-G6, G8.

## S23 — Real behavioral drift

- **Evidence:** A previously supported morning-coffee pattern is followed by a later period in which coffee repeatedly occurs in the afternoon across comparable fully observable days; morning non-occurrence is observable.
- **Opportunity/context:** Comparable days and coffee opportunities are known across both periods.
- **Observability limitations:** Coverage stable across the transition.
- **Explicit feedback:** None.
- **Question:** Is change semantically supportable?
- **Expected classification:** `CHANGE/DRIFT` from morning to afternoon scope.
- **Expected status:** `SUPPORTED` for behavioral change in the bounded history.
- **Allowed claim:** Timing pattern changed from morning to afternoon.
- **Forbidden claim:** Why it changed or that a context caused the change.
- **Reason:** Behavior changes while observability remains comparable.
- **Relevant gates:** L1-G7, G11.

## S24 — [ADV] Coverage-induced fake drift

- **Evidence:** Morning coffee observations disappear exactly when background permission is lost; afternoon source remains observable.
- **Opportunity/context:** Morning opportunities likely continue, but their outcome cannot be observed.
- **Observability limitations:** Morning source becomes unavailable after the apparent transition.
- **Explicit feedback:** None.
- **Question:** Did the coffee pattern drift?
- **Expected classification:** Observability change, not behavioral drift evidence.
- **Expected status:** `NOT_OBSERVABLE` for morning outcome; current drift claim `INSUFFICIENT_EVIDENCE`.
- **Allowed claim:** Morning coverage disappeared.
- **Forbidden claim:** User stopped morning coffee or moved it to afternoon because morning records vanished.
- **Reason:** Drift must be separated from telemetry coverage loss.
- **Relevant gates:** L1-G7, G8, G13.

## S25 — Behavioral reversal

- **Evidence:** Earlier supported choice pattern selects A under comparable alternatives; later fully observable comparable opportunities repeatedly select B instead of A, with the earlier relation no longer observed.
- **Opportunity/context:** Same scoped choice context and meaningful alternatives across periods.
- **Observability limitations:** Stable/full in both periods.
- **Explicit feedback:** None.
- **Question:** What temporal semantic change is permitted?
- **Expected classification:** `REVERSAL` as a strong form of `CHANGE/DRIFT`.
- **Expected status:** `SUPPORTED` in the bounded history.
- **Allowed claim:** The prior A-selection tendency has been replaced by a B-selection tendency in the same scope.
- **Forbidden claim:** Permanent future preference or causal explanation.
- **Reason:** Incompatible later behavior replaces earlier behavior under comparable observable opportunities.
- **Relevant gates:** L1-G4, G7.

## S26 — [ADV] Stale vs never-supported

- **Evidence:** Case A: a commute routine was previously supported but there has been no recent observable evidence relevant to current behavior. Case B: only two old commute observations ever existed.
- **Opportunity/context:** Current commute scope requested.
- **Observability limitations:** Recent period unavailable in both cases.
- **Explicit feedback:** None.
- **Question:** Should both be `STALE`?
- **Expected classification:** Case A historical routine; Case B sparse observations only.
- **Expected status:** A=`STALE`; B=`INSUFFICIENT_EVIDENCE`.
- **Allowed claim:** A had a historical supported pattern whose current applicability is stale; B never established one.
- **Forbidden claim:** Treat stale and insufficient as synonyms.
- **Reason:** Stale presupposes prior support; insufficient does not.
- **Relevant gates:** L1-G7, G8.

## S27 — [ADV] User rejects passive preference

- **Evidence:** Passive history supports a scoped behavioral X preference. User states, “No. Stop using the assumption that I prefer X.”
- **Opportunity/context:** Rejection targets the same personalization scope.
- **Observability limitations:** Passive history remains observable.
- **Explicit feedback:** `REJECT`.
- **Question:** What is active PPF state?
- **Expected classification:** Historical behavioral preference evidence + explicit user rejection operation.
- **Expected status:** `USER_REJECTED` for the active X preference claim.
- **Allowed claim:** The claim was inferred historically and then explicitly rejected.
- **Forbidden claim:** Continue surfacing X as active preference merely because passive evidence exists; delete the raw history implicitly.
- **Reason:** User rejection changes active personalization semantics while preserving provenance.
- **Relevant gates:** L1-G8, G9, G10.

## S28 — Correct a wrong observation

- **Evidence:** A derived location observation says gym; user states, “That was wrong; I was at home.”
- **Opportunity/context:** Correction targets the specific observation.
- **Observability limitations:** Original source record remains historical evidence of what was reported, not necessarily what happened.
- **Explicit feedback:** `CORRECT_OBSERVATION`.
- **Question:** What changes semantically?
- **Expected classification:** Explicit user correction of observation; original observation becomes corrected/invalid for the targeted interpretation.
- **Expected status:** Target observation=`INVALIDATE` for the corrected interpretation; correction itself=`SUPPORTED` as user feedback evidence.
- **Allowed claim:** The original observation was corrected by the user and should not silently continue as valid gym evidence.
- **Forbidden claim:** Original record never existed or correction physically deletes it.
- **Reason:** Correction preserves lineage and changes evidence validity, not history invisibly.
- **Relevant gates:** L1-G9, G10.

## S29 — Edit pattern scope

- **Evidence:** Existing user-confirmed claim: “I go to the gym on weekdays.” User edits: “Actually only Tuesday and Thursday.”
- **Opportunity/context:** Same gym domain, corrected day-of-week scope.
- **Observability limitations:** Not relevant to explicit scope edit.
- **Explicit feedback:** `EDIT_SCOPE`.
- **Question:** How are old and new assertions related?
- **Expected classification:** User correction/scope edit.
- **Expected status:** Old assertion `SUPERSEDED`; new scoped assertion `SUPPORTED` as explicit user assertion.
- **Allowed claim:** Tue/Thu is the current user-stated scope with lineage to the broader older assertion.
- **Forbidden claim:** Both are simultaneously current for identical scope or old assertion was deleted.
- **Reason:** Supersession preserves history while replacing current scope.
- **Relevant gates:** L1-G9, G10.

## S30 — User declares an exception

- **Evidence:** Existing routine: “I normally go home after work.” User says, “Except Wednesdays; I pick up my child.”
- **Opportunity/context:** Explicit Wednesday condition.
- **Observability limitations:** Passive evidence is not required to represent the declaration.
- **Explicit feedback:** `DECLARE_EXCEPTION`.
- **Question:** What may PPF represent?
- **Expected classification:** Parent routine assertion plus explicit `EXCEPTION` scope.
- **Expected status:** Exception `SUPPORTED` as user-declared semantic scope.
- **Allowed claim:** User declares Wednesday child pickup as exception to general pattern.
- **Forbidden claim:** The exception is passively verified or parent routine is invalidated.
- **Reason:** User can explicitly qualify personalization scope without destructive rewrite.
- **Relevant gates:** L1-G6, G9.

## S31 — Confirm a previously inferred pattern

- **Evidence:** Passive history supports an after-work home routine; user says, “Yes, that's usually right.”
- **Opportunity/context:** Confirmation targets the scoped routine claim.
- **Observability limitations:** Passive support remains separately provenance-bearing.
- **Explicit feedback:** `CONFIRM`.
- **Question:** What semantic effect occurs?
- **Expected classification:** Routine plus explicit confirmation evidence.
- **Expected status:** `SUPPORTED` with user-confirmation provenance.
- **Allowed claim:** User confirmed the scoped routine claim.
- **Forbidden claim:** Confirmation proves permanence, causality, or deletes counterevidence.
- **Reason:** Confirmation adds explicit evidence without overwriting passive history.
- **Relevant gates:** L1-G9.

## S32 — Hide is not delete

- **Evidence:** User says, “Don't show me this gym routine in summaries, but don't forget it.”
- **Opportunity/context:** Targets presentation of one active pattern.
- **Observability limitations:** None.
- **Explicit feedback:** `HIDE` semantic request.
- **Question:** What is the semantic effect?
- **Expected classification:** Visibility state change, not evidence invalidation/deletion.
- **Expected status:** Pattern may remain `SUPPORTED` but `HIDE` applies to surfacing.
- **Allowed claim:** Pattern remains valid but should not be surfaced in the targeted presentation scope.
- **Forbidden claim:** Pattern is deleted or invalid.
- **Reason:** Hide changes presentation, not semantic validity.
- **Relevant gates:** L1-G10.

## S33 — Delete targeted personalization

- **Evidence:** User requests, “Delete everything PPF knows about my gym routine.”
- **Opportunity/context:** Target is the gym personalization claim/evidence scope.
- **Observability limitations:** None relevant to semantic request.
- **Explicit feedback:** `REQUEST_DELETE`.
- **Question:** What may active PPF later return?
- **Expected classification:** Deletion operation over targeted personalization scope.
- **Expected status:** `DELETED` for targeted active/retrievable PPF state.
- **Allowed claim:** Deletion was requested/applied as represented by later lineage semantics.
- **Forbidden claim:** Continue returning the deleted gym routine from stale derived state.
- **Reason:** Delete is stronger than hide/reject/invalidate; physical mechanics remain L2/implementation work.
- **Relevant gates:** L1-G9, G10.

## S34 — Reset personalization

- **Evidence:** User requests, “Reset my personalization.”
- **Opportunity/context:** Broad PPF personalization scope rather than one claim.
- **Observability limitations:** None relevant.
- **Explicit feedback:** `RESET_PERSONALIZATION`.
- **Question:** What semantic scope changes?
- **Expected classification:** Broad reset operation.
- **Expected status:** `RESET_PERSONALIZATION` operation applies to the defined PPF scope; affected prior claims are no longer active personalization. This is broader than targeted `DELETE` and is not renamed to `DELETE`.
- **Allowed claim:** PPF personalization state in reset scope is no longer active.
- **Forbidden claim:** Reset unrelated host/app data or silently narrow reset to one pattern.
- **Reason:** Reset is a broad user-directed operation distinct from targeted deletion.
- **Relevant gates:** L1-G9, G10, G12.

## S35 — Source correction supersedes an observation

- **Evidence:** Source first reports location A, then emits an explicit correction stating the record should be location B.
- **Opportunity/context:** Same underlying observation scope.
- **Observability limitations:** Both source records visible with correction relation conceptually available.
- **Explicit feedback:** No user feedback; source correction.
- **Question:** Can both A and B be treated as current evidence?
- **Expected classification:** Observation correction/supersession.
- **Expected status:** A=`SUPERSEDED`; B is the current source observation for that scope.
- **Allowed claim:** Source corrected A to B with lineage.
- **Forbidden claim:** Count both as independent current evidence or treat A as deleted without deletion semantics.
- **Reason:** Supersession is replacement, not duplication or deletion.
- **Relevant gates:** L1-G10.

## S36 — [ADV] High-quality single observation

- **Evidence:** A sensor/source provides one extremely high-quality restaurant-choice observation with meaningful alternatives.
- **Opportunity/context:** One choice opportunity.
- **Observability limitations:** Observation quality is excellent.
- **Explicit feedback:** None.
- **Question:** Does quality make preference supported?
- **Expected classification:** High-quality `OBSERVATION`, candidate preference evidence.
- **Expected status:** `INSUFFICIENT_EVIDENCE` for behavioral preference.
- **Allowed claim:** One high-quality choice was observed.
- **Forbidden claim:** High observation quality implies high pattern support/confidence.
- **Reason:** Evidence quality and recurrence/pattern support are separate semantics.
- **Relevant gates:** L1-G4, G8.

## S37 — Degraded source does not erase other evidence

- **Evidence:** One phone source becomes low quality, while several independent valid evidence streams continue to support an already established scoped commute routine across observable opportunities.
- **Opportunity/context:** Comparable commute opportunities remain observable through the other valid evidence.
- **Observability limitations:** One source degraded; overall relevant evidence remains adequate by scenario stipulation.
- **Explicit feedback:** None.
- **Question:** Must the pattern become low-confidence/unsupported solely because one source degrades?
- **Expected classification:** Routine plus source-quality degradation evidence.
- **Expected status:** `SUPPORTED` for routine in this bounded scenario; degraded source itself has poorer observation quality.
- **Allowed claim:** Routine remains supported by other valid evidence while one source quality is degraded.
- **Forbidden claim:** Observation-quality degradation numerically defines pattern confidence.
- **Reason:** Quality is source/evidence-specific and not identical to pattern support.
- **Relevant gates:** L1-G7, G8.

## S38 — [ADV] One observation fits multiple candidate patterns

- **Evidence:** User goes to a gym after work once on Friday while alone.
- **Opportunity/context:** Friday + after work + alone known; only one occurrence.
- **Observability limitations:** Fully observed.
- **Explicit feedback:** None.
- **Question:** Which pattern does the event prove: Friday routine, alone-context association, gym preference, or sequence endpoint?
- **Expected classification:** `OBSERVATION` relevant to multiple candidates.
- **Expected status:** `INSUFFICIENT_EVIDENCE` for all recurring pattern claims.
- **Allowed claim:** One event may contribute evidence to several future hypotheses.
- **Forbidden claim:** Force the observation into exactly one pattern type or declare all candidate patterns supported.
- **Reason:** Semantic roles can overlap; evidence-to-pattern mapping is not exclusive.
- **Relevant gates:** L1-G1, G2, G8.

## S39 — [ADV] Contradictory global conclusion, coherent contextual slices

- **Evidence:** Under fully observed comparable opportunities: alone→destination A recurs; with family→destination B recurs.
- **Opportunity/context:** Social context is known and materially separates the slices.
- **Observability limitations:** None material.
- **Explicit feedback:** None.
- **Question:** Can two apparently contradictory patterns both be supported?
- **Expected classification:** Two scoped context-action/relationship-conditioned patterns.
- **Expected status:** Each `SUPPORTED`; an unscoped global A-or-B assertion is `CONFLICTING_EVIDENCE`/mis-scoped.
- **Allowed claim:** Both contextual patterns coexist under distinct scopes.
- **Forbidden claim:** Collapse them into one global assertion merely to avoid contradiction.
- **Reason:** Pattern support is scope-relative; contradictory global summaries can arise from valid contextual structure.
- **Relevant gates:** L1-G5, G8.

## S40 — [ADV] Exception becomes temporal replacement

- **Evidence:** Earlier supported pattern: weekdays→home with Wednesday child-pickup exception. In a later fully observable period, child pickup recurs across all comparable weekdays and the former home-only behavior no longer holds in the old scope.
- **Opportunity/context:** Same weekday commute scope across periods; later change is not limited to Wednesday.
- **Observability limitations:** Coverage stable and outcomes observable.
- **Explicit feedback:** None.
- **Question:** Is child pickup still only an exception?
- **Expected classification:** `CHANGE/DRIFT` of the parent pattern; former Wednesday exception has expanded into the later general behavior.
- **Expected status:** New later pattern `SUPPORTED`; old parent pattern historical/superseded in current temporal scope.
- **Allowed claim:** The behavioral structure changed over time from scoped exception to broader current recurrence.
- **Forbidden claim:** Keep labeling all later pickups as Wednesday-style exception or infer why the change occurred.
- **Reason:** The distinguishing dimension is temporal replacement across the parent scope, not a stable sub-scope deviation.
- **Relevant gates:** L1-G6, G7, G13.

## S41 — Deactivate without hiding or deleting

- **Evidence:** User says, “Pause using my commute routine for personalization for now, but keep it available so I can re-enable it later.”
- **Opportunity/context:** Targets active use of one existing routine; no claim that the routine is false.
- **Observability limitations:** None relevant.
- **Explicit feedback:** `DEACTIVATE` semantic request.
- **Question:** What happens to the routine semantically?
- **Expected classification:** Active-personalization state change, not evidence correction or deletion.
- **Expected status:** `DEACTIVATE`; the routine is not active for personalization until reactivated/re-established, while historical validity/provenance may remain.
- **Allowed claim:** The routine is deactivated for active personalization use.
- **Forbidden claim:** It is hidden-only, invalid, superseded, or deleted.
- **Reason:** Deactivation changes active use; it does not change presentation only (`HIDE`), truth/evidence validity (`INVALIDATE`), replacement (`SUPERSEDE`), or retrievability/deletion semantics (`DELETE`).
- **Relevant gates:** L1-G10, G12.

## Coverage summary

The set covers all Protocol-v2 families: routine, preference, conditional preference, relationship-conditioned behavior, temporal sequence, context-action association, exception, drift, reversal, correction, deletion, insufficient evidence, conflicting evidence, unknown/unobservable, multi-label context, false correlation, and sparse evidence. It also directly tests `HIDE`, `DEACTIVATE`, `INVALIDATE`, `SUPERSEDE`, `DELETE`, and `RESET_PERSONALIZATION` separation.

Explicit adversarial scenarios: **18** (`S05`, `S08`, `S11`, `S13`, `S14`, `S15`, `S17`, `S18`, `S19`, `S21`, `S22`, `S24`, `S26`, `S27`, `S36`, `S38`, `S39`, `S40`).

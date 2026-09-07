# MindForge PPF — Research Ledger

Purpose: chronological high-level source of truth for the Personal Pattern Foundation (PPF) research track.

This ledger records the research question, evidence, verdict, frozen state, relevant commit, unresolved findings, and next authorized research step. Detailed evidence remains in the stage-specific reports; this file does not replace them.

## Current status

```text
L1 — PASS / FROZEN
L2 — PASS / FROZEN
L3 — PASS / DATASETS FROZEN
L4 — PASS_WITH_FINDING / COMPLETE
L5 — NOT STARTED

Next candidate:
PPF-L5 — Minimum Missing Mechanism
```

Architecture boundary remains:

```text
Model != Kernel
Kernel = generic runtime primitives only
PPF = optional plugin / extension research by default
PPF cannot self-authorize Model or Kernel changes
```

## L1 — Define “Recognize Me”

Question: what does it mean for a system to correctly recognize a user's personal pattern?

Established: semantic pattern categories; supported/insufficient/conflicting/stale/unknown/deleted states; opportunity-aware routine semantics; preference requiring meaningful alternatives; compositional context; association/sequence distinct from causality; explicit correction semantics; mandatory abstention when evidence is insufficient or not observable.

Evidence: 41 scenarios, 18 adversarial scenarios, L1-G1..G13 PASS.

Verdict: **PASS / FROZEN**.

Key lesson: recurrence alone is not enough; recognition requires scope, opportunity, context, observability, abstention, and correction semantics.

## L2 — Personal Event Foundation

Question: what evidence representation is sufficient to support L1 semantics without prematurely encoding pattern conclusions?

Critical distinction:

```text
NO_OBSERVATION != OBSERVABLE_NON_OCCURRENCE
```

Established: opportunity, occurrence, observable non-occurrence, unknown outcome, not-observable/missingness, provenance, quality/coverage, correction/deletion lineage, raw vs derived evidence, and multi-device evidence relationships.

Evidence: 60 fixtures, 35 adversarial, 81 events, 8/8 negative tests, L2-G1..G18 PASS.

Verdict: **PASS / FROZEN**.

Key lesson: evidence storage must preserve observability, provenance, opportunity, and lineage independently from pattern conclusions.

## L3 — Ground-Truth Personal Pattern Benchmark

Question: can PPF semantics be converted into a falsifiable benchmark with hidden truth, visible L2 histories, controlled counterfactuals, and protected splits?

Benchmark model:

```text
hidden personal truth
→ opportunity/context process
→ behavioral realization
→ observation process
→ visible L2 history
→ semantic checkpoint oracle
```

Frozen benchmark: 30 synthetic persons, 32 truth configurations, 188 histories; DEV 38, VALIDATION 38, FINAL 112; at least 42 counterfactual instances. No recognizer is part of the generator.

### E0 — Generator Smoke

Verdict: **PASS**.

Evidence: 9 histories, 32 checkpoints, 33/33 L2-valid events, 13/13 tests, 0 truth leaks, 0 future leaks.

Key result: truth→opportunity→behavior→observation separation validated.

### E1 — Generator Hardening

Closed: L2 semantic bridge PARTIAL→FULL and counterfactual QA ADEQUATE→STRONGER.

Evidence: 30 histories, 218/218 L2-valid events, 29/29 E0+E1 tests, 8/8 L2 negatives.

Verdict: **PASS**.

### E2 — Canonical DEV Generation

Commit: `8f44b55b7cd39d21fd33183e3408ff05ae390b46`

Generated: 6 persons, 7 configs, 38 histories, 1130/1130 L2-valid events, 14/14 counterfactual templates, 0 rerolls.

Independent review: **REVISE** because counterfactual diff checking allowed overly broad `records.*` changes and did not prove the required controlled difference actually occurred.

### E2-CF.A — Counterfactual Contract Hardening

Commit: `a6f2f630d42cc62c48d2b170cc76797656bf7ef7`

Added machine-enforced `held_constant_paths`, `allowed_changed_paths`, `required_changed_paths`, semantic relation checks, and mutation tests M1–M9.

Result: 14/14 pair contracts PASS, 0 held-constant violations, 0 unexpected changes, 0 missing required changes; canonical DEV unchanged; seed registry unchanged; 0 rerolls.

Verdict: **PASS / DEV DATASET FROZEN**.

Key lesson: counterfactual QA must prove both absence of unintended differences and presence of the intended controlled difference.

### E3 — VALIDATION Generation

Commit: `d39ee271c8925d6dd5126e74a6e73439f0029f7d`

Generated: 6 new persons, 7 new configs, 38 histories, 1298/1298 L2-valid events, 14/14 pair contracts, 0 DEV overlap, 0 rerolls; DEV unchanged.

Verdict: **PASS / VALIDATION DATASET FROZEN**.

Key result: the frozen generator generalized to a protected validation split without tuning.

### E4 — FINAL TEST Generation

Commit: `b94645cc9d69a50a098683e543489ba01fda0057`

Generated: 18 persons, 18 configs, 112 histories, 3980/3980 L2-valid events, 616 evaluation units, 14/14 counterfactual templates, 4 structural holdouts, 0 rerolls, 0 DEV/VALIDATION overlap. FINAL truth stored under evaluator-private artifacts.

Verdict: **PASS / FINAL DATASET FROZEN / L3 COMPLETE**.

Key result: PPF now has frozen DEV / VALIDATION / FINAL benchmark splits suitable for falsifying future mechanisms.

## L4 — Minimal / Stupid Baselines

Question: can the frozen PPF benchmark be beaten or substantially shortcut using trivial heuristics rather than meaningful personal-pattern recognition?

Commit: `d1f9c88c646a238fcd49afa6137519d84b7137e9`

Procedure:

```text
DEV → VALIDATION → BASELINE LOCK → FINAL ONE-SHOT
```

Baseline lock SHA-256:

```text
477619a6375621a4514a07baa37e2f112e6e9b8709917c7ea075484de0744006
```

Baselines B0–B11 covered always-abstain, always-supported, last-observation, any-occurrence, raw count, naive frequency, recency, global majority, context-keyed majority, lifecycle-naive, provenance-naive, and provenance-dedup heuristics.

Strongest exact-state baseline:

```text
B9 — Lifecycle-Naive Rule
DEV        73.91%
VALIDATION 75.36%
FINAL      65.58%
FINAL false-promotion 38.54%
```

Major B9 FINAL failures: 77 NOT_OBSERVABLE-as-current, 31 UNKNOWN_CONTEXT positives, 8 conflict positives, 3 stale-as-current. B8 lowers FINAL false promotion to 21.20% but exact-state accuracy drops to 54.87%.

Verdict: **PASS_WITH_FINDING / PARTIALLY_SHORTCUTTABLE**.

Interpretation: trivial heuristics can capture meaningful parts of the benchmark, especially explicit lifecycle controls and aggregate recurrence, but none is sufficient as a PPF mechanism.

Minimum unresolved capability clusters:
1. observability must be separated from behavioral negative evidence;
2. explicit currentness / staleness handling;
3. first-class `UNKNOWN_CONTEXT` abstention;
4. first-class `CONFLICTING_EVIDENCE` abstention;
5. lifecycle controls must dominate passive recurrence;
6. compositional context reasoning;
7. provenance hygiene without confusing deduplication with recognition.

## L5 — Minimum Missing Mechanism

Prior status at starting commit: **NOT STARTED**.

Question: what is the smallest symbolic addition that causally improves the frozen B9 failure dimensions without becoming a full PPF recognizer?

Treatments: preregistered T0–T7 over E1 Observability, E2 Context, E3 Conflict, and E4 Currentness/Staleness eligibility; VALIDATION was executed once after source/selection freeze.

Result: **PASS — MINIMUM_MECHANISM_FOUND** on DEV + protected VALIDATION.

Selected minimum: **T1 = B9 + E1 Observability Eligibility**, one component, zero learned parameters. T1 preserved `SUPPORTED` recall and correction/deletion invariants while removing 4/4 `NOT_OBSERVABLE` active violations on both splits and lowering false promotion from 0.3311→0.2905 DEV and 0.3243→0.2838 VALIDATION.

Mechanism lock SHA-256: `092cb0bb367eac49284f377d1f7e3cfba425edf1f5298136bf8068dbe7cd4e70`.

E2 also qualified independently; E3/E4 produced no measurable gain under strict method-visible signals. T1 does not dominate the lower-false-promotion B8 frontier on every metric.

L3 FINAL was not used for L5 evaluation. Confirmatory status: **NOT YET CONFIRMED ON A NEW BLIND HOLDOUT**.

Commit: this L5 completion commit.

Next candidate: decision on a new protected blind confirmatory experiment/split; **not authorized in L5**.
## Current research conclusion

PPF has not yet been proven feasible as a production mechanism.

Established so far:

```text
semantic contract        — established
event/evidence contract  — established
benchmark foundation     — established
protected splits         — established
trivial-baseline floor   — established
minimum mechanism        — identified on DEV + VALIDATION; blind confirmation pending
```

Current state: **PPF L5 COMPLETE — MINIMUM MECHANISM FOUND; NEW BLIND CONFIRMATION NOT YET AUTHORIZED**.

## C1 — Blind Confirmatory Experiment

Question: does locked `T1 = B9 + E1 Observability Eligibility` reproduce its L5 advantage over frozen B9 on a new protected blind holdout?

Preregistered holdout: 12 persons, 12 configs, 64 histories, 8 STANDARD / 4 HIGH-RISK, 4 structural holdouts, 8 focused counterfactual pairs; canonical preregistration SHA-256 `ed63bd5a3dcd2364b5bb9fd13f70d34e6be11513e8ec8a4c2e272f13a8ce92e7`.

Result: **REVISE — generator QA failed before dataset persistence/evaluation**. The single generation attempt produced 64/64 histories with zero overlaps/leaks/rerolls, but only 598/650 visible events were L2-valid: 52 observability-loss records used the non-enum `missingness_reason=C1_OBSERVATION_LIMITATION`.

Policy consequence: no dataset lock, no run lock, semantic run count 0, and no T0/T1 confirmatory metrics. L5 remains **NOT BLINDLY CONFIRMED**.

Commit: this C1 REVISE closure commit.

Next candidate: separately reviewed C1 protocol repair/re-preregistration; no further stage authorized by this task.

## Ledger maintenance rule

From L5 onward, every research task that changes the scientific state of PPF must update this ledger in the same commit. Historical verdicts are append-only: do not erase prior failures or revise history silently; if a result is superseded, record what superseded it and why. Keep each new stage entry concise and link detailed evidence to its dedicated report.

## PPF-F1 Feasibility & Capability Placement Review

Question:
Determine what PPF has proven after PPF-C1 and where the capability belongs architecturally.

Evidence reviewed:
- PPF-L1/L2 frozen contracts
- PPF-L3 frozen benchmark
- PPF-L4 baseline analysis
- PPF-L5 minimum missing mechanism analysis
- PPF-C1 blind confirmation result

Placement decision:
PPF remains a research extension candidate. The proven primitive, Observability Eligibility, is not a kernel primitive and should be evaluated as an optional plugin capability.

Continue/stop decision:
Continue research.

Next candidate:
PPF Plugin Contract / Prototype Feasibility.

No mechanisms, recognizer, production integration, or architecture changes introduced.

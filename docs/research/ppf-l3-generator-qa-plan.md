# PPF-L3 Generator and Oracle QA Plan

Status: **FROZEN QA PLAN / GENERATOR NOT IMPLEMENTED**

This document freezes generator, oracle, mutation, counterfactual, reproducibility, split, and leakage checks before implementation. No recognizer is involved.

## 1. QA principle

The benchmark must prove its own correctness before it can evaluate a recognition method.

Required direction:

```text
truth -> opportunities -> behavior -> observation -> L2-visible history
```

Forbidden:

```text
recognizer output -> truth
visible counts -> redefine latent truth
method failure -> silently retune same final benchmark
```

## 2. Generator QA families

| QA family | Required check | Failure consequence |
|---|---|---|
| schema validity | every visible event validates against frozen L2 schema/contract | STOP generated case |
| truth consistency | truth record is complete, internally coherent, and predates rendering | STOP case/config |
| opportunity consistency | opportunity-dependent truths have explicit hidden opportunities/choice sets | STOP case/config |
| behavior-rule consistency | realized behavior obeys truth rule and declared stochastic variation | STOP case/config |
| observation correctness | corruption changes visibility/quality/representation only as declared | STOP case/config |
| seed reproducibility | same complete seed tuple yields canonical semantic equality | STOP generator freeze |
| seed independence | observation-seed-only change preserves truth/behavior; behavior-seed-only change preserves truth | STOP generator freeze |
| counterfactual invariance | held-constant fields in every pair are equal | STOP pair |
| counterfactual expected-change | declared controlled factor actually changes intended semantic target | STOP pair |
| truth leakage | no truth/family/status/secret-seed hint in method-visible IDs/paths/payloads | STOP release |
| checkpoint consistency | visible prefix contains no post-checkpoint/future events | STOP case |
| correction timing | semantic state changes at declared effective time/scope | STOP case |
| deletion timing | active state becomes DELETED at declared effective time/scope | STOP case |
| unrelated-truth preservation | scoped correction/delete does not alter unrelated truth | STOP case |
| multi-device lineage | SAME_ORIGIN_REPLICATED never multiplies behavioral occurrence truth | STOP case |
| raw/derived lineage | derived evidence references lineage and does not become independent recurrence | STOP case |
| split leakage | protected persons/configurations do not cross splits | STOP dataset freeze |
| manifest consistency | all case/checkpoint/unit refs resolve once and totals reconcile | STOP dataset freeze |

## 3. Frozen oracle checks

The initial oracle QA suite must implement at least the following checks before generator freeze.

```text
O1  truth is registered before rendering.
O2  every opportunity-dependent truth has an explicit hidden opportunity process.
O3  behavioral realization obeys the frozen truth configuration.
O4  observation corruption never changes latent behavioral truth.
O5  every method-visible record is L2-valid.
O6  no evaluator-only truth field appears in method-visible history/metadata/path.
O7  checkpoint answer depends only on frozen truth/control state + visible prefix at T.
O8  permission loss may change identifiability/status but not latent behavior.
O9  same-origin replication changes evidence-record count, not behavioral occurrence count.
O10 correction changes active semantic answer at the correct effective time/scope.
O11 deletion/reset changes active semantic answer at the correct effective time/scope.
O12 unrelated truth survives scoped correction/delete/reset.
O13 true drift change point aligns with a latent behavioral regime transition.
O14 coverage-induced fake drift contains no latent behavioral transition.
O15 each counterfactual pair differs only in its declared controlled variable(s).
O16 relationship-conditioned claims require relationship identity to be visible/established when expected SUPPORTED.
O17 unknown required relationship/context produces UNKNOWN_CONTEXT/PARTIAL/NO rather than a guessed scoped positive.
O18 USER_REJECTED remains active despite similar later passive behavior unless scenario truth explicitly transitions it.
O19 SUPERSEDED and STALE remain distinct from REVERSAL.
O20 negative evaluation units are preregistered before method output and resolve to a finite denominator.
```

The oracle is a **semantic judge**, not a reference recognizer. It may know hidden scenario truth and corruption provenance. It must not implement a count/probability/confidence threshold that a future recognizer is expected to reproduce.

## 4. Identifiability oracle QA

Assignments are preregistered from scenario construction.

```text
YES:
all semantic ingredients deliberately exposed for the expected current positive answer.

PARTIAL:
some required pattern/scope/status dimensions are recoverable, at least one remains unjustified.

NO:
critical evidence/context is intentionally unavailable; positive latent truth cannot be justified from visible history.
```

Checks:

- identical visible history cannot receive different identifiability merely because a method succeeds/fails;
- observation corruption can move `YES -> PARTIAL/NO` without changing latent truth;
- restoration of relevant observability can move identifiability back when scenario semantics permit;
- `NO` does not imply latent `NO_PATTERN`.

## 5. Mutation QA matrix

| Mutation | Latent truth | Expected visible semantic answer | Identifiability |
|---|---|---|---|
| remove 30% visible observations | unchanged | may stay or become abstention/stale | may decrease |
| add same-origin replicas | unchanged | must not gain recurrence support solely from replicas | unchanged |
| change platform/source label only | unchanged | unchanged unless source observability semantics explicitly differ | unchanged |
| degrade observation quality | unchanged | may weaken/abstain; must not create behavioral drift | may decrease |
| delay ingestion | unchanged | checkpoint answer may change until delayed event becomes visible | may transiently decrease |
| hide relationship identity | unchanged | relationship-specific positive -> UNKNOWN_CONTEXT/abstention | decreases |
| change hidden preference | changed | should change after sufficient comparable visible opportunities | scenario-dependent |
| move true change point | changed valid-time relation | lifecycle checkpoint answers shift accordingly | scenario-dependent |
| insert correction/rejection | behavioral truth unchanged unless separately specified | active semantic state changes at control time | may remain same |
| insert deletion/reset | historical truth preserved in evaluator provenance; active state changes | DELETED/reset-scoped answer | not a proxy for truth recovery |

Mutation QA validates benchmark semantics; it is not used to tune recognizers.

## 6. Seed QA

Required reproducibility level: **canonical JSON semantic stability**.

Canonicalization must make incidental key ordering/formatting irrelevant while requiring equality of semantically significant values.

Tests:

```text
same version + full seed tuple -> same truth/opportunities/behavior/visible history/checkpoint answers
change observation seed only -> truth/opportunities/behavior unchanged
change behavior seed only -> truth/opportunities unchanged; behavior may vary
change person seed -> person structural realization may vary within registered template
change scenario seed -> scenario structure may vary within registered family constraints
```

Seed-derived filenames or case IDs must be opaque and must not reveal family/status.

## 7. Split leakage QA

Before each dataset freeze, assert:

```text
intersection(DEV persons, VALIDATION persons) = empty
intersection(DEV persons, FINAL persons) = empty
intersection(VALIDATION persons, FINAL persons) = empty

truth_configuration_id unique to one protected split
case_id unique globally
final secret seed manifest absent from public release artifacts
final expected answers absent from public release artifacts
structural holdout combinations absent from DEV/VALIDATION configurations
```

Reuse of literal integer seed values is not by itself leakage if namespaced deterministic derivation yields distinct streams; reuse of the same derived stream/config across protected splits is forbidden.

## 8. Counterfactual-pair QA

Every pair manifest freezes:

```text
pair_id
controlled_field_paths
held_constant_field_paths
case_a
case_b
expected latent-truth change/invariance
expected visible-answer change/invariance
primary metric
```

QA computes semantic diffs and fails the pair if undeclared fields change.

Special invariants:

- full coverage vs permission loss: truth/opportunities/behavior identical;
- single evidence vs replicas: behavioral episode identity identical;
- true drift vs observation-only change: pre-T truth/history construction matched as registered, only true-drift side changes latent regime;
- correction/deletion pairs: pre-control history identical;
- known vs hidden relationship: behavior identical; only relationship observability differs.

## 9. Checkpoint QA

For every checkpoint T:

- visible history contains only events available by T under the three-time model;
- delayed future-ingestion records are absent until their ingestion availability;
- expected answer uses the visible prefix plus evaluator truth/control provenance, not future evidence;
- lifecycle state changes only at effective time;
- stale/currentness checks use registered currentness semantics, not an algorithmic score.

## 10. Lifecycle QA

### Correction/rejection

Verify target identity, scope, effective time, resulting active state, preserved historical lineage, preservation of unrelated evidence, and no passive resurrection while rejection remains active.

### Deletion/reset

Verify target/reset scope, effective time, `DELETED` active state where required, zero active-return of deleted personalization, and preservation of unrelated personalization outside scope.

### Drift/reversal/staleness

Verify actual latent change for true drift/reversal; verify no latent change for coverage fake drift; keep stale state distinct from reversal and never-supported state.

## 11. Lineage QA

### Multi-device

Test all L2 evidence relationships:

```text
SAME_ORIGIN_REPLICATED
INDEPENDENT_CORROBORATION
UNKNOWN_RELATIONSHIP
```

Same-origin copies cannot create extra behavioral episodes. Independent corroboration may strengthen evidence provenance but still does not multiply the underlying action when records refer to the same episode.

### Raw/derived

Validate `DERIVED_FROM` lineage, procedure provenance where present, and no double counting of raw + derivative as independent recurrence.

## 12. Manifest/totals QA

Generator QA must reconcile canonical execution totals:

```text
30 persons
32 base truth configurations
20 STANDARD configurations
12 HIGH-RISK configurations
188 histories
38 DEV + 38 VALIDATION + 112 FINAL_TEST
48 SHORT + 84 MEDIUM + 56 LONG
14 counterfactual templates
>=42 instantiated pairs
~1,004 planned checkpoints, with actual count reported and deviations explained
```

Actual evaluation-unit/event counts may fall within the frozen planning ranges, but target balance must pass:

```text
no-correct-active-positive >=35%, target ~40%
identifiability YES/PARTIAL/NO within 60/20/20 +/-5 percentage points
```

If generator realization cannot satisfy these without post-hoc case cherry-picking, generator execution is REVISE.

## 13. Truth leakage audit

Search method-visible artifacts for evaluator-only values and semantic hints across:

```text
file/directory names
case IDs
source/provider names
payload fields
context labels
seed strings
scenario-family names
truth/pattern IDs
expected status labels
case ordering
public metadata
```

Opaque IDs must be generated without embedding semantic class labels.

## 14. QA release gates

```text
GQA-1 L2 schema/semantic validity: PASS required
GQA-2 truth/opportunity/behavior consistency: PASS required
GQA-3 seed reproducibility + independence: PASS required
GQA-4 oracle checkpoint semantics: PASS required
GQA-5 mutation invariance/change suite: PASS required
GQA-6 counterfactual isolation: PASS required
GQA-7 lifecycle timing/lineage: PASS required
GQA-8 split leakage: PASS required
GQA-9 truth leakage: PASS required
GQA-10 manifest/totals reconciliation: PASS required
```

Failure of any gate blocks generator freeze and all later benchmark dataset freezes.

## 15. Current status

```text
QA plan: PASS / FROZEN
QA implementation: NOT STARTED
Generator: NOT IMPLEMENTED
Benchmark data: NOT GENERATED
Recognizer: NOT IMPLEMENTED
L4: BLOCKED
```

## 16. L3-EP.A exact split/config QA amendment

Future generator/manifest QA must assert the exact protected split allocation below; these are not targets and may not drift silently:

```text
DEV:
  persons = 6
  STANDARD configs = 5
  HIGH-RISK configs = 2
  total configs = 7
  histories = 38
  minimum counterfactual pair instances = 14

VALIDATION:
  persons = 6
  STANDARD configs = 5
  HIGH-RISK configs = 2
  total configs = 7
  histories = 38
  minimum counterfactual pair instances = 14

FINAL TEST:
  persons = 18
  STANDARD configs = 10
  HIGH-RISK configs = 8
  total configs = 18
  histories = 112
  minimum counterfactual pair instances = 14
```

Additional mandatory checks:

```text
GQA-S1 every truth_configuration_id belongs to exactly one protected split
GQA-S2 no truth configuration is reused in another split under alternate seeds
GQA-S3 STANDARD/HIGH-RISK config totals reconcile exactly to 20/12
GQA-S4 split history totals derive exactly from replication policy
GQA-S5 pair-instance totals satisfy DEV>=14, VALIDATION>=14, FINAL>=14, TOTAL>=42
GQA-S6 each history has at most one registered counterfactual pair-instance membership
```

For `GQA-S6`, the frozen v1 accounting is:

```text
minimum 42 pair instances
x 2 distinct histories per pair
= 84 distinct paired histories
```

The two members of a pair must be in the same protected split. All paired histories are included in the canonical 188 histories. Pair registration therefore cannot inflate the benchmark history total.

The manifest/totals gate must also verify:

```text
7 DEV configs + 7 VALIDATION configs + 18 FINAL configs = 32
5+5+10 STANDARD configs = 20
2+2+8 HIGH-RISK configs = 12
38+38+112 histories = 188
```

Failure of any `GQA-S*` check blocks generator freeze and all dataset freeze stages.

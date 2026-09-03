# PPF-L3 Dataset Matrix

Status: **FROZEN EXECUTION ALLOCATION / NO DATA GENERATED**

Canonical totals:

```text
persons: 30
base truth configurations: 32
STANDARD configs: 20 -> 80 histories at 2x2 replication
HIGH-RISK configs: 12 -> 108 histories at 3x3 replication
total histories: 188
counterfactual templates: 14
minimum instantiated pairs: 42
estimated checkpoints: 1,004
estimated evaluation units: 2,000-2,800
estimated visible L2 events: 18,000-28,000
```

Family rows overlap by design. A single history may satisfy several rows; **do not sum family-history counts to derive the canonical 188 total**.

## Coverage matrix

| Family | Role | Identifiability | Regime | Min persons | Min histories | Replication | Checkpoints | Pair? | Split presence | Primary metrics |
|---|---|---|---|---:|---:|---|---|---|---|---|
| routine/opportunity | positive + abstention | YES/PARTIAL/NO | S/M/L | 8 | 16 | standard | C0-C4 | CF-01/04 | D/V/T | precision, recall, abstention, false promotion |
| preference/availability | positive/adversarial | YES/PARTIAL | S/M/L | 8 | 16 | standard | C0-C4 | CF-07 | D/V/T | preference/scope correctness |
| conditional preference | positive/scope | YES/PARTIAL | M/L | 6 | 12 | standard | C1-C4 | CF-08 | D/V/T | scope correctness |
| relationship-conditioned | positive/unknown-context | YES/PARTIAL/NO | M/L | 6 | 12 | standard | C1-C4 | CF-12 | D/V/T | scope, abstention subtype |
| temporal sequence | positive/negative | YES/PARTIAL | S/M/L | 6 | 12 | standard | C1-C4 | optional | D/V/T | precision, counterexample sensitivity |
| context-action association | positive/scope | YES/PARTIAL | M/L | 6 | 12 | standard | C1-C4 | CF-08 | D/V/T | scope correctness |
| confounding | adversarial | YES/PARTIAL | M/L | 6 | 18 | high-risk | C1-C4 | yes | D/V/T | scope correctness, false discovery |
| Simpson-like aggregation | adversarial | YES | M/L | 6 | 18 | high-risk | C1-C4 | CF-08 | D/V/T | scope collapse |
| exception | positive/lifecycle | YES/PARTIAL | M/L | 6 | 14 | standard | parent+exception cuts | CF-09 | D/V/T | exception correctness |
| random deviation control | negative control | YES | S/M/L | 6 | 12 | standard | C1-C4 | CF-09 | D/V/T | false promotion, counterexample sensitivity |
| real drift | lifecycle positive | YES/PARTIAL | L | 6 | 18 | high-risk | pre/post/later | CF-06 | D/V/T | drift correctness, latency |
| coverage-induced fake drift | adversarial abstention | PARTIAL/NO | M/L | 6 | 18 | high-risk | pre-loss/post-loss/stale | CF-01/05/06 | D/V/T | false drift, abstention |
| reversal | lifecycle positive | YES/PARTIAL | L | 5 | 12 | standard | pre/post/later | CF-06 | D/V/T | reversal correctness, staleness |
| correction/rejection | lifecycle/control | YES/PARTIAL | M/L | 6 | 18 | high-risk | pre/immediate/later | CF-10 | D/V/T | correction correctness, resurrection |
| deletion/reset | lifecycle/control | YES | M/L | 6 | 18 | high-risk | pre/immediate/later | CF-11 | D/V/T | deletion correctness, active-return violations |
| multi-device replication | adversarial | YES | S/M/L | 6 | 18 | high-risk | C1-C4 | CF-03/14 | D/V/T | replica inflation |
| independent corroboration | evidence relation | YES | M/L | 5 | 10 | standard | C1-C4 | CF-14 | D/V/T | corroboration correctness |
| raw/derived evidence | evidence relation | YES/PARTIAL | M/L | 5 | 10 | standard | C1-C4 | CF-13 | D/V/T | raw-derived inflation |
| missingness | abstention/adversarial | PARTIAL/NO | S/M/L | 8 | 18 | standard | before/after loss | CF-01 | D/V/T | abstention, staleness |
| observation quality | abstention/adversarial | YES/PARTIAL/NO | S/M/L | 6 | 12 | standard | C1-C4 | CF-02 | D/V/T | abstention, quality-vs-truth separation |
| cold start | abstention | PARTIAL/NO | S | 8 | 16 | standard | C0/C1 | no | D/V/T | abstention correctness |
| unknown context | abstention | PARTIAL/NO | S/M | 6 | 12 | standard | C1-C3 | CF-12 | D/V/T | UNKNOWN_CONTEXT correctness |
| unidentifiable latent truth | adversarial abstention | NO | S/M/L | 6 | 18 | high-risk | C1-C4 | CF-01/12 | D/V/T | abstention, omniscience penalty |
| pattern overlap | positive interaction | YES/PARTIAL | M/L | 6 | 12 | standard | C1-C4 | optional | D/V/T | multi-pattern recall/scope |
| NO_PATTERN controls | negative | YES/PARTIAL | S/M/L | 8 | 18 | standard | C0-C4 | CF-04 | D/V/T | false promotion/discovery |
| sparse coincidence | negative adversarial | YES | S | 6 | 18 | high-risk | C0-C2 | CF-04 | D/V/T | false promotion |
| conflicting structure | abstention/negative | PARTIAL/NO | M/L | 6 | 12 | standard | C1-C4 | optional | D/V/T | CONFLICTING_EVIDENCE correctness |

Legend: D=DEV, V=VALIDATION, T=FINAL_TEST; S/M/L=SHORT/MEDIUM/LONG.

## Protected split allocation

```text
DEV:         6 persons / 38 histories
VALIDATION:  6 persons / 38 histories
FINAL_TEST: 18 persons / 112 histories
```

Persons and truth configurations are disjoint across protected splits.

## Structural archetype coverage

Counts overlap because each person receives 3-5 tags.

| Tag | Minimum persons |
|---|---:|
| P-A stable/simple | 10 |
| P-B context-dependent | 12 |
| P-C relationship-conditioned | 8 |
| P-D exception-heavy | 8 |
| P-E drift/reversal-heavy | 8 |
| P-F poor-observability | 10 |
| P-G multi-device-heavy | 8 |
| P-H correction/deletion-heavy | 8 |
| P-I overlap-heavy | 10 |
| P-J mostly-no-pattern/sparse | 10 |

## Evaluation-unit balance

Target over the preregistered evaluation-unit denominator:

```text
active positive/current support: 60% +/- 3%
pure negative/no-pattern:         22% +/- 3%
required abstention/lifecycle:    23% +/- 3%
negative+abstention overlap:       5% +/- 2%
no-correct-active-positive total: target 40%, never below 35%
```

Identifiability:

```text
YES 60% +/- 5%
PARTIAL 20% +/- 5%
NO 20% +/- 5%
```

## History regimes

```text
SHORT: 4-10 opportunities; 48 histories
MEDIUM: 16-32 opportunities; 84 histories
LONG: 48-96 opportunities; 56 histories
```

These ranges control generator construction only and are not recognizer thresholds.

## High-risk configurations

The 12 HIGH-RISK base configurations must collectively cover at minimum:

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

Each HIGH-RISK configuration receives `3 behavior x 3 observation` replication.

## Structural holdouts

FINAL_TEST must include:

```text
SH-1 relationship-conditioned + missingness + correction
SH-2 exception + multi-device replication + raw/derived lineage
SH-3 drift/reversal + partial observability + derived evidence
```

The exact person/config/seed assignments are evaluator-only.

## Matrix gate

```text
all frozen L3 scenario families represented: PASS
all major metrics have dedicated failure cases: PASS
negative/no-positive denominator >= 35% target: PASS
identifiability YES/PARTIAL/NO represented: PASS
person-disjoint split: PASS
high-risk repeated seeds: PASS
structural holdout > unseen seed only: PASS
canonical totals reconciled independently of overlapping family rows: PASS
```

## L3-EP.A split-level canonical reconciliation

The protected split allocation is frozen at truth-configuration level as well as person/history level:

| Split | Persons | STANDARD configs | HIGH-RISK configs | Total configs | Histories | Minimum CF pair instances |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 5 | 2 | 7 | 38 | 14 |
| VALIDATION | 6 | 5 | 2 | 7 | 38 | 14 |
| FINAL TEST | 18 | 10 | 8 | 18 | 112 | 14 |
| **TOTAL** | **30** | **20** | **12** | **32** | **188** | **42** |

Replication reconciliation:

```text
DEV:        5 STANDARD*4 + 2 HIGH-RISK*9 = 38
VALIDATION: 5 STANDARD*4 + 2 HIGH-RISK*9 = 38
FINAL TEST: 10 STANDARD*4 + 8 HIGH-RISK*9 = 112
```

Frozen split-disjoint rules:

```text
each truth_configuration_id belongs to exactly one protected split
no truth configuration is reused in another split under alternate seeds
no synthetic person crosses protected splits
no history crosses protected splits
```

Counterfactual accounting for v1 is also frozen:

```text
DEV        >=14 pair instances
VALIDATION >=14 pair instances
FINAL TEST >=14 pair instances
TOTAL      >=42 pair instances

one history participates in at most one registered pair instance
minimum 42 pair instances = 84 distinct paired histories
all paired histories are included within the canonical 188 histories
```

The exact FINAL_TEST mappings remain evaluator-only. Public counts freeze the protected set at **18 persons / 18 truth configurations / 112 histories**, including at least three structural-holdout combinations.

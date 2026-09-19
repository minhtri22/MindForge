# MindForge Kernel Continual Learning — KCL-6.5.9.4 Action-Target Failure-Mode Decomposition

Status: **FROZEN BEFORE ANY KCL-6.5.9.4 DISCOVERY OR REPLICATION OUTCOME**

## 1. Trigger

KCL-6.5.9.3 closed:

```
NEGATIVE
BOUNDARY_ACTION_IDENTIFIABILITY_DECOMPOSITION_INCONCLUSIVE
```

The persistent failure was concentrated in `A_ONLY`: substantial fresh support,
but near-zero recall under stage-only, global state, localized LRBS-v1 and a
zero-step future-task oracle probe.

The next admissible question is therefore structural:

> does `A_ONLY` itself collapse multiple reproducible ways in which policies
> B and C violate the frozen safe-action contract?

KCL-6.5.9.4 is an **outcome/target decomposition** only. It does not train a
predictor, select features, implement a controller, or touch the protected
confirmatory cohort.

## 2. Frozen parent target and policy contract

Reuse `SAFE_ACTION_SET-v1` and the exact KCL-6.5.9 policy predicates.

Policies:

```
A = A_CARRY_ALL
B = B_RESET_ALL
C = C_CARRY_STEP_RESET_MOMENTS
```

Frozen thresholds:

```
STRICT_CURRENT_MIN      = 0.95
PLASTICITY_BENEFIT_MIN  = 0.01
RETENTION_MARGIN        = 1/24
```

For P in {B,C}, relative to A:

```
plasticity_gain =
    auc_delta_vs_A >= 0.01
    OR
    (A.final_accuracy < 0.95 AND P.final_accuracy >= 0.95)

retention_ok =
    retention_delta_vs_A >= -(1/24)

absolute_ok =
    P.final_accuracy >= 0.95

safe_P =
    plasticity_gain AND retention_ok AND absolute_ok
```

`A_ONLY` is exactly:

```
safe_B = false
safe_C = false
```

No target threshold may change after outcome inspection.

## 3. Atomic failure reasons

For each unsafe policy P in {B,C}, freeze exactly three atomic failure reasons:

```
PLASTICITY_SHORTFALL
    := NOT plasticity_gain

RETENTION_MARGIN_VIOLATION
    := NOT retention_ok

STRICT_ACCURACY_FAILURE
    := NOT absolute_ok
```

Because an unsafe policy fails the conjunction above, its failure-reason set
must contain at least one of these three reasons.

No reason may be added, removed, merged or redefined after discovery.

## 4. Per-policy cause codes

Each unsafe policy receives the sorted non-empty set of its atomic failure
reasons.

There are exactly seven logically possible per-policy cause codes:

```
P
R
A
P+R
P+A
R+A
P+R+A
```

where:

```
P = PLASTICITY_SHORTFALL
R = RETENTION_MARGIN_VIOLATION
A = STRICT_ACCURACY_FAILURE
```

The order inside a code is canonical: P, R, A.

## 5. Joint signatures

For each `A_ONLY` boundary report two frozen signatures.

### 5.1 Ordered policy signature

```
B:<cause_B>|C:<cause_C>
```

This preserves which intervention failed by which mechanism.

### 5.2 Mechanism multiset signature — PRIMARY

To avoid mistaking a simple B↔C role swap for a new causal mechanism, the
primary signature sorts the two cause codes lexicographically and discards
policy identity:

```
MECH{min(cause_B,cause_C),max(cause_B,cause_C)}
```

Example:

```
B:P|C:R+A
B:R+A|C:P
```

share the same primary mechanism-multiset signature.

Also report:

```
SAME_CAUSE_SET := cause_B == cause_C
DIFFERENT_CAUSE_SET := cause_B != cause_C
```

These are descriptive and cannot replace the primary signature after outcome
inspection.

## 6. Scientific hypotheses

### H-FMD — replicated internal target heterogeneity

`A_ONLY` contains at least two distinct mechanism-multiset signatures that:

1. are supported in fresh discovery;
2. independently recur with support in fresh replication;
3. have stable prevalence across discovery and replication under the frozen
   stability rule.

### H-HOM — homogeneous/unstable alternative

The data do not establish at least two stable replicated mechanism signatures.

KCL-6.5.9.4 does **not** ask whether the modes are predictable from boundary
state.

## 7. Fresh cohorts

Generate exactly 480 fresh non-confirmatory seeds with:

```
Python 3.12
random.Random(6594).sample(range(2000001, 3000000), 480)
```

The explicit lists below are authoritative.

### Discovery — 240 whole seeds

```
2838987,2260592,2786574,2479853,2849829,2852497,2908145,2080106,2286404,2923169,2986655,2477765,2436718,2531113,2891994,2941301,2085125,2386776,2836284,2549218,2338458,2784786,2329345,2410357,2345916,2062582,2791619,2285711,2551197,2442934,2151929,2588465,2157141,2834675,2571303,2599700,2970554,2216653,2965635,2821119,2709055,2542053,2428100,2192579,2183894,2648510,2774048,2136955,2181100,2727385,2325116,2174117,2210080,2470384,2013173,2372554,2424797,2393968,2151760,2730988,2532283,2392389,2230993,2983541,2925089,2487584,2097508,2142666,2597042,2366001,2504330,2989512,2123595,2762808,2883383,2233773,2050678,2029919,2711889,2704446,2596340,2830290,2958432,2854038,2616299,2190666,2554806,2640809,2927117,2417880,2057149,2987294,2416967,2773190,2450486,2288025,2783391,2949568,2624351,2302243,2075928,2455045,2726968,2210745,2925313,2305862,2813366,2944679,2760931,2416608,2689954,2665406,2740781,2016948,2272065,2769628,2247070,2647996,2907796,2470203,2693296,2333491,2113978,2362450,2335654,2541679,2772355,2554840,2077445,2521311,2777826,2180893,2154552,2849592,2361135,2857454,2569352,2377537,2856913,2258271,2096314,2061725,2240941,2474862,2283101,2454961,2286917,2886307,2359945,2769515,2494437,2374346,2064652,2647283,2364659,2342239,2701993,2736318,2577030,2629436,2922194,2635262,2172441,2220601,2595902,2360852,2646141,2553403,2283006,2738301,2755583,2001544,2908099,2917404,2753311,2691245,2181318,2534370,2458667,2648886,2038185,2406340,2893445,2595257,2109243,2441882,2268569,2145664,2843344,2787643,2027519,2218282,2260691,2447928,2245448,2814432,2536964,2845106,2218531,2323234,2956473,2333783,2104934,2757138,2461385,2177700,2279584,2103367,2834059,2861663,2744191,2352342,2091361,2588936,2697988,2181857,2278784,2814232,2813593,2514473,2371123,2033483,2259710,2029515,2699583,2059981,2239769,2550088,2449329,2510737,2224245,2903218,2892533,2023362,2289489,2227855,2636528,2648244,2035272,2648660
```

### Replication — 240 whole seeds

```
2035692,2263915,2655053,2528233,2922969,2918842,2071656,2540777,2092438,2352149,2963136,2648628,2172504,2578521,2486484,2316485,2962298,2726493,2024815,2733605,2224063,2262954,2470224,2069954,2216219,2072573,2819666,2530061,2452773,2781148,2395423,2191726,2733983,2841608,2022881,2857621,2499287,2614848,2265971,2863799,2511932,2488257,2329170,2148536,2003957,2832096,2443980,2580789,2460825,2373072,2945123,2613283,2705434,2717252,2885414,2642547,2846737,2599958,2964189,2363316,2259815,2972088,2450919,2175593,2832782,2665328,2124147,2234675,2459396,2395082,2991148,2564279,2179031,2081756,2852890,2444777,2410931,2054090,2449515,2830727,2805804,2017057,2459845,2626913,2147944,2009603,2493186,2090507,2442975,2276976,2651759,2299249,2629017,2079205,2181039,2541142,2565778,2248481,2375714,2391088,2045831,2072841,2264631,2521218,2603703,2479603,2647359,2938188,2861181,2939371,2866933,2395241,2741432,2781366,2249594,2924061,2173166,2143518,2158890,2267168,2628089,2739204,2523827,2454644,2273811,2673889,2055498,2652152,2480569,2777475,2675520,2917155,2074810,2718380,2779397,2401884,2668796,2901199,2629863,2601117,2694783,2262423,2821568,2568151,2619440,2380974,2847500,2628201,2724004,2320365,2828047,2817238,2649069,2592655,2545805,2007014,2324586,2614370,2085908,2832615,2681706,2319939,2128916,2682585,2520020,2437099,2474455,2171918,2624287,2391873,2356084,2250958,2762081,2713295,2790136,2515489,2798844,2544810,2270714,2786656,2856705,2027670,2046968,2601035,2249520,2216878,2473424,2519548,2066190,2252381,2984397,2113894,2629241,2036049,2960474,2691059,2271308,2804781,2466294,2316216,2759275,2902572,2570037,2242884,2605334,2682645,2803730,2987332,2562137,2525274,2348540,2432806,2411940,2680915,2955452,2479019,2713189,2315154,2254742,2128442,2455763,2615050,2869162,2600750,2279766,2706960,2212275,2414878,2899952,2372196,2078180,2361339,2246457,2012451,2803978,2223355,2158266,2763657,2162434,2008759
```

Each seed contributes boundaries 1, 2 and 3:

```
discovery   = 240 × 3 = 720 boundaries
replication = 240 × 3 = 720 boundaries
total       = 1440 boundaries
```

Required disjointness:

- discovery ∩ replication = empty;
- no KCL-6.5.6 discovery/protected-confirmatory overlap;
- no KCL-6.5.9.1 replication overlap;
- no KCL-6.5.9.2 train/validation overlap;
- no KCL-6.5.9.3 train/validation overlap.

The protected confirmatory cohort remains untouched.

## 8. Execution substrate

Reuse the frozen KCL-6.5.6 A/B/C counterfactual harness and A-reference
trajectory.

For each fresh seed and each boundary:

1. construct the canonical boundary state;
2. execute A/B/C counterfactuals exactly as upstream;
3. derive `safe_B`, `safe_C` using the unchanged KCL-6.5.9 predicates;
4. if and only if target = `A_ONLY`, derive B/C atomic failure reasons and
   frozen signatures.

No classifier, encoder, feature selection or policy optimization is invoked.

## 9. Phase support gate

Each phase is valid for primary inference only if `A_ONLY` itself has:

```
A_ONLY boundary count      >= 150
A_ONLY unique seed count   >= 100
```

If discovery support fails:

```
NEGATIVE
A_ONLY_FAILURE_MODE_DISCOVERY_SUPPORT_INSUFFICIENT
```

Replication is not authorized.

If replication support fails after an authorized discovery:

```
NEGATIVE
A_ONLY_FAILURE_MODE_REPLICATION_SUPPORT_INSUFFICIENT
```

## 10. Discovery mode support

For a primary mechanism-multiset signature to be DISCOVERY_SUPPORTED, all are
required:

```
count among A_ONLY          >= 12
unique seed count           >= 10
prevalence among A_ONLY     >= 0.05
```

If fewer than two distinct primary signatures are discovery-supported:

```
NEGATIVE
NO_SUPPORTED_A_ONLY_FAILURE_MODE_HETEROGENEITY
```

Replication is not authorized.

This gate is frozen before discovery.

## 11. Seed-cluster prevalence bootstrap

For discovery and replication separately:

```
20,000 whole-seed bootstrap resamples
all 3 boundaries travel with the sampled seed
prevalence denominator = A_ONLY boundaries in that resample
```

Frozen RNG seeds:

```
discovery bootstrap   = 659401
replication bootstrap = 659402
```

Report 95% percentile CIs for every observed primary mechanism signature.

## 12. Replication support

Only discovery-supported primary signatures are eligible for primary
replication adjudication.

A discovery-supported mode is REPLICATION_SUPPORTED iff:

```
replication count among A_ONLY        >= 12
replication unique seed count         >= 10
replication prevalence among A_ONLY   >= 0.05
```

No new replication-only mode can create primary PASS. It is descriptive only.

## 13. Frozen prevalence-stability test

For each discovery-supported mode, use 20,000 independent whole-seed bootstrap
pairs:

```
delta = prevalence_replication - prevalence_discovery
RNG seed = 659403
```

A mode is STABLY_REPLICATED iff:

```
DISCOVERY_SUPPORTED
AND REPLICATION_SUPPORTED
AND abs(point_delta) <= 0.10
AND bootstrap_95pct_delta_lower <= 0
AND bootstrap_95pct_delta_upper >= 0
```

Thus a mode must recur at meaningful support and the fresh cohorts must not show
a resolved prevalence shift.

## 14. Primary adjudication

### PASS

If at least two distinct primary mechanism-multiset signatures are
STABLY_REPLICATED:

```
PASS
A_ONLY_CONTAINS_REPLICATED_FAILURE_MODE_HETEROGENEITY
```

Interpretation:

`SAFE_ACTION_SET-v1/A_ONLY` collapses multiple reproducible failure
mechanisms. A subsequent study may define a more causally specific target
against these frozen modes.

### NEGATIVE

If discovery found at least two supported modes but fewer than two stably
replicate:

```
NEGATIVE
A_ONLY_FAILURE_MODE_HETEROGENEITY_NOT_REPLICATED
```

If discovery itself has fewer than two supported modes, use the discovery
negative verdict from Section 10.

### REVISE

Only technical/provenance/integrity defects may produce REVISE.

Threshold failure is scientific NEGATIVE, not REVISE.

## 15. Secondary descriptive outputs

Report without changing the verdict:

- ordered B/C pair signatures;
- per-policy cause-code counts;
- atomic-reason prevalence for B and C;
- SAME_CAUSE_SET vs DIFFERENT_CAUSE_SET;
- boundary-index counts by mode;
- Shannon entropy of primary mechanism signatures within A_ONLY;
- effective number of modes `2^H`;
- continuous margins:
  - AUC delta vs A;
  - final-accuracy delta vs A;
  - retention delta vs A.

No secondary result may replace the frozen primary gate.

## 16. Integrity requirements

Each phase requires:

1. exact frozen seed set and count;
2. exactly three boundaries per seed;
3. boundaries exactly {1,2,3};
4. no overlap with prior/protected cohorts;
5. all A/B/C counterfactual integrity checks valid;
6. exact target truth table;
7. every unsafe B/C policy has a non-empty atomic failure set;
8. every atomic reason agrees exactly with the frozen predicate complement;
9. every `A_ONLY` record has both B and C unsafe;
10. primary signature is invariant to B/C role exchange by construction;
11. all reported continuous margins finite;
12. no classifier trained;
13. no controller implemented;
14. protected confirmatory cohort untouched;
15. KCL-7 not started.

## 17. Anti-peeking / phase order

The replication cohort is frozen in this protocol but must not execute before:

1. discovery completes;
2. discovery evidence is preserved in git;
3. discovery support gate is adjudicated;
4. replication is explicitly authorized by the frozen gate.

No replication statistics may influence discovery thresholds or taxonomy.

## 18. Scope exclusions

KCL-6.5.9.4 does not:

- train a predictor;
- choose a representation;
- tune failure thresholds;
- merge rare modes after outcome inspection;
- add seeds after outcome inspection;
- use protected confirmatory seeds;
- implement an adaptive controller;
- open KCL-7;
- modify replay or memory.

## 19. STOP / PIVOT

### If PASS

Freeze the stably replicated mechanism signatures.

The next admissible question may test whether a **mechanism-specific target**
is more identifiable/predictable than `A_ONLY`, but that requires a new
preregistered cohort and protocol.

### If NEGATIVE

Do not post-hoc merge/split the failure taxonomy.

Reassess whether the safe-action conjunction itself is the right intervention
target before another predictor experiment.

### If REVISE

Repair implementation/provenance only. Taxonomy, cohorts and gates remain
frozen.

## 20. Required artifacts

```
docs/research/kernel-continual-learning/kcl6594-protocol.md
experiments/kernel_cl/kcl6594_action_target_failure_modes.py
tests/test_kernel_cl_kcl6594.py
.github/workflows/kernel-cl-kcl6594-discovery.yml
experiments/kernel_cl/results/kcl6594_discovery.json
.github/workflows/kernel-cl-kcl6594-replication.yml   # only if authorized
experiments/kernel_cl/results/kcl6594_replication.json
docs/research/kernel-continual-learning/kcl6594-paper.md
Lineage.md
README.md
```

No rule or controller artifact is authorized.

## 21. Closure

PASS path:

- protocol freeze before discovery;
- implementation + contract tests;
- one canonical discovery run;
- exact discovery evidence preservation;
- frozen support adjudication;
- only then open replication;
- one canonical replication run;
- exact replication evidence preservation;
- paper + append-only Lineage + README review.

Discovery-negative path closes without replication.

Protected confirmatory seeds remain untouched and KCL-7 remains NOT STARTED.

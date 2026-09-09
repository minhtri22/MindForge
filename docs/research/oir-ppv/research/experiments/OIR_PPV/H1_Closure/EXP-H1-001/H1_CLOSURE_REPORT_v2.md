# H1 Closure Report v2 - DEV_TASK_009_FIX_01

Developer candidate only: `SUPPORTED`. PM/QA owns final H1 acceptance.

Frozen epsilon: `0.02`. Original scientific matrix retained: 140/140 cells; failures: 0.

Corrected complexity uses deterministic, replayable canonical `X -> I` inference state. Utility is read unchanged from the original 140-cell evidence.

## Learner comparisons vs MEM

| Learner | Pairs | H1 wins/losses/ties | C_total W/L/T | Utility W/L/T | H1 rate | C delta mean/median/min/max | Utility delta mean/median/min/max |
|---|---:|---|---|---|---:|---|---|
| L0 | 20 | 20/0/0 | 20/0/0 | 20/0/0 | 1.000 | -59859.800/-62046.500/-78534.000/-34941.000 | 0.556100/0.588889/0.320000/0.716667 |
| L1 | 20 | 19/1/0 | 20/0/0 | 19/1/0 | 0.950 | -58421.800/-60552.500/-77120.000/-33591.000 | 0.309382/0.285294/-0.077500/0.705556 |
| L2 | 20 | 19/1/0 | 20/0/0 | 19/1/0 | 0.950 | -58388.800/-60519.500/-77087.000/-33558.000 | 0.329538/0.295000/-0.057500/0.711111 |
| L3 | 20 | 20/0/0 | 20/0/0 | 20/0/0 | 1.000 | -58396.800/-60527.500/-77095.000/-33566.000 | 0.316654/0.285294/0.010000/0.716667 |
| L4 | 20 | 19/1/0 | 20/0/0 | 19/1/0 | 0.950 | -58384.800/-60515.500/-77083.000/-33554.000 | 0.317117/0.308824/-0.076250/0.722222 |

## Learner comparisons vs RAW

| Learner | Pairs | Utility W/L/T | Non-inferior | Utility delta mean/median/min/max | C_total delta mean/median/min/max | Ratio handling |
|---|---:|---|---:|---|---|---|
| L0 | 20 | 1/8/11 | 15/20 | -0.070424/0.000000/-0.328750/0.005556 | 1307.250/1381.500/852.000/1614.000 | null: RAW C_total=0 |
| L1 | 20 | 0/20/0 | 1/20 | -0.317141/-0.241667/-0.827500/-0.011111 | 2745.250/2811.500/2202.000/3156.000 | null: RAW C_total=0 |
| L2 | 20 | 2/18/0 | 2/20 | -0.296985/-0.188725/-0.807500/0.038889 | 2778.250/2844.500/2235.000/3189.000 | null: RAW C_total=0 |
| L3 | 20 | 0/19/1 | 1/20 | -0.309869/-0.241667/-0.740000/0.000000 | 2770.250/2836.500/2227.000/3181.000 | null: RAW C_total=0 |
| L4 | 20 | 1/19/0 | 1/20 | -0.309406/-0.208333/-0.826250/0.005556 | 2782.250/2848.500/2239.000/3193.000 | null: RAW C_total=0 |

## Per-environment evidence

### L0

| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |
|---|---:|---:|---:|---|
| ENV-1 | 5/5 | 5/5 | 5/5 | 0.000000/0.000000/0.000000 |
| ENV-2 | 5/5 | 5/5 | 0/5 | -0.279250/-0.328750/-0.250000 |
| ENV-3 | 5/5 | 5/5 | 5/5 | -0.001333/-0.006667/0.000000 |
| ENV-4 | 5/5 | 5/5 | 5/5 | -0.001111/-0.005556/0.005556 |

### L1

| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |
|---|---:|---:|---:|---|
| ENV-1 | 5/5 | 5/5 | 0/5 | -0.334239/-0.515464/-0.193182 |
| ENV-2 | 4/5 | 4/5 | 0/5 | -0.664000/-0.827500/-0.597500 |
| ENV-3 | 5/5 | 5/5 | 0/5 | -0.209216/-0.310000/-0.129412 |
| ENV-4 | 5/5 | 5/5 | 1/5 | -0.061111/-0.138889/-0.011111 |

### L2

| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |
|---|---:|---:|---:|---|
| ENV-1 | 5/5 | 5/5 | 0/5 | -0.334284/-0.509259/-0.156863 |
| ENV-2 | 4/5 | 4/5 | 0/5 | -0.633500/-0.807500/-0.498750 |
| ENV-3 | 5/5 | 5/5 | 0/5 | -0.186824/-0.370000/-0.066667 |
| ENV-4 | 5/5 | 5/5 | 2/5 | -0.033333/-0.100000/0.038889 |

### L3

| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |
|---|---:|---:|---:|---|
| ENV-1 | 5/5 | 5/5 | 0/5 | -0.340512/-0.515464/-0.204545 |
| ENV-2 | 5/5 | 5/5 | 0/5 | -0.629750/-0.740000/-0.563750 |
| ENV-3 | 5/5 | 5/5 | 0/5 | -0.205882/-0.300000/-0.129412 |
| ENV-4 | 5/5 | 5/5 | 1/5 | -0.063333/-0.144444/0.000000 |

### L4

| Environment | MEM H1 wins | MEM utility NI | RAW utility NI | RAW utility delta mean/min/max |
|---|---:|---:|---:|---|
| ENV-1 | 5/5 | 5/5 | 0/5 | -0.324023/-0.484536/-0.193182 |
| ENV-2 | 4/5 | 4/5 | 0/5 | -0.673250/-0.826250/-0.597500 |
| ENV-3 | 5/5 | 5/5 | 0/5 | -0.173686/-0.210000/-0.111765 |
| ENV-4 | 5/5 | 5/5 | 1/5 | -0.066667/-0.116667/0.005556 |

## Limitations

- **MEM_ZERO_TEST_HITS**: MEM exact-row lookup has 0 test hits across all 20 MEM environment/seed cells; test utility uses the frozen global-majority fallback.
- **RAW_ZERO_C_TOTAL**: RAW C_total=0 because raw input storage and the common downstream task head are excluded by the frozen accounting.
- **MEM_COMPARATOR_SCOPE**: H1 evidence supports claims only relative to the frozen exact-row MEM comparator under ENV-1..ENV-4 and the five frozen seeds.
- **NO_RAW_SUPERIORITY**: The evidence does not establish learned-representation superiority to RAW; negative RAW utility deltas are retained.
- **FIDELITY_LABELS**: L3 remains IRM-style surrogate and L4 remains adapted DANN exactly as frozen in EXP-LRN-001.

## Interpretation boundary

The candidate H1 result is relative only to the frozen exact-row MEM comparator. RAW remains a control and materially constrains interpretation. This report does not claim learned-representation superiority to RAW.

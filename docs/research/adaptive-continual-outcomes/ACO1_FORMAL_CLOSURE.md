# ACO-1 Formal Closure

Status: **STOP / CLOSED**

Date: 2026-09-20

Canonical verdict:

```text
TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

## Execution integrity

ACO-1 executed under independently verified Execution Lock v2.

- workflow run: `35511418837`
- lock SHA-256: `2104913295e85b66e8ef8f7bb66d7a182869d334ea2a6b2e0766f99e83787db8`
- protocol SHA-256: `a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb`
- seed-manifest SHA-256: `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`
- collection records: `120/120`
- collection integrity: **PASS**
- protected KCL overlap: `0`
- collection SHA-256: `b7ab6f5e0a6896f37f77112c3a0ef0c5597a940516a2947ecd2bbd410307e340`
- collection-before-adjudication artifact ID: `10606116496`
- collection-before-adjudication ZIP SHA-256: `25959db42a26440f2d1f29602ff0aba28f4fafa690f1a16ea00d70e0654b449d`
- one-shot adjudicator calls: `1`
- formal-result SHA-256: `60da9b69c903b93253e72ccc074f6af1edd1285a7db15d11afbaa94348723f9b`
- complete-evidence artifact ID: `10605063022`
- complete-evidence ZIP SHA-256: `3e09b7947fb825f24c3440a973668dcb86e0822405a141e686cb800db7300c28`
- canonical evidence commit: `2f82881fdc3bde203f7df04b17389ea362612d87`

No scientific metric was inspected between collection and one-shot adjudication.

## Formal support result

The preregistered primary population was canonical `Y_PRR = MECH{P+R,R}` boundaries.

Frozen support requirement:

```text
>= 30 canonical Y_PRR boundaries
across >= 2 boundary stages
```

Observed by the one-shot adjudicator:

```text
primary_count  = 12
primary_stages = [1, 2, 3]
integrity_ok   = true
support_ok     = false
```

Therefore:

```text
ACO-1 = STOP
TARGET_STABILITY_SUPPORT_INSUFFICIENT
```

## What this result establishes

It establishes that the **frozen 40-seed ACO-1 design does not contain enough canonical Y_PRR support to adjudicate the preregistered target-stability hypothesis**.

The result is not a PASS, NEGATIVE, or INCONCLUSIVE estimate of near-margin instability. The support gate stops the analysis before those statistics are scientifically admissible as the ACO-1 primary adjudication.

The presence of 12 canonical Y_PRR boundaries across all three stages confirms that the target occurs in the fresh cohort, but does not satisfy the frozen minimum support contract.

## What this result does not establish

ACO-1 does **not** establish that:

- Y_PRR is stable;
- Y_PRR is unstable;
- the thresholds should change;
- more seeds may be appended to the same ACO-1 study;
- the hard-label controller program should reopen;
- continuous outcomes are or are not predictable;
- ACO-2 is authorized.

The protocol explicitly prohibits adding extra seeds after outcome inspection.

## Program-level consequence

The frozen ACO roadmap contains the STOP condition:

> stop the active program if fresh support is insufficient under frozen design.

That condition is now met.

Therefore:

```text
ACO ACTIVE PROGRAM = STOP
ACO-2              = NOT AUTHORIZED
ACO-3..ACO-5       = NOT AUTHORIZED
CONTROLLER          = CLOSED
KCL-7               = CLOSED
PROTECTED KCL COHORT= UNTOUCHED
```

Any future work must begin with a formal convergence review and a newly justified research object/program. It may not be framed as “add more seeds to ACO-1” or an in-family rescue.

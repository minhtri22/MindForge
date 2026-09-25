# CLRM-0 — Freshness and Spent-Evidence Exclusions

Status: **FROZEN**

Every future CLRM scientific seed manifest must be disjoint from all previously
consumed scientific cohorts.

Mandatory exclusions include:

## KCL

- all historical KCL scientific seeds;
- protected KCL confirmatory seeds:

```text
13635,13837,14039,14241,14443,
14645,14847,15049,15251,15453,
15655,15857,16059,16261,16463,
16665,16867,17069,17271,17473
```

Protected KCL seeds remain untouched.

## ACO-1 spent cohort

Manifest SHA-256:

```text
9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91
```

## CPRM-1 spent cohort

Manifest SHA-256:

```text
d213e307a25fd49813d060cc6c88b91f6e2e7939a45d48ce29ab1048691bcfc3
```

## MSA-1 spent cohort

Manifest SHA-256:

```text
e5dbdfeb46889c422336bbc4b77a45ce8c87bbef48326ce6f48bfef75709e347
```

## MSA-3 spent confirmatory cohort

Manifest SHA-256:

```text
5fbcddd66c9094051721f0dd549031e621e66a2d4c62f5866b29eb7fc1efcbb8
```

## Future CLRM cohorts

Once a CLRM support, discovery-validation, or replication cohort is consumed,
it becomes spent for every later scientific role except exact reproduction.

No replacement seed may be chosen after scientific outcomes are inspected to
repair support or model performance.

CLRM-0 itself creates no fresh seed manifest.


## CLRM-1 spent support cohort

After canonical Gate-1 execution, the full Role-S cohort is spent.

Manifest SHA-256:

```text
3b8566fed61c625d2dee30406f5c40671a1f88a4b73d2e5a9c8aab0e00ab8ee6
```

This cohort is excluded from every CLRM-2 D-train/D-val manifest and every
future CLRM independent replication manifest.

It may be used only for provenance and exact reproduction of the CLRM-1
support verdict.

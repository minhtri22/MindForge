# CLRM-0 — Accuracy Sentinel Contract

Status: **FROZEN**

Terminal accuracy remains available only as a semantic/correctness diagnostic.

For each policy at the same terminal state used by the primary loss vector,
record:

```text
S_acc(X,a) = [
  current_terminal_accuracy,
  min_prior_terminal_accuracy
]
```

where `min_prior_terminal_accuracy` is the minimum terminal accuracy across
all tasks completed before the boundary.

These values:

- are not CLRM predictor targets;
- do not enter baseline-superiority qualification;
- do not enter point-calibration qualification;
- do not define boundary eligibility;
- do not define training weights;
- cannot be used to choose a model/feature family after outcomes.

No `0.95` or other correctness threshold is imported into CLRM-0.

A later decision study may preregister a correctness/safety threshold, but only
after response prediction independently qualifies and replicates.

This preserves terminal accuracy as an interpretable sentinel without treating
a replicated coarse endpoint as a high-resolution continuous target.

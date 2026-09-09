# Q-H2.1 — What Makes an Invariant Transferable?

Date: 2026-09-09

## Purpose

This is a PM/research analysis artifact executed before H3 closure.

It does not modify H3 code, protocol semantics, matrix, seeds, thresholds,
metrics, or previously completed H3 work.

## Question

> Một invariant phải có những thuộc tính nào thì mới chuyển giao tốt sang
> environment/context chưa thấy?

## Historical functional definition carried forward

The pre-v0.13.10 research lineage converged toward a functional definition:

```text
I = minimal causal representation
```

with four required properties:

```text
causal + transferable + generative + minimal
```

These are requirements on `I`, not fixed internal fields of `I`.

Mechanisms such as protection, replay, hierarchy, lifecycle, intervention
selection, and experiment selection remain mechanisms around `I` rather than
parts of its definition.

## Clean ground-truth example

A controlled stability environment gives a concrete example of a candidate
minimal causal representation.

Let an object remain stable when the projection of its center of mass lies inside
its support area:

```text
Y = 1[proj(CoM) in SupportArea]
```

A compact candidate representation can be the signed support margin:

```text
m = signed distance of proj(CoM) to the support boundary
Y = 1[m > 0]
```

This candidate is useful because it can, in principle, satisfy all four desired
properties under a known SCM:

- causal: intervention on CoM/support geometry changes stability according to the
  known mechanism;
- transferable: the same rule can apply to unseen shapes and contexts;
- generative: a generator can construct new stable configurations constrained by
  the rule;
- minimal: color, texture, object ID, background, and timestamps can be removed if
  they do not affect stability.

This example shows that the intended concept is coherent. It does not establish
that current OIR-PPV learners have discovered such a representation.

## Evidence from H1 and H2

H1 established, with limits, that some tested representations can use less
retained inference state than the frozen MEM comparator while retaining utility.

H2 then falsified the tested transfer prediction for L1-L4 relative to L0/PCA on
ENV-1, ENV-3, ENV-4 x five frozen seeds.

Therefore current evidence rejects the shortcut:

```text
compact / learned / more complex representation
    => transferable representation
```

Compression is not sufficient evidence of transfer.

## Directional evidence relevant to H3

The accepted reference evidence also contains a pattern relevant to Q-H2.1:

- L0/PCA is the strongest H2 transfer reference in the frozen comparison;
- prior QA aggregation found fewer nuisance-leakage runs for L0/PCA than for the
  tested L1-L4 configurations;
- the tested learned representations therefore do not currently show the
  combination of better transfer and better nuisance suppression.

This is directionally consistent with the idea that transferable representations
may need to retain task-relevant signal while suppressing nuisance/shortcut
information.

However, this is not yet causal evidence that nuisance suppression causes
transfer. It can also reflect learner fidelity, optimization quality, information
loss, environment-specific structure, or other representation differences.

## Candidate refinement of I

The current evidence motivates a narrower candidate definition:

```text
I_candidate = causal sufficient statistic for the task under the tested shifts
```

Operationally, such an `I_candidate` should retain the smallest structure needed
to preserve task-relevant causal response while removing nuisance information that
does not belong to that response.

This creates a useful hierarchy:

```text
I_surface
  -> I_predictive
  -> I_causal_sufficient
```

where:

- `I_surface` can encode stable appearance or shortcuts;
- `I_predictive` can predict well in the observed domain without being causal;
- `I_causal_sufficient` is expected to preserve the task-relevant causal
  structure under intervention and shift with no unnecessary state.

## What is and is not supported now

Supported by current evidence:

1. minimality/compression alone is insufficient for transfer;
2. learned/nonlinear method class alone is insufficient for transfer;
3. nuisance suppression plus retained predictive utility is a plausible property
   to test as part of transferable invariance;
4. a known-SCM benchmark can instantiate a genuine minimal causal invariant, such
   as the center-of-mass/support-margin example.

Not yet supported:

1. that nuisance suppression is sufficient for transfer;
2. that current PCA has discovered the true causal invariant rather than a useful
   benchmark-specific projection;
3. that a causal sufficient statistic has been learned by any current L0-L4
   learner;
4. that causal sufficiency alone guarantees generative capability;
5. that the four historical properties collapse into one uniquely identifiable
   latent representation.

## Q-H2.1 status

`UNRESOLVED`

Reason: current evidence narrows the candidate properties of a transferable
invariant, but does not identify or causally establish the required representation.

Directional interpretation to carry into H3:

```text
transferability may require:
retain task/causal signal
+ suppress nuisance/shortcut signal
+ preserve utility under task-preserving intervention
```

H3 can strengthen, contradict, or leave this explanation unresolved using its
already-defined nuisance-robustness closure evidence. H3 must not be redesigned to
make this candidate hypothesis pass.

## Next use

Resume the existing H3 closure preparation unchanged.

When H3 evidence is available, compare its paired `do(N)` robustness, leakage,
and retained utility results against this analysis. Record whether H3:

- strengthens the causal-sufficiency interpretation;
- contradicts nuisance suppression as a useful discriminator; or
- leaves Q-H2.1 unresolved.


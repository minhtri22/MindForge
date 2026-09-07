# OIR-PPV Formal Model Specification

## Purpose

This document defines the mathematical layer required before OIR-PPV reconstruction or validation.

The current hypothesis documents define semantic concepts (invariant, generator, validation), but a reproducible research protocol requires formal objects, metrics, and acceptance criteria.

This document does NOT claim the hypothesis is proven. It defines what must be formalized and tested.

---

# 1. Experience Representation

Let an experience trajectory be:

$$
E = \{(s_t, a_t, r_t, c_t)\}_{t=1}^{T}
$$

where:

- $s_t$: system state
- $a_t$: action/intervention
- $r_t$: observed outcome/value
- $c_t$: context/environment

A simulator must define the transition function:

$$
s_{t+1}=F(s_t,a_t,c_t)
$$

before claiming experimental validity.

---

# 2. Invariant Definition

The invariant extractor is modeled as:

$$
I=f(E)
$$

A valid invariant should minimize representation complexity while preserving explanatory power:

$$
I^*=\arg\min_I C(I)+\lambda L(E|I)
$$

where:

- $C(I)$: complexity of invariant representation
- $L(E|I)$: unexplained evidence after using invariant

Required properties:

1. causal stability
2. transferability
3. generativity
4. minimality

---

# 3. Generator Model

A generator maps invariant and context into manifestations:

$$
x=G(I,c)
$$

A valid generator should produce multiple manifestations:

$$
\{G(I,c_1),G(I,c_2),...,G(I,c_n)\}
$$

while preserving invariant properties.

---

# 4. Validation Metrics

## Observation

Measure explanatory fit:

$$
M_{obs}=Accuracy(E,G(I,c))
$$

## Intervention

Intervention uses causal operation:

$$
do(X=x')
$$

Effect difference:

$$
\Delta Y=Y(do(X=x'))-Y(do(X=x))
$$

## Counterfactual

Compare predicted and observed alternative worlds:

$$
D(Y_{pred},Y_{actual})
$$

## Cross Environment

Evaluate transfer:

$$
T(I,c_1,c_2)
$$

## Novel Manifestation

Evaluate generation validity:

$$
V(G(I,c_{new}))
$$

---

# 5. Experiment Definition

An experiment is a controlled uncertainty reduction procedure:

$$
Experiment=(H,B,I,O,M)
$$

where:

- $H$: hypothesis
- $B$: baseline
- $I$: intervention
- $O$: observation
- $M$: metric

---

# 6. Reconstruction Requirement

Any reconstructed experiment must provide:

- state model
- simulator implementation
- seed
- configuration
- metrics
- acceptance threshold

Without these, the result is a hypothesis illustration, not an experiment.

---

# Research Gate

No OIR-PPV v1.0 claim should be accepted without connecting:

semantic hypothesis → mathematical model → simulator → experiment → evidence.

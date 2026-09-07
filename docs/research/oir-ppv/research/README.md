# OIR-PPV Controlled Causal Benchmark (CCB)

## Overview

OIR-PPV (Invariant Representation → Prediction → Validation) is a research benchmark protocol for testing whether an invariant representation can support reliable prediction, controlled generation, and causal validation under distribution shift.

The goal is not to introduce a new invariant learning method. Existing work has studied invariant prediction, causal representation learning, and domain generalization. OIR-PPV defines an evaluation pipeline that connects these capabilities into one measurable protocol.

## Research Question

Given experience generated from a controlled environment:

\[
E=(S,A,Y,Z,N)
\]

can a learned invariant representation \(I\) preserve useful structure when:

- context changes,
- nuisance variables change,
- new manifestations must be generated,
- interventions are applied,
- counterfactual outcomes are evaluated?

## Architecture

```text
                 Ground Truth SCM
                       |
                       v
             Environment Generator
                       |
                       v
          Experience Collector (S,A,Y,Z,N)
                       |
                       v
             Invariant Learner
                       |
                       v
              Latent Invariant I
                 /             \
                v               v
       Policy Generator   Manifestation Generator
          π(I,S,Z)             G(I,Z,N)
                \             /
                 v           v
              Intervention Engine
                       |
                       v
            Counterfactual Evaluator
                       |
                       v
                    Evidence
```

## Benchmark Families

### ENV-1 Identity and Style Shift

Keep the underlying mechanism fixed while changing style, identity, or presentation variables.

### ENV-2 Compositional Generation

Evaluate unseen combinations of character, style, and context factors.

### ENV-3 Causal Dynamics

Evaluate structural stability using state, action, outcome and intervention variables.

### ENV-4 Adversarial Shortcut

Introduce training correlations between nuisance variables and outcomes, then test shortcut resistance.

## Baselines

| ID | Method |
|---|---|
| B0 | ERM / context memorization |
| B1 | Domain generalization baseline (IRM, VREx class) |
| B2 | Encoder representation baseline |
| B3 | Invariant representation only |
| B4 | OIR-PPV invariant + generator pipeline |
| B5 | Oracle invariant |

## Current Research Status

This repository contains the research specification, theory, and benchmark design. Experimental implementations must preserve provenance, controlled environments, and frozen evaluation protocols.


# OIR-PPV Pre-Reconstruction Audit Prompt for Local Agent

## Mission

Before any reconstruction of OIR-PPV experiments, independently audit the complete research chain v0.1 -> v0.13.10.

The goal is NOT to prove the hypothesis. The goal is to determine whether the previous evidence chain is reproducible, traceable, mathematically defined, and scientifically valid.

Current concern:

The previous sandbox does not contain executable artifacts from the exploration. All claims from v0.1-v0.13.10 must be treated as unverified until source code, seeds, simulator versions, configs, results, and formal definitions are recovered.

---

# Mandatory Reading

Read first:

```
docs/research/oir-ppv/hypothesis.md
docs/research/oir-ppv/OIR-PPV-Research-Protocol-v1.0.md
docs/research/oir-ppv/FORMAL_MODEL_SPEC.md
```

The audit must verify the connection:

```
semantic hypothesis
        ↓
formal mathematical model
        ↓
simulator implementation
        ↓
experiment protocol
        ↓
evidence artifact
```

---

# Frozen Research Hypothesis

A system can discover compact latent invariants from experience that:

1. explain observed manifestations;
2. survive causal validation;
3. transfer across environments;
4. generate novel valid manifestations.

The hypothesis must be evaluated together with its formal model.

---

# Mathematical Audit Requirements

Verify whether experiments define:

## Experience

$$E=\{(s_t,a_t,r_t,c_t)\}_{t=1}^{T}$$

## State transition

$$s_{t+1}=F(s_t,a_t,c_t)$$

## Invariant extraction

$$I=f(E)$$

## Generator

$$x=G(I,c)$$

## Metrics

- observation accuracy
- intervention effect
- counterfactual distance
- cross-environment transfer
- novel manifestation validity

If missing, classify as:

```
formalization_missing
```

Do not invent formulas after the fact to justify historical experiments.

---

# Audit Objectives

## Objective 1 — Recover Evidence Chain

Inventory:

```
v0.1
 |
v0.11 failure discovery
 |
v0.12 hypothesis refinement
 |
v0.13.x validation experiments
 |
v0.13.10 final architecture
 |
v1.0 benchmark
```

For every stage identify:

- source code
- simulator version
- configuration
- random seed
- input data
- output artifact
- commit SHA
- execution command
- mathematical model mapping

---

# Objective 2 — Provenance Classification

Classify every artifact:

## ORIGINAL

Original evidence with source, seed, config and output.

## RECOVERED

Recovered from git/history/archive.

## RECONSTRUCTED

Recreated from specification.

Must NOT be called replay.

## NEW VALIDATION

Fresh experiment after audit.

---

# Objective 3 — Simulator Lineage Audit

For every simulator version record:

```
simulator_id
version
source_location
commit_sha
changes_from_previous
new_capabilities
known_limitations
formal_model_supported
validation_status
```

Verify whether v0.13.10 actually implements claimed mechanisms:

- protected invariant
- replay
- counterfactual validation
- invariant discovery
- adversarial testing

---

# Objective 4 — Reproduce Before Reconstruct

Do NOT create historical artifacts such as:

```
S11-A.json
S11-B.json
S11-C.json
```

until searching:

```
git log --all
git grep
branch history
deleted files
tags
```

Search:

```
S11
failure
seed
replay
benchmark
experiment
simulator
invariant
counterfactual
```

---

# Required Outputs

Create:

```
audit/
├── provenance_matrix.md
├── simulator_lineage.md
├── failure_history_review.md
├── missing_artifacts.md
├── reconstruction_boundary.md
└── formal_model_gap_analysis.md
```

Also:

```
audit_manifest.json
```

---

# Acceptance Criteria

Audit complete only when:

1. Every experiment has provenance status.
2. Every simulator version has lineage.
3. Every seed is identified or marked missing.
4. Every claim is classified:

```
verified
recovered
reconstructed
unverified
```

5. Formal model completeness is assessed.
6. Reconstruction starts ONLY after boundary approval.

---

# Final Rule

Do not optimize for green CI.

A failed reproduction with correct provenance is more valuable than a successful experiment with unknown origin.

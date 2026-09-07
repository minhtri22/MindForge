# OIR-PPV Pre-Reconstruction Audit Prompt for Local Agent

## Mission

Before any reconstruction of OIR-PPV experiments, independently audit the complete research chain v0.1 -> v0.13.10 on the local machine.

The goal is NOT to prove the hypothesis. The goal is to determine whether the previous evidence chain is reproducible, traceable, and scientifically valid.

Current concern:

The sandbox snapshot does not contain executable artifacts from the previous exploration. Therefore all claims from v0.1-v0.13.10 must be treated as unverified until source code, seeds, simulator versions, configs, and results are recovered.

---

# Frozen Research Hypothesis

OIR-PPV hypothesis:

A system can discover compact latent invariants from experience that:

1. explain observed manifestations;
2. survive causal validation;
3. transfer across environments;
4. generate novel valid manifestations.

Definitions:

## Invariant

A minimal causal principle that maintains effect across contexts, interventions and manifestations.

Required properties:

- causal
- transferable
- generative
- minimal

## Generator

A minimal mechanism that maps an invariant into multiple concrete manifestations.

## Validation ladder

Required validation sequence:

1. Observation
2. Intervention
3. Counterfactual validation
4. Cross-environment validation
5. Novel manifestation prediction
6. Self experiment

---

# Audit Objectives

## Objective 1 — Recover Evidence Chain

Build a complete inventory:

```
v0.1
 |
v0.11 failure discovery
 |
v0.12 hypothesis refinement
 |
v0.13.x causal validation
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

---

# Objective 2 — Provenance Classification

Classify every artifact into exactly one category:

## ORIGINAL

Evidence generated during the original experiment.

Requires:

- commit SHA
- source
- seed
- config
- output

## RECOVERED

Artifact restored from git history or archived storage.

## RECONSTRUCTED

Artifact recreated from description/specification because original evidence is unavailable.

Must NOT be called replay.

## NEW VALIDATION

A fresh experiment using the frozen hypothesis and protocol.

---

# Objective 3 — Simulator Lineage Audit

For every simulator version create:

```
simulator_id
version
source_location
changes_from_previous
new_capabilities
known_limitations
validation_status
```

Verify whether v0.13.10 actually contains all claimed mechanisms:

- protected invariant
- replay
- counterfactual validation
- invariant discovery
- adversarial testing

---

# Objective 4 — Reproduce Before Reconstruct

Do NOT create:

```
S11-A.json
S11-B.json
S11-C.json
```

until the following searches are completed:

```
git log --all

git grep

branch history

deleted files

tags
```

Search keywords:

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

# Objective 5 — Failure History Review

Review all failures from:

```
v0.11 -> v0.13.10
```

For each failure record:

```
Failure ID
Initial hypothesis
Observed failure
Why architecture changed
Expected improvement
Actual evidence
Remaining uncertainty
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
└── reconstruction_boundary.md
```

Also create:

```
audit_manifest.json
```

containing:

- commit SHA
- machine environment
- python version
- simulator version
- execution commands

---

# Acceptance Criteria

The audit is complete only when:

1. Every experiment has provenance status.
2. Every simulator version has lineage.
3. Every seed used is identified or marked missing.
4. Every claim is classified as:

```
verified
recovered
reconstructed
unverified
```

5. Reconstruction starts ONLY after the boundary document is approved.

---

# Final Rule

Do not optimize for green CI.

A failed reproduction with correct provenance is more valuable than a successful experiment with unknown origin.

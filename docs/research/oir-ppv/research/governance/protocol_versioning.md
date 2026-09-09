# OIR-PPV Protocol Versioning Policy

## Core rules

1. Protocols are immutable after freeze. Corrective semantics require an amendment or successor version.
2. Evidence remains attached to the exact protocol version under which it was generated.
3. Reinterpretation of historical evidence may narrow a claim but may not broaden it beyond the tested scope.
4. Re-evaluation after a scientific-semantic change requires a new protocol version and new evidence.
5. H3R is a new protocol lineage. It supersedes H3 protocol semantics for future work and does not overwrite historical H3 evidence.
6. Failed, invalidated, and superseded protocol artifacts remain preserved with provenance.

## Version-bump triggers

A protocol version bump or explicit amendment is required if any of the following changes after freeze:

- estimand;
- primary metric;
- shift class;
- split rule;
- representation scope or lifecycle;
- probe/equivalence contract;
- noise model;
- test lock;
- acceptance threshold;
- candidate-selection rule;
- causal-identification basis.

Changes to formatting or metadata that do not alter scientific semantics may be recorded as an erratum. An erratum must never mutate frozen evidence bytes when provenance depends on those bytes.

## H3 / H3R rule

```text
H3  = historical pre-Formal-v1 protocol + preserved evidence
H3R = Formal-Spec-v1 revised successor + new freeze + future new evidence
```

`H3R` does not inherit H3 scientific evidence. Historical H3 artifacts may be used only for protocol lineage, baseline selection, design constraints, and negative-result context.


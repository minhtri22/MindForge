# OIR-PPV v1.0 Research Plan

## Objective

Build OIR-PPV as a controlled causal benchmark that evaluates whether invariant representations can support generation, intervention, and counterfactual validation.

## Governance

PM/QA owns milestone acceptance, evidence review, artifact tracking, and release decisions. Dev owns implementation, experiments, and code changes. Every milestone requires a handoff package before QA review.

## Roadmap

### M0 - Research foundation freeze
Goal:
- Freeze research scope, claims, terminology, and repository structure.

Acceptance:
- README.md and THEORY.md reviewed.
- PLAN.md and HANDOFF.md available.
- Initial developer task issued.

Artifacts:
- docs/research/oir-ppv/research/*.md

### M1 - Controlled environment implementation
Goal:
- Implement SCM based environment generators.

Acceptance:
- ENV-1 to ENV-4 specification converted into executable configurations.
- Seed and provenance tracking available.

Artifacts:
- environment configs
- seed manifests
- execution logs

### M2 - Baseline benchmark suite
Goal:
- Implement B0-B5 comparison framework.

Acceptance:
- Same evaluation protocol for all baselines.
- Metrics defined for generalization, intervention stability, and generation quality.

Artifacts:
- benchmark runners
- baseline results

### M3 - OIR-PPV pipeline
Goal:
- Implement invariant learner and manifestation generator.

Acceptance:
- I representation extraction works.
- G(I,Z,N) generation path produces measurable outputs.

Artifacts:
- model checkpoints
- experiment reports

### M4 - Intervention and counterfactual validation
Goal:
- Validate causal robustness.

Acceptance:
- do(A), do(Z), do(N) experiments completed.
- Counterfactual evidence recorded.

Artifacts:
- intervention reports
- evaluation datasets

### M5 - Research release
Goal:
- Produce reproducible benchmark package.

Acceptance:
- Full provenance.
- Reproducible experiments.
- Final technical report.

Artifacts:
- release documentation
- benchmark package

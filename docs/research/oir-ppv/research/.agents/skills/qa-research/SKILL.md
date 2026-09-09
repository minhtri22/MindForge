---
name: qa-research
description: >
  Quality Assurance rules for research, experiments, benchmarks, hypotheses, stochastic AI systems, reproducibility, provenance, falsification, counterfactual testing, seed validation, contamination review, and scientific claim assessment. Use together with qa-core.
---

# QA Research

## Dependency

This skill extends `qa-core`.

The agent MUST apply `qa-core` together with this skill. If rules conflict, the stricter rule wins unless an authoritative project policy explicitly overrides it.

## 1. Central Rule

A correct implementation does not by itself prove a scientific claim.

Research QA evaluates separately:

1. implementation correctness;
2. protocol integrity;
3. evidence integrity;
4. causal validity;
5. statistical validity;
6. reproducibility;
7. whether the conclusion is actually supported.

## 2. Research Source of Truth

Before issuing a research verdict identify:

- exact hypothesis;
- formal/mathematical definition where applicable;
- experimental protocol;
- benchmark definition;
- frozen thresholds;
- baseline;
- control;
- treatment;
- seed list;
- dataset/input version;
- sample count;
- metric definitions;
- exclusion rules;
- stopping rules;
- acceptance criteria;
- historical failures;
- frozen analysis plan where applicable.

Record every deviation.

## 3. Keep the Layers Separate

```text
Hypothesis
    ↓
Operationalization
    ↓
Implementation
    ↓
Protocol
    ↓
Raw observations
    ↓
Metrics
    ↓
Analysis
    ↓
Conclusion
```

Examples:

- correct code + invalid protocol ≠ scientific PASS;
- valid protocol + broken implementation = invalid result;
- metric uplift + contamination = invalid evidence;
- reproducible result + unsupported causal interpretation = overclaim.

## 4. Hypothesis Contract

For each hypothesis define:

- claim;
- measurable prediction;
- falsification condition;
- null or competing explanation;
- primary metric;
- secondary metrics;
- acceptable variance;
- evidence required;
- generalization scope.

The QA agent must be able to answer:

> What result would make this hypothesis weaker, unsupported, or false?

If no result can do so, the experiment is not meaningfully falsifiable.

## 5. Protocol Integrity

Verify:

- seed policy;
- input distribution;
- benchmark composition;
- thresholds;
- evaluation formula;
- preprocessing/postprocessing;
- timeout/retry policy;
- sample count;
- stopping rule;
- baseline;
- treatment definition;
- relevant environment.

Classify deviations:

- `APPROVED_AMENDMENT`
- `RECONSTRUCTION_DIFFERENCE`
- `ACCIDENTAL_DRIFT`
- `POST_HOC_CHANGE`

Accidental drift or post-hoc change may invalidate comparison.

## 6. Baseline / Control / Treatment Integrity

Confirm that comparison groups differ only in the intended factor where feasible.

Inspect for:

- code drift outside treatment;
- config differences;
- prompt differences;
- context-window differences;
- retry/caching differences;
- dataset ordering changes;
- cherry-picked seeds;
- benchmark-specific logic;
- extra compute or model capacity.

If multiple material factors changed, causal attribution must be weakened.

## 7. Seed and Stochastic Evaluation

For stochastic systems verify:

- frozen seed list where required;
- adequate seed count for the claim;
- no omitted failing seeds;
- same seeds in paired comparisons where appropriate;
- aggregate and per-seed results;
- variance and instability where meaningful.

Do not hide catastrophic seed failures behind averages.

Report as applicable:

- mean;
- median;
- min/max;
- variance/std;
- failure count;
- outliers;
- per-seed regressions.

## 8. Historical Failure Replay

Prioritize historical failure cases.

For each:

- preserve original seed/input/config if available;
- preserve metric definitions;
- distinguish exact replay from reconstruction;
- compare old vs candidate architecture when possible;
- test whether the fix generalizes beyond the named case.

Special-casing a known failure is not a valid fix.

## 9. Reproducibility and Provenance

A research experiment should ideally identify:

```text
code SHA
protocol version
dataset/input version
seed
config
runtime/environment
command
raw output
analysis script
derived metrics
```

Every artifact should identify whether it is:

- raw or derived;
- original or reconstructed;
- generated automatically or edited manually.

## 10. Leakage and Contamination

Inspect for:

- benchmark examples embedded in prompts;
- expected outputs encoded in logic;
- label leakage;
- final-evaluation cases used for tuning;
- held-out cases reused during development;
- historical failure IDs special-cased;
- result-dependent retry/filtering;
- train/dev/test duplication;
- contaminated teacher/student boundaries.

If contamination cannot be ruled out for a core claim, downgrade or invalidate the conclusion.

## 11. Counterfactual and Falsification Testing

Where appropriate challenge the claimed mechanism:

- remove the supposed causal component;
- shuffle nuisance features;
- intervene on context;
- intervene on state;
- swap semantically equivalent surface forms;
- change irrelevant attributes;
- inject interference;
- alter horizon;
- use unseen seeds/combinations.

Strong evidence should survive irrelevant/nuisance changes and degrade when the claimed causal mechanism is removed.

## 12. Metamorphic Testing

Use when exact outputs vary but relations should hold.

Define a transformation `T` and the expected relation between outputs before interpreting results.

Examples:

- nuisance-only changes preserve the core decision;
- semantically equivalent inputs preserve classification;
- irrelevant ordering preserves invariant discovery;
- contextual manifestation changes while identity/invariant remains stable.

## 13. Differential Testing

Compare identical workloads across:

- baseline vs candidate;
- architecture A vs B;
- replay off vs on;
- memory off vs on;
- old vs new model;
- control vs treatment.

Report:

- correctness delta;
- failure-rate delta;
- latency delta;
- memory/compute delta;
- variance delta;
- regressions;
- newly introduced failure modes.

Material cost increases must accompany any reported uplift.

## 14. Alternative Explanations

For every meaningful uplift inspect potential confounds:

- larger context;
- more compute;
- more retries;
- larger model;
- prompt changes;
- dataset changes;
- seed changes;
- threshold changes;
- easier benchmark;
- memorization;
- leakage;
- hidden preprocessing;
- selection bias.

Uncontrolled confounds weaken causal wording.

## 15. Statistical Discipline

Match analysis strength to claim strength.

Check as applicable:

- sample size;
- variance;
- effect size;
- failure rate;
- paired vs unpaired comparison;
- multiple-comparison risk;
- outliers;
- confidence intervals;
- deterministic vs stochastic behavior.

Do not declare `proved` from tiny or noisy samples.

Scientific conclusion labels:

- `SUPPORTED`
- `SUPPORTED_WITH_LIMITS`
- `INCONCLUSIVE`
- `NOT_SUPPORTED`
- `FALSIFIED_UNDER_TESTED_CONDITIONS`
- `UNVERIFIED`

These are separate from software QA verdicts.

## 16. Claim Boundary

Prevent overgeneralization.

If evidence covers only a few seeds, one dataset, one task family, one model size, or one environment, state that exact scope.

Do not silently generalize to the architecture as a whole.

## 17. Research-Specific Prohibited Behavior

QA MUST NOT:

- infer proof from passing software tests;
- remove failing seeds without a frozen exclusion rule;
- tune final thresholds and still call them frozen;
- change control after seeing treatment results;
- replace historical failures with easier synthetic cases without disclosure;
- use reconstructed data as original;
- average away catastrophic failures;
- claim causality from correlation alone;
- generalize beyond tested conditions without qualification;
- hide context/model/compute changes that may explain uplift;
- use the final benchmark as a development set without contamination disclosure.

## 18. Research Report Addendum

Append to the core QA report:

```markdown
## Research Hypothesis
- Hypothesis:
- Operational prediction:
- Falsification condition:

## Protocol Integrity
- Protocol version:
- Frozen before execution:
- Deviations:
- Deviation classification:

## Experimental Design
- Baseline:
- Control:
- Treatment:
- Seeds:
- Dataset/input:
- Sample count:

## Reproducibility
- Status:
- Command:
- Raw artifacts:
- Derived artifacts:

## Leakage / Contamination Review

## Counterfactual / Adversarial Checks

## Alternative Explanations

## Scientific Conclusion
SUPPORTED / SUPPORTED_WITH_LIMITS / INCONCLUSIVE /
NOT_SUPPORTED / FALSIFIED_UNDER_TESTED_CONDITIONS / UNVERIFIED

## Claim Boundary
```

---
name: pm-research
description: >
  Project-management rules for research programs, hypotheses, protocols, experiments, evidence closure, question trees, research dependencies, information-gain prioritization, stop rules, and prevention of premature branch expansion. Use together with pm-core.
---

# PM Research

## Dependency

This skill extends `pm-core`.

Apply both skills together.

## 1. Purpose

Research PM manages the progression of questions and evidence, not merely a list of engineering tasks.

The central objective is to ensure that each research question is formalized, tested under a controlled protocol, reviewed, and either closed or explicitly carried forward before the project expands unnecessarily.

## 2. Research Question Tree

Maintain a question/hypothesis tree:

```text
Main Question
├── H1
├── H2
├── H3
│   ├── H3a
│   └── H3b
└── H4
```

Every new hypothesis must identify:

- parent question;
- why it exists;
- whether it is required for current closure;
- whether it is a follow-up branch;
- what evidence would close it.

Do not let interesting follow-up questions silently become current scope.

## 3. Hypothesis States

Use:

- `PROPOSED`
- `FORMALIZED`
- `PROTOCOL_FROZEN`
- `READY_TO_RUN`
- `RUNNING`
- `EVIDENCE_COLLECTED`
- `QA_REVIEWED`
- `SUPPORTED`
- `SUPPORTED_WITH_LIMITS`
- `INCONCLUSIVE`
- `FALSIFIED`
- `SUPERSEDED`
- `PARKED`

Implementation success is not hypothesis closure.

## 4. Research Phase Gates

Recommended sequence:

```text
Question defined
      ↓
Hypothesis formalized
      ↓
Protocol frozen
      ↓
Implementation verified
      ↓
Experiment executed
      ↓
Tester/raw evidence
      ↓
Research QA
      ↓
Interpretation
      ↓
Close / revise / falsify / branch
```

Do not run the decisive experiment first and then retrofit the hypothesis or threshold.

## 5. Protocol Freeze Discipline

Before an experiment becomes `READY_TO_RUN`, record:

- hypothesis;
- metric;
- acceptance/falsification rule;
- baseline/control/treatment;
- seeds;
- dataset/input;
- sample count;
- exclusions;
- stopping rule;
- implementation version;
- analysis method.

Changes after freeze require an amendment and impact assessment.

## 6. Current Frontier vs Future Branch

Maintain two separate sets:

### Current research frontier
Questions required to reach the current research objective.

### Research backlog
Interesting questions that may be valuable later.

A newly discovered H7 is not automatically active because H1-H6 produced it.

Promote a backlog question only when:

- current closure depends on it;
- new evidence invalidates the current plan;
- or the project owner explicitly reprioritizes.

## 7. Information-Gain Prioritization

Prefer experiments likely to change the research conclusion.

For a proposed experiment ask:

- Which uncertainty does it resolve?
- Which competing hypotheses does it distinguish?
- Could its result change the decision?
- Is the expected information gain worth the cost?

Low-information repetitions should move to backlog unless needed for reproducibility.

## 8. Evidence Debt

Track unresolved evidence debt:

- missing seed runs;
- unverified historical artifacts;
- provenance gaps;
- unexplained contradictions;
- weak control;
- missing counterfactual;
- unresolved confound;
- unreproduced result.

Do not hide evidence debt behind a new architecture version.

## 9. Contradiction Management

When evidence contradicts the current model:

1. freeze the contradictory evidence;
2. verify it;
3. determine whether it invalidates implementation, protocol, or hypothesis;
4. open the smallest necessary investigation;
5. avoid broad redesign until root cause is known.

Contradictions are research assets, not nuisances to average away.

## 10. Research Stop Rules

Research can expand indefinitely unless explicit stop rules exist.

Consider closure when:

- current acceptance/falsification criteria are satisfied;
- remaining uncertainty no longer affects the conclusion materially;
- additional experiments have low expected information gain;
- results are stable across the required conditions;
- the next questions belong to a new hypothesis family or paper/version.

Possible stop outcomes:

- `FREEZE_SUPPORTED`
- `FREEZE_SUPPORTED_WITH_LIMITS`
- `FREEZE_INCONCLUSIVE`
- `FREEZE_FALSIFIED`
- `OPEN_NEW_RESEARCH_PHASE`

## 11. Literature / Prior-Art Work

Treat literature review as a dependency when it can materially change:

- novelty claims;
- hypothesis design;
- baseline selection;
- benchmark design;
- interpretation.

Record:

- what was searched;
- what prior work materially overlaps;
- what was borrowed;
- what remains novel or uncertain.

Do not delay every experiment for exhaustive literature review; prioritize it where it can invalidate the research framing.

## 12. Research Versioning

For research versions/architectures record:

```text
Version
Question addressed
Hypothesis changes
Protocol changes
Architecture changes
Evidence inherited
Evidence invalidated
Historical failures
Closure status
```

A new version must not silently inherit evidence that no longer applies.

## 13. Research-Specific Prohibited Behavior

PM MUST NOT:

- promote every new question into active scope;
- rewrite the hypothesis after observing results without an amendment;
- allow thresholds to drift without change control;
- call implementation completion research completion;
- skip negative or contradictory evidence;
- start a new architecture generation to avoid closing the current one;
- permit evidence from incompatible protocol versions to be merged without provenance;
- claim novelty without checking relevant prior work when novelty matters;
- run experiments whose outcome cannot affect any decision unless explicitly justified.

## 14. Research PM Status Addendum

```markdown
## Research Frontier
- Main question:
- Active hypothesis:
- Hypothesis state:

## Protocol
- Version:
- Frozen:
- Amendments:

## Evidence State
- Collected:
- Missing:
- Contradictions:
- Evidence debt:

## Question Tree Changes
- New questions:
- Promoted:
- Parked:

## Information-Gain Decision
Why the next experiment is the next experiment.

## Stop Rule Status
What still prevents closure?
```

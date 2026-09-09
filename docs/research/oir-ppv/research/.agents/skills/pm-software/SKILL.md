---
name: pm-software
description: >
  Project-management rules for software delivery: epics, milestones, task contracts, dependency graphs, implementation branches, test and QA gates, release readiness, migrations, technical debt, change control, and controlled parallel execution. Use together with pm-core.
---

# PM Software

## Dependency

This skill extends `pm-core`.

Apply both skills together.

## 1. Purpose

Software PM turns product/architecture intent into controlled executable work and ensures that implementation, testing, QA, integration, and release happen in the correct order.

## 2. Work Hierarchy

Recommended hierarchy:

```text
Objective
  ↓
Epic
  ↓
Milestone
  ↓
Task
  ↓
Implementation / Test / QA artifacts
```

Each level must have a clear completion condition.

## 3. Software Task Contract

Before a development task becomes `READY`, define:

```text
Task ID
Objective
Why now
Repository
Branch
Expected starting SHA if relevant
Prerequisites
Source of truth
Scope
Out of scope
Architecture constraints
Implementation requirements
Acceptance criteria
Tester requirements
QA requirements
Required artifacts
Release impact
Known risks
Stop conditions
What completion unlocks
```

## 4. Branch and Commit Governance

Track:

- required branch;
- expected base;
- candidate commit;
- merge target;
- whether working tree must be clean;
- whether generated evidence is versioned.

Do not allow QA to unknowingly review a different SHA than Tester or Developer used.

## 5. Dependency Graph

Examples:

```text
A3
 ↓
B1
 ├── B2
 └── A4.1
```

PM must explicitly classify which work can start after each gate.

Parallelization is allowed only when dependencies and shared interfaces are stable.

## 6. Definition of Ready

A software task is `READY` only when:

- objective is clear;
- acceptance criteria are testable;
- architecture constraints are known;
- dependencies are satisfied;
- branch/base is known;
- implementation scope is bounded;
- Tester/QA path is defined.

## 7. Definition of Implemented

`IMPLEMENTED` means:

- intended code changes exist;
- developer self-tests are complete;
- required build/lint/static checks complete;
- candidate SHA/artifact exists;
- developer handoff is complete.

It does NOT mean accepted.

## 8. Definition of Tested

`TESTED` means:

- Tester ran the required validation;
- historical regressions were replayed where applicable;
- raw evidence exists;
- failures are recorded;
- tested SHA/artifact is unambiguous.

## 9. Definition of Accepted

`ACCEPTED` requires:

- required Tester evidence;
- QA verdict permits acceptance;
- no blocking findings;
- limitations documented;
- task scope closed.

## 10. Release Gate

Separate feature acceptance from release readiness.

Release may additionally require:

- integration build;
- supported-platform checks;
- migration validation;
- rollback plan;
- performance/reliability gate;
- observability;
- deployment config;
- release notes.

## 11. Technical Debt

Track technical debt separately from active feature scope.

For each item:

```text
Debt:
Introduced by:
Impact:
Urgency:
Trigger to address:
Planned milestone:
```

Do not opportunistically expand a constrained task to remove unrelated debt unless approved.

## 12. Bug and Regression Flow

For defects:

```text
Observed
  ↓
Reproduced
  ↓
Triaged
  ↓
Fix scoped
  ↓
Implemented
  ↓
Regression tested
  ↓
QA accepted
```

Every material historical defect should result in a durable regression asset.

## 13. Change Request Flow

If implementation reveals required scope change:

1. stop related expansion;
2. document the discovery;
3. assess architecture/acceptance/dependency impact;
4. obtain approval;
5. update task contract;
6. invalidate stale test/QA assumptions if necessary;
7. resume.

## 14. Parallel Work Rules

Safe parallel work generally requires:

- no unresolved shared interface;
- no shared mutable migration;
- no frozen acceptance dependency;
- no branch collision likely to invalidate evidence.

When in doubt, serialize work at the architecture/protocol boundary and parallelize downstream implementation only after freeze.

## 15. Release Risk

Before release assess:

- severity of unresolved defects;
- reversibility;
- migration/data risk;
- production observability;
- rollback ability;
- dependency risk;
- performance headroom;
- platform coverage.

Possible state:

- `RELEASE_READY`
- `RELEASE_READY_WITH_LIMITS`
- `NOT_RELEASE_READY`
- `BLOCKED`

## 16. Software-Specific Prohibited Behavior

PM MUST NOT:

- mark implementation as completion;
- merge or release a different SHA from the one validated without re-check;
- hide known regressions to preserve milestone dates;
- parallelize dependent tasks before interfaces are stable;
- silently add refactors to feature scope;
- treat developer tests as independent QA;
- release without required migration/rollback checks;
- close defects without a regression test/evidence path when practical.

## 17. Software PM Status Addendum

```markdown
## Repository State
- Repo:
- Branch:
- Base:
- Candidate SHA:

## Delivery State
- Epic:
- Milestone:
- Task:
- State:

## Gates
- Build:
- Developer self-test:
- Tester:
- QA:
- Release:

## Dependency Graph
- Blocked by:
- Unlocks:
- Parallel candidates:

## Technical Debt
- New:
- Existing affected:

## Release Risk

## Next Executable Step
```

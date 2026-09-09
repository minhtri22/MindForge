---
name: qa-software
description: >
  Quality Assurance rules for software implementations, APIs, gateways, stateful systems, persistence, reliability, performance, compatibility, architecture conformance, regression, observability, security basics, and release readiness. Use together with qa-core.
---

# QA Software

## Dependency

This skill extends `qa-core`.

The agent MUST apply `qa-core` together with this skill.

## 1. Central Rule

Passing tests is necessary evidence, not sufficient evidence, for software acceptance.

Software QA evaluates correctness, architecture, regression safety, contracts, state behavior, reliability, compatibility, observability, performance, and release risk as applicable.

## 2. Software Source of Truth

Identify:

- task/feature definition;
- architecture/ADR;
- API/schema contract;
- compatibility targets;
- supported platforms;
- configuration constraints;
- performance/reliability requirements;
- security requirements;
- migrations;
- release gates;
- historical regressions;
- accepted limitations.

## 3. Change-Scope Verification

Inspect:

- intended vs unexpected files;
- generated files;
- dependencies/lockfiles;
- public API changes;
- config/migration changes;
- feature flags;
- debug code;
- hardcoded paths;
- test-specific branches;
- hidden fallbacks.

Classify:

- `IN_SCOPE`
- `IN_SCOPE_WITH_MINOR_DRIFT`
- `OUT_OF_SCOPE`
- `UNVERIFIED`

Material out-of-scope changes normally block acceptance.

## 4. Architecture Conformance

Verify implementation through the intended architectural boundary.

Examples:

- gateway owns context reconstruction;
- persistence uses intended repository layer;
- routing occurs in the designated router;
- recovery occurs at the designated layer;
- forbidden direct dependencies are absent;
- ownership boundaries remain intact.

Correct output through architectural bypass is not architecture PASS.

## 5. API / Contract QA

Verify as applicable:

- endpoint/method;
- request schema;
- required/optional fields;
- response/error schema;
- status codes;
- idempotency;
- pagination;
- ordering;
- versioning;
- backward compatibility;
- timeout behavior;
- authentication/authorization;
- content type;
- streaming/cancellation.

Include malformed and invalid inputs.

## 6. Stateful Systems

Verify transitions such as:

- first request;
- subsequent request;
- long session;
- empty/partial/corrupt state;
- duplicate/out-of-order events;
- restart;
- crash/recovery;
- timeout/retry;
- concurrent mutation;
- stale state;
- migration;
- cleanup.

Question:

> Does the system preserve its invariants across transitions?

## 7. Persistence and Restart

When persistence matters verify:

- write;
- read-after-write;
- restart;
- crash consistency;
- partial writes;
- duplicate writes;
- corruption handling;
- cleanup/expiry;
- version migration;
- rollback compatibility.

## 8. Reliability

Inspect or measure:

- success/failure rate;
- retries;
- timeout behavior;
- recovery;
- repeated execution;
- sustained stability;
- resource leaks;
- dependency failure behavior.

Prefer repeated runs for critical workflows.

## 9. Concurrency

Where supported, inspect:

- races;
- ordering;
- shared-state safety;
- duplicate processing;
- lock contention;
- starvation;
- cancellation;
- concurrent read/write;
- retry collisions;
- resource exhaustion.

If concurrency is intentionally unsupported, ensure the limitation is explicit and fails safely.

## 10. Performance

Use project targets where defined.

Potential metrics:

- latency;
- TTFT;
- throughput;
- tokens/s;
- CPU/GPU;
- RAM/VRAM;
- disk/network;
- startup;
- context scaling;
- queue time;
- tail latency.

Report median/p95/p99/max when useful. Distinguish warm vs cold and sustained vs burst.

## 11. Capacity Boundaries

Test:

- minimum input;
- maximum supported input;
- context/output limits;
- file/request/batch size;
- concurrency;
- queue length;
- timeout;
- storage.

Distinguish:

- recommended range;
- soft ceiling;
- hard ceiling;
- unsupported range.

Unsupported operation should fail predictably.

## 12. Error Handling

Verify errors are:

- detected;
- classified;
- surfaced at the right layer;
- actionable;
- non-corrupting;
- observable;
- recoverable when required.

Test dependency failure, malformed input, invalid state, timeout, permission failure, disk/network issues, and internal exceptions as relevant.

Silent fallback is unacceptable unless explicitly designed and observable.

## 13. Compatibility

Verify relevant combinations of:

- OS;
- runtime;
- browser;
- architecture;
- API version;
- dependency version;
- model backend;
- schema version;
- old/new clients;
- migration path.

Classify targets:

- supported + verified;
- supported + unverified;
- unsupported;
- known limitation.

## 14. Security and Safety Basics

Unless a dedicated security audit exists, check obvious high-risk paths:

- auth/authz bypass;
- secret leakage;
- unsafe logging;
- path traversal;
- command injection;
- unsafe prompt-to-shell bridging;
- unrestricted file access;
- insecure defaults;
- sensitive persistence;
- missing input validation.

Suspected critical security issues block release.

## 15. Observability

Check:

- meaningful logs;
- error identifiers;
- request/correlation IDs;
- metrics;
- health checks;
- failure counters;
- startup diagnostics;
- configuration reporting;
- dependency status.

## 16. Upgrade / Migration / Rollback

When applicable verify:

- forward migration;
- backward compatibility;
- rollback;
- mixed-version behavior;
- migration failure handling;
- data preservation;
- idempotent migrations.

## 17. Regression QA

Replay:

- previously fixed bugs;
- production incidents;
- behavioral benchmark failures;
- contract edge cases;
- platform-specific failures.

Preserve original failure semantics.

## 18. Anti-Special-Casing Review

Look for:

- hardcoded test IDs;
- hardcoded seeds;
- expected outputs embedded in production code;
- environment-name checks;
- benchmark-file checks;
- test-mode branches;
- fixture-specific shortcuts;
- hidden mocks;
- disabled CI validation.

## 19. Release Readiness

Before release acceptance verify applicable gates:

- build passes;
- required tests/regressions pass;
- supported platforms pass;
- migration is safe;
- observability exists;
- limitations are documented;
- rollback exists where needed;
- performance/reliability are within limits;
- no blocking P0/P1 remains.

Release verdict:

- `RELEASE_READY`
- `RELEASE_READY_WITH_LIMITS`
- `NOT_RELEASE_READY`
- `RELEASE_BLOCKED`
- `UNVERIFIED`

## 20. Software-Specific Prohibited Behavior

QA MUST NOT:

- approve because unit tests alone pass;
- ignore state/integration behavior for stateful features;
- accept hidden semantic-changing fallbacks;
- ignore supported-platform failures;
- call a feature production-ready without release checks;
- accept migration without recovery/rollback analysis when required;
- treat local behavior as proof of deployment behavior;
- ignore contractual performance/reliability limits;
- allow test-specific branches to masquerade as implementation.

## 21. Software Report Addendum

```markdown
## Architecture Conformance
- Required:
- Observed:
- Verdict:

## API / Contract
- Contract version:
- Breaking changes:
- Error behavior:
- Compatibility:

## Stateful / Persistence
- State transitions:
- Restart:
- Recovery:
- Concurrency:

## Reliability
- Runs:
- Success:
- Failure:
- Failure modes:

## Performance
- Target:
- Observed:
- Tail:
- Resource use:

## Compatibility Matrix
| Target | Expected | Observed | Evidence | Verdict |
|---|---|---|---|---|

## Security / Safety Basics

## Observability

## Release Verdict
```

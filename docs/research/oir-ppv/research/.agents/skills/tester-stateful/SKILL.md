---
name: tester-stateful
description: >
  Tester rules for stateful systems, multi-turn interactions, persistence, restart, recovery, ordering, retries, duplicate events, context reconstruction, lifecycle invariants, and concurrent state mutation. Use together with tester-core.
---

# Tester Stateful

## Dependency

Use together with `tester-core`.

## 1. Scope

Use for:

- conversational/multi-turn systems;
- gateways owning context;
- persistent services;
- caches;
- session systems;
- workflows/state machines;
- replay/memory systems.

## 2. State Transition Matrix

Cover:

- empty -> initialized;
- initialized -> updated;
- updated -> updated;
- updated -> restarted;
- restarted -> recovered;
- partial -> recovered/rejected;
- invalid -> rejected safely;
- expired -> renewed/rejected;
- concurrent -> resolved safely.

## 3. Multi-Turn Testing

For conversational systems test:

- system message preservation;
- role ordering;
- assistant/user alternation;
- tool-result placement;
- client sends full history;
- client sends only delta;
- long history;
- trimming/summarization;
- restart between turns;
- duplicate turn;
- out-of-order turn;
- conversation-ID mixup.

## 4. Persistence

Test:

- write/read;
- restart;
- partial write;
- duplicate write;
- stale state;
- deletion/expiry;
- migration;
- corruption;
- recovery.

## 5. Retry and Duplicate Events

Test:

- same operation twice;
- timeout then retry;
- operation succeeds but response is lost;
- duplicate event ID;
- reordered event delivery.

Verify idempotency or documented behavior.

## 6. Recovery

Inject or simulate:

- process restart;
- dependency restart;
- transient failure;
- timeout;
- malformed stored state;
- missing state.

Verify invariant preservation.

## 7. Concurrency

Where supported:

- two writers;
- reader during write;
- duplicate concurrent requests;
- conflicting updates;
- cancellation during mutation.

## 8. Invariants

Define state invariants explicitly before testing, e.g.:

- no turn reordering;
- no cross-session leakage;
- no duplicate committed event;
- state after restart is equivalent to pre-restart committed state.

## 9. Evidence

Capture before/after state identifiers, logs, commands, request sequence, and persisted artifacts where available.

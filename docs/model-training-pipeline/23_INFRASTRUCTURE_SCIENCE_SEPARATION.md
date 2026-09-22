# Model Pipeline — Infrastructure / Science Separation Reframe

**Status:** GOVERNANCE AMENDMENT / ZERO SCIENCE  
**Date:** 2026-09-22  
**Parent:** `fdfec8a926ff11f5e10ce0e360251b0ce86e5221`

## 1. Problem

The M6/M6R sequence allowed Ollama packaging, process invocation, Windows runtime configuration, and scientific/runtime-parity evidence to share one serial gate chain.

That made an infrastructure defect capable of:
- consuming a research attempt;
- terminally closing a study before its endpoint was measured;
- forcing repeated governance micro-gates;
- delaying scientific design even when only the execution substrate was unresolved.

RFD-C1 proved the immediate M6R HTTP 500 cause was a runtime launch-configuration conflict: quantized V-cache was active while flash-attention was off. That is a substrate/runtime-adapter problem, not a new model-quality hypothesis.

## 2. Lessons adopted from ArcLLM

This amendment adopts the separation principle established in ArcLLM TTFT_M2 A1:

```
research package
orchestration / transport
execution substrate
scientific execution
```

The critical principle is:

> Governance protects scientific degrees of freedom and provenance; it must not convert unrelated transport/orchestration/substrate defects into scientific failures.

ArcLLM also separates semantic model from execution topology. MindForge adopts the analogous distinction:

```
SCIENTIFIC CONTRACT
model/artifact + fixture + endpoint + comparator + threshold
             │
             │ binds through
             ▼
RUNTIME ADAPTER CONTRACT
backend translation + process/runtime config + evidence capture
             │
             │ executes on
             ▼
EXECUTION SUBSTRATE
OS + installed runtime + driver/backend + local machine
```

Changing a runtime-adapter implementation while the scientific contract is exact-unchanged is not automatically a scientific intervention.

## 3. Lessons adopted from NEXUS

NEXUS HR-WMT v0.2 demonstrates a stronger reusable pattern:

- harness qualification is a **non-scientific program**;
- it has an explicit scientific firewall;
- it uses non-study fixtures;
- its result qualifies a harness/environment scope, not a hypothesis;
- future studies bind to the qualified harness through their own frozen contracts;
- infrastructure qualification cannot reinterpret a prior scientific result;
- durable observability begins before qualification logic so infrastructure failure remains diagnosable without rerunning science.

MindForge adopts this reusable qualification model.

## 4. Three control objects

### 4.1 SCIENCE_GATE

Controls only:
- scientific question/hypothesis;
- model/artifact identity when scientifically relevant;
- intervention/treatment;
- data/fixtures used for the claim;
- endpoint/metric/comparator;
- threshold/materiality;
- freshness;
- outcome-exposure/retry semantics.

Only a SCIENCE_GATE may produce a scientific PASS/FAIL.

### 4.2 INFRA_QUALIFICATION

Controls:
- runtime executable/version/hash;
- runtime-adapter implementation;
- backend/process launch behavior;
- environment variables that affect backend execution;
- toolchain/driver/substrate capability;
- process I/O;
- observability/evidence durability;
- safe namespace and cleanup;
- synthetic/non-study fixture execution.

INFRA_QUALIFICATION may return:

```
QUALIFIED
FAIL_INFRA
UNRESOLVED_INFRA
```

It may not produce or change a scientific PASS/FAIL.

### 4.3 INFRA_BINDING_CHECK

A future study does not re-run the full qualification when a reusable infra qualification already exists.

It only verifies the study is executing inside the qualified scope:

```
qualification artifact identity
runtime executable/version/hash
adapter blob
relevant environment contract
target-machine/substrate scope
required API/capability identity
```

If exact binding PASSes, execution proceeds.

If binding fails, execution is unavailable until infrastructure is requalified. The scientific hypothesis remains unchanged.

## 5. Failure-domain semantics

### Before scientific outcome exposure

Infrastructure/orchestration/substrate failure:
- does not produce scientific FAIL;
- does not consume scientific retry/repair budget;
- may be repaired/versioned in the infrastructure lane;
- may not modify scientific artifacts, endpoints, thresholds, fixtures, seeds, comparator, or treatment.

### After scientific outcome exposure

A proven infrastructure invariant violation makes the run invalid for scientific interpretation.

A replacement scientific execution is allowed only when:
1. the scientific contract remains exact-unchanged;
2. the infrastructure defect is independently identified;
3. repair belongs only to infrastructure;
4. the prior outcome is not used to tune the scientific design;
5. the scientific contract's predeclared invalid-run policy allows replacement.

This rule preserves anti-rescue without treating infrastructure as science.

## 6. Parallel-progress rule

Infrastructure availability gates **execution**, not scientific thinking.

The following may proceed while infrastructure is unresolved:
- prior-art review;
- scientific question/specification;
- causal design;
- falsification criteria;
- endpoint/comparator freeze;
- static implementation;
- zero-science QA.

Only the first action that requires the qualified runtime is blocked.

## 7. Qualification reuse rule

A successful infra qualification is reusable until one of its scope keys changes.

Canonical scope tuple:

```
runtime family/version/hash
adapter implementation blob
OS/substrate scope
backend-selection contract
runtime environment contract
API contract
fixture class used for qualification
```

No repeated micro-gates are required when all scope keys are unchanged.

A study needs one consolidated binding check.

## 8. M6R/RFD consequence

Historical results remain immutable:

```
M6  = FAIL_PACKAGE / CLOSED
M6R = FAIL_RUNTIME / CLOSED
RFD-C1 = ROOT_CAUSE_IDENTIFIED
```

RFD-C1 root cause remains valid.

The earlier decision that proposed:

```
q4_0 KV cache -> f16
```

as the single **scientific intervention** for M6R2 is superseded.

Correct classification:

```
q4_0 KV cache -> f16/default
= infrastructure/runtime-adapter repair
≠ scientific treatment
```

It may therefore be qualified in a separate non-scientific infrastructure program.

## 9. M6R2 scientific identity after reframe

M6R2 is a fresh parity replication, not an infrastructure experiment.

Its scientific/evidence contract must preserve:
- exact admitted Q4 artifact;
- frozen Modelfile semantics;
- frozen eval_v1 fixtures;
- frozen generation contract;
- frozen llama.cpp parent comparator;
- task-vector/accuracy/format parity criteria;
- reasoning mapping.

M6R2 has **no scientific treatment corresponding to the KV-cache repair**.

Its runtime execution may begin only after one exact INFRA_BINDING_CHECK binds it to a separately qualified Ollama runtime adapter.

## 10. Infrastructure program

The reusable infrastructure lane is named:

`OWRQ — OLLAMA_WINDOWS_RUNTIME_QUALIFICATION`

OWRQ is:
- non-scientific;
- reusable;
- independent from M6/M6R/M6R2 outcomes;
- forbidden from using M6R parity outcomes as qualification criteria;
- allowed to qualify runtime configuration and observability using non-study fixtures.

Its first target is the already-identified launch conflict:
- quantized KV cache must not be present when incompatible with resolved flash-attention mode;
- default/f16 KV-cache path must be proven by runtime evidence;
- flash-attention must not be enabled merely to rescue the previous failure.

## 11. Milestone dependency rule

The model pipeline is no longer governed by one global serial rule.

Use dependency edges:

```
scientific/model work ───────────────► scientific claims
         │
         └── artifacts ──────────────► export/parity studies

infra qualification ────────────────► runtime execution availability

security/evidence hardening ────────► release eligibility
```

An infra FAIL can block an execution that depends on it, but cannot block unrelated research design or change a scientific verdict.

## 12. Next canonical steps

Two lanes now proceed independently:

```
OWRQ lane
  specification-only
  -> QA
  -> implementation
  -> non-study local qualification
  -> reusable QUALIFIED binding artifact

M6R2 lane
  science-only specification
  -> QA
  -> static implementation
  -> wait only at runtime-binding boundary
  -> one fresh execution after OWRQ binding PASS
```

M7 and bulk training are not authorized by this amendment.

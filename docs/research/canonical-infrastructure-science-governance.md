# Canonical Research Governance — Infrastructure Is Not Science

Status: **ADOPTED CANONICAL GOVERNANCE**

Source evidence:
- `governance/model-pipeline-infra-science-separation@750d6358a88e738cfaf971b3a5db3192f7622889`
- `research/model-pipeline-m6r-runtime-failure-decomposition@fdfec8a926ff11f5e10ce0e360251b0ce86e5221`

## Rule

MindForge separates three control objects:

~~~text
SCIENCE_GATE
INFRA_QUALIFICATION
INFRA_BINDING_CHECK
~~~

Only a SCIENCE_GATE may produce a scientific PASS/FAIL.

INFRA_QUALIFICATION governs execution substrate, runtime adapter, backend/process launch, environment, I/O, observability, namespace/cleanup and non-study qualification fixtures.

INFRA_BINDING_CHECK verifies that a study is running inside an already-qualified infrastructure scope.

## Failure semantics

Before scientific outcome exposure, infrastructure/orchestration/substrate failure:

- does not produce scientific FAIL;
- does not consume scientific repair/retry budget;
- may be repaired only in the infrastructure lane;
- may not modify scientific artifacts, endpoints, thresholds, fixtures, comparator, treatment, or frozen population.

After scientific outcome exposure, a proven infrastructure invariant violation may invalidate interpretation only under the study's predeclared invalid-run policy. Any replacement execution requires an exact-unchanged scientific contract and independently identified infra-only defect.

## Parallel progress

Infrastructure gates dependent **execution**, not scientific thinking.

The following remain allowed while infrastructure is unresolved:

- prior-art review;
- scientific question/specification;
- causal design;
- endpoint/comparator freeze;
- falsification criteria;
- static implementation;
- zero-science QA.

## Qualification reuse

A successful infrastructure qualification is reusable until a scope key changes:

~~~text
runtime family/version/hash
adapter implementation blob
OS/substrate scope
backend-selection contract
runtime environment contract
API contract
qualification fixture class
~~~

A dependent study performs one consolidated binding check rather than repeating qualification micro-gates.

## Historical lesson

M6/M6R/RFD demonstrated why this separation is required. RFD directly identified the historical runtime failure mechanism as quantized V-cache with flash-attention disabled. That failure mechanism remains historical evidence; it does not convert infrastructure repair into a scientific treatment.

## Portfolio consequence

Platform/runtime qualification may support research but is not itself a MindForge scientific axis. A platform PASS does not authorize a model-science successor.

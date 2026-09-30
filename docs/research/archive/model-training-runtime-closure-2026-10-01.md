# Model Training / Runtime Portfolio Closure — 2026-10-01

Status: **SCIENCE CLOSED; SUPPORTING PLATFORM RETAINED**

## Scientific/diagnostic history

~~~text
M5/Q4
  reproducible quantization/export capability
        ↓
M6
  FAIL_PACKAGE / CLOSED
        ↓
M6R
  FAIL_RUNTIME / CLOSED
        ↓
RFD-C1
  runtime root cause identified
        ↓
OWRQ
  QUALIFIED_RUNTIME_SCOPE / supporting infrastructure
        ↓
M6R2
  one fresh parity execution
  PASS_PARITY / CLOSED
~~~

## M6R2 final evidence

- branch closure: `research/model-pipeline-m6r2-parity@f8934c7af7e00a456f7b7a0761ae3953c69c71d6`
- source report SHA256: `86a970f61064682e3f5ebb4edb9107e61f762d16735486e0a547a4a34b32aed8`
- attempts authorized: 1
- attempts consumed: 1
- rerun authorized: no
- cleanup: pass
- parent task vector: `[false,false]`
- Ollama task vector: `[false,false]`
- parent accuracy: `0`
- Ollama accuracy: `0`

Interpretation: runtime/packaging behavioral parity under the frozen study contract. No model-quality, reasoning-improvement, or runtime-superiority claim is supported.

## Retained supporting platform

The following remain available as tooling/infrastructure, not active science:

- evidence-governed model-training/export specifications;
- reproducible Q4_K_M qualification;
- OWRQ qualified Windows/Ollama runtime scope.

M7, bulk training, and automatic model-pipeline successors remain unauthorized.

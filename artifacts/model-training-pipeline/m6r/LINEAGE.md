# M6R LINEAGE

## 2026-09-22 — Program opened from closed M6

Parent commit:
c9952ac66be2a15776dcfb92d7bd7e2e1355242e

M6 authoritative state:
FAIL_PACKAGE / CLOSED / one scientific attempt consumed / zero remaining.

M6R is opened as a fresh installed-runtime replication. It is not a rescue rerun.

Frozen changes relative to M6:
- venue: user-installed Windows Ollama instead of isolated extracted runtime
- system host: 127.0.0.1:11434
- exact target version: 0.34.2
- pre-attempt upgrade from older installed version is allowed
- user's existing model store is preserved and audited by initial/final model-name sets
- native Ollama CLI calls must use Start-Process with redirected stdout/stderr and explicit exit code

Frozen unchanged science:
- exact Q4 bytes/hash/manifest
- frozen Modelfile
- eval_v1 fixtures
- generation parameters
- llama-parent task vector [false,false]
- llama-parent accuracy 0
- tagged-text reasoning mapping
- one-attempt/no-rescue semantics

M7 and bulk training remain closed.

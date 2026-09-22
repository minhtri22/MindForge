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


## 2026-09-22 — System Ollama implementation locked / one local execution authorized

Authoritative implementation:
f9ffccc2a51ffea307d3acba76cd323aec505d65

Exact implementation blobs:
- script: e98d5aae30ff7f36f925f6cbd38ca298940e810a
- tests: 136474cc53cf9a3d03e1d7ddab151d487403616c
- workflow: 56009d74bcc0dacd2848db53418ef0455a8e8ce2
- preregistration: e06a290937dd1fd36fd76dbc466e99a777385d83

Static zero-science QA:
- run 35737544519
- job 106778562602
- 17/17 contract tests PASS
- PowerShell parse PASS
- system Ollama upgrade executed=false
- ollama create=false
- ollama chat=false
- M6R scientific execution=false

One local M6R attempt is now authorized.

If installed Ollama is older than 0.34.2, exact official v0.34.2 may be upgraded
before the scientific attempt. The upgrade installer is pinned by SHA256 and
Ollama Inc. Authenticode signer. Missing Ollama or a newer installed version
fails closed before attempt; fresh install and downgrade are not authorized.

The attempt is consumed only by the durable marker immediately before installed
ollama create starts. Native Ollama CLI processes use redirected stdout/stderr
and explicit exit codes; direct PowerShell native pipeline capture is forbidden.

M6 remains FAIL_PACKAGE/CLOSED. M7 and bulk training remain closed.

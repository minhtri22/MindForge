# 20 — Security, Privacy & Execution Sandbox Contract

## 1. Default security posture

Pipeline is local-first but must assume datasets, generated code, model files and external tooling can be untrusted.

Default:
- no automatic privilege escalation;
- no arbitrary host mutation;
- no secrets in logs/evidence;
- remote code denied unless explicitly allowlisted and pinned.

## 2. Runtime/tool installation policy

`RuntimeAdapter.locate()` is read-only.

Installation/update is a separate explicit operation:
```text
pipeline runtime install <runtime> --version <pinned>
```
and requires user/policy approval. Training/preflight must not silently update llama.cpp, Ollama, Python, drivers or packages.

## 3. Generated-code evaluation sandbox

Any execution of model-generated or dataset-derived code must occur in an isolated sandbox with:

- network disabled by default;
- no inherited cloud/HF/Git/GitHub tokens;
- dedicated temp working directory;
- host repository mounted read-only or not mounted;
- write access only to sandbox temp path;
- process timeout;
- CPU quota;
- memory quota;
- output-size cap;
- child-process/process-count cap;
- deterministic environment variables where applicable;
- explicit allowlist for compiler/interpreter executable.

A timeout/resource violation is a benchmark failure category, not permission to rerun with larger limits after viewing fresh results.

## 4. Windows sandbox

MVP Windows path must at minimum:
- use a dedicated temp directory;
- clear sensitive environment variables;
- disable network for code-eval process by supported host policy or mark benchmark BLOCKED if isolation cannot be provided;
- use Job Object/process-tree termination equivalent;
- enforce timeout and cleanup.

Release code benchmark cannot claim safe execution if no-network isolation is unavailable.

## 5. Dataset PII policy

Every text dataset has:
```yaml
privacy:
  detector: <name/version>
  action: report|quarantine|redact|deny
  ruleset_hash: ...
```

Release default for high-confidence sensitive PII is quarantine/deny unless documented lawful/ethical basis says otherwise.

Evidence stores counts, hashes and categories; it does not echo sensitive raw values.

## 6. Code secret scanning

Every code corpus has pinned secret scanner/ruleset. High-confidence live-credential patterns are quarantined. Scanner output raw secret values are redacted from logs/evidence.

## 7. License policy

Text source: source-level license/provenance required.

Code release corpus:
- repository revision required;
- per-file/repository license evidence retained when available;
- unknown license default deny;
- license conflicts/quarantine counts included in data manifest.

Model license:
- base model license metadata and redistribution constraints are recorded;
- pipeline never upgrades rights.

## 8. Supply chain

Freeze:
- Python dependency lock/hashes where available;
- trainer/backend versions;
- model revision/hash;
- dataset artifact hashes;
- llama.cpp commit/build;
- Ollama exact version;
- external verifier/judge versions.

Downloaded executable or archive checksum must be verified when an authoritative checksum is available.

## 9. Remote code

`trust_remote_code=true` requires:
- explicit allowlist entry;
- immutable source revision;
- reviewed code record/hash;
- sandbox/restricted execution policy;
- evidence entry.

Confirmatory/release cannot auto-enable remote code in response to load failure.

## 10. Evidence redaction

Before bundle:
- scan logs/config/environment dumps for token/key patterns;
- redact user paths when policy requests;
- store secret-presence finding without secret content;
- evidence bundle creation FAIL if unredacted known secret is detected.

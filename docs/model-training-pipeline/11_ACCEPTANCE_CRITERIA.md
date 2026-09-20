# 11 — Acceptance Criteria

MVP DONE requires machine-verifiable evidence for all required AC.

## AC-01 — One-command smoke preflight
pipeline preflight -c examples/end_to_end_small.yaml
must validate schema and pinned Qwen2.5-0.5B-Instruct revision 7ae557604adf67be50417f59c2c2f167def9a775 plus local fixture manifests.

## AC-02 — Public data adapters
At least one Wikimedia dump adapter and one concrete public code adapter exist. Reference configs are train_wikipedia_cpt.yaml and train_code_cpt.yaml. Code reference is non-release-eligible until license enrichment proves policy.

## AC-03 — Exact train/resume
Training writes >1 checkpoint; kill/restart resumes committed logical stream state and parent lineage correctly.

## AC-04 — Real two-phase reference
R0 performs both domain_cpt and reasoning_sft phases. No “minimal equivalent” substitution.

## AC-05 — Canonical HF
Reload in fresh process with exact tokenizer/template/hash identity.

## AC-06 — High-fidelity GGUF
Convert from canonical HF using pinned llama.cpp and load/infer PASS.

## AC-07 — Quantized GGUF
At least one required quantized target load/infer PASS and frozen smoke regression gate PASS.

## AC-08 — Ollama
Generated Modelfile creates namespaced ephemeral model; chat PASS; cleanup only owned artifact.

## AC-09 — Reasoning semantics
Visible mode on reasoning fixture returns non-empty rationale + answer when capability supports it; hidden/off obey normalized contract; raw transport/parser evidence retained.

## AC-10 — Cross-runtime parity
Same frozen inference fixture/parameters across HF, llama.cpp and Ollama; metric parity gate PASS.

## AC-11 — Evidence
Payload hashes, chain seal, evidence.zip and external evidence.zip.sha256 verify with no circular checksum.

## AC-12 — Freshness guard
CLI blocks fresh seeds, split IDs and fixture-set IDs before locked confirmatory access.

## AC-13 — Unsupported architecture fail-fast
Synthetic unsupported fixture fails compatibility before training.

## AC-14 — No silent rescue
Quality FAIL cannot auto-change LR/threshold/seed/data/retry.

## AC-15 — Baseline/comparator
Metrics name exact parent baseline; a matched-control fixture proves comparator machinery and budget/seed matching.

## AC-16 — Concurrency/atomicity
Second writer for same run is rejected; partial checkpoint is not resumable/canonical after injected crash.

## AC-17 — Security sandbox
Generated-code escape fixture cannot access network, host secrets or writable repo; timeout/resource quotas enforced.

## AC-18 — Spec/schema consistency
All shipped examples validate canonical schemas and documentation QA reports zero unresolved BLOCKER.

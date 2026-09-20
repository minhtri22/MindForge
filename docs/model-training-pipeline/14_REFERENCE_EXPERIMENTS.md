# 14 — Reference Experiments

## R0 — End-to-end smoke

Purpose: plumbing only, not quality claim.

Canonical model:
- Qwen/Qwen2.5-0.5B-Instruct
- exact revision 7ae557604adf67be50417f59c2c2f167def9a775
- local tracked fixture text/code/reasoning datasets
- domain_cpt + reasoning_sft both required
- save/kill/resume
- HF -> F16 GGUF -> Q4_K_M -> llama.cpp -> Ollama
- evidence bundle.

Config: examples/end_to_end_small.yaml. Model/serializer profile: profiles/qwen2.5-0.5b-instruct-r0.yaml.

## R1 — Wikipedia CPT qualification

Reference source identity: enwiki 20260301 pages-articles-multistream dump. Acquire verifies published checksum then computes local SHA-256. Run evaluates exact parent before CPT and protected capabilities after CPT.

## R2 — Code CPT qualification

Reference ingestion path: codeparrot/codeparrot-clean pinned at revision 35a59fb025bc0a102f7d96eac09d145b896d487b. It exposes repo/path/license/hash metadata and is suitable for development adapter/provenance plumbing. Release training is forbidden until exact repository-revision provenance and license policy requirements are satisfied. Secret scanning required.

## R3 — Mixed real study

Exact parent instruct/reasoning model -> CPT Wikipedia+code mixture -> frozen instruction replay -> reasoning SFT -> fresh confirmatory evaluation -> HF canonical -> high-fidelity/quantized GGUF -> llama.cpp/Ollama -> sealed evidence.

R3 must define exact parent baseline, phase deltas, protected capability suite, and matched control when making method-improvement claims.

## Expected user-facing response

Normalized API returns answer, visible rationale only when requested/supported, reasoning_kind=model_generated_rationale, transport/parser/runtime/artifact metadata. It never claims rationale is faithful hidden computation.

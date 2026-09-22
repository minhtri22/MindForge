# 12 — Implementation Plan

## M0 — Contract compiler
Typed config models, JSON Schemas, canonical resolver/hash, RunState + PhaseState, baseline/comparator types, lineage split, CLI skeleton.

Exit: all examples schema-validate; state transition negative tests PASS.

## M1 — Data/token-stream plane
Source identity, public/fixture adapters, license/privacy/secret checks, normalize/filter/dedup/contamination/split/tokenize/pack, freshness registry, TokenStreamContract, data manifest.

Exit: deterministic fixture manifest + resume cursor simulation PASS.

## M2 — Trainer/checkpoint backend
One HF/PyTorch path, CPT + SFT/reasoning SFT, phase transitions, atomic checkpoint writer, exact resume, metrics.

Exit: pinned tiny reference two-phase save/kill/resume/reload PASS.

## M3 — Governance/evaluation
Execution lock, baseline/matched-control, evaluation contracts, adjudicator, phase/final verdict history.

Exit: intentional FAIL cannot rescue; fresh resources guarded.

## M4 — Reasoning layers
Model-specific serializer, capability model, runtime parser abstraction, normalized API.

Exit: visible/hidden/off semantics tests PASS.

## M5 — llama.cpp
Pinned build/converter capability evidence, high-fidelity GGUF, shard-aware quantization, frozen inference runtime fixtures.

## M6 — Ollama
Generated Modelfile, safe ephemeral namespace, capability/think mapping, cleanup, parity.

## M7 — Security/evidence
Sandbox, PII/secret/license gates, run locks, evidence seal, bundle ordering, external ZIP checksum.

## M8 — Full E2E + hardening
AC-01..AC-18, Windows bootstrap, failure injection, reproducibility replay, docs.

## Dependency rule

The original single serial rule is superseded by `23_INFRASTRUCTURE_SCIENCE_SEPARATION.md`.

Core semantic/model dependencies remain ordered where one artifact truly depends on another. Infrastructure and product-hardening work use dependency edges rather than a global stop-the-world gate.

In particular:
- Ollama runtime/harness qualification may block Ollama-dependent execution;
- it does not block unrelated scientific design, analysis or implementation;
- qualified infrastructure is reusable by exact binding rather than repeated qualification;
- M7/M8 release/product requirements remain required for release eligibility.

Software-development Git lineage remains separate from training-run lineage.

# 00 — Product Requirements

## PR-001 — Job to be done

Exact base artifact + frozen datasets/token stream + phase training contracts + baseline/comparator contract + evaluation/runtime contracts phải tạo validated canonical checkpoint, GGUF + llama.cpp + Ollama và auditable evidence.

## PR-002 — Required workflows

1. Wikipedia/public text CPT với immutable source identity.
2. Public code CPT với license, privacy/secret, dedup và contamination controls.
3. Instruction/reasoning SFT qua model-specific serializer.
4. Exact checkpoint/resume có sampler/token-stream state.
5. Evaluation với exact parent baseline và matched control khi claim yêu cầu.
6. GGUF export/quantization.
7. Real llama.cpp/Ollama load + inference.
8. Evidence bundle + external ZIP checksum.
9. Normalized reasoning/answer API.

## PR-003 — Non-functional

Windows + Linux orchestration; Unicode/space-safe paths; machine + human logs; content-addressed idempotency; no secrets in evidence; one writer per run; atomic writes; host mutation/install requires explicit action.

## PR-004 — State

Canonical run/phase state machines chỉ được định nghĩa trong 16_CANONICAL_CONFIG_STATE_MACHINE.md và schemas/run_manifest.schema.json.

## PR-005 — Success

Release artifact chỉ PASS nếu required matrix PASS cho HF reload, quality/protected capability metrics so với named baseline, GGUF, llama.cpp, Ollama, reasoning contract nếu required, runtime parity, security/license/privacy, reproducibility QA và evidence seal.

Smoke/development không được promote thành release chỉ vì plumbing chạy.

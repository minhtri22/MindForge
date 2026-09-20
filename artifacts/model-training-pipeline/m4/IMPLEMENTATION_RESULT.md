# M4 Implementation Result — Reasoning Layers Qualification

## Verdict

```text
M4_STATUS: PASS

M0_REGRESSION: PASS
M1_REGRESSION: PASS
M2_REAL_MODEL_REGRESSION: PASS
M3_GOVERNANCE_REGRESSION: PASS
M4_REASONING: PASS

MODEL_WEIGHTS_LOADED_BY_M4: NO
TRAINING_STARTED_BY_M4: NO
PUBLIC_BULK_TRAINING: NO

VISIBLE_SEMANTICS: PASS
HIDDEN_SEMANTICS: PASS
OFF_SEMANTICS: PASS_AS_EXPLICIT_UNSUPPORTED_FOR_R0
MALFORMED_TAG_REJECTION: 7/7
M4_GATES: 13/13 PASS

M5_AUTHORIZED_BY_M4: YES
M5_EXECUTED: NO
```

## Qualified source identity

- Repository: `minhtri22/MindForge`
- Branch: `docs/evidence-model-training-pipeline`
- M3 evidence parent: `c2b0f4e691adf0e46c6ebf76c86eca292d584a9d`
- Initial M4 candidate: `f328587bafcb5f41ffb6f06cc92e91bc6bf5ea98`
- Dependency repair: `85fa1d6ad45941c5a5c77ff426f1ecc943105943`
- Final qualified M4 implementation: `a6066acc7da6123d156744ae0555a4c682bc313d`

The first M4 candidate reached all M4 unit/adversarial tests but exact tokenizer qualification failed before reasoning serialization because the tokenizer-only environment omitted Jinja2, which the pinned Qwen chat template requires. This was a technical dependency omission, not a reasoning-semantic FAIL.

The repair added pinned `jinja2==3.1.6`. A subsequent M4-only run passed. A final code change then bound exact reasoning dependency versions into the M4 qualification gates so that M0→M4 were all re-run on one exact SHA.

## Implemented reasoning chain

```text
semantic reasoning fixture
        ↓
exact pinned Qwen tokenizer/chat template
        ↓
qwen_chat_tagged_reasoning@1 serializer
        ↓
assistant-only loss mask
        ↓
ReasoningCapability
        ↓
visible / hidden / off request decision
        ↓
strict tagged parser
        ↓
native-runtime-field abstraction
        ↓
normalized ReasoningResponse schema
        ↓
M4 adjudication
```

## Model-specific serializer

R0 remains bound to:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision:
7ae557604adf67be50417f59c2c2f167def9a775

training serializer:
qwen_chat_tagged_reasoning@1

loss mask:
assistant_only
```

M4 downloads only the pinned tokenizer/chat-template assets. It does not load model weights.

The serializer rejects reserved-marker injection in user messages, rationale, or answer fields. It verifies that the assistant serialization is prefixed by the prompt serialization, masks every prompt token with `-100`, keeps assistant tokens supervised, and refuses a zero-supervision sample.

M2 `reasoning_sft` was refactored to use this same serializer, rather than a separate hard-coded tag path. The M2 real-model regression on the final M4 SHA passed, proving the shared serializer did not break forward/backward, checkpoint, interruption/resume, or canonical save/reload.

## Capability semantics

The R0 pinned Qwen profile compiles to:

```text
supported: true
training_format: qwen_chat_tagged_reasoning@1
transport_options:
  - tagged_text
visibility_modes:
  - visible
  - hidden
supports_hide: true
supports_disable: false

native_runtime_support:
  hf: tagged_text_parser
  llama_cpp: not_qualified_m5
  ollama: not_qualified_m6
```

The important decision is that R0 Qwen is **not claimed to support true reasoning disable**.

Therefore:

```text
visible → supported
hidden  → supported
off     → explicit UNSUPPORTED
          degraded_to = null
```

There is no silent mapping `off → hidden`.

A synthetic capability that explicitly declares `supports_disable=true` is used only to test normalized off-mode semantics. It is not evidence that R0 Qwen supports disable.

## Visible semantics

For valid tagged output:

```text
<think>model-generated rationale</think>
<answer>final answer</answer>
```

visible mode returns:

```json
{
  "reasoning": "model-generated rationale",
  "reasoning_present": true,
  "reasoning_kind": "model_generated_rationale",
  "reasoning_mode": "visible",
  "transport": "tagged_text",
  "parser_status": "ok"
}
```

Both reasoning fixtures passed.

## Hidden semantics

The parser still validates the rationale but normalized output suppresses its text:

```json
{
  "reasoning": null,
  "reasoning_present": true,
  "reasoning_mode": "hidden",
  "transport": "tagged_text",
  "parser_status": "ok"
}
```

Both reasoning fixtures passed.

## Off semantics

For the actual R0 capability:

```text
request: off
supports_disable: false

result:
UNSUPPORTED_REASONING_MODE
degraded_to: null
```

This is considered PASS because the contract explicitly requires unsupported failure rather than pretending disable occurred.

For a synthetic test-only capability that truly declares disable support, an answer-only output is normalized with:

```text
reasoning = null
reasoning_present = false
reasoning_mode = off
```

## Strict parser failure coverage

Seven malformed forms are explicitly rejected:

1. missing reasoning close tag;
2. nested reasoning tag;
3. duplicate reasoning block;
4. duplicate answer block;
5. answer/reasoning order reversal;
6. non-whitespace leading content;
7. empty answer block.

Mixed `tagged_text` + `native_runtime_field` input is also rejected as ambiguous.

The parser does not attempt recovery that could reinterpret malformed evidence into a valid response.

## Native runtime abstraction

M4 also implements a normalized parser for runtimes that provide a native reasoning field.

This is an abstraction test only; M4 does not claim llama.cpp or Ollama support yet.

Synthetic native-field tests prove:

```text
visible → expose non-empty rationale
hidden  → suppress rationale, reasoning_present=true
off     → requires supports_disable=true and no emitted rationale
```

Actual llama.cpp and Ollama capability resolution remains M5/M6 work.

## Pinned reasoning environment

Final M4 qualification freezes:

```text
transformers==5.17.0
huggingface-hub==1.32.0
tokenizers==0.23.2
jinja2==3.1.6
```

The exact dependency versions are checked by the executable M4 gate, not only by requirements text.

## Authoritative workflows

All authoritative workflows executed on exact SHA:

```text
a6066acc7da6123d156744ae0555a4c682bc313d
```

### M0
- run: `35521742088`
- conclusion: `success`

### M1
- run: `35521742085`
- conclusion: `success`

### M2 real-model regression
- run: `35521742065`
- conclusion: `success`
- M0 tests: 15 PASS
- M1 tests: 15 PASS
- M2 checkpoint tests: 4 PASS
- pinned-Qwen two-phase interruption/resume: PASS
- exact resume phases: 2
- public bulk download: false

### M3
- run: `35521742099`
- conclusion: `success`

### M4
- run: `35521742077`
- conclusion: `success`

M4 workflow evidence:

```text
M0 regression:             15 passed
M1 regression:             15 passed
M3 governance regression:  10 passed
M4 reasoning tests:        15 passed

M4 qualification:
status:                    PASS
gates:                     13 / 13
serialized_samples:        2
visible_pass:              2
hidden_pass:               2
malformed_rejections:      7
model_weights_loaded:      false
training_started:          false
```

## Identity hashes

```text
capability_hash:
748a4c391291e48c8572b12020b33457771052a0079aa5ae33f12bcc09f3aa8c

tokenizer_snapshot_hash:
cddbecc432af46e4fcddc7611d940b7d4d41667810bbe0324e0885238c8e1e6d

M4 qualification_hash:
068e19b95dd1fd0336600b0e6777abc8921af625b73c6ae04df7ae1d405cfce7
```

## Scientific interpretation

M4 establishes that the pipeline now has one model-specific reasoning serializer, a strict assistant-only mask contract, explicit capability semantics, strict tagged parsing, normalized visible/hidden/off behavior, and no silent transport/mode degradation.

M4 does **not** establish:

- that generated rationale is faithful hidden computation;
- that reasoning SFT improves reasoning quality;
- that R0 Qwen can truly disable reasoning;
- llama.cpp reasoning/parser compatibility;
- Ollama thinking-field compatibility;
- cross-runtime parity;
- production-scale corpus training quality.

## Next scientific step

M4 authorizes **M5 — llama.cpp**.

M5 should remain controlled and first prove:

```text
pin llama.cpp commit
      ↓
converter capability evidence
      ↓
HF canonical → high-fidelity GGUF
      ↓
GGUF hash / shard identity
      ↓
real llama.cpp load
      ↓
deterministic inference fixture
      ↓
reasoning parser capability mapping
      ↓
HF vs llama.cpp task/format parity
      ↓
only then optional q8/q4 quantization
      ↓
M5 qualification
```

Bulk Wikipedia/CodeParrot training is still not justified solely by M4 PASS.

# M5.1 Result — Canonical Tokenizer Export Fidelity Decomposition

## Verdict

```text
M5_1_DIAGNOSTIC_STATUS: PASS
MECHANISM: M2_CANONICAL_TOKENIZER_EXPORT_FIDELITY_DEFECT

ARM_A_CURRENT_M2_CANONICAL_TOKENIZER: FAIL
ARM_B_PINNED_QWEN_RAW_TOKENIZER:       PASS

M5_STATUS:                    OPEN
QUANTIZATION_AUTHORIZED:      NO
M6_AUTHORIZED:                NO
BULK_TRAINING_AUTHORIZED:     NO
M2_REPAIR_AUTHORIZED:         YES — tokenizer export contract only
```

This closes only the preregistered M5.1 mechanism decomposition. It does **not**
close M5 and does not authorize Q8/Q4.

## Frozen parent failure

```text
parent implementation SHA:
8c8eba03d71ab4c4463b6811b2cc475465553304

parent M5 workflow:
35565868782

parent failure stage:
F16_HF_TO_GGUF_CONVERSION
```

The parent failure was frozen before M5.1. Production files responsible for M2
canonical export and M5 conversion were Git-blob locked and verified unchanged
before the A/B diagnostic executed.

## Qualified M5.1 source

```text
diagnostic implementation SHA:
60e7b435a9578531b2652d7382dc91865b64420a

workflow:
Model Pipeline M5.1 Tokenizer Decomposition

run:
35573429361

job:
106249820506

conclusion:
success
```

The immediately preceding run `35573096511` on SHA
`212f003aba540adcb4774e2e97cec09b6bc1a1ec` was technical-invalid before
scientific execution because the standalone diagnostic script could not import
the repository package. The workflow-only repair changed invocation to
`python -m tools.m5_1_decomposition` and enabled `pipefail`; preregistration,
arm construction, converter, thresholds, and adjudication were unchanged.

## Frozen controls

Both arms used exactly:

```text
config:
docs/model-training-pipeline/examples/end_to_end_small.yaml

model:
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775

llama.cpp:
ce8caa6e60a03093351d6016a818720e0d46f0fb

converter Git blob:
e09616b190cf124e818d8a740468d4e84086015c

outtype:
f16
```

The converter environment was the exact environment declared by the pinned
llama.cpp source and passed its import preflight.

## Controlled-variable proof

```text
only independent variable:
tokenizer_source

non_tokenizer_manifest_equal:
true

non_tokenizer_manifest_hash:
9286c6fecfbd084f653c52e59050159d983aff96e735d406685794cadf1795a7

converter_command_shape_equal:
true

quantization_executed:
false
```

Arm B was created by cloning Arm A and replacing **only** tokenizer assets with
byte-for-byte files from the exact pinned Qwen source snapshot. No
`save_pretrained()` call was used to generate Arm B tokenizer files.

## M2 canonical identity used by both arms

```text
run_id:
e2e-small-cd9bfabe9280

canonical_directory_hash:
6edb0d843984e611580f895131c12ba5d0f47dfee0ab2050e45de1e3bc6b5684

M2 adjudication hash:
99217423fc9f2877f703a46fcf7bff7bbaac9381c3ea514e48cb8672c05e6203
```

## Arm A — current M2 canonical tokenizer

Tokenizer asset manifest:

```text
chat_template.jinja
  size   2507
  sha256 cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f

tokenizer.json
  size   11421989
  sha256 3258b7421a917d3a0549ee7e2541cce708949ae478777aea1dfff10c464e9219

tokenizer_config.json
  size   692
  sha256 1cc816812993bff176eb4f7495433b736f06fba9b6e7b05cac7b4a1780650c95

manifest hash:
3d79ee3bedf5394d6858a1dc50d1b5916f63b6e751c3697041f8187923af4992
```

Pre-conversion inspection:

```text
load_ok: false
error_type: AttributeError
error: 'list' object has no attribute 'keys'
```

F16 conversion:

```text
return_code: 1
pass: false
output_exists: false
```

The failure reproduced the frozen parent mechanism: the converter first found
no `tokenizer.model`, then its GPT2/Qwen2 fallback failed while loading the
canonical tokenizer because the resulting special-token structure was
incompatible with the converter environment's Transformers tokenizer loader.

## Arm B — exact pinned Qwen tokenizer assets

Source tokenizer assets copied byte-for-byte from revision
`7ae557604adf67be50417f59c2c2f167def9a775`:

```text
merges.txt
  size   1671839
  sha256 599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3

tokenizer.json
  size   7031645
  sha256 c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539

tokenizer_config.json
  size   7305
  sha256 5b5d4f65d0acd3b2d56a35b56d374a36cbc1c8fa5cf3b3febbbfabf22f359583

vocab.json
  size   2776833
  sha256 ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910

manifest hash:
1567e178abe4f245846c6bd59e7e6f3b7e842fde92200ddfc74851559a402023
```

Pre-conversion inspection:

```text
load_ok: true
tokenizer_class: Qwen2TokenizerFast
tokenizer_vocab_type: dict
tokenizer_vocab_size: 151665
vocab_max_id: 151664

tokenizer_vocab_hash:
54a4e00eec5a8c5f40d137afdde38da75f4c46ffa802b509cb5fb2157b5a5b0d

chat_template_hash:
2e2d2512cfe46af53dc1eed45368ecaab26ac4461c480e6b69fe571cf0ceaa75

special_tokens_map_hash:
94f02d4e8b7a6569bef78a7ff2c3b40744a0fd54e603a9c5a5bdba4d05256a10

encode/decode roundtrip:
true

encode/decode token_ids_hash:
e1f2df5444bc84f46588ff8fd5a2385854b3a4f4fa3cc02647394cd12cda9fa6
```

F16 conversion:

```text
return_code: 0
pass: true
output_exists: true
output_size: 994156416

output_sha256:
34ad95997c9ed9d188e4163652c9175ec52a5ba12057d75dc5d9192de263a3d8
```

## Preregistered adjudication

Observed:

```text
A FAIL + B PASS
```

Therefore, per the preregistered matrix:

```text
MECHANISM:
M2_CANONICAL_TOKENIZER_EXPORT_FIDELITY_DEFECT

NEXT ACTION:
REPAIR_M2_CANONICAL_TOKENIZER_EXPORT_CONTRACT_THEN_RERUN_M2_TO_M5
```

This result rules out the frozen hypothesis that the pinned llama.cpp converter
is inherently unable to convert the exact pinned Qwen tokenizer/model under the
same F16 conditions. The source tokenizer succeeds with the same model
weights/config and converter.

## Test / execution evidence

```text
M0 regression:   15 passed
M1 regression:   15 passed
M2 unit:          4 passed
M3 regression:   10 passed
M4 regression:   15 passed
M5.1 tests:      18 passed
```

Converter import preflight also passed.

## Evidence identities

```text
preregistration_hash:
25a277477659f9466741b619b18d99e0ffb1c192377f3f78ff290535633261de

converter_sha256:
e9a1da876330bbce9687541ab31736542a01b4ac43c6686126514a50f122fb7f

M5.1 result_hash:
890015fe543f70b508d885de0d42bde0996d0a9f1b9631f576eba37f09efd986
```

## Scientific boundary after M5.1

M5.1 authorizes one bounded repair target only:

```text
M2 canonical tokenizer export fidelity
```

It does **not** authorize:

```text
Q8/Q4
M6
new llama.cpp commit
converter patching
bulk Wikipedia/CodeParrot training
threshold/parity relaxation
```

After the M2 tokenizer export repair, the required chain is still:

```text
M0→M4 regressions
        ↓
M2 canonical artifact regenerated
        ↓
F16 conversion
        ↓
real llama-cli load
        ↓
HF ↔ llama.cpp parity
        ↓
F16 PASS
        ↓
only then quantization qualification
```

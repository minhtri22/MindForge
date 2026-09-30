# MKS-1 Core Promotion Receipt

Status: SELECTIVE PROMOTION CANDIDATE

Canonical base:

```text
main
924654c81c08832c23ff192fdcbf63d3f2680d3a
```

Validated source:

```text
refactor/mks-1-model-kernel-separation
5280243a54ba8977b0d02a5b4ed85c657e03193f
```

MKS-1 scientific/architectural status:

```text
PASS / CLOSED
FULL LOCAL EVIDENCE VALIDATED
```

Promotion rule: copy only exact MKS-1 model/runtime contract code, focused tests, and closure/ADR/architecture documents. Do not merge the source branch wholesale because that branch also contains unrelated PPF research material.

Compatibility check before promotion:

- MKS starting reference: `1b0392a2550ecee0e65941e0590f21507797610d`.
- Current main differs from that starting reference only by the OIR workflow path; no `mindforge/` runtime/training source drift was observed.
- Promoted source blobs are the exact blobs covered by the closed MKS-1 validation.
- Transformer math remains unchanged.
- Checkpoint format remains version 1.
- Evaluation and generation semantics remain unchanged.
- No PPF/plugin semantics are introduced into the Model Contract.
- No physical package move is performed.

Promoted runtime contract:

```text
Kernel/runtime consumers
        ↓
TokenModel protocol
        ↓
current TransformerLM

research/tooling construction
        ↓
create_model(ModelConfig)
```

Files promoted:

- `mindforge/__init__.py`
- `mindforge/checkpoint.py`
- `mindforge/config.py`
- `mindforge/evaluate.py`
- `mindforge/generate.py`
- `mindforge/model.py`
- `mindforge/model_contract.py`
- `mindforge/train.py`
- `tests/test_mks_model_kernel.py`
- MKS-1 ADR, invariants, QA, validation, UAT, technical-debt and closure documents.

Explicitly excluded from promotion:

- PPF fixtures;
- PPF protocols;
- PPF benchmark data;
- source-branch README changes carrying PPF state;
- any plugin framework;
- any new model research mechanism.

Promotion semantics:

```text
MKS-1 capability → eligible for canonical core
PPF               → unchanged / separate research
Model science      → unchanged
```

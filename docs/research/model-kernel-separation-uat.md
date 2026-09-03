# Model / Kernel Separation MKS-1 — UAT Report

Status: **PASS WITH ENVIRONMENT LIMITATION — DOES NOT CLOSE MKS-G5**

Branch: `refactor/mks-1-model-kernel-separation`

Implementation head tested/reviewed: `d17a5ed8eb5083049411cfafa382204edaafa79b`

Starting reference: `1b0392a2550ecee0e65941e0590f21507797610d`

## Purpose

This UAT validates the MKS-1 change from the perspective of current MindForge consumers rather than only unit-level implementation details. It tests whether existing current behaviors still work through the new model/runtime boundary without changing Transformer mathematics, checkpoint format, evaluation semantics, generation semantics, or legacy run-config shape.

The UAT does **not** rerun the six canonical Phase-2 training runs.

## Environment limitation

The execution sandbox cannot resolve `github.com`, so a normal full repository clone and replay of all historical artifacts is unavailable in this environment.

The committed changed subset was reconstructed from the exact GitHub branch sources and executed locally. Source-level checks were performed against the committed branch through the GitHub connector.

Therefore this report distinguishes:

- executable UAT of the changed MKS path: performed;
- full historical repository regression and Phase-2 artifact replay: not performed here.

The latter remains required for MKS-G5 closure in the normal local checkout.

## Acceptance scenarios

| ID | Scenario | Acceptance criterion | Result |
|---|---|---|---|
| UAT-01 | Default model construction | `create_model(ModelConfig())` produces exactly `10,339,200` parameters | PASS |
| UAT-02 | Runtime contract conformance | current `TransformerLM` structurally satisfies `TokenModel`; context/vocabulary properties resolve correctly | PASS |
| UAT-03 | Forward compatibility | direct `TransformerLM` and `create_model()` with identical state produce bit-identical logits | PASS |
| UAT-04 | Existing validation semantics | empty context, over-limit context, out-of-range token ID, and wrong tensor rank still raise `ValueError` | PASS |
| UAT-05 | Deterministic one-step training | direct/factory paths end with identical parameter tensors and optimizer parameter groups | PASS |
| UAT-06 | Legacy config compatibility | `KernelConfig.save/load` preserves exact legacy type and `{data, model, training}` JSON shape | PASS |
| UAT-07 | Checkpoint round-trip | format v1 payload saves, reads, reconstructs through `create_model`, and restores exact model state/optimizer groups | PASS |
| UAT-08 | Evaluation consumer path | evaluator consumes `TokenModel.context_limit`, returns finite metrics, and restores prior train/eval mode | PASS |
| UAT-09 | Generation consumer path | greedy generation through `TokenModel` is deterministic for fixed state/input and respects `context_limit` truncation | PASS |
| UAT-10 | Runtime source boundary | `evaluate.py` and `generate.py` no longer import `TransformerLM` or inspect Transformer architecture internals | PASS (source audit) |
| UAT-11 | PPF/plugin non-interference | branch diff contains no PPF semantic/evidence changes and no plugin framework | PASS (source/diff audit) |
| UAT-12 | Full historical pytest + Phase-2 summarize/check | complete checkout must pass without rerunning canonical Phase-2 training | NOT EXECUTED IN SANDBOX |

## Executed sandbox result

The focused compatibility/UAT harness executed:

```text
9 passed
compileall PASS
```

The executable cases cover the changed model contract, model factory, config compatibility, checkpoint reconstruction, evaluator boundary, generator boundary, forward parity, validation behavior, and deterministic one-step training parity.

An initial pytest collection failure occurred because the reconstructed subset was not installed as a package; rerunning with the workspace on `PYTHONPATH` resolved the harness/environment issue. This was not a product-code failure.

## Checkpoint acceptance detail

The checkpoint acceptance scenario verified:

- `format_version = 1` remains unchanged;
- serialized `model_config` remains a `ModelConfig` mapping;
- reconstruction uses `create_model(saved_model_config)`;
- state-dict keys/tensors round-trip exactly;
- optimizer parameter groups round-trip;
- tokenizer/dataset fingerprint match validation remains present.

No new checkpoint schema or migration was introduced.

## Evaluation acceptance detail

The current evaluator now depends on:

```text
TokenModel
  context_limit
  training
  eval()
  train(mode)
  token forward -> logits
```

The UAT confirms the current `TransformerLM` path returns finite CE/BPB-style metrics and returns the model to its prior training state.

No evaluator threshold or BPB formula was changed by MKS-1.

## Generation acceptance detail

Generation now truncates prompt/history using:

```text
model.context_limit
```

instead of:

```text
model.config.max_context
```

For the current Transformer these resolve to the same value. Greedy generation in the UAT is deterministic across repeated runs with identical model state/input/options.

## UAT decision

```text
MKS-1 focused UAT: PASS
FULL FROZEN-EVIDENCE UAT: PENDING LOCAL CHECKOUT
MKS-G5: REMAINS REVISE
CANONICAL PHASE-2 RERUN: NOT PERFORMED
```

No behavioral mismatch was found in the executable MKS path. The remaining blocker is evidence completeness plus the contract-quality findings recorded separately in the QA report.

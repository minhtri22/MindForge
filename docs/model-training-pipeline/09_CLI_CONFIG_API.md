# 09 — CLI, Config & API

## 1. CLI surface

```text
pipeline init <workspace>
pipeline doctor
pipeline model inspect <model-spec>
pipeline data prepare -c <config>
pipeline data audit <run-id>
pipeline preflight -c <config>
pipeline lock <run-id>
pipeline train <run-id>
pipeline resume <run-id> --checkpoint <id>
pipeline eval <run-id>
pipeline adjudicate <run-id>
pipeline export <run-id>
pipeline verify-runtime <run-id> --runtime llama.cpp
pipeline verify-runtime <run-id> --runtime ollama
pipeline chat --model run:<id> --reasoning on
pipeline bundle <run-id>
pipeline status <run-id>
```

## 2. Config inheritance

Cho phép YAML includes/profiles nhưng sau resolve phải ghi một `frozen/run_config.yaml` fully expanded. Hash tính trên expanded canonical form.

## 3. Example top-level config

```yaml
experiment:
  id: wiki-code-reasoning-v1
  mode: confirmatory

model:
  source: huggingface
  id: <supported-base-model>
  revision: <commit-or-tag-resolved-to-hash>

phases:
  - id: cpt
    type: cpt
    data: [wikipedia, code]
  - id: reasoning_sft
    type: reasoning_sft
    data: [reasoning]

evaluation:
  fixture_set: eval/v1
  thresholds_file: thresholds/v1.yaml

export:
  hf: true
  gguf:
    base: f16
    quantize: [q8_0, q4_k_m]
  llama_cpp: true
  ollama: true
```

## 4. Programmatic API

```python
from pipeline import Pipeline

p = Pipeline(workspace="...")
run = p.prepare("experiment.yaml")
p.preflight(run)
p.lock(run)
p.train(run)
p.evaluate(run)
p.adjudicate(run)
p.export(run)
p.verify_runtime(run, "llama.cpp")
p.verify_runtime(run, "ollama")
```

Mọi method trả typed result, không chỉ print.

## 5. Error model

Mỗi failure có:

```json
{
  "code": "GGUF_LOAD_FAIL",
  "stage": "runtime_verification",
  "message": "...",
  "recoverability": "infra_retry|new_run|required_fix",
  "evidence_refs": []
}
```

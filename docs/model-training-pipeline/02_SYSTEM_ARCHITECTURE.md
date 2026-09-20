# 02 — System Architecture

## 1. Kiến trúc module

```text
pipeline/
├── cli/
├── config/
├── registry/
│   ├── models.py
│   ├── datasets.py
│   └── runtimes.py
├── data/
│   ├── acquire.py
│   ├── license.py
│   ├── normalize.py
│   ├── dedup.py
│   ├── contamination.py
│   ├── split.py
│   └── tokenize.py
├── training/
│   ├── backends/
│   ├── checkpoint.py
│   ├── resume.py
│   └── callbacks.py
├── reasoning/
│   ├── format.py
│   ├── parser.py
│   └── validators.py
├── eval/
│   ├── hf.py
│   ├── tasks.py
│   ├── parity.py
│   └── adjudicator.py
├── export/
│   ├── hf.py
│   ├── gguf.py
│   ├── quantize.py
│   ├── modelfile.py
│   └── ollama.py
├── provenance/
│   ├── hashing.py
│   ├── environment.py
│   └── lineage.py
├── runtime/
│   ├── llama_cpp.py
│   └── ollama.py
└── evidence/
    ├── report.py
    └── bundle.py
```

## 2. Adapter interfaces

### ModelAdapter

```python
class ModelAdapter(Protocol):
    def validate_compatibility(self) -> CompatibilityReport: ...
    def load_for_train(self, cfg): ...
    def save_hf(self, out_dir): ...
    def chat_template(self) -> str | None: ...
    def reasoning_capability(self) -> str: ...
```

### DatasetAdapter

```python
class DatasetAdapter(Protocol):
    def resolve_snapshot(self, spec): ...
    def license_manifest(self): ...
    def stream_documents(self): ...
    def fingerprint(self): ...
```

### TrainingBackend

```python
class TrainingBackend(Protocol):
    def preflight(self, cfg): ...
    def train(self, run_ctx): ...
    def resume(self, checkpoint, run_ctx): ...
```

### RuntimeAdapter

```python
class RuntimeAdapter(Protocol):
    def install_or_locate(self): ...
    def load(self, model_artifact): ...
    def infer(self, messages, *, reasoning): ...
    def unload(self): ...
```

## 3. Storage

MVP dùng filesystem + JSON/JSONL/YAML. Không yêu cầu database. Mọi state quan trọng phải có thể audit chỉ từ `runs/<run_id>`.

## 4. Dependency pinning

Tạo:

```text
locks/
├── python.lock
├── trainer.lock.json
├── llama_cpp.lock.json
└── ollama.lock.json
```

Không gọi trực tiếp `main/latest` trong confirmatory run. Resolve commit/version trước rồi freeze.

## 5. Compatibility matrix

Trước training, pipeline phải tạo matrix:

| Check | Required |
|---|---|
| HF model loads | PASS |
| Tokenizer round-trip | PASS |
| Chat template valid | PASS for SFT/chat |
| llama.cpp architecture supported | PASS |
| GGUF converter recognizes architecture | PASS |
| Ollama import path supported | PASS or approved GGUF path |
| reasoning parser/template available | PASS for reasoning target |

Không PASS matrix -> không cho train production run.

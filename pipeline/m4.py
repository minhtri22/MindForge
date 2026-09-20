"""M4 fixture-scale reasoning-layer qualification."""

from __future__ import annotations

import importlib.metadata
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from .canonical import sha256_file, sha256_object
from .errors import ReasoningParseError, UnsupportedReasoningMode
from .io import atomic_write_json
from .loader import load_experiment_config, load_model_profile
from .reasoning import (
    ReasoningCapability,
    capability_from_profile,
    normalize_native_output,
    normalize_tagged_output,
    reject_mixed_transport,
    request_decision,
    serialize_reasoning_sample,
)


@dataclass(frozen=True)
class M4Result:
    status: str
    run_dir: Path
    serialized_samples: int
    visible_pass: int
    hidden_pass: int
    malformed_rejections: int
    gates_passed: int
    gates_total: int
    capability_hash: str
    tokenizer_snapshot_hash: str
    qualification_hash: str
    model_weights_loaded: bool
    training_started: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "run_dir": str(self.run_dir),
            "serialized_samples": self.serialized_samples,
            "visible_pass": self.visible_pass,
            "hidden_pass": self.hidden_pass,
            "malformed_rejections": self.malformed_rejections,
            "gates_passed": self.gates_passed,
            "gates_total": self.gates_total,
            "capability_hash": self.capability_hash,
            "tokenizer_snapshot_hash": self.tokenizer_snapshot_hash,
            "qualification_hash": self.qualification_hash,
            "model_weights_loaded": self.model_weights_loaded,
            "training_started": self.training_started,
        }


def run_m4_qualification(
    config_path: str | Path,
    repo_root: str | Path = ".",
    runs_root: str | Path = "runs",
) -> M4Result:
    repo_root = Path(repo_root).resolve()
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    config = load_experiment_config(config_path, repo_root)
    profile = load_model_profile(config, repo_root)
    m3_evidence_path = repo_root / "artifacts/model-training-pipeline/m3/M3_QUALIFICATION_EVIDENCE.json"
    m3_evidence = _read_object(m3_evidence_path)
    if m3_evidence.get("verdict") != "PASS":
        raise ReasoningParseError("M3 qualification prerequisite is not PASS")

    runs_root = Path(runs_root)
    if not runs_root.is_absolute():
        runs_root = repo_root / runs_root
    run_dir = runs_root / f"m4-{config.experiment_id}"
    if run_dir.exists():
        import shutil
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)

    snapshot = Path(
        snapshot_download(
            repo_id=config.model.id,
            revision=config.model.revision,
            cache_dir=str(runs_root / ".hf-tokenizer-cache"),
            allow_patterns=[
                "tokenizer*",
                "vocab*",
                "merges*",
                "*.model",
                "*.jinja",
                "config.json",
                "generation_config.json",
            ],
        )
    ).resolve()
    tokenizer = AutoTokenizer.from_pretrained(
        snapshot,
        local_files_only=True,
        trust_remote_code=False,
    )
    files = [
        {
            "path": path.relative_to(snapshot).as_posix(),
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in sorted(snapshot.rglob("*"))
        if path.is_file()
    ]
    tokenizer_snapshot_hash = sha256_object(files)
    capability = capability_from_profile(profile)
    environment_versions = {
        "transformers": importlib.metadata.version("transformers"),
        "huggingface-hub": importlib.metadata.version("huggingface-hub"),
        "tokenizers": importlib.metadata.version("tokenizers"),
        "jinja2": importlib.metadata.version("jinja2"),
    }

    records = _read_jsonl(repo_root / "tests/fixtures/data/reasoning_mini.jsonl")
    serialization = []
    visible = []
    hidden = []
    artifact = f"hf:{config.model.id}@{config.model.revision}"
    tags = profile["reasoning"]["tagged_serializer"]
    for record in records:
        serialized = serialize_reasoning_sample(tokenizer, profile, record, max_length=256)
        serialization.append({"id": record["id"], **serialized.to_dict()})
        raw = (
            f"{tags['start_tag']}{record['reasoning']}{tags['end_tag']}\n"
            f"{tags['answer_start_tag']}{record['answer']}{tags['answer_end_tag']}"
        )
        visible.append(
            normalize_tagged_output(
                raw_text=raw,
                mode="visible",
                capability=capability,
                profile=profile,
                runtime="hf-fixture-parser",
                model_artifact=artifact,
                repo_root=repo_root,
            )
        )
        hidden.append(
            normalize_tagged_output(
                raw_text=raw,
                mode="hidden",
                capability=capability,
                profile=profile,
                runtime="hf-fixture-parser",
                model_artifact=artifact,
                repo_root=repo_root,
            )
        )

    off_decision = request_decision(capability, "off")
    off_unsupported = False
    try:
        normalize_tagged_output(
            raw_text="<answer>42</answer>",
            mode="off",
            capability=capability,
            profile=profile,
            runtime="hf-fixture-parser",
            model_artifact=artifact,
            repo_root=repo_root,
        )
    except UnsupportedReasoningMode:
        off_unsupported = True

    # Synthetic capability proves the normalized API semantics for a runtime that
    # really can disable reasoning, without claiming R0 Qwen has that capability.
    disable_capability = ReasoningCapability(
        supported=True,
        training_format="synthetic-test-only",
        transport_options=("tagged_text", "native_runtime_field"),
        visibility_modes=("visible", "hidden", "off"),
        effort_levels=(),
        supports_disable=True,
        supports_hide=True,
        native_runtime_support={"fixture": "synthetic"},
    )
    off_supported_response = normalize_tagged_output(
        raw_text="<answer>42</answer>",
        mode="off",
        capability=disable_capability,
        profile=profile,
        runtime="synthetic-disable-fixture",
        model_artifact="synthetic:test-only",
        repo_root=repo_root,
    )
    native_visible = normalize_native_output(
        answer="42",
        native_reasoning="Add the two integers.",
        mode="visible",
        capability=disable_capability,
        runtime="synthetic-native-fixture",
        model_artifact="synthetic:test-only",
        repo_root=repo_root,
    )
    native_hidden = normalize_native_output(
        answer="42",
        native_reasoning="Add the two integers.",
        mode="hidden",
        capability=disable_capability,
        runtime="synthetic-native-fixture",
        model_artifact="synthetic:test-only",
        repo_root=repo_root,
    )
    native_off = normalize_native_output(
        answer="42",
        native_reasoning=None,
        mode="off",
        capability=disable_capability,
        runtime="synthetic-native-fixture",
        model_artifact="synthetic:test-only",
        repo_root=repo_root,
    )

    malformed = [
        "<think>reason<answer>42</answer>",
        "<think>outer <think>inner</think></think><answer>42</answer>",
        "<think>a</think><think>b</think><answer>42</answer>",
        "<think>a</think><answer>42</answer><answer>43</answer>",
        "<answer>42</answer><think>late</think>",
        "prefix<think>a</think><answer>42</answer>",
        "<think>a</think><answer></answer>",
    ]
    rejected = []
    for raw in malformed:
        try:
            normalize_tagged_output(
                raw_text=raw,
                mode="visible",
                capability=capability,
                profile=profile,
                runtime="hf-fixture-parser",
                model_artifact=artifact,
                repo_root=repo_root,
            )
        except ReasoningParseError:
            rejected.append(sha256_object(raw))

    mixed_rejected = False
    try:
        reject_mixed_transport(raw_text="<answer>42</answer>", native_reasoning="reason")
    except ReasoningParseError:
        mixed_rejected = True

    gates = {
        "m3_prerequisite": m3_evidence.get("verdict") == "PASS",
        "exact_pinned_tokenizer": snapshot.name == config.model.revision and len(files) > 0,
        "profile_capability_compiled": capability.supported
        and capability.training_format == "qwen_chat_tagged_reasoning@1",
        "pinned_reasoning_dependencies": environment_versions == {
            "transformers": "5.17.0",
            "huggingface-hub": "1.32.0",
            "tokenizers": "0.23.2",
            "jinja2": "3.1.6",
        },
        "assistant_only_serializer": len(serialization) == len(records)
        and all(item["prompt_token_count"] > 0 and item["supervised_token_count"] > 0 for item in serialization),
        "visible_semantics": len(visible) == len(records)
        and all(item["reasoning"] and item["reasoning_present"] is True for item in visible),
        "hidden_semantics": len(hidden) == len(records)
        and all(item["reasoning"] is None and item["reasoning_present"] is True for item in hidden),
        "r0_off_explicit_unsupported": off_decision["status"] == "unsupported"
        and off_decision["degraded_to"] is None
        and off_unsupported,
        "true_off_semantics_when_supported": off_supported_response["reasoning"] is None
        and off_supported_response["reasoning_present"] is False,
        "native_transport_abstraction": native_visible["reasoning"] is not None
        and native_hidden["reasoning"] is None
        and native_hidden["reasoning_present"] is True
        and native_off["reasoning_present"] is False,
        "malformed_tags_rejected": len(rejected) == len(malformed),
        "mixed_transport_rejected": mixed_rejected,
        "no_model_weights_or_training": True,
    }
    failed = [name for name, passed in gates.items() if not passed]
    qualification = {
        "schema": "mindforge-model-pipeline-m4-qualification-v1",
        "model": {"id": config.model.id, "revision": config.model.revision},
        "tokenizer_snapshot_hash": tokenizer_snapshot_hash,
        "chat_template_hash": sha256_object(getattr(tokenizer, "chat_template", None)),
        "capability": capability.to_dict(),
        "environment_versions": environment_versions,
        "capability_hash": capability.sha256,
        "serialization": serialization,
        "visible_responses": visible,
        "hidden_responses": hidden,
        "off_decision": off_decision,
        "synthetic_supported_off_response": off_supported_response,
        "synthetic_native_responses": {
            "visible": native_visible,
            "hidden": native_hidden,
            "off": native_off,
        },
        "malformed_rejection_hashes": rejected,
        "mixed_transport_rejected": mixed_rejected,
        "gates": {name: {"required": True, "pass": bool(value)} for name, value in gates.items()},
        "failed_required_gates": failed,
        "model_weights_loaded": False,
        "training_started": False,
        "verdict": "PASS" if not failed else "FAIL",
    }
    qualification_hash = sha256_object(qualification)
    atomic_write_json(
        run_dir / "m4_qualification.json",
        {**qualification, "qualification_hash": qualification_hash},
    )
    if failed:
        raise ReasoningParseError(f"M4 qualification failed required gates: {failed}")

    result = M4Result(
        status="PASS",
        run_dir=run_dir,
        serialized_samples=len(serialization),
        visible_pass=len(visible),
        hidden_pass=len(hidden),
        malformed_rejections=len(rejected),
        gates_passed=len(gates),
        gates_total=len(gates),
        capability_hash=capability.sha256,
        tokenizer_snapshot_hash=tokenizer_snapshot_hash,
        qualification_hash=qualification_hash,
        model_weights_loaded=False,
        training_started=False,
    )
    atomic_write_json(run_dir / "m4_result.json", result.to_dict())
    return result


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ReasoningParseError(f"fixture row must be object: {path}")
            rows.append(value)
    return rows


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReasoningParseError(f"expected object: {path}")
    return value

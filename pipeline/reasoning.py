"""M4 reasoning serializer, capability model, parsers and normalized API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .canonical import sha256_object
from .errors import (
    ReasoningParseError,
    ReasoningSerializationError,
    UnsupportedReasoningMode,
)
from .loader import validate_mapping


@dataclass(frozen=True)
class ReasoningCapability:
    supported: bool
    training_format: str
    transport_options: tuple[str, ...]
    visibility_modes: tuple[str, ...]
    effort_levels: tuple[str, ...]
    supports_disable: bool
    supports_hide: bool
    native_runtime_support: Mapping[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "supported": self.supported,
            "training_format": self.training_format,
            "transport_options": list(self.transport_options),
            "visibility_modes": list(self.visibility_modes),
            "effort_levels": list(self.effort_levels),
            "supports_disable": self.supports_disable,
            "supports_hide": self.supports_hide,
            "native_runtime_support": dict(self.native_runtime_support),
        }

    @property
    def sha256(self) -> str:
        return sha256_object(self.to_dict())


@dataclass(frozen=True)
class SerializedReasoningSample:
    prompt_text: str
    full_text: str
    input_ids: tuple[int, ...]
    labels: tuple[int, ...]
    prompt_token_count: int
    supervised_token_count: int
    serializer_id: str
    serializer_version: str
    chat_template_hash: str
    sample_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_token_count": self.prompt_token_count,
            "supervised_token_count": self.supervised_token_count,
            "serializer_id": self.serializer_id,
            "serializer_version": self.serializer_version,
            "chat_template_hash": self.chat_template_hash,
            "sample_hash": self.sample_hash,
            "input_ids_hash": sha256_object(list(self.input_ids)),
            "labels_hash": sha256_object(list(self.labels)),
        }


def capability_from_profile(profile: Mapping[str, Any]) -> ReasoningCapability:
    serializer = profile["training_serializer"]
    reasoning = profile["reasoning"]
    tagged = reasoning["tagged_serializer"]
    if serializer["id"] != "qwen_chat_tagged_reasoning" or str(serializer["version"]) != "1":
        raise ReasoningSerializationError(
            f"unsupported R0 reasoning serializer {serializer['id']}@{serializer['version']}"
        )
    if serializer["loss_mask"] != "assistant_only":
        raise ReasoningSerializationError("R0 reasoning serializer must use assistant_only loss mask")
    if not tagged["enabled"]:
        raise ReasoningSerializationError("R0 tagged serializer is disabled")
    if reasoning["native_training_channel"]:
        raise ReasoningSerializationError("R0 profile unexpectedly declares native training channel")

    # For the R0 pinned Qwen profile, tags are a serializer/output convention,
    # not a model-native switch. Hiding can be enforced by the normalized API.
    # True disable cannot be claimed until a runtime/model contract proves it.
    return ReasoningCapability(
        supported=True,
        training_format="qwen_chat_tagged_reasoning@1",
        transport_options=("tagged_text",),
        visibility_modes=("visible", "hidden"),
        effort_levels=(),
        supports_disable=False,
        supports_hide=True,
        native_runtime_support={
            "hf": "tagged_text_parser",
            "llama_cpp": "not_qualified_m5",
            "ollama": "not_qualified_m6",
        },
    )


def serialize_reasoning_sample(
    tokenizer: Any,
    profile: Mapping[str, Any],
    record: Mapping[str, Any],
    *,
    max_length: int | None = None,
) -> SerializedReasoningSample:
    capability = capability_from_profile(profile)
    if not capability.supported:
        raise ReasoningSerializationError("reasoning serialization unsupported")

    messages = record.get("messages")
    reasoning = record.get("reasoning")
    answer = record.get("answer")
    if not isinstance(messages, list) or not messages:
        raise ReasoningSerializationError("reasoning sample messages must be non-empty list")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ReasoningSerializationError("reasoning sample rationale must be non-empty")
    if not isinstance(answer, str) or not answer.strip():
        raise ReasoningSerializationError("reasoning sample answer must be non-empty")

    tags = profile["reasoning"]["tagged_serializer"]
    reserved = (
        tags["start_tag"],
        tags["end_tag"],
        tags["answer_start_tag"],
        tags["answer_end_tag"],
    )
    values_to_check = [reasoning, answer]
    for message in messages:
        if not isinstance(message, dict):
            raise ReasoningSerializationError("reasoning sample message must be object")
        content = message.get("content")
        if not isinstance(content, str):
            raise ReasoningSerializationError("reasoning sample message content must be string")
        values_to_check.append(content)
    if any(marker in value for marker in reserved for value in values_to_check):
        if tags["reserved_marker_policy"] == "reject_sample":
            raise ReasoningSerializationError("reasoning sample contains reserved marker")
        raise ReasoningSerializationError("escape_v1 is not implemented for R0")

    assistant_content = (
        f"{tags['start_tag']}{reasoning.strip()}{tags['end_tag']}\n"
        f"{tags['answer_start_tag']}{answer.strip()}{tags['answer_end_tag']}"
    )
    try:
        prompt_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        full_messages = [*messages, {"role": "assistant", "content": assistant_content}]
        full_text = tokenizer.apply_chat_template(
            full_messages,
            tokenize=False,
            add_generation_prompt=False,
        )
    except Exception as error:
        raise ReasoningSerializationError(f"chat-template serialization failed: {error}") from error

    prompt_ids = tokenizer(
        prompt_text,
        add_special_tokens=False,
        truncation=max_length is not None,
        max_length=max_length,
    )["input_ids"]
    full_ids = tokenizer(
        full_text,
        add_special_tokens=False,
        truncation=max_length is not None,
        max_length=max_length,
    )["input_ids"]
    if not isinstance(prompt_ids, list) or not isinstance(full_ids, list):
        raise ReasoningSerializationError("tokenizer returned non-list token ids")
    prefix_len = min(len(prompt_ids), len(full_ids))
    if full_ids[:prefix_len] != prompt_ids[:prefix_len]:
        raise ReasoningSerializationError("assistant serialization is not prefixed by prompt serialization")

    labels = list(full_ids)
    for index in range(prefix_len):
        labels[index] = -100
    supervised = sum(value != -100 for value in labels)
    if supervised <= 0:
        raise ReasoningSerializationError("assistant-only mask produced zero supervised tokens")

    # The mask must suppress all prompt tokens and retain every token remaining
    # after the prompt prefix. This is the executable assistant-only contract.
    if any(value != -100 for value in labels[:prefix_len]):
        raise ReasoningSerializationError("prompt token leaked into supervised loss mask")
    if any(value == -100 for value in labels[prefix_len:]):
        raise ReasoningSerializationError("assistant token was unexpectedly masked")

    serializer = profile["training_serializer"]
    return SerializedReasoningSample(
        prompt_text=prompt_text,
        full_text=full_text,
        input_ids=tuple(int(value) for value in full_ids),
        labels=tuple(int(value) for value in labels),
        prompt_token_count=prefix_len,
        supervised_token_count=supervised,
        serializer_id=serializer["id"],
        serializer_version=str(serializer["version"]),
        chat_template_hash=sha256_object(getattr(tokenizer, "chat_template", None)),
        sample_hash=sha256_object(
            {
                "messages": messages,
                "reasoning": reasoning.strip(),
                "answer": answer.strip(),
            }
        ),
    )


def request_decision(capability: ReasoningCapability, mode: str) -> dict[str, Any]:
    if mode not in {"visible", "hidden", "off"}:
        raise UnsupportedReasoningMode(f"unknown reasoning mode {mode!r}")
    if mode == "hidden" and not capability.supports_hide:
        return {
            "requested_mode": mode,
            "status": "unsupported",
            "degraded_to": None,
            "reason": "capability_does_not_support_hide",
        }
    if mode == "off" and not capability.supports_disable:
        return {
            "requested_mode": mode,
            "status": "unsupported",
            "degraded_to": None,
            "reason": "capability_does_not_support_disable",
        }
    if mode not in capability.visibility_modes and mode != "off":
        return {
            "requested_mode": mode,
            "status": "unsupported",
            "degraded_to": None,
            "reason": "mode_not_in_visibility_modes",
        }
    return {
        "requested_mode": mode,
        "status": "supported",
        "degraded_to": None,
        "reason": None,
    }


def normalize_tagged_output(
    *,
    raw_text: str,
    mode: str,
    capability: ReasoningCapability,
    profile: Mapping[str, Any],
    runtime: str,
    model_artifact: str,
    repo_root: Path,
) -> dict[str, Any]:
    decision = request_decision(capability, mode)
    if decision["status"] != "supported":
        raise UnsupportedReasoningMode(
            f"{mode} unsupported: {decision['reason']}; silent degradation is forbidden"
        )

    tags = profile["reasoning"]["tagged_serializer"]
    reasoning, answer = _strict_tagged_parse(raw_text, tags, allow_reasoning=(mode != "off"))
    if mode == "visible":
        response_reasoning: str | None = reasoning
        reasoning_present: bool | None = True
    elif mode == "hidden":
        response_reasoning = None
        reasoning_present = True
    else:
        response_reasoning = None
        reasoning_present = False

    response = {
        "answer": answer,
        "reasoning": response_reasoning,
        "reasoning_kind": "model_generated_rationale",
        "reasoning_mode": mode,
        "reasoning_present": reasoning_present,
        "transport": "tagged_text",
        "parser_status": "ok",
        "runtime": runtime,
        "model_artifact": model_artifact,
    }
    validate_reasoning_response(response, repo_root)
    return response


def normalize_native_output(
    *,
    answer: str,
    native_reasoning: str | None,
    mode: str,
    capability: ReasoningCapability,
    runtime: str,
    model_artifact: str,
    repo_root: Path,
) -> dict[str, Any]:
    if "native_runtime_field" not in capability.transport_options:
        raise ReasoningParseError("native runtime field supplied to capability without native transport")
    decision = request_decision(capability, mode)
    if decision["status"] != "supported":
        raise UnsupportedReasoningMode(
            f"{mode} unsupported: {decision['reason']}; silent degradation is forbidden"
        )
    if not isinstance(answer, str) or not answer.strip():
        raise ReasoningParseError("native runtime answer is empty")
    if mode == "visible":
        if not isinstance(native_reasoning, str) or not native_reasoning.strip():
            raise ReasoningParseError("visible native reasoning is empty")
        exposed = native_reasoning.strip()
        present: bool | None = True
    elif mode == "hidden":
        exposed = None
        present = bool(native_reasoning and native_reasoning.strip())
    else:
        if native_reasoning not in {None, ""}:
            raise ReasoningParseError("off mode produced native reasoning despite disable contract")
        exposed = None
        present = False
    response = {
        "answer": answer.strip(),
        "reasoning": exposed,
        "reasoning_kind": "model_generated_rationale",
        "reasoning_mode": mode,
        "reasoning_present": present,
        "transport": "native_runtime_field",
        "parser_status": "ok",
        "runtime": runtime,
        "model_artifact": model_artifact,
    }
    validate_reasoning_response(response, repo_root)
    return response


def reject_mixed_transport(*, raw_text: str | None, native_reasoning: str | None) -> None:
    if raw_text is not None and native_reasoning is not None:
        raise ReasoningParseError("mixed tagged_text and native_runtime_field payload is ambiguous")


def validate_reasoning_response(response: Mapping[str, Any], repo_root: Path) -> None:
    schema_path = repo_root / "docs/model-training-pipeline/schemas/reasoning_response.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validate_mapping(response, schema, "ReasoningResponse")


def _strict_tagged_parse(
    raw_text: str,
    tags: Mapping[str, Any],
    *,
    allow_reasoning: bool,
) -> tuple[str, str]:
    if not isinstance(raw_text, str):
        raise ReasoningParseError("tagged output must be string")

    start = tags["start_tag"]
    end = tags["end_tag"]
    answer_start = tags["answer_start_tag"]
    answer_end = tags["answer_end_tag"]
    markers = (start, end, answer_start, answer_end)

    if allow_reasoning:
        expected_counts = {start: 1, end: 1, answer_start: 1, answer_end: 1}
    else:
        expected_counts = {start: 0, end: 0, answer_start: 1, answer_end: 1}
    actual_counts = {marker: raw_text.count(marker) for marker in markers}
    if actual_counts != expected_counts:
        raise ReasoningParseError(
            f"tag cardinality mismatch expected={expected_counts} actual={actual_counts}"
        )

    stripped = raw_text.strip()
    if allow_reasoning:
        if not stripped.startswith(start) or not stripped.endswith(answer_end):
            raise ReasoningParseError("tagged output has unexpected leading/trailing content")
        reasoning_end = stripped.find(end)
        answer_begin = stripped.find(answer_start, reasoning_end + len(end))
        if reasoning_end < len(start) or answer_begin < 0:
            raise ReasoningParseError("tag order is invalid")
        between = stripped[reasoning_end + len(end) : answer_begin]
        if between.strip():
            raise ReasoningParseError("non-whitespace content exists between reasoning and answer blocks")
        reasoning = stripped[len(start) : reasoning_end]
        answer = stripped[answer_begin + len(answer_start) : -len(answer_end)]
        if any(marker in reasoning or marker in answer for marker in markers):
            raise ReasoningParseError("nested or injected reserved marker detected")
        if not reasoning.strip():
            raise ReasoningParseError("reasoning block is empty")
    else:
        if not stripped.startswith(answer_start) or not stripped.endswith(answer_end):
            raise ReasoningParseError("off-mode tagged output must contain only answer block")
        reasoning = ""
        answer = stripped[len(answer_start) : -len(answer_end)]
        if any(marker in answer for marker in markers):
            raise ReasoningParseError("nested or injected reserved marker detected")

    if not answer.strip():
        raise ReasoningParseError("answer block is empty")
    return reasoning.strip(), answer.strip()

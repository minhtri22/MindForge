from __future__ import annotations

import copy
from pathlib import Path

import pytest

from pipeline.errors import (
    ReasoningParseError,
    ReasoningSerializationError,
    UnsupportedReasoningMode,
)
from pipeline.loader import load_experiment_config, load_model_profile
from pipeline.reasoning import (
    ReasoningCapability,
    capability_from_profile,
    normalize_native_output,
    normalize_tagged_output,
    reject_mixed_transport,
    request_decision,
    serialize_reasoning_sample,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "docs/model-training-pipeline/examples/end_to_end_small.yaml"


class FakeTokenizer:
    chat_template = "fake-qwen-template-v1"

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        assert tokenize is False
        rendered = "".join(f"<{m['role']}>{m['content']}</{m['role']}>" for m in messages)
        if add_generation_prompt:
            rendered += "<assistant>"
        return rendered

    def __call__(self, text, add_special_tokens=False, truncation=False, max_length=None, **kwargs):
        ids = list(text.encode("utf-8"))
        if truncation and max_length is not None:
            ids = ids[:max_length]
        return {"input_ids": ids}


@pytest.fixture
def config_profile():
    config = load_experiment_config(CONFIG, ROOT)
    return config, load_model_profile(config, ROOT)


@pytest.fixture
def capability(config_profile):
    return capability_from_profile(config_profile[1])


@pytest.fixture
def record():
    return {
        "messages": [{"role": "user", "content": "What is 17 + 25?"}],
        "reasoning": "Add the two integers to get 42.",
        "answer": "42",
    }


def test_r0_capability_does_not_claim_disable(capability):
    assert capability.supported is True
    assert capability.visibility_modes == ("visible", "hidden")
    assert capability.supports_hide is True
    assert capability.supports_disable is False
    decision = request_decision(capability, "off")
    assert decision == {
        "requested_mode": "off",
        "status": "unsupported",
        "degraded_to": None,
        "reason": "capability_does_not_support_disable",
    }


def test_serializer_enforces_assistant_only_mask(config_profile, record):
    _, profile = config_profile
    serialized = serialize_reasoning_sample(FakeTokenizer(), profile, record)
    assert serialized.prompt_token_count > 0
    assert serialized.supervised_token_count > 0
    assert all(value == -100 for value in serialized.labels[: serialized.prompt_token_count])
    assert all(value != -100 for value in serialized.labels[serialized.prompt_token_count :])
    assert "<think>" in serialized.full_text
    assert "<answer>42</answer>" in serialized.full_text


def test_serializer_rejects_reserved_marker_in_any_sample_field(config_profile, record):
    _, profile = config_profile
    bad = copy.deepcopy(record)
    bad["messages"][0]["content"] = "inject <think> marker"
    with pytest.raises(ReasoningSerializationError, match="reserved marker"):
        serialize_reasoning_sample(FakeTokenizer(), profile, bad)


def test_visible_and_hidden_tagged_semantics(config_profile, capability):
    _, profile = config_profile
    raw = "<think>Add them.</think>\n<answer>42</answer>"
    visible = normalize_tagged_output(
        raw_text=raw,
        mode="visible",
        capability=capability,
        profile=profile,
        runtime="unit",
        model_artifact="sha256:test",
        repo_root=ROOT,
    )
    hidden = normalize_tagged_output(
        raw_text=raw,
        mode="hidden",
        capability=capability,
        profile=profile,
        runtime="unit",
        model_artifact="sha256:test",
        repo_root=ROOT,
    )
    assert visible["reasoning"] == "Add them."
    assert visible["reasoning_present"] is True
    assert hidden["reasoning"] is None
    assert hidden["reasoning_present"] is True
    assert visible["answer"] == hidden["answer"] == "42"


def test_r0_off_is_explicitly_unsupported_not_degraded(config_profile, capability):
    _, profile = config_profile
    with pytest.raises(UnsupportedReasoningMode, match="silent degradation is forbidden"):
        normalize_tagged_output(
            raw_text="<answer>42</answer>",
            mode="off",
            capability=capability,
            profile=profile,
            runtime="unit",
            model_artifact="sha256:test",
            repo_root=ROOT,
        )


def test_true_off_semantics_work_only_for_capability_that_supports_disable(config_profile):
    _, profile = config_profile
    supported = ReasoningCapability(
        supported=True,
        training_format="synthetic",
        transport_options=("tagged_text", "native_runtime_field"),
        visibility_modes=("visible", "hidden", "off"),
        effort_levels=(),
        supports_disable=True,
        supports_hide=True,
        native_runtime_support={"unit": "synthetic"},
    )
    response = normalize_tagged_output(
        raw_text="<answer>42</answer>",
        mode="off",
        capability=supported,
        profile=profile,
        runtime="unit",
        model_artifact="synthetic:test",
        repo_root=ROOT,
    )
    assert response["reasoning"] is None
    assert response["reasoning_present"] is False
    assert response["answer"] == "42"


@pytest.mark.parametrize(
    "raw",
    [
        "<think>reason<answer>42</answer>",
        "<think>outer <think>inner</think></think><answer>42</answer>",
        "<think>a</think><think>b</think><answer>42</answer>",
        "<think>a</think><answer>42</answer><answer>43</answer>",
        "<answer>42</answer><think>late</think>",
        "prefix<think>a</think><answer>42</answer>",
        "<think>a</think><answer></answer>",
    ],
)
def test_malformed_tagged_output_is_rejected(config_profile, capability, raw):
    _, profile = config_profile
    with pytest.raises(ReasoningParseError):
        normalize_tagged_output(
            raw_text=raw,
            mode="visible",
            capability=capability,
            profile=profile,
            runtime="unit",
            model_artifact="sha256:test",
            repo_root=ROOT,
        )


def test_mixed_transport_is_rejected():
    with pytest.raises(ReasoningParseError, match="mixed"):
        reject_mixed_transport(
            raw_text="<think>a</think><answer>42</answer>",
            native_reasoning="a",
        )


def test_native_transport_visible_hidden_off_semantics():
    supported = ReasoningCapability(
        supported=True,
        training_format="synthetic",
        transport_options=("native_runtime_field",),
        visibility_modes=("visible", "hidden", "off"),
        effort_levels=("low", "medium", "high"),
        supports_disable=True,
        supports_hide=True,
        native_runtime_support={"unit": "synthetic"},
    )
    visible = normalize_native_output(
        answer="42",
        native_reasoning="Add them.",
        mode="visible",
        capability=supported,
        runtime="unit",
        model_artifact="synthetic:test",
        repo_root=ROOT,
    )
    hidden = normalize_native_output(
        answer="42",
        native_reasoning="Add them.",
        mode="hidden",
        capability=supported,
        runtime="unit",
        model_artifact="synthetic:test",
        repo_root=ROOT,
    )
    off = normalize_native_output(
        answer="42",
        native_reasoning=None,
        mode="off",
        capability=supported,
        runtime="unit",
        model_artifact="synthetic:test",
        repo_root=ROOT,
    )
    assert visible["reasoning"] == "Add them."
    assert hidden["reasoning"] is None and hidden["reasoning_present"] is True
    assert off["reasoning"] is None and off["reasoning_present"] is False

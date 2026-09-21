from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.errors import RuntimeParityError
from pipeline.m5 import (
    absolute_preserving_symlink,
    build_gguf_manifest,
    evaluate_runtime_parity,
    git_blob_sha1,
    run_llama_fixture,
    task_success,
    valid_runtime_output,
)

ROOT = Path(__file__).resolve().parents[1]


def test_git_blob_sha1_matches_known_git_blob(tmp_path: Path):
    path = tmp_path / "x.txt"
    path.write_bytes(b"hello\n")
    assert git_blob_sha1(path) == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_single_file_gguf_manifest_is_hashed(tmp_path: Path):
    path = tmp_path / "model-f16.gguf"
    path.write_bytes(b"GGUFfixture")
    manifest = build_gguf_manifest(path, "f16")
    assert manifest["topology"] == "single_file"
    assert len(manifest["files"]) == 1
    assert len(manifest["files"][0]["sha256"]) == 64
    assert len(manifest["aggregate_hash"]) == 64


def test_shard_set_manifest_is_ordered(tmp_path: Path):
    primary = tmp_path / "model-f16.gguf"
    (tmp_path / "model-f16-00002-of-00002.gguf").write_bytes(b"b")
    (tmp_path / "model-f16-00001-of-00002.gguf").write_bytes(b"a")
    manifest = build_gguf_manifest(primary, "f16")
    assert manifest["topology"] == "shard_set"
    assert [row["name"] for row in manifest["files"]] == [
        "model-f16-00001-of-00002.gguf",
        "model-f16-00002-of-00002.gguf",
    ]


def test_runtime_parity_is_task_metric_not_exact_text():
    hf = {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
    }
    runtime = {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
        "exact_text_equal_count": 0,
    }
    result = evaluate_runtime_parity(hf, runtime)
    assert result["pass"] is True
    assert result["exact_text_equal_count"] == 0
    assert result["exact_text_required"] is False


def test_runtime_parity_rejects_task_vector_drift():
    hf = {
        "task_vector": [True, False],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
    }
    runtime = {
        "task_vector": [False, True],
        "accuracy": 0.5,
        "all_outputs_nonempty": True,
        "exact_text_equal_count": 0,
    }
    assert evaluate_runtime_parity(hf, runtime)["pass"] is False


def test_runtime_parity_rejects_empty_output():
    hf = {
        "task_vector": [True],
        "accuracy": 1.0,
        "all_outputs_nonempty": True,
    }
    runtime = {
        "task_vector": [True],
        "accuracy": 1.0,
        "all_outputs_nonempty": False,
        "exact_text_equal_count": 1,
    }
    assert evaluate_runtime_parity(hf, runtime)["pass"] is False


def test_exact_answer_task_is_strict():
    task = {"type": "exact_answer", "expected": "42"}
    assert task_success(task, "42\n") is True
    assert task_success(task, "The answer is 42") is False


def test_runtime_output_format_guard():
    assert valid_runtime_output("42") is True
    assert valid_runtime_output("   ") is False
    assert valid_runtime_output("ok\x01") is False


def test_unknown_fixture_type_is_rejected():
    with pytest.raises(RuntimeParityError):
        task_success({"type": "judge", "expected": "x"}, "x")


def test_converter_probe_script_is_standalone_and_compiles():
    path = ROOT / "pipeline/m5_converter_probe.py"
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    assert "from . " not in source
    assert "import pipeline" not in source


def test_converter_python_path_preserves_venv_symlink(tmp_path: Path):
    target = tmp_path / "system-python"
    target.write_text("#!/bin/sh\n", encoding="utf-8")
    link_dir = tmp_path / "venv" / "bin"
    link_dir.mkdir(parents=True)
    link = link_dir / "python"
    link.symlink_to(target)
    absolute = absolute_preserving_symlink(link)
    assert absolute == link.absolute()
    assert absolute != link.resolve()
    assert absolute.is_symlink()


def test_llama_fixture_enforces_single_turn_process_exit(monkeypatch, tmp_path: Path):
    calls: list[list[str]] = []

    def fake_run(command, *, cwd=None, label: str, combine: bool = False):
        calls.append(list(command))
        return {
            "returncode": 0,
            "stdout": "42\n",
            "stderr": "",
            "combined": "42\n",
            "command_hash": "fixture",
        }

    monkeypatch.setattr("pipeline.m5._run", fake_run)
    model = tmp_path / "model-f16.gguf"
    model.write_bytes(b"GGUFfixture")

    result = run_llama_fixture(
        llama_cli=Path("llama-cli"),
        model_path=model,
        hf_baseline={
            "rows": [
                {
                    "id": "arith-1",
                    "type": "exact_answer",
                    "expected": "42",
                    "prompt_text": "<prompt>",
                    "output": "42",
                }
            ]
        },
        inference={
            "max_new_tokens": 128,
            "context_length": 2048,
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 0,
            "seed": 42,
        },
    )

    assert result["task_success_count"] == 1
    assert len(calls) == 1
    assert "--single-turn" in calls[0]
    assert calls[0].count("--single-turn") == 1

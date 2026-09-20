from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pytest
import torch

from pipeline.errors import DataIntegrityError
from pipeline.m2_checkpoint import (
    create_incomplete_checkpoint_sentinel,
    restore_checkpoint,
    trainable_state_hash,
    verify_checkpoint,
    write_checkpoint,
)


def _tiny():
    torch.manual_seed(123)
    model = torch.nn.Sequential(torch.nn.Linear(4, 4), torch.nn.Tanh(), torch.nn.Linear(4, 2))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)
    return model, optimizer, scheduler


def _step(model, optimizer, scheduler):
    x = torch.tensor([[1.0, 2.0, 3.0, 4.0]])
    target = torch.tensor([[0.25, -0.5]])
    optimizer.zero_grad(set_to_none=True)
    loss = torch.nn.functional.mse_loss(model(x), target)
    loss.backward()
    optimizer.step()
    scheduler.step()
    return float(loss.item())


def _sampler_state():
    return {
        "resume_fidelity": "exact",
        "dataset_or_shard_id": "fixture",
        "document_index": 1,
        "token_offset": 0,
        "packed_sequence_index": 1,
        "shuffle_state": {"order": [0, 1], "next_index": 1},
        "worker_states": [],
        "mixture_state": {"phase_id": "unit", "batch_count": 2},
    }


def test_atomic_checkpoint_roundtrip_restores_weights_optimizer_scheduler_and_rng(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    random.seed(7)
    np.random.seed(7)
    torch.manual_seed(7)
    model, optimizer, scheduler = _tiny()
    _step(model, optimizer, scheduler)
    expected_state_hash = trainable_state_hash(model)

    checkpoint = write_checkpoint(
        checkpoints_root=tmp_path,
        repo_root=repo_root,
        run_id="m2-unit",
        phase_id="unit",
        checkpoint_id="checkpoint-step-000001",
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        step=1,
        consumed_tokens=8,
        sampler_state=_sampler_state(),
        config_hash="1" * 64,
        data_manifest_hash="2" * 64,
        parent_artifact_hash="3" * 64,
    )
    expected_random = random.random()
    expected_numpy = float(np.random.random())
    expected_torch = float(torch.rand(1).item())

    random.seed(999)
    np.random.seed(999)
    torch.manual_seed(999)
    fresh_model, fresh_optimizer, fresh_scheduler = _tiny()
    manifest = restore_checkpoint(checkpoint, repo_root, fresh_model, fresh_optimizer, fresh_scheduler)

    assert manifest["status"] == "COMMITTED"
    assert manifest["sampler_state"]["resume_fidelity"] == "exact"
    assert trainable_state_hash(fresh_model) == expected_state_hash
    assert fresh_scheduler.last_epoch == scheduler.last_epoch
    assert fresh_optimizer.param_groups[0]["lr"] == optimizer.param_groups[0]["lr"]
    assert random.random() == expected_random
    assert float(np.random.random()) == expected_numpy
    assert float(torch.rand(1).item()) == expected_torch


def test_incomplete_checkpoint_is_not_accepted(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    partial = create_incomplete_checkpoint_sentinel(tmp_path, "checkpoint-step-000002")
    with pytest.raises(DataIntegrityError, match="not COMMITTED"):
        verify_checkpoint(partial, repo_root)


def test_checkpoint_detects_payload_corruption(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    model, optimizer, scheduler = _tiny()
    _step(model, optimizer, scheduler)
    checkpoint = write_checkpoint(
        checkpoints_root=tmp_path,
        repo_root=repo_root,
        run_id="m2-unit",
        phase_id="unit",
        checkpoint_id="checkpoint-step-000001",
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        step=1,
        consumed_tokens=8,
        sampler_state=_sampler_state(),
        config_hash="1" * 64,
        data_manifest_hash="2" * 64,
        parent_artifact_hash="3" * 64,
    )
    with (checkpoint / "trainable_weights.pt").open("ab") as handle:
        handle.write(b"corrupt")
    with pytest.raises(DataIntegrityError, match="hash mismatch"):
        verify_checkpoint(checkpoint, repo_root)


def test_scheduler_and_optimizer_are_nontrivial_state():
    model, optimizer, scheduler = _tiny()
    before = optimizer.param_groups[0]["lr"]
    _step(model, optimizer, scheduler)
    assert optimizer.state
    assert scheduler.last_epoch == 1
    assert optimizer.param_groups[0]["lr"] != before

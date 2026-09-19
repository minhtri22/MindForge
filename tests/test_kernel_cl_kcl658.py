from __future__ import annotations

from experiments.kernel_cl import kcl658_localized_boundary_state as k658


def test_canonical_source_is_valid() -> None:
    src = k658._load_canonical()
    assert src["valid"]
    assert len(src["records"]) == 60


def test_confirmatory_seeds_are_not_in_discovery() -> None:
    src = k658._load_canonical()
    seeds = {int(r["seed"]) for r in src["records"]}
    assert seeds.isdisjoint(k658.CONFIRM_SEEDS)


def test_feature_contract_is_frozen() -> None:
    assert k658.FEATURE_ORDER == tuple(f"F{i}" for i in range(1, 14))
    assert k658.RIDGE_LAMBDA == 1.0
    assert k658.DISCOVERY_BA_MIN == 0.70
    assert k658.DISCOVERY_SENS_MIN == 0.65
    assert k658.DISCOVERY_SPEC_MIN == 0.65
    assert k658.BASELINE_SUPERIORITY_MIN == 0.03


def test_parameter_groups_cover_model() -> None:
    cfg = k658.KCL1Config()
    model = k658.build_model(cfg, k658.DISCOVERY_SEEDS[0])
    groups = k658.k653.parameter_groups(model)
    assert k658.k653.group_coverage_valid(model, groups)
    assert tuple(groups.keys()) == k658.GROUP_ORDER


def test_localized_feature_extraction_shares_sum_to_one_and_clears_grads() -> None:
    cfg = k658.KCL1Config()
    seed = k658.DISCOVERY_SEEDS[0]
    tasks = k658.task_sequence(cfg)

    model = k658.build_model(cfg, seed)
    opt = k658.optimizer_for(model, cfg)
    pre = {k: v.detach().clone() for k, v in model.state_dict().items()}

    k658.train_stage(
        model, opt, tasks[0][1],
        steps=250, batch_size=16, seed=seed + 101
    )
    out = k658.extract_localized_features(
        model=model,
        optimizer=opt,
        pre_task_model_state=pre,
        observed_tasks=[tasks[0]],
        boundary_index=1,
    )

    sums = out["details"]["share_sums"]
    assert abs(sums["drift"] - 1.0) <= 1e-9
    assert abs(sums["pressure"] - 1.0) <= 1e-9
    assert abs(sums["retention"] - 1.0) <= 1e-9
    assert all(p.grad is None for p in model.parameters())
    assert tuple(out["features"][f"F{i}"] for i in range(1, 14))


def test_one_seed_reproduces_canonical_boundaries() -> None:
    src = k658._load_canonical()
    cfg = k658.KCL1Config()
    rows = k658.build_localized_records(
        k658.DISCOVERY_SEEDS[0], cfg, src["by_key"]
    )
    assert len(rows) == 3
    assert all(
        r["integrity"]["canonical_reproduction"] for r in rows
    ), [
        {
            "boundary": r["boundary_index"],
            "detail": r["integrity"]["canonical_reproduction_detail"],
        }
        for r in rows
    ]
    assert all(r["integrity"]["gradients_cleared_before_counterfactual"] for r in rows)


def test_ablation_contract_is_fixed() -> None:
    assert set(k658.ABLATIONS) == {
        "A_OVERLAP", "A_MISMATCH", "A_IDENTITY", "A_NO_DIRECTION"
    }
    for names in k658.ABLATIONS.values():
        assert set(names).issubset(k658.FEATURE_ORDER)


def test_loso_holds_out_whole_seed() -> None:
    src = k658._load_canonical()
    cfg = k658.KCL1Config()
    rows = []
    for seed in k658.DISCOVERY_SEEDS[:4]:
        rows.extend(k658.build_localized_records(seed, cfg, src["by_key"]))
    out = k658.loso(rows)
    assert {f["held_seed"] for f in out["folds"]} == set(k658.DISCOVERY_SEEDS[:4])


def test_scalar_baselines_use_same_reconstructed_records() -> None:
    src = k658._load_canonical()
    cfg = k658.KCL1Config()
    rows = []
    for seed in k658.DISCOVERY_SEEDS[:4]:
        rows.extend(k658.build_localized_records(seed, cfg, src["by_key"]))
    out = k658._scalar_baselines(rows)
    assert "stage" in out
    assert "H4_drift" in out


def test_qualification_requires_all_gates() -> None:
    baselines = {
        "stage": {"metrics": {"balanced_accuracy": 0.60}},
        "H4_drift": {"metrics": {"balanced_accuracy": 0.65}},
    }
    good = {
        "balanced_accuracy": 0.72,
        "sensitivity": 0.70,
        "specificity": 0.70,
    }
    bad_spec = {**good, "specificity": 0.60}
    assert k658._qualified(good, baselines)
    assert not k658._qualified(bad_spec, baselines)

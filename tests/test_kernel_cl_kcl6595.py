from __future__ import annotations

from experiments.kernel_cl import kcl6595_mechanism_target_identifiability as k6595


def test_frozen_cohort_hashes_and_sizes() -> None:
    assert len(k6595.TRAIN_SEEDS) == 480
    assert len(k6595.VALIDATION_SEEDS) == 240
    assert set(k6595.TRAIN_SEEDS).isdisjoint(k6595.VALIDATION_SEEDS)
    assert k6595.sha_seed_list(k6595.TRAIN_SEEDS) == k6595.TRAIN_SEED_SHA256
    assert (
        k6595.sha_seed_list(k6595.VALIDATION_SEEDS)
        == k6595.VALIDATION_SEED_SHA256
    )
    assert (
        k6595.sha_seed_list(
            tuple(list(k6595.TRAIN_SEEDS) + list(k6595.VALIDATION_SEEDS))
        )
        == k6595.ALL_SEED_SHA256
    )
    assert k6595.prior_overlap_absent(k6595.TRAIN_SEEDS)
    assert k6595.prior_overlap_absent(k6595.VALIDATION_SEEDS)


def test_primary_targets_are_exact_stable_mechanisms() -> None:
    assert k6595.MECH_PR == "MECH{P,R}"
    assert k6595.MECH_PRR == "MECH{P+R,R}"
    assert k6595.TARGETS == ("Y_A", "Y_PR", "Y_PRR")


def test_information_sets_are_frozen_and_preboundary_only() -> None:
    assert k6595.S0_FEATURES == ("STAGE_2", "STAGE_3")
    assert k6595.S1_FEATURES == k6595.k6592.PRIMARY_FEATURES
    assert k6595.S2_FEATURES == (
        k6595.S1_FEATURES + tuple(f"F{i}" for i in range(1, 14))
    )
    assert not any("_NEXT_" in x for x in k6595.S2_FEATURES)


def test_support_and_gain_gates_are_frozen() -> None:
    assert k6595.TRAIN_MIN_COUNT == 50
    assert k6595.TRAIN_MIN_SEEDS == 40
    assert k6595.VAL_MIN_COUNT == 25
    assert k6595.VAL_MIN_SEEDS == 20
    assert k6595.QUAL_MACRO_RECALL == 0.60
    assert k6595.QUAL_MACRO_F1 == 0.50
    assert k6595.QUAL_CLASS_RECALL == 0.50
    assert k6595.QUAL_CLASS_F1 == 0.35
    assert k6595.QUAL_BOOTSTRAP_LOWER == 0.45
    assert k6595.GAIN_POINT_MIN == 0.10
    assert k6595.GAIN_CI_LOWER_MIN == 0.03
    assert k6595.BOOTSTRAP_RESAMPLES == 20_000
    assert k6595.BOOTSTRAP_SEED == 6595


def test_exact_kcl6594_mechanism_labeling() -> None:
    # Build synthetic component states via the already-frozen helper shape.
    def outcomes_for(b, c):
        # A is the reference. B/C values below are chosen so the frozen
        # predicates give exactly the requested cause codes.
        a = {"auc": 0.80, "final_accuracy": 1.0, "retention": 0.80}

        def policy(code):
            # Start safe enough, then induce exact failures.
            auc = 0.82
            final = 1.0
            retention = 0.80
            if "P" in code:
                auc = 0.80
            if "R" in code:
                retention = 0.70
            if "A" in code:
                final = 0.90
            return {"auc": auc, "final_accuracy": final, "retention": retention}

        return {
            k6595.k659.A: a,
            k6595.k659.B: policy(b),
            k6595.k659.C: policy(c),
        }

    labels = k6595.labels_from_outcomes(outcomes_for("P", "R"))
    assert labels == {"Y_A": True, "Y_PR": True, "Y_PRR": False}

    labels = k6595.labels_from_outcomes(outcomes_for("P+R", "R"))
    assert labels == {"Y_A": True, "Y_PR": False, "Y_PRR": True}


def test_one_fresh_seed_preserves_subset_and_integrity_contract() -> None:
    rows = k6595.build_records((k6595.TRAIN_SEEDS[0],))
    assert len(rows) == 3
    assert {int(r["boundary_index"]) for r in rows} == {1, 2, 3}
    assert all(r["integrity"]["counterfactual_valid"] for r in rows)
    assert all(r["integrity"]["lrbs_shares_valid"] for r in rows)
    assert all(
        (not r["labels"]["Y_PR"] or r["labels"]["Y_A"])
        and (not r["labels"]["Y_PRR"] or r["labels"]["Y_A"])
        for r in rows
    )
    assert all(not any("_NEXT_" in k for k in r["features"]) for r in rows)


def test_family_pass_requires_both_mechanism_routes() -> None:
    def m(mr):
        return {
            "macro_recall": mr,
            "macro_f1": 0.70,
            "per_class": {
                "NEG": {"recall": 0.70, "f1": 0.70},
                "POS": {"recall": 0.70, "f1": 0.70},
            },
        }

    metrics = {
        "Y_A": {"S2": m(0.60)},
        "Y_PR": {"S2": m(0.75)},
        "Y_PRR": {"S2": m(0.76)},
    }
    bootstrap = {
        "arms": {
            t: {"S2": {"macro_recall": {"ci_lower": 0.60, "ci_upper": 0.80}}}
            for t in k6595.TARGETS
        },
        "deltas": {
            "D_PR": {"ci_lower": 0.05, "ci_upper": 0.25},
            "D_PRR": {"ci_lower": 0.06, "ci_upper": 0.26},
        },
    }
    out = k6595.adjudicate(metrics, bootstrap)
    assert out["status"] == "PASS"
    assert out["routes"] == {"H_PR": True, "H_PRR": True}

    bootstrap["deltas"]["D_PRR"]["ci_lower"] = 0.0
    out = k6595.adjudicate(metrics, bootstrap)
    assert out["status"] == "NEGATIVE"
    assert out["verdict"] == (
        "MECHANISM_SPECIFIC_IDENTIFIABILITY_GAIN_NOT_GENERALIZED_ACROSS_BOTH_TARGETS"
    )

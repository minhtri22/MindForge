from tools.research.ppf_l3 import e2


def _cases():
    return [e2.generate_case(spec) for spec in e2.preregistered_histories()]


def test_all_pair_contracts_are_declarative():
    assert set(e2.PAIR_CONTRACTS) == set(e2.PAIR_TEMPLATES)
    for template, contract in e2.PAIR_CONTRACTS.items():
        assert contract.template == template
        assert contract.held_constant_paths
        assert contract.allowed_changed_paths
        assert contract.required_changed_paths


def test_current_dev_pairs_pass_hardened_contracts():
    reports = e2._strong_pair_reports(_cases())
    assert len(reports) == 14
    for report in reports.values():
        assert report["pass"]
        assert report["held_constant_violations"] == []
        assert report["unexpected_changed_paths"] == []
        assert report["missing_required_changes"] == []
        assert all(check["pass"] for check in report["semantic_relation_checks"])


def test_contract_mutations_reject_bad_counterfactuals():
    mutations = e2.counterfactual_contract_mutation_results(_cases())["mutations"]
    assert set(mutations) == {f"M{i}" for i in range(1, 10)}
    for mutation_id, result in mutations.items():
        assert result["checker_pass"] is False, mutation_id
        assert result["rejected"] is True, mutation_id
        assert result["pass"] is True, mutation_id


def test_undeclared_record_context_change_is_rejected():
    result = e2.counterfactual_contract_mutation_results(_cases())["mutations"]["M4"]
    assert result["checker_pass"] is False
    assert "base_records[0].context.period.value" in result["unexpected_changed_paths"]


def test_missing_required_controlled_changes_are_rejected():
    mutations = e2.counterfactual_contract_mutation_results(_cases())["mutations"]
    assert "observation_policy" in mutations["M5"]["missing_required_changes"]
    assert "evidence_records[*]" in mutations["M6"]["missing_required_changes"]
    assert "B requires CORRECTS" in mutations["M7"]["failed_semantic_checks"]
    assert "B requires DERIVED_FROM" in mutations["M8"]["failed_semantic_checks"]
    assert "A requires INDEPENDENT_CORROBORATION" in mutations["M9"]["failed_semantic_checks"]

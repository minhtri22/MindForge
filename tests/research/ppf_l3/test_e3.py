import tempfile
from pathlib import Path

from tools.research.ppf_l3 import e2, e3


class TestPPFL3E3:
    @classmethod
    def setup_class(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "ppf_l3"
        e2.run_e2(cls.root)
        cls.summary = e3.run_e3(cls.root)
        cls.qa = cls.summary["qa"]

    @classmethod
    def teardown_class(cls):
        cls.tmp.cleanup()

    def test_exact_validation_allocation(self):
        assert self.summary["persons"] == 6
        assert self.summary["truth_configs"] == 7
        assert self.summary["standard_configs"] == 5
        assert self.summary["high_risk_configs"] == 2
        assert self.summary["histories"] == 38
        assert self.summary["standard_histories"] == 20
        assert self.summary["high_risk_histories"] == 18

    def test_preregister_generate_retain_no_reroll(self):
        manifest = self.root / "manifests" / "validation_manifest.json"
        registry = self.root / "specs" / "validation_scenario_registry.json"
        assert registry.exists()
        assert manifest.exists()
        assert self.qa["qa_checks"]["no_cherry_picking"]
        assert self.summary["reroll_count"] == 0
        assert self.summary["histories"] == 38

    def test_split_disjoint_and_dev_immutable(self):
        overlap = self.qa["split_overlap"]
        assert overlap["dev_person_overlap"] == []
        assert overlap["dev_truth_config_overlap"] == []
        assert overlap["dev_history_overlap"] == []
        assert overlap["dev_case_id_overlap"] == []
        assert self.qa["dev_immutability"]["canonical_dev_unchanged"]
        assert self.qa["dev_immutability"]["changed_artifacts"] == []

    def test_counterfactual_contracts_and_l2_validity(self):
        assert self.summary["counterfactual_template_count"] == 14
        assert self.summary["pair_instance_count"] == 14
        assert self.summary["paired_history_count"] == 28
        assert self.summary["pair_qa_summary"]["pair_pass_count"] == 14
        assert self.summary["pair_qa_summary"]["held_constant_violations"] == 0
        assert self.summary["pair_qa_summary"]["unexpected_changed_paths"] == 0
        assert self.summary["pair_qa_summary"]["missing_required_changes"] == 0
        assert self.summary["visible_events"] == self.summary["l2_valid_events"]
        assert not any(self.qa["l2_errors"].values())

    def test_identifiability_negative_denominator_and_leakage(self):
        ident = self.summary["identifiability_distribution"]
        assert set(ident) == {"YES", "PARTIAL", "NO"}
        assert all(count > 0 for count in ident.values())
        assert self.summary["negative_denominator_count"] > 0
        assert self.qa["qa_checks"]["negative_denominator"]
        assert self.summary["future_leak_count"] == 0
        assert self.summary["truth_leak_count"] == 0

    def test_scope_and_regression_gates(self):
        assert not (self.root / "generated" / "final").exists()
        assert not (self.root / "evaluator" / "final").exists()
        assert self.qa["qa_checks"]["validation_only_scope"]
        assert self.qa["qa_checks"]["regression"]
        assert all(self.summary["e3_gates"].values())
        assert self.summary["status"] == "PASS"

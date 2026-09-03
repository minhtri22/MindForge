import tempfile
import unittest
import json
from pathlib import Path

from tools.research.ppf_l3.e2 import CHECKPOINT_OFFSETS, PAIR_TEMPLATES, generate_dev, truth_configs


class TestPPFL3E2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "ppf_l3"
        cls.summary = generate_dev(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_status(self):
        self.assertEqual(self.summary["status"], "PASS")
        self.assertTrue(all(self.summary["qa"]["qa_checks"].values()))

    def test_canonical_dev_totals(self):
        self.assertEqual(self.summary["synthetic_persons"], 6)
        self.assertEqual(self.summary["truth_configurations"], 7)
        self.assertEqual(self.summary["standard_truth_configurations"], 5)
        self.assertEqual(self.summary["high_risk_truth_configurations"], 2)
        self.assertEqual(self.summary["histories"], 38)
        self.assertEqual(self.summary["standard_histories"], 20)
        self.assertEqual(self.summary["high_risk_histories"], 18)

    def test_counterfactual_templates(self):
        self.assertEqual(self.summary["counterfactual_pair_instances"], 14)
        self.assertEqual(self.summary["counterfactual_templates_covered"], len(PAIR_TEMPLATES))
        self.assertTrue(self.summary["qa"]["qa_checks"]["one_pair_per_history"])

    def test_visible_events_validate_as_l2(self):
        self.assertTrue(self.summary["qa"]["qa_checks"]["l2_validity"])
        self.assertEqual(self.summary["visible_l2_events"], self.summary["l2_valid_visible_events"])
        self.assertGreater(self.summary["visible_l2_events"], 1000)

    def test_truth_not_visible(self):
        self.assertTrue(self.summary["qa"]["qa_checks"]["truth_leakage"])

    def test_dev_only_layout(self):
        self.assertTrue((self.root / "generated" / "dev").exists())
        self.assertTrue((self.root / "evaluator" / "dev").exists())
        self.assertFalse((self.root / "generated" / "validation").exists())
        self.assertFalse((self.root / "generated" / "final").exists())
        self.assertFalse((self.root / "manifests" / "dev").exists())
        for path in (
            "specs/public_execution_contract.json",
            "specs/public_case_schema.json",
            "specs/dev_scenario_registry.json",
            "specs/validation_policy.json",
            "manifests/public_benchmark_manifest.json",
            "manifests/dev_manifest.json",
            "manifests/pair_public_contract.json",
            "reports/generator_qa.json",
            "reports/oracle_qa.json",
            "reports/dev_dataset_summary.json",
        ):
            self.assertTrue((self.root / path).exists(), path)

    def test_frozen_regimes_and_checkpoint_count(self):
        ranges = {"SHORT": (4, 10), "MEDIUM": (16, 32), "LONG": (48, 96)}
        for config in truth_configs():
            low, high = ranges[config.history_regime]
            self.assertGreaterEqual(len(config.occurrence_plan), low)
            self.assertLessEqual(len(config.occurrence_plan), high)
        self.assertEqual({k: len(v) for k, v in CHECKPOINT_OFFSETS.items()}, {"SHORT": 4, "MEDIUM": 5, "LONG": 7})
        self.assertEqual(self.summary["checkpoints"], 207)
        self.assertEqual(self.summary["evaluation_units"], 207)

    def test_preregister_generate_retain_contract(self):
        registry = json.loads((self.root / "specs" / "dev_scenario_registry.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.root / "manifests" / "dev_manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(registry["registered_before_generation"])
        self.assertEqual(len(registry["histories"]), 38)
        self.assertEqual(manifest["registered_history_count"], 38)
        self.assertEqual(manifest["generated_history_count"], 38)
        self.assertEqual(manifest["retained_history_count"], 38)
        self.assertEqual(manifest["reroll_count"], 0)
        self.assertEqual(len(registry["negative_denominator_unit_ids"]), self.summary["false_promotion_denominator"])
        self.assertTrue(self.summary["qa"]["qa_checks"]["preregistered_before_generation"])
        self.assertTrue(self.summary["qa"]["qa_checks"]["registration_matches_generation"])

    def test_lifecycle_and_evidence_semantics_are_concrete(self):
        self.assertTrue(all(self.summary["qa"]["lifecycle_checks"].values()))
        self.assertTrue(all(self.summary["qa"]["evidence_non_inflation"].values()))
        self.assertTrue(all(self.summary["qa"]["family_evidence"].values()))
        self.assertTrue(all(self.summary["qa"]["e2_gates"].values()))

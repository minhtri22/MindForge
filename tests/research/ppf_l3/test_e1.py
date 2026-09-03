import copy, unittest
from tools.research.ppf_l2_validation import validate_fixture
from tools.research.ppf_l3.e1 import scenarios, generate_case, run_e1, pair_contracts, check_pair
class TestPPFL3E1(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.summary=run_e1(); cls.sm={s.key:s for s in scenarios()}; cls.cases={k:generate_case(s) for k,s in cls.sm.items()}
 def test_g0a(self): self.assertTrue(self.summary['E1-G0A']); self.assertTrue(self.summary['shared_l2_validator']); self.assertFalse(self.summary['reduced_l3_local_validator'])
 def test_g0b(self): self.assertTrue(self.summary['E1-G0B']); self.assertTrue(all(x['pass'] for x in self.summary['pair_reports'].values()))
 def test_e0_regression(self): self.assertEqual(self.summary['e0_regression'],'PASS')
 def test_scale(self): self.assertEqual((self.summary['smoke_persons'],self.summary['smoke_structures'],self.summary['smoke_histories']),(6,10,30)); self.assertGreaterEqual(self.summary['smoke_checkpoints'],100); self.assertLessEqual(self.summary['smoke_checkpoints'],160); self.assertGreaterEqual(self.summary['visible_l2_events'],200); self.assertLessEqual(self.summary['visible_l2_events'],500)
 def test_all_e1_gates(self): self.assertEqual(self.summary['status'],'PASS'); self.assertTrue(all(self.summary['gates'].values()))
 def test_all_events_valid(self): self.assertEqual(self.summary['l2_valid_visible_events'],self.summary['visible_l2_events'])
 def test_mutations(self): self.assertTrue(all(self.summary['mutations'].values()))
 def test_pair_count(self): self.assertGreaterEqual(self.summary['counterfactual_pair_instances'],6)
 def test_preference(self): self.assertTrue(self.summary['preference_availability_distinction'])
 def test_unknown_context(self): self.assertTrue(self.summary['unknown_context_abstention'])
 def test_raw_derived(self): self.assertTrue(self.summary['raw_derived_non_inflation'])
 def test_seed_isolation(self): self.assertTrue(self.summary['multi_structure_seed_isolation'])
 def test_leakage(self): self.assertEqual(self.summary['truth_leak_violations'],0); self.assertEqual(self.summary['checkpoint_future_leak_violations'],0)
 def test_oracle(self): self.assertFalse(self.summary['oracle_generic_threshold_found'])
 def test_undeclared_pair_mutation_fails(self):
  c=pair_contracts()[0]; cases=copy.deepcopy(self.cases); cases[c.b]['behavior'][0]['occurred']=not cases[c.b]['behavior'][0]['occurred']; self.assertFalse(check_pair(c,cases)['pass'])
 def test_schema_valid_semantic_invalid_rejected(self):
  f=copy.deepcopy(self.cases['s1']['fixture']); f['records'][0]['payload']['pattern_confidence']=0.9; self.assertTrue(validate_fixture(f))

import unittest
from datetime import datetime, timezone
from tools.research.ppf_l3.e0 import specs, gen, run_e0, sh, method, prefix, z

class TestPPFL3E0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ss={s[0]:s for s in specs()}; cls.summary=run_e0()
    def test_all_gates(self): self.assertEqual(self.summary['status'],'PASS'); self.assertTrue(all(self.summary['gates'].values()))
    def test_scale(self): self.assertEqual((self.summary['smoke_persons'],self.summary['smoke_structures'],self.summary['counterfactual_pairs']),(6,6,3))
    def test_seed_determinism(self):
        a,b=gen(self.ss['s1']),gen(self.ss['s1']); self.assertEqual(sh(a['eval']),sh(b['eval'])); self.assertEqual(sh(method(a)),sh(method(b)))
    def test_observation_seed_isolation(self):
        a,b=gen(self.ss['s1'],0,0),gen(self.ss['s1'],0,1); self.assertEqual(a['truth'],b['truth']); self.assertEqual(a['opps'],b['opps']); self.assertEqual(a['behavior'],b['behavior']); self.assertNotEqual(sh(method(a)),sh(method(b)))
    def test_behavior_seed_isolation(self):
        a,b=gen(self.ss['s1'],0,0),gen(self.ss['s1'],1,0); self.assertEqual(a['truth'],b['truth']); self.assertEqual(a['opps'],b['opps']); self.assertNotEqual(sh(a['behavior']),sh(b['behavior']))
    def test_l2(self): self.assertEqual(self.summary['l2_valid_visible_events'],self.summary['visible_l2_events'])
    def test_checkpoint(self):
        c=gen(self.ss['s1']); delayed=c['fixture']['records'][3]['event_id']; base=datetime(2026,1,1,8,tzinfo=timezone.utc); self.assertNotIn(delayed,[x['event_id'] for x in prefix(c['fixture']['records'],z(base,65))]); self.assertIn(delayed,[x['event_id'] for x in prefix(c['fixture']['records'],z(base,190))])
    def test_permission_pair(self):
        a,b=gen(self.ss['s3a']),gen(self.ss['s3b']); self.assertEqual(a['truth'],b['truth']); self.assertEqual(a['opps'],b['opps']); self.assertEqual(a['behavior'],b['behavior'])
    def test_replica_pair(self): self.assertEqual(self.summary['replica_pair'],{'occurrences_a':1,'occurrences_b':1,'records_a':1,'records_b':2})
    def test_lifecycle(self): self.assertEqual(self.summary['correction_lifecycle'][-2:],['USER_REJECTED']*2); self.assertEqual(self.summary['deletion_lifecycle'][-2:],['DELETED']*2)
    def test_leakage(self): self.assertEqual(self.summary['truth_leak_violations'],0)
    def test_pairs(self):
        for x in self.summary['pair_isolation'].values(): self.assertTrue(all(x.values()))
    def test_oracle(self): self.assertFalse(self.summary['oracle_boundary']['generic_threshold_patterns_found'])

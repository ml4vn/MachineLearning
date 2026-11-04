import unittest
import numpy as np
from sklearn.metrics import f1_score, roc_auc_score
from .algorithms import measure, auc_pairwise, select_votes

class MetricsTests(unittest.TestCase):
    def test_toy_and_library(self):
        y=[1,0,1,1,0,1,0,0,0,0];s=np.array([.95,.9,.85,.7,.6,.55,.4,.3,.2,.1])
        m=measure(y,s>=.5)
        self.assertEqual([m[k] for k in ['tn','fp','fn','tp']],[4,2,0,4])
        self.assertAlmostEqual(m['f1'],f1_score(y,s>=.5))
        self.assertGreater(measure(y,s>=.85)['precision'],measure(y,s>=.9)['precision'])

    def test_undefined(self):
        self.assertIsNone(measure([0,1],[0,0])['precision'])
        self.assertEqual(measure([0,1],[0,0])['recall'],0)
        self.assertIsNone(measure([0,0],[0,0])['f1'])

    def test_auc_ties(self):
        self.assertEqual(auc_pairwise([1,1,0,0],[.8,.4,.6,.2]),.75)
        self.assertEqual(auc_pairwise([0,1],[.5,.5]),.5)
        self.assertAlmostEqual(auc_pairwise([1,0,1,0],[.1,.1,.9,.7]),roc_auc_score([1,0,1,0],[.1,.1,.9,.7]))

    def test_selection_and_margins(self):
        scan,chosen=select_votes([1,1,0,0],[8,4,5,0])
        for row in scan:
            self.assertEqual(row['tp']+row['fn'],2)
            self.assertEqual(row['tn']+row['fp'],2)
        self.assertTrue(all(a['alerts']>=b['alerts'] for a,b in zip(scan,scan[1:])))
        for key,row in chosen.items(): self.assertEqual(row[key],min(r[key] for r in scan))

    def test_bad_inputs(self):
        for y,p in [([],[]),([2],[1]),([1],[1,0])]:
            with self.assertRaises(ValueError): measure(y,p)
        with self.assertRaises(ValueError): auc_pairwise([1,1],[0,1])
        with self.assertRaises(ValueError): select_votes([0],[.5])

if __name__=='__main__': unittest.main()

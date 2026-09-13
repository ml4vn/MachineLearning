import unittest
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold,GroupShuffleSplit,train_test_split
from sklearn.preprocessing import StandardScaler
from .algorithms import asof_fold,memorize_groups,repeated_selection
from .main import pipeline

class EvaluationTests(unittest.TestCase):
    def test_scaler_exact(self):
        a=StandardScaler().fit([[0],[2]]);b=StandardScaler().fit([[0],[2],[10]])
        self.assertEqual(a.transform([[10]])[0,0],9)
        self.assertAlmostEqual(b.mean_[0],4);self.assertAlmostEqual(b.var_[0],56/3)
        self.assertEqual(np.argmin(abs(a.transform([[0],[2]])-a.transform([[10]]))),np.argmin(abs(b.transform([[0],[2]])-b.transform([[10]]))))

    def test_fold_coverage_and_pipeline(self):
        X=np.arange(0,12,2.)[:,None];y=np.array([0,0,0,1,1,1]);seen=[]
        for tr,va in KFold(3).split(X):
            self.assertFalse(set(tr)&set(va));seen.extend(va)
            p=pipeline().fit(X[tr],y[tr]);self.assertAlmostEqual(p.named_steps['scaler'].mean_[0],X[tr].mean())
        self.assertEqual(sorted(seen),list(range(6)))

    def test_group_split_reference(self):
        rng=np.random.default_rng(73);group=np.repeat(np.arange(200),4);y=rng.permutation(np.repeat([0,1],100))[group]
        tr,va=train_test_split(np.arange(800),test_size=.2,random_state=42);_,a=memorize_groups(group,y,tr,va)
        tr,va=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(group,groups=group));_,b=memorize_groups(group,y,tr,va)
        self.assertEqual(a['shared_groups'],118);self.assertEqual(b['shared_groups'],0)
        self.assertEqual(a['accuracy'],.975);self.assertEqual(b['accuracy'],.425)

    def test_asof_boundary(self):
        d=pd.DataFrame({'order_approved_at':pd.to_datetime(['2017-04-01','2017-04-30','2017-05-01','2017-06-01']),
                        'order_delivered_customer_date':pd.to_datetime(['2017-04-05','2017-05-02','2017-05-10','2017-07-01'])})
        tr,va=asof_fold(d,'2017-01-01','2017-05-01','2017-07-01')
        self.assertEqual(list(tr),[0]);self.assertEqual(list(va),[2])

    def test_multiple_selection(self):
        rows,_=repeated_selection()
        self.assertAlmostEqual(rows[0]['selected_mean'],.49982)
        self.assertAlmostEqual(rows[2]['selected_mean'],.62396)
        self.assertTrue(all(abs(r['fresh_mean']-.5)<.02 for r in rows))

    def test_invalid(self):
        with self.assertRaises(ValueError):memorize_groups([0,0],[0,1],[0],[0])
        with self.assertRaises(ValueError):repeated_selection(repetitions=0)

if __name__=='__main__':unittest.main()

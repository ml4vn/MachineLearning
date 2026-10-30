import unittest
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from .algorithms import gini,enumerate_splits,export_tree,walk,impurity_contributions,toy_data

class TreeTests(unittest.TestCase):
    def test_weighted_gains(self):
        X,y=toy_data();r=max(enumerate_splits(X,y),key=lambda a:a['gain'])
        self.assertEqual((r['feature'],r['threshold']),(1,15))
        self.assertAlmostEqual(r['gain'],.25)
        mask=X[:,1]>15;c=max(enumerate_splits(X[mask],y[mask]),key=lambda a:a['gain'])
        self.assertEqual((c['feature'],c['threshold']),(0,10));self.assertAlmostEqual(c['gain'],.375)
        self.assertAlmostEqual(r['gain']+8/12*c['gain'],.5)

    def test_traversal_and_mdi(self):
        X,y=toy_data();m=DecisionTreeClassifier(random_state=42).fit(X,y);nodes=export_tree(m)
        for x in X:
            leaf,p,_=walk(nodes,x);self.assertEqual(leaf,m.apply([x])[0]);self.assertAlmostEqual(p,m.predict_proba([x])[0,1])
        v=impurity_contributions(nodes,2);np.testing.assert_allclose(v/v.sum(),m.feature_importances_)
        self.assertEqual((m.get_n_leaves(),len(nodes)),(3,5))

    def test_pruning(self):
        X,y=toy_data();m=DecisionTreeClassifier(random_state=42).fit(X,y)
        path=m.cost_complexity_pruning_path(X,y)
        np.testing.assert_allclose(path.ccp_alphas,[0,.25]);np.testing.assert_allclose(path.impurities,[0,.5])
        self.assertEqual(DecisionTreeClassifier(ccp_alpha=.3,random_state=42).fit(X,y).get_n_leaves(),1)

    def test_xor_and_tie(self):
        X=[[0,0],[0,1],[1,0],[1,1]];y=[0,1,1,0]
        self.assertEqual(DecisionTreeClassifier(max_depth=2,min_impurity_decrease=0,random_state=42).fit(X,y).score(X,y),1)
        self.assertEqual(DecisionTreeClassifier(max_depth=2,min_impurity_decrease=.01,random_state=42).fit(X,y).score(X,y),.5)
        m=DecisionTreeClassifier(min_samples_split=3).fit([[0],[1]],[0,1])
        self.assertEqual(m.predict([[.5]])[0],0);self.assertEqual(m.predict_proba([[.5]])[0,1],.5)

    def test_nonlinear_monotone_counterexample(self):
        a=DecisionTreeClassifier().fit([[0],[2]],[0,1]);b=DecisionTreeClassifier().fit([[0],[4]],[0,1])
        self.assertEqual(a.predict([[1.2]])[0],1);self.assertEqual(b.predict([[1.2**2]])[0],0)

    def test_empty_and_constant(self):
        self.assertEqual(enumerate_splits([[2],[2]],[0,1]),[])
        with self.assertRaises(ValueError):gini([])
        with self.assertRaises(ValueError):gini([0,2])
        with self.assertRaises(ValueError):enumerate_splits([[np.nan]],[0])

if __name__=='__main__':unittest.main()

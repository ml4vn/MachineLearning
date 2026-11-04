import unittest
import numpy as np
from sklearn.metrics import log_loss
from .algorithms import sigmoid,logistic_loss_gradient,logistic_gd
from mlcourse.classification import evaluate,select_threshold

class LogisticTests(unittest.TestCase):
    def test_sigmoid_extremes(self):
        with np.errstate(over='raise',invalid='raise'):
            np.testing.assert_allclose(sigmoid([-1000,0,1000]),[0,.5,1])
        self.assertEqual(float(sigmoid(0)),.5)

    def test_first_step_and_gradient(self):
        X=np.column_stack([np.ones(4),[-1,0,1,2]]);y=np.array([0,0,1,1])
        th,h=logistic_gd(X,y,1.,1)
        np.testing.assert_allclose(th,[0,.5]);self.assertAlmostEqual(h[1]['loss'],.48864070910959534,places=12)
        th=np.array([-.2,.7]);_,g=logistic_loss_gradient(X,y,th)
        fd=[(logistic_loss_gradient(X,y,th+e*1e-5)[0]-logistic_loss_gradient(X,y,th-e*1e-5)[0])/2e-5 for e in np.eye(2)]
        np.testing.assert_allclose(g,fd,atol=1e-9)

    def test_stable_bce(self):
        X=np.eye(2);y=[0,1];theta=[-2,3]
        self.assertAlmostEqual(logistic_loss_gradient(X,y,theta)[0],log_loss(y,sigmoid(theta)))
        self.assertEqual(logistic_loss_gradient(X,y,[1000,-1000])[0],1000)

    def test_threshold_keeps_probability_scores(self):
        y=[0,0,1,1];p=[.05,.2,.1,.6]
        a=evaluate(y,p,.5);b=evaluate(y,p,.1)
        self.assertEqual(a['log_loss'],b['log_loss']);self.assertEqual(a['brier'],b['brier'])
        self.assertNotEqual(a['alerts'],b['alerts'])
        scan,best=select_threshold(y,p);self.assertEqual(best['cost'],min(r['cost'] for r in scan))

    def test_grouped_score_and_odds(self):
        x=np.arange(1,5);n=np.array([9,5,3,2]);X=np.column_stack([np.ones(4),x])
        p=sigmoid(X@[-np.log(16),np.log(2)])
        np.testing.assert_allclose(p,1/n);np.testing.assert_allclose(X.T@(n*p-1),[0,0],atol=1e-12)
        self.assertAlmostEqual(2*(.2/.8)/(1+2*(.2/.8)),1/3)

    def test_invalid(self):
        with self.assertRaises(ValueError): logistic_loss_gradient([[1]],[2],[0])
        with self.assertRaises(ValueError): sigmoid(np.nan)
        with self.assertRaises(ValueError): evaluate([0,1],[-.1,.5],.5)

if __name__=='__main__': unittest.main()

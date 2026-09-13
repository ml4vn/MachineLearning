import unittest
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from mlcourse.sms import text_features
from lessons.bai02.algorithms import knn_steps

class KNNTests(unittest.TestCase):
    def test_slide_votes(self):
        X=[[0,0],[2,0],[0,3],[4,4],[1,4]];y=[0,1,1,0,0]
        a=knn_steps(X,y,[1,1],3);b=knn_steps(X,y,[1,1],5)
        np.testing.assert_array_equal(a["d2"],[2,2,5,18,9])
        self.assertEqual(a["prediction"],1);self.assertEqual(b["prediction"],0)
        self.assertFalse(a["boundary_tie"])
    def test_ties_and_zero_weight(self):
        a=knn_steps([[0],[2]],[0,1],[1],2)
        self.assertEqual(a["vote_fraction"],.5);self.assertEqual(a["prediction"],0)
        a=knn_steps([[0],[2],[3]],[1,0,0],[0],3,True)
        self.assertEqual(a["vote_fraction"],1)
    def test_library_away_from_boundary(self):
        X=np.array([[0.,0.],[1.,0.],[3.,1.],[6.,2.]])
        y=np.array([0,1,1,0]);q=[1.2,.5]
        for weighted in [False,True]:
            own=knn_steps(X,y,q,3,weighted)
            lib=KNeighborsClassifier(n_neighbors=3,weights="distance" if weighted else "uniform").fit(X,y)
            self.assertAlmostEqual(own["vote_fraction"],lib.predict_proba([q])[0,1])
    def test_unicode_character_definition(self):
        f=text_features("A 12²!")
        self.assertEqual(f["n_chars"],6);self.assertEqual(f["n_digits"],3)
        self.assertEqual(f["digit_fraction"],.5)
        with self.assertRaises(ValueError):text_features("")
    def test_train_scaler_and_unit_invariance(self):
        X=np.array([[10,.01],[20,.02],[60,.2]])
        np.testing.assert_allclose(StandardScaler().fit_transform(X),StandardScaler().fit_transform(X*[1,100]))
        s=StandardScaler().fit([[0],[2]])
        self.assertEqual(s.transform([[10]])[0,0],9)
    def test_bad_k_and_nan(self):
        for k in [0,3,1.5,True]:
            with self.assertRaises(ValueError):knn_steps([[0],[1]],[0,1],[0],k)
        with self.assertRaises(ValueError):knn_steps([[np.nan]],[0],[0],1)

if __name__=="__main__":unittest.main()

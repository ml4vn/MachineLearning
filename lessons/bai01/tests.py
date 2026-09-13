import unittest
import numpy as np
from lessons.bai01.algorithms import cosine, multi_hot, genre_set

class CosineTests(unittest.TestCase):
    def test_geometry_and_zero_policy(self):
        self.assertEqual(cosine([0,0],[1,0]),None)
        self.assertEqual(cosine([1,0],[-2,0]),-1)
        self.assertAlmostEqual(cosine([1,2],[2,1]),cosine([3,6],[2,1]))
        u=np.array([1.,2.,3.]);v=np.array([3.,1.,2.])
        self.assertAlmostEqual(np.sum((u/np.linalg.norm(u)-v/np.linalg.norm(v))**2),2-2*cosine(u,v))
    def test_reject_invalid(self):
        for u,v in [([],[]),([1],[1,2]),([[1]],[[1]]),([np.nan],[1]),([np.inf],[1])]:
            with self.subTest(u=u),self.assertRaises(ValueError):cosine(u,v)
    def test_large_finite_and_small(self):
        self.assertAlmostEqual(cosine([1e308,1e308],[1,1]),1)
        self.assertAlmostEqual(cosine([1e-300,0],[1,0]),1)
    def test_representation_and_missing(self):
        np.testing.assert_array_equal(multi_hot(genre_set("Drama|Romance"),["Action","Comedy","Sci-Fi"]),[0,0,0])
        self.assertTrue(genre_set("Drama|Romance"))
        self.assertFalse(genre_set("(no genres listed)"))
        with self.assertRaises(ValueError):multi_hot({"A"},["A","A"])
    def test_counterexample_dot_and_cosine(self):
        self.assertGreater(np.dot([1,0],[2,2]),np.dot([1,0],[1,0]))
        self.assertLess(cosine([1,0],[2,2]),cosine([1,0],[1,0]))

if __name__=="__main__":unittest.main()

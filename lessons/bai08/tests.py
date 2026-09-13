import unittest
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_samples, adjusted_rand_score
from .algorithms import POINTS, lloyd, exhaustive_sse, silhouette_manual, prepare_rfm, independent_rfm_check

class KMeansTests(unittest.TestCase):
    def test_half_steps(self):
        h = lloyd(POINTS, POINTS[[0, 2]])
        np.testing.assert_allclose([x["J"] for x in h[:4]], [39, 12, 93/8, 22/3])
        self.assertTrue(np.all(np.diff([x["J"] for x in h]) <= 1e-12))
        np.testing.assert_allclose(h[-1]["centers"], [[2, 5/3], [6, 14/3]])
    def test_global_optima(self):
        best = exhaustive_sse(POINTS)
        self.assertAlmostEqual(best[2], 22/3)
        self.assertAlmostEqual(best[3], 19/6)
        self.assertEqual(best[6], 0)
    def test_silhouette(self):
        X = np.array([[0], [2], [10], [12]])
        s = silhouette_manual(X, [0, 0, 1, 1])
        self.assertAlmostEqual(s[1], 7/9)
        np.testing.assert_allclose(s, silhouette_samples(X, [0, 0, 1, 1]))
    def test_singleton_and_degenerate(self):
        self.assertEqual(silhouette_manual([[0], [2], [10]], [0, 0, 1])[2], 0)
        with self.assertRaises(ValueError): silhouette_manual([[0], [2]], [0, 1])
        with self.assertRaises(ValueError): lloyd(POINTS, [[1, 1], [1, 1]])
    def test_label_permutation(self):
        self.assertEqual(adjusted_rand_score([0, 0, 1, 1], [5, 5, 2, 2]), 1)
    def test_rfm_semantics(self):
        d = pd.DataFrame(dict(CustomerID=[1, 1, 1, 2, None], InvoiceNo=["A", "A", "B", "C9", "D"], Quantity=[1, 2, 1, 1, 1], UnitPrice=[.123, 2, 3, 5, 2], InvoiceDate=pd.to_datetime(["2011-12-09 23:59", "2011-12-09 23:59", "2011-12-08 10:00", "2011-12-09 12:00", "2011-12-09 13:00"])))
        a, f, _ = prepare_rfm(d)
        self.assertEqual(len(a), 3); self.assertEqual(f.recency.iloc[0], 1)
        self.assertEqual(f.frequency.iloc[0], 2)
        self.assertAlmostEqual(f.monetary.iloc[0], 7.123)
        self.assertLess(independent_rfm_check(a, f), 1e-12)

if __name__ == "__main__": unittest.main()

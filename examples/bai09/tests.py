import struct
import unittest
import numpy as np
from sklearn.decomposition import PCA
from mlcourse.fashion import decode_idx, split_indices
from .algorithms import POINTS, fit_pca_eigh, project_reconstruct

class PCATests(unittest.TestCase):
    def test_covariance_and_library(self):
        mu, ev, W = fit_pca_eigh(POINTS)
        np.testing.assert_allclose(mu, [5, 5]); np.testing.assert_allclose(ev, [4.5, .5])
        lib = PCA().fit(POINTS)
        np.testing.assert_allclose(ev * 4 / 3, lib.explained_variance_)
        np.testing.assert_allclose(W[:1].T @ W[:1], lib.components_[:1].T @ lib.components_[:1])
    def test_projection_errors(self):
        mu, ev, W = fit_pca_eigh(POINTS); z, rec = project_reconstruct(POINTS, mu, W, 1)
        np.testing.assert_allclose(rec, [[3.5, 3.5], [3.5, 3.5], [6.5, 6.5], [6.5, 6.5]])
        self.assertAlmostEqual(np.mean((POINTS - rec) ** 2), .25)
        self.assertAlmostEqual(np.mean(np.sum((POINTS - rec) ** 2, axis=1)), ev[1])
    def test_sign_and_all_dimensions(self):
        mu, _, W = fit_pca_eigh(POINTS)
        np.testing.assert_allclose(project_reconstruct(POINTS, mu, W, 1)[1], project_reconstruct(POINTS, mu, -W, 1)[1])
        np.testing.assert_allclose(project_reconstruct(POINTS, mu, W, 2)[1], POINTS)
    def test_variance_not_label(self):
        mu, _, W = fit_pca_eigh(POINTS); z, _ = project_reconstruct(POINTS, mu, W, 1)
        self.assertAlmostEqual(z[0, 0], z[1, 0])
        self.assertNotEqual(int(POINTS[0, 0] > POINTS[0, 1]), int(POINTS[1, 0] > POINTS[1, 1]))
    def test_idx_validation(self):
        b = struct.pack(">II", 2049, 3) + bytes([0, 5, 9])
        np.testing.assert_array_equal(decode_idx(b), [0, 5, 9])
        with self.assertRaises(ValueError): decode_idx(b[:-1])
        with self.assertRaises(ValueError): decode_idx(b"bad")
    def test_split_and_unit_constraint(self):
        y = np.repeat(np.arange(10), 6000); tr, va = split_indices(y)
        self.assertEqual(len(np.intersect1d(tr, va)), 0)
        np.testing.assert_array_equal(np.bincount(y[tr]), [1200] * 10)
        with self.assertRaises(ValueError): project_reconstruct(POINTS, [5, 5], [[2, 0]], 1)

if __name__ == "__main__": unittest.main()

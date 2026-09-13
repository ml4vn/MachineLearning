import unittest
import numpy as np
from sklearn.neural_network import MLPClassifier
from threadpoolctl import threadpool_limits
from .algorithms import XOR, XOR_Y, TINY_THETA, xor_hidden, sigmoid, softmax, bce_logits, ce_logits, finite_gradient, tiny_forward, forward, parameters

class NeuralTests(unittest.TestCase):
    def test_xor_first_step(self):
        H = xor_hidden(XOR); t = np.zeros(3); d = np.full(4, .5) - XOR_Y
        g = np.r_[H.T @ d / 4, d.mean()]
        np.testing.assert_array_equal(g, [0, .125, 0])
        np.testing.assert_allclose(g, finite_gradient(lambda z: bce_logits(H @ z[:2]+z[2], XOR_Y), t), atol=1e-9)
        t -= 8*g; self.assertAlmostEqual(bce_logits(H@t[:2]+t[2], XOR_Y), .5981758073394709)
    def test_constructed_solution(self):
        z = xor_hidden(XOR) @ [2, -4] - 1
        np.testing.assert_array_equal(z >= 0, XOR_Y)
        self.assertGreater(bce_logits(z, XOR_Y), 0)
        self.assertLess(bce_logits(10*z, XOR_Y), bce_logits(z, XOR_Y))
    def test_all_nine_gradients(self):
        result = tiny_forward(TINY_THETA)
        numeric = finite_gradient(lambda t: tiny_forward(t)["loss"], TINY_THETA)
        np.testing.assert_allclose(result["gradient"], numeric, atol=1e-9, rtol=1e-7)
        self.assertAlmostEqual(result["logit"], .204)
        self.assertLess(tiny_forward(TINY_THETA-.1*result["gradient"])["loss"], result["loss"])
    def test_stable_probabilities(self):
        np.testing.assert_allclose(softmax([1000, 1001, 999]), softmax([0, 1, -1]))
        self.assertAlmostEqual(ce_logits(np.zeros((4, 10)), np.array([0, 1, 5, 9])), np.log(10))
        np.testing.assert_allclose(sigmoid([-1000, 1000]), [0, 1])
        self.assertEqual(bce_logits(np.array([1000, -1000]), np.array([0, 1])), 1000)
        with self.assertRaises(ValueError): ce_logits([[1, 2]], np.array([-1]))
    def test_affine_composition(self):
        rng = np.random.RandomState(7); X=rng.randn(5, 3); A=rng.randn(3, 4); B=rng.randn(4, 2); a=rng.randn(4); b=rng.randn(2)
        np.testing.assert_allclose((X@A+a)@B+b, X@(A@B)+(a@B+b))
    def test_library_forward(self):
        with threadpool_limits(limits=2):
            model=MLPClassifier(hidden_layer_sizes=(4,), random_state=42, batch_size=4).partial_fit(XOR, XOR_Y, classes=[0, 1, 2])
            _, _, p = forward(XOR, *parameters(model))
            np.testing.assert_allclose(p, model.predict_proba(XOR), atol=1e-12)
    def test_covariance_condition(self):
        H=xor_hidden(XOR); y=np.array([0, 1, 1, 1]); cov=((H-H.mean(0))*(y-y.mean())[:, None]).mean(0)
        g=H.T@(.5-y)/4
        np.testing.assert_allclose(g, -cov+(.5-y.mean())*H.mean(0))
        self.assertFalse(np.allclose(g, -cov))

if __name__ == "__main__": unittest.main()

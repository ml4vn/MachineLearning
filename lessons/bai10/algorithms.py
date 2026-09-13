"""Forward, loss và backpropagation minh bạch bằng NumPy."""
import numpy as np

XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
XOR_Y = np.array([0, 1, 1, 0])
TINY_THETA = np.array([.5, -.4, .3, .8, .1, .1, .7, -.5, .2])
PARAM_NAMES = ["W11", "W12", "W21", "W22", "b1", "b2", "v1", "v2", "c"]

def sigmoid(z):
    return np.exp(-np.logaddexp(0, -np.asarray(z, dtype=float)))

def bce_logits(logits, y):
    logits, y = np.asarray(logits, float), np.asarray(y)
    if logits.shape != y.shape or logits.size == 0 or not np.isfinite(logits).all() or not np.isin(y, [0, 1]).all():
        raise ValueError("Logit hữu hạn và nhãn nhị phân phải cùng shape, không rỗng.")
    return float(np.mean(np.logaddexp(0, (1 - 2 * y) * logits)))

def softmax(logits):
    logits = np.asarray(logits, float)
    if logits.ndim not in (1, 2) or logits.size == 0 or not np.isfinite(logits).all():
        raise ValueError("Cần vector/ma trận logit hữu hạn, không rỗng.")
    shifted = logits - logits.max(axis=-1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=-1, keepdims=True)

def ce_logits(logits, y):
    logits, y = np.asarray(logits, float), np.asarray(y)
    if logits.ndim != 2 or len(logits) == 0 or y.shape != (len(logits),) or not np.issubdtype(y.dtype, np.integer) or np.any(y < 0) or np.any(y >= logits.shape[1]) or not np.isfinite(logits).all():
        raise ValueError("Nhãn nguyên 0…C−1 phải khớp ma trận logit hữu hạn.")
    return float(np.mean(np.logaddexp.reduce(logits, axis=1) - logits[np.arange(len(y)), y]))

def finite_gradient(fun, theta, eps=1e-6):
    theta = np.asarray(theta, float)
    if theta.ndim != 1 or eps <= 0: raise ValueError("theta là vector và eps > 0.")
    gradient = np.zeros_like(theta)
    for i in range(len(theta)):
        delta = np.zeros_like(theta); delta[i] = eps
        gradient[i] = (fun(theta + delta) - fun(theta - delta)) / (2 * eps)
    return gradient

def xor_hidden(X):
    sums = np.asarray(X, float).sum(axis=1)
    return np.c_[np.maximum(sums, 0), np.maximum(sums - 1, 0)]

def tiny_forward(theta):
    """Một mẫu x=(.6,.2), y=1; W có mỗi hàng là một neuron ẩn."""
    theta = np.asarray(theta, float)
    if theta.shape != (9,) or not np.isfinite(theta).all(): raise ValueError("Mạng nhỏ cần 9 tham số hữu hạn.")
    x = np.array([.6, .2]); W = theta[:4].reshape(2, 2); b = theta[4:6]; v = theta[6:8]; c = theta[8]
    a = W @ x + b; h = np.maximum(a, 0); z = float(v @ h + c); p = float(sigmoid(z))
    delta = p - 1
    hidden_delta = delta * v * (a > 0)  # Quy ước ReLU'(0)=0; finite check tránh điểm gãy.
    gradient = np.r_[np.outer(hidden_delta, x).ravel(), hidden_delta, delta * h, delta]
    return dict(x=x, preactivation=a, hidden=h, logit=z, probability=p, loss=bce_logits(z, np.array(1)), delta=delta, hidden_delta=hidden_delta, gradient=gradient)

def forward(X, W1, b1, W2, b2):
    """Mạng thật theo quy ước hàng = quan sát, giống sklearn."""
    h = np.maximum(np.asarray(X) @ W1 + b1, 0)
    logits = h @ W2 + b2
    return h, logits, softmax(logits)

def parameters(model):
    return [model.coefs_[0], model.intercepts_[0], model.coefs_[1], model.intercepts_[1]]

"""PCA từ ma trận hiệp phương sai; dùng đối chiếu ví dụ nhỏ."""
import numpy as np

POINTS = np.array([[3, 4], [4, 3], [6, 7], [7, 6]], dtype=float)

def fit_pca_eigh(X, ddof=0):
    X = np.asarray(X, float)
    if X.ndim != 2 or len(X) <= ddof or ddof not in (0, 1) or X.shape[1] < 1 or not np.isfinite(X).all():
        raise ValueError("Cần ma trận hữu hạn, n > ddof, ddof=0 hoặc 1.")
    mean = X.mean(axis=0); centered = X - mean
    covariance = centered.T @ centered / (len(X) - ddof)
    eigenvalues, vectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    components = vectors[:, order].T
    # Cố định dấu để đọc dễ; không làm thay đổi không gian chiếu.
    for row in components:
        if row[np.argmax(np.abs(row))] < 0: row *= -1
    return mean, np.maximum(eigenvalues[order], 0), components

def project_reconstruct(X, mean, components, k):
    X, mean, components = np.asarray(X, float), np.asarray(mean, float), np.asarray(components, float)
    if X.ndim != 2 or mean.shape != (X.shape[1],) or components.ndim != 2 or components.shape[1] != X.shape[1] or not 1 <= k <= len(components):
        raise ValueError("Shape hoặc k không hợp lệ.")
    W = components[:k]
    if not np.allclose(W @ W.T, np.eye(k), atol=1e-10): raise ValueError("Các hướng phải trực chuẩn.")
    scores = (X - mean) @ W.T
    return scores, scores @ W + mean

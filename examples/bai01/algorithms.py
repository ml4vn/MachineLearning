"""Phần toán của Bài 1: hàm nhỏ, đọc được và kiểm tra được."""
from __future__ import annotations
import numpy as np

MISSING = "(no genres listed)"

def genre_set(text):
    return set(str(text).split("|")) - {MISSING, ""}

def multi_hot(labels, axes):
    """Một tọa độ cho mỗi nhãn, giữ cùng thứ tự axes cho mọi đối tượng."""
    if not axes or len(axes) != len(set(axes)):
        raise ValueError("Bộ trục phải khác rỗng và không trùng tên")
    return np.array([float(axis in labels) for axis in axes])

def cosine(u, v):
    """Cosine toán học; None nếu ít nhất một vector bằng 0.

    Chia mỗi vector cho phần tử có trị tuyệt đối lớn nhất trước khi chuẩn hóa
    để tránh tràn số khi tính chuẩn của những đầu vào hữu hạn rất lớn.
    Hai phép chia đều dương, nên không làm thay đổi cosine.
    """
    u, v = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
    if u.ndim != 1 or v.ndim != 1 or u.shape != v.shape or u.size == 0:
        raise ValueError("Cần hai vector 1D khác rỗng, cùng số chiều")
    if not np.isfinite(u).all() or not np.isfinite(v).all():
        raise ValueError("Vector không được chứa NaN hoặc vô cực")
    scale_u, scale_v = np.max(np.abs(u)), np.max(np.abs(v))
    if scale_u == 0 or scale_v == 0:
        return None
    u, v = u / scale_u, v / scale_v
    value = (u / np.linalg.norm(u)) @ (v / np.linalg.norm(v))
    # Clip chỉ khử sai số làm tròn ngoài [-1,1], không xử lý vector 0.
    return float(np.clip(value, -1, 1))

def contributions(u, v):
    u, v = np.asarray(u, float), np.asarray(v, float)
    score = cosine(u, v)  # Cũng kiểm đầu vào trước khi nhân.
    return {"products": u*v, "dot": float(u@v),
            "norm_u": float(np.linalg.norm(u)), "norm_v": float(np.linalg.norm(v)),
            "cosine": score}

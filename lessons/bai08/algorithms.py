"""K-means từng nửa bước và kiểm tra độc lập cho RFM."""
from datetime import date
from decimal import Decimal
import numpy as np
import pandas as pd

POINTS = np.array([[1, 1], [2, 1], [3, 3], [5, 4], [6, 5], [7, 5]], dtype=float)
NAMES = ["An", "Bình", "Chi", "Dung", "Hà", "Lan"]
FEATURES = ["recency", "frequency", "monetary"]
SNAPSHOT = pd.Timestamp("2011-12-10")

def lloyd(X, centers, max_iter=100):
    X, centers = np.asarray(X, float), np.asarray(centers, float).copy()
    if X.ndim != 2 or centers.ndim != 2 or X.shape[1] != centers.shape[1]:
        raise ValueError("X và centers phải có cùng số đặc trưng.")
    if not 1 <= len(centers) <= len(X) or not np.isfinite(X).all() or not np.isfinite(centers).all() or max_iter < 1:
        raise ValueError("Dữ liệu hữu hạn, 1 ≤ K ≤ n và max_iter ≥ 1.")
    history = []
    for iteration in range(max_iter):
        d2 = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = d2.argmin(axis=1)  # Nếu hòa khoảng cách: cụm có chỉ số nhỏ nhất.
        history.append(dict(iteration=iteration, phase="assign", centers=centers.copy(), labels=labels.copy(), d2=d2, J=float(d2[np.arange(len(X)), labels].sum())))
        if len(np.unique(labels)) != len(centers):
            raise ValueError("Có cụm rỗng: ví dụ giảng dạy yêu cầu chọn lại khởi tạo.")
        updated = np.array([X[labels == j].mean(axis=0) for j in range(len(centers))])
        history.append(dict(iteration=iteration, phase="update", centers=updated.copy(), labels=labels.copy(), J=float(((X - updated[labels]) ** 2).sum())))
        if np.allclose(updated, centers, atol=1e-12, rtol=0):
            return history
        centers = updated
    raise RuntimeError("Chưa hội tụ trong max_iter.")

def exhaustive_sse(X):
    """Vét cạn phân hoạch tập hợp, chỉ dùng tối đa 9 điểm."""
    X = np.asarray(X, float)
    if X.ndim != 2 or not 1 <= len(X) <= 9 or not np.isfinite(X).all():
        raise ValueError("Chỉ dùng ma trận hữu hạn gồm 1…9 điểm.")
    best = {k: float("inf") for k in range(1, len(X) + 1)}
    def visit(labels):
        if len(labels) == len(X):
            lab = np.array(labels)
            k = max(labels) + 1
            cost = sum(float(((X[lab == j] - X[lab == j].mean(axis=0)) ** 2).sum()) for j in range(k))
            best[k] = min(best[k], cost)
            return
        for label in range(max(labels) + 2): visit(labels + [label])
    visit([0])
    return best

def silhouette_manual(X, labels):
    X, labels = np.asarray(X, float), np.asarray(labels)
    groups = np.unique(labels)
    if X.ndim != 2 or len(labels) != len(X) or not 2 <= len(groups) < len(X):
        raise ValueError("Silhouette cần 2 ≤ số cụm ≤ n−1 và nhãn khớp dữ liệu.")
    if not np.isfinite(X).all(): raise ValueError("Dữ liệu phải hữu hạn.")
    distances = np.linalg.norm(X[:, None] - X[None, :], axis=2)
    values = np.zeros(len(X))
    for i in range(len(X)):
        same = labels == labels[i]
        same[i] = False
        if not same.any(): continue  # Quy ước singleton có s=0.
        a = distances[i, same].mean()
        b = min(distances[i, labels == g].mean() for g in groups if g != labels[i])
        values[i] = (b - a) / max(a, b) if max(a, b) else 0
    return values

def prepare_rfm(d):
    rules = [("Có CustomerID", d.CustomerID.notna()), ("Quantity > 0", d.Quantity > 0),
             ("UnitPrice > 0", d.UnitPrice > 0), ("Không phải hóa đơn C", ~d.InvoiceNo.astype(str).str.lower().str.startswith("c"))]
    mask = pd.Series(True, index=d.index)
    filters = []
    for label, valid in rules:
        before = int(mask.sum()); mask &= valid
        filters.append(dict(rule=label, removed=before - int(mask.sum()), remaining=int(mask.sum())))
    a = d.loc[mask].copy()
    a["CustomerID"] = a.CustomerID.astype("int64")
    a["InvoiceNo"] = a.InvoiceNo.astype(str)
    a["line_value"] = a.Quantity * a.UnitPrice
    f = a.groupby("CustomerID").agg(last_date=("InvoiceDate", "max"), frequency=("InvoiceNo", "nunique"), monetary=("line_value", "sum"), retained_lines=("InvoiceNo", "size"))
    f["recency"] = (SNAPSHOT - f.last_date.dt.normalize()).dt.days
    return a, f.reset_index(), filters

def independent_rfm_check(a, f):
    """Không dùng groupby: ngày Python, set hóa đơn, tiền Decimal."""
    ledger = {}
    for cid, inv, when, qty, price in a[["CustomerID", "InvoiceNo", "InvoiceDate", "Quantity", "UnitPrice"]].itertuples(index=False, name=None):
        entry = ledger.setdefault(cid, [date.min, set(), Decimal(0)])
        entry[0] = max(entry[0], when.date()); entry[1].add(inv)
        entry[2] += Decimal(str(qty)) * Decimal(str(price))
    errors = []
    for row in f.itertuples(index=False):
        last, invoices, money = ledger[row.CustomerID]
        if row.recency != (SNAPSHOT.date() - last).days or row.frequency != len(invoices):
            raise AssertionError("Định nghĩa R/F không khớp kiểm tra độc lập.")
        errors.append(abs(row.monetary - float(money)))
    if max(errors) > 1e-7: raise AssertionError("M không khớp phép tính Decimal.")
    return float(max(errors))

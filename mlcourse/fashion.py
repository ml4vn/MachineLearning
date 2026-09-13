"""Fashion-MNIST: kiểm IDX gốc, tạo đúng tập con có thể truy vết."""
import gzip
import hashlib
import struct
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, log_loss
from threadpoolctl import threadpool_limits
from .data import entries, verify
from .common import require_file

NAMES = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]

def decode_idx(data):
    if len(data) < 8: raise ValueError("IDX thiếu header.")
    magic = struct.unpack(">I", data[:4])[0]; ndim = magic & 255
    if magic >> 8 != 8 or ndim not in (1, 3): raise ValueError("Chỉ hỗ trợ IDX uint8 1D/3D.")
    header = 4 + 4 * ndim
    if len(data) < header: raise ValueError("IDX thiếu kích thước.")
    shape = struct.unpack(">" + "I" * ndim, data[4:header])
    if any(s == 0 for s in shape) or len(data) - header != int(np.prod(shape, dtype=np.int64)):
        raise ValueError("Số byte IDX không khớp kích thước.")
    return np.frombuffer(data, dtype=np.uint8, offset=header).reshape(shape)

def split_indices(y, seed=42):
    tr, rem = train_test_split(np.arange(len(y)), train_size=12000, stratify=y, random_state=seed)
    va, _ = train_test_split(rem, train_size=3000, stratify=y[rem], random_state=seed)
    if np.intersect1d(tr, va).size: raise AssertionError("Train/validation có ID giao nhau.")
    return tr, va

def load_fashion(data_dir, seed=42, include_test=False):
    arrays = []
    for entry in entries("fashion")[:4 if include_test else 2]:
        path = require_file(data_dir, entry["name"]); verify(path, entry["sha256"])
        arrays.append(decode_idx(gzip.decompress(path.read_bytes())))
    x, y = arrays[:2]
    if x.shape != (60000, 28, 28) or y.shape != (60000,) or not np.array_equal(np.bincount(y), [6000] * 10):
        raise ValueError("Nguồn Fashion train không khớp cấu trúc chuẩn.")
    tr, va = split_indices(y, seed)
    result = dict(train=x[tr].reshape(-1, 784).astype(np.float64) / 255,
                  validation=x[va].reshape(-1, 784).astype(np.float64) / 255,
                  y_train=y[tr], y_validation=y[va], train_ids=tr, validation_ids=va)
    blocks = {"train": x[tr], "validation": x[va]}
    if include_test:
        xt, yt = arrays[2:]
        if xt.shape != (10000, 28, 28) or yt.shape != (10000,) or not np.array_equal(np.bincount(yt), [1000] * 10):
            raise ValueError("Nguồn Fashion test không khớp cấu trúc chuẩn.")
        result.update(test=xt.reshape(-1, 784).astype(np.float64) / 255, y_test=yt, test_ids=np.arange(len(yt)))
        blocks["test"] = xt
    hashes = {key: [hashlib.sha256(row.tobytes()).hexdigest() for row in value] for key, value in blocks.items()}
    audit = {f"within_{key}_duplicate_rows": len(vals) - len(set(vals)) for key, vals in hashes.items()}
    keys = list(hashes)
    for i, key in enumerate(keys):
        for other in keys[i + 1:]: audit[f"{key}_{other}_shared_hashes"] = len(set(hashes[key]) & set(hashes[other]))
    result["duplicate_audit"] = audit
    return result

def membership(d):
    frames = []
    for split in ["train", "validation", "test"]:
        if split + "_ids" not in d: continue
        source = "test" if split == "test" else "train"
        frames.append(pd.DataFrame(dict(source_id=[f"{source}:{i}" for i in d[split + "_ids"]], split=split, label=d["y_" + split])))
    return pd.concat(frames, ignore_index=True)

def fit_pixel_baseline(X, y):
    model = LogisticRegression(C=1, solver="newton-cg", max_iter=200)
    with threadpool_limits(limits=2), warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(X, y)
    return model

def classification_report(y, probabilities):
    prediction = np.argmax(probabilities, axis=1)
    return dict(n=len(y), correct=int((prediction == y).sum()), accuracy=accuracy_score(y, prediction), macro_f1=f1_score(y, prediction, average="macro"), cross_entropy=log_loss(y, probabilities, labels=np.arange(10)), confusion=confusion_matrix(y, prediction, labels=np.arange(10)))

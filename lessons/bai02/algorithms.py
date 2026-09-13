"""kNN nhị phân bằng NumPy cho ví dụ nhỏ; dùng để hiểu từng bước."""
import numpy as np

def knn_steps(X, y, query, k=3, weighted=False):
    X=np.asarray(X,float);y=np.asarray(y);query=np.asarray(query,float)
    if X.ndim!=2 or query.ndim!=1 or X.shape[1]!=len(query) or len(X)!=len(y):
        raise ValueError("Kích thước X/y/query không phù hợp")
    if y.ndim!=1 or not np.isin(y,[0,1]).all():
        raise ValueError("Ví dụ này chỉ có nhãn 0/1")
    if not isinstance(k,(int,np.integer)) or isinstance(k,bool) or not 1<=k<=len(X):
        raise ValueError("k phải là số nguyên trong [1,n_train]")
    if not np.isfinite(X).all() or not np.isfinite(query).all():
        raise ValueError("Dữ liệu phải hữu hạn")
    d2=((X-query)**2).sum(axis=1)
    # Hòa khoảng cách: giữ thứ tự đầu vào. Đây là quy tắc của hàm minh họa.
    order=np.argsort(d2,kind="stable");chosen=order[:k]
    weights=np.ones(k)
    if weighted:
        distances=np.sqrt(d2[chosen])
        if np.any(distances==0):
            weights=(distances==0).astype(float)
        else:
            weights=1/distances
    fraction=float(weights@y[chosen]/weights.sum())
    return {"d2":d2,"order":order,"chosen":chosen,"weights":weights,
            "vote_fraction":fraction,"prediction":int(fraction>.5),
            "boundary_tie":bool(k<len(X) and np.isclose(d2[order[k-1]],d2[order[k]]))}

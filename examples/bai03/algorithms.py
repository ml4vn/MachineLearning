"""Các phép đếm minh bạch; None biểu thị tỷ số không xác định."""
import numpy as np

def binary_pair(y, pred):
    y, pred = np.asarray(y), np.asarray(pred)
    if y.ndim != 1 or pred.shape != y.shape or not len(y):
        raise ValueError("Hai vector cùng chiều dài dương")
    if not np.isin(y, [0, 1]).all() or not np.isin(pred, [0, 1]).all():
        raise ValueError("Nhãn phải là 0 hoặc 1")
    return y, pred

def measure(y, pred):
    y, pred = binary_pair(y, pred)
    tn = int(((y == 0) & (pred == 0)).sum())
    fp = int(((y == 0) & (pred == 1)).sum())
    fn = int(((y == 1) & (pred == 0)).sum())
    tp = int(((y == 1) & (pred == 1)).sum())
    def ratio(a, b): return a / b if b else None
    return dict(tn=tn, fp=fp, fn=fn, tp=tp, n=len(y), alerts=tp+fp,
                accuracy=(tp+tn)/len(y), precision=ratio(tp, tp+fp),
                recall=ratio(tp, tp+fn), f1=ratio(2*tp, 2*tp+fp+fn),
                cost_5fp_fn=5*fp+fn, cost_fp_5fn=fp+5*fn)

def auc_pairwise(y, score):
    y, _ = binary_pair(y, y)
    score = np.asarray(score, dtype=float)
    if score.shape != y.shape or not np.isfinite(score).all():
        raise ValueError("Điểm phải hữu hạn và khớp nhãn")
    positive, negative = score[y == 1], score[y == 0]
    if not len(positive) or not len(negative):
        raise ValueError("AUC cần cả hai lớp")
    # Dùng lặp từng dương để không tạo ma trận quá lớn khi dữ liệu tăng.
    wins = sum(np.sum(s > negative) + .5*np.sum(s == negative) for s in positive)
    return float(wins/(len(positive)*len(negative)))

def select_votes(y, votes, k=11):
    votes = np.asarray(votes)
    binary_pair(y, y)
    if votes.shape != np.asarray(y).shape or not np.isin(votes, np.arange(k+1)).all():
        raise ValueError("Phiếu phải là số nguyên từ 0 đến k, cùng số mẫu")
    scan = [dict(min_votes=m, **measure(y, votes >= m)) for m in range(1, k+2)]
    chosen = {key: min(scan, key=lambda r: (r[key], r['alerts'], -r['min_votes']))
              for key in ['cost_5fp_fn', 'cost_fp_5fn']}
    return scan, chosen

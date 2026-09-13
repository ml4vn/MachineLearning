"""Hóa đơn thật → RFM → K-means → đọc và phản biện kết quả."""
from pathlib import Path
import sys
if __package__ in (None, ""): sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from itertools import combinations
from zipfile import ZipFile
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.datasets import make_moons
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from mlcourse.common import parser, setup, figure, save_figure, write_csv, write_json, finish, require_file, COLORS
from mlcourse.data import entries, verify
from lessons.bai08.algorithms import POINTS, NAMES, FEATURES, lloyd, exhaustive_sse, silhouette_manual, prepare_rfm, independent_rfm_check

def toy(args):
    history = lloyd(POINTS, POINTS[[0, 2]])
    best = exhaustive_sse(POINTS)
    starts = []
    for initial in combinations(range(6), 3):
        h = lloyd(POINTS, POINTS[list(initial)])
        starts.append(dict(initial=str(initial), J=h[-1]["J"]))
    write_json(args.output_dir / "toy_lloyd_history.json", history)
    write_csv(args.output_dir / "toy_20_starts.csv", starts)
    fig, axes = figure("K-means: gán cụm rồi cập nhật tâm", ncols=2, nrows=2)
    for ax, state in zip(axes.flat, history[:4]):
        for i, point in enumerate(POINTS):
            ax.scatter(*point, color=COLORS[state["labels"][i]], s=85)
            offset = [.08, -.38] if NAMES[i] == "Dung" else [.08, .12]
            ax.annotate(NAMES[i], point + offset, fontsize=10)
        ax.scatter(*state["centers"].T, marker="X", c="black", s=120)
        phase = "Gán về tâm gần nhất" if state["phase"] == "assign" else "Tâm = trung bình cụm"
        ax.set(title=f"{phase} — SSE = {state['J']:.3f}", xlim=(0, 8), ylim=(0, 6))
        ax.set_aspect("equal"); ax.grid(alpha=.2)
    save_figure(fig, args, "toy_half_steps", r"$J=\sum_i\|x_i-\mu_{c_i}\|^2$: mỗi nửa bước không làm tăng J; X đen là tâm cụm.")
    fig, axes = figure("Nhiều khởi tạo giúp tránh nghiệm địa phương", ncols=2)
    axes[0, 0].plot(range(1, 21), [s["J"] for s in starts], "o", color=COLORS[0])
    axes[0, 0].axhline(best[3], color=COLORS[2], label=f"Tối ưu vét cạn: {best[3]:.3f}")
    axes[0, 0].set(xlabel="Khởi tạo K=3 (20 tổ hợp)", ylabel="SSE sau hội tụ"); axes[0, 0].legend()
    X, y = make_moons(n_samples=180, noise=.06, random_state=8)
    with threadpool_limits(limits=2): km = KMeans(2, n_init=20, random_state=args.seed).fit(X)
    axes[0, 1].scatter(*X.T, c=[COLORS[j] for j in km.labels_], s=35)
    axes[0, 1].set(title="Dữ liệu mô phỏng: hai vành trăng", xlabel="Đặc trưng 1", ylabel="Đặc trưng 2")
    save_figure(fig, args, "toy_limits", "K-means chia theo tâm gần nhất; hình dạng không lồi có thể không phù hợp với giả định này.")
    s = silhouette_manual([[0], [2], [10], [12]], [0, 0, 1, 1])
    return dict(first_four_J=[h["J"] for h in history[:4]], global_optima=best, starts=starts, silhouette=s, silhouette_formula="(b-a)/max(a,b)")

def real(args):
    entry = entries("retail")[0]
    path = require_file(args.data_dir, entry["name"])
    verify(path, entry["sha256"])
    print("Bài 08: đọc hóa đơn XLSX và kiểm RFM bằng Decimal...", flush=True)
    with ZipFile(path) as z:
        member = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
        with z.open(member) as stream: raw = pd.read_excel(stream)
    a, f, filters = prepare_rfm(raw)
    max_money_error = independent_rfm_check(a, f)
    dedup_a, dedup_f, _ = prepare_rfm(raw.drop_duplicates())
    money2 = dedup_f.set_index("CustomerID").monetary.reindex(f.CustomerID).to_numpy()
    changed = ~np.isclose(f.monetary.to_numpy(), money2, atol=1e-8, rtol=0)
    X0 = f[FEATURES].to_numpy(float)
    scaler = StandardScaler().fit(np.log1p(X0)); X = scaler.transform(np.log1p(X0))
    np.testing.assert_allclose(np.expm1(scaler.inverse_transform(X)), X0, rtol=1e-10, atol=1e-9)
    np.testing.assert_allclose(X.mean(axis=0), 0, atol=1e-12)
    sample = np.random.RandomState(args.seed).permutation(len(X))[:2000]
    experiments, models = [], {}
    with threadpool_limits(limits=2):
        for k in range(2, 7):
            model = KMeans(k, n_init=20, random_state=args.seed, algorithm="lloyd").fit(X)
            models[k] = model
            experiments.append(dict(k=k, inertia=model.inertia_, silhouette_sample=silhouette_score(X[sample], model.labels_[sample]), sizes=np.bincount(model.labels_).tolist()))
        raw_model = KMeans(2, n_init=20, random_state=args.seed).fit(X0)
        raw_sil = silhouette_score(X0, raw_model.labels_)
        stability = []
        for seed in range(12):
            m = KMeans(4, n_init=1, random_state=seed).fit(X)
            stability.append(dict(seed=seed, inertia=m.inertia_, ARI=adjusted_rand_score(models[4].labels_, m.labels_)))
    f["cluster_k2"] = models[2].labels_; f["cluster_k4"] = models[4].labels_
    profile = f.groupby("cluster_k4").agg(n=("CustomerID", "size"), R=("recency", "median"), F=("frequency", "median"), M=("monetary", "median")).reset_index()
    example = a.loc[a.CustomerID == args.customer_id].copy()
    if example.empty: raise ValueError("customer-id không có trong tập giao dịch hợp lệ.")
    idx = int(np.flatnonzero(f.CustomerID.to_numpy() == args.customer_id)[0])
    transformed = scaler.transform(np.log1p(f.loc[[idx], FEATURES].to_numpy(float)))
    assigned = int(models[4].predict(transformed)[0])
    distances = ((transformed - models[4].cluster_centers_) ** 2).sum(axis=1)
    if assigned != int(distances.argmin()): raise AssertionError("predict không khớp tâm gần nhất.")
    write_csv(args.output_dir / "rfm_customers.csv", f)
    write_csv(args.output_dir / "raw_customer_invoices.csv", example)
    write_csv(args.output_dir / "filters.csv", filters)
    write_csv(args.output_dir / "k_grid.csv", experiments)
    write_csv(args.output_dir / "cluster_profiles.csv", profile)
    write_csv(args.output_dir / "initialization_stability.csv", stability)
    write_csv(args.output_dir / "silhouette_sample_ids.csv", f.iloc[sample][["CustomerID"]])
    write_csv(args.output_dir / "duplicate_sensitivity.csv", pd.DataFrame(dict(CustomerID=f.CustomerID, M_keep=f.monetary, M_drop=money2, changed=changed)))
    write_json(args.output_dir / "kmeans_model.json", dict(features=FEATURES, transform="log1p then standardize", snapshot="2011-12-10", mean=scaler.mean_, scale=scaler.scale_, centers_k4=models[4].cluster_centers_))
    fig, axes = figure(f"Dữ liệu thật: từ dòng hàng đến khách hàng {args.customer_id}", ncols=2)
    ax = axes[0, 0]; ax.axis("off")
    rows = example[["InvoiceNo", "Quantity", "UnitPrice", "line_value"]].head(8).copy()
    rows["UnitPrice"] = rows.UnitPrice.map(lambda x: f"{x:,.3f}")
    rows["line_value"] = rows.line_value.map(lambda x: f"{x:,.3f}")
    table = ax.table(cellText=rows.values, colLabels=["Hóa đơn", "SL", "Đơn giá £", "Thành tiền £"], loc="center", cellLoc="center")
    table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1.05, 2)
    ax.set_title(f"{len(example)} dòng hợp lệ; hiển thị tối đa 8 dòng")
    row = f.iloc[idx]; ax = axes[0, 1]; ax.axis("off")
    lines = [f"R = {int(row.recency)} ngày lịch", f"F = {int(row.frequency)} hóa đơn khác nhau", f"M = £{row.monetary:,.2f}", f"Cụm K=4: {assigned}", f"Ảnh chụp: 10/12/2011"]
    for i, line in enumerate(lines): ax.text(.04, .84 - i * .16, line, fontsize=19, color=COLORS[i % 3])
    save_figure(fig, args, "real_invoices", "M = tổng Quantity × UnitPrice trên các dòng được giữ; các dòng cùng hóa đơn chỉ đóng góp 1 vào F.")
    fig, axes = figure("Chọn K: nhiều tiêu chí, không có một con số tự quyết định", ncols=2)
    axes[0, 0].plot([r["k"] for r in experiments], [r["inertia"] for r in experiments], "o-", color=COLORS[0]); axes[0, 0].set(xlabel="K", ylabel="SSE trong không gian đã xử lý")
    axes[0, 1].plot([r["k"] for r in experiments], [r["silhouette_sample"] for r in experiments], "o-", color=COLORS[2]); axes[0, 1].set(xlabel="K", ylabel="Silhouette — cùng mẫu 2.000 khách")
    save_figure(fig, args, "real_choose_k", "K=4 được dùng để luyện đọc profile; trên cấu hình này K=2 có silhouette mẫu cao hơn.")
    fig, axes = figure("K=4: đọc profile bằng đơn vị gốc", ncols=3)
    for ax, col, title in zip(axes.flat, ["R", "F", "M"], ["R: trung vị số ngày", "F: trung vị số hóa đơn", "M: trung vị số tiền (£)"]):
        bars = ax.bar(profile.cluster_k4.astype(str), profile[col], color=COLORS[:4]); ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=11)
        ax.set(title=title, xlabel="Mã cụm (không phải thứ hạng)", ylim=(0, float(profile[col].max()) * 1.2))
    save_figure(fig, args, "real_profiles", "Số khách từng cụm: " + "; ".join(f"{r.cluster_k4}: {r.n}" for r in profile.itertuples()) + ". Hành động marketing cần kiểm chứng tiếp.")
    fig, axes = figure("Silhouette cao vẫn cần đọc lại ý nghĩa của dữ liệu", ncols=2)
    ax = axes[0, 0]
    sizes = np.bincount(raw_model.labels_); bars = ax.bar(["Cụm 0", "Cụm 1"], sizes, color=COLORS[:2]); ax.bar_label(bars, padding=5)
    ax.set(title=f"RFM thô: silhouette toàn bộ = {raw_sil:.4f}", ylabel="Số khách", ylim=(0, max(sizes) * 1.15))
    ax = axes[0, 1]; ax.plot([s["seed"] for s in stability], [s["ARI"] for s in stability], "o-", color=COLORS[2]); ax.set(title="K=4: n_init=1 so với nghiệm tham chiếu", xlabel="Seed khởi tạo", ylabel="Adjusted Rand Index", ylim=(0, 1.03))
    save_figure(fig, args, "real_cautions", "Tiền chi phối khoảng cách RFM thô; ARI đo sự đồng thuận của phân hoạch, không phải chất lượng kinh doanh.")
    return dict(raw_rows=len(raw), retained_rows=len(a), customers=len(f), filters=filters, raw_exact_duplicates=int(raw.duplicated().sum()), eligible_duplicates=int(a.drop(columns="line_value").duplicated().sum()), independent_money_max_error=max_money_error, dedup_retained=len(dedup_a), dedup_changed_customers=int(changed.sum()), one_cluster_SSE=float((X ** 2).sum()), experiments=experiments, raw_k2=dict(silhouette_full=raw_sil, sizes=sizes), profile=profile.to_dict("records"), stability=stability, example=dict(customer_id=args.customer_id, R=int(row.recency), F=int(row.frequency), M=float(row.monetary), lines=len(example), cluster=assigned, squared_distances=distances))

def main():
    p = parser(8, __doc__); p.add_argument("--customer-id", type=int, default=12755)
    args = p.parse_args(); setup(args); results = {}
    if args.mode in ("toy", "all"): results["toy"] = toy(args)
    if args.mode in ("real", "all"): results["real"] = real(args)
    finish(args, 8, results)

if __name__ == "__main__": main()

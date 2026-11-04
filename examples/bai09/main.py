"""PCA: phép chiếu, phương sai và tái tạo ảnh Fashion-MNIST."""
from pathlib import Path
import sys
if __package__ in (None, ""): sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from threadpoolctl import threadpool_limits
from mlcourse.common import parser, setup, figure, save_figure, write_csv, write_json, finish, COLORS
from mlcourse.fashion import NAMES, load_fashion, membership, fit_pixel_baseline, classification_report
from examples.bai09.algorithms import POINTS, fit_pca_eigh, project_reconstruct

def toy(args):
    from mlcourse.teaching_visuals import covariance_trace
    covariance_trace(args)
    mu, ev, W = fit_pca_eigh(POINTS)
    scores, rec = project_reconstruct(POINTS, mu, W, 1)
    theta = np.linspace(0, np.pi, 361); directions = np.array([np.cos(theta), np.sin(theta)]).T
    C = (POINTS - mu).T @ (POINTS - mu) / len(POINTS)
    variance = np.einsum("bi,ij,bj->b", directions, C, directions)
    error = np.array([np.mean(np.sum((POINTS - mu - np.outer((POINTS - mu) @ w, w)) ** 2, axis=1)) for w in directions])
    np.testing.assert_allclose(variance + error, 5, atol=1e-12)
    fig, axes = figure("PCA: tìm hướng, chiếu xuống rồi dựng lại", ncols=2)
    ax = axes[0, 0]; ax.plot([2, 8], [2, 8], color=COLORS[2], label="PC1 qua tâm (5,5)")
    for i, (point, rebuilt) in enumerate(zip(POINTS, rec)):
        ax.scatter(*point, color=COLORS[0], s=100); ax.scatter(*rebuilt, marker="X", color=COLORS[1], s=120)
        ax.plot([point[0], rebuilt[0]], [point[1], rebuilt[1]], "--", color=COLORS[3]); ax.annotate("ABCD"[i], point + [.05, .15])
    ax.set(xlabel="x₁", ylabel="x₂", xlim=(2, 8), ylim=(2, 8)); ax.set_aspect("equal"); ax.legend(fontsize=11)
    ax = axes[0, 1]; ax.plot(theta * 180 / np.pi, variance, label="Phương sai giữ lại"); ax.plot(theta * 180 / np.pi, error, label="Sai số bình phương / điểm")
    ax.axvline(45, color=COLORS[2], linestyle=":"); ax.set(xlabel="Góc của hướng đơn vị (độ)", ylabel="Đơn vị bình phương"); ax.legend()
    save_figure(fig, args, "toy_projection", r"$z=(x-\mu)^Tw,\ \hat{x}=\mu+zw,\ \|w\|=1$. Tổng phương sai giữ lại và sai số / điểm luôn bằng 5.")
    # Nhãn do người thiết kế ví dụ gán theo PC2, không phải dữ liệu thật.
    labels = (POINTS[:, 0] > POINTS[:, 1]).astype(int)
    fig, axes = figure("Giữ 90% phương sai vẫn có thể mất thông tin về nhãn", ncols=2)
    for c in [0, 1]:
        sel = labels == c
        axes[0, 0].scatter(*POINTS[sel].T, s=130, color=COLORS[c], label=f"Nhãn {c}")
        axes[0, 1].scatter(scores[sel, 0], np.full(sel.sum(), c), s=130, color=COLORS[c], label=f"Nhãn {c}")
    axes[0, 0].set(xlabel="x₁", ylabel="x₂", title="Nhãn mô phỏng: 1 nếu x₁ > x₂"); axes[0, 0].legend(loc="upper left")
    axes[0, 1].set(xlabel="PC1 score", ylabel="Nhãn (chỉ để tách điểm khi vẽ)", title="A/B và C/D có cùng PC1 score", yticks=[0, 1], ylim=(-.4, 1.4)); axes[0, 1].legend()
    save_figure(fig, args, "toy_label_loss", "Trục dọc bên phải chỉ hiển thị nhãn; nhãn không có trong đầu vào PCA. Một score không phân biệt được hai nhãn.")
    write_csv(args.output_dir / "toy_projection.csv", pd.DataFrame(dict(name=list("ABCD"), x1=POINTS[:, 0], x2=POINTS[:, 1], score=scores[:, 0], reconstructed_x1=rec[:, 0], reconstructed_x2=rec[:, 1], synthetic_label=labels)))
    write_csv(args.output_dir / "toy_all_angles.csv", dict(angle_degrees=theta * 180 / np.pi, retained_variance=variance, point_error=error))
    return dict(mean=mu, eigenvalues_ddof0=ev, components=W, scores=scores, reconstructed=rec, evr=ev / ev.sum(), point_error=float(np.mean(np.sum((POINTS-rec)**2, axis=1))), coordinate_mse=float(np.mean((POINTS-rec)**2)))

def real(args):
    d = load_fashion(args.data_dir, args.seed, include_test=False)
    X, V = d["train"], d["validation"]; yt, yv = d["y_train"], d["y_validation"]
    write_csv(args.output_dir / "split_membership.csv", membership(d))
    print("Bài 09: fit PCA full SVD trên 12.000 ảnh train...", flush=True)
    with threadpool_limits(limits=2):
        pca = PCA(svd_solver="full").fit(X); Z = pca.transform(X); ZV = pca.transform(V)
        np.testing.assert_allclose(pca.components_ @ pca.components_.T, np.eye(784), atol=1e-10)
        np.testing.assert_allclose(pca.mean_, X.mean(axis=0), atol=1e-14)
        np.testing.assert_allclose(ZV, (V-pca.mean_) @ pca.components_.T, atol=1e-12)
        np.testing.assert_allclose(pca.inverse_transform(ZV), V, atol=1e-10)
        cumulative = np.cumsum(pca.explained_variance_ratio_); k90 = int(np.searchsorted(cumulative, .9) + 1)
        positions = [int(np.flatnonzero(yv == c)[0]) for c in range(10)]
        reconstructions, rows = {}, []
        for k in [2, 16, 64, 128]:
            reconstructed = ZV[:, :k] @ pca.components_[:k] + pca.mean_
            train_rec = Z[:, :k] @ pca.components_[:k] + pca.mean_
            train_mse = float(np.mean((X - train_rec) ** 2))
            tail = float(pca.explained_variance_[k:].sum() * (len(X)-1) / len(X) / X.shape[1])
            np.testing.assert_allclose(train_mse, tail, atol=1e-12)
            rows.append(dict(k=k, train_evr=cumulative[k-1], train_mse_pixel=train_mse, validation_mse_pixel=float(np.mean((V-reconstructed)**2)), validation_mse_clipped=float(np.mean((V-np.clip(reconstructed, 0, 1))**2)), outside_display_range=float(np.mean((reconstructed < 0) | (reconstructed > 1)))))
            reconstructions[k] = reconstructed[positions]
    print("Bài 09: fit hai mô hình logistic, chỉ đánh giá validation...", flush=True)
    pixel = fit_pixel_baseline(X, yt); reduced = fit_pixel_baseline(Z[:, :64], yt)
    metrics_pixel = classification_report(yv, pixel.predict_proba(V)); metrics_reduced = classification_report(yv, reduced.predict_proba(ZV[:, :64]))
    np.testing.assert_array_equal(np.argmax(V @ pixel.coef_.T + pixel.intercept_, axis=1), pixel.predict(V))
    np.savez_compressed(args.output_dir / "pca_model.npz", mean=pca.mean_, components=pca.components_, eigenvalues=pca.explained_variance_, evr=pca.explained_variance_ratio_, pixel_coef=pixel.coef_, pixel_intercept=pixel.intercept_, pca64_coef=reduced.coef_, pca64_intercept=reduced.intercept_)
    write_csv(args.output_dir / "reconstruction_metrics.csv", rows)
    write_csv(args.output_dir / "explained_variance.csv", pd.DataFrame(dict(component=np.arange(1, 785), eigenvalue=pca.explained_variance_, EVR=pca.explained_variance_ratio_, cumulative=cumulative)))
    write_csv(args.output_dir / "validation_predictions.csv", pd.DataFrame(dict(source_id=[f"train:{i}" for i in d["validation_ids"]], truth=yv, pixel=pixel.predict(V), pca64=reduced.predict(ZV[:, :64]), PC1=ZV[:, 0], PC2=ZV[:, 1])))
    examples = [dict(source_id=f"train:{int(d['validation_ids'][i])}", validation_position=i, label=int(yv[i]), name=NAMES[yv[i]]) for i in positions]
    write_csv(args.output_dir / "display_examples.csv", examples)
    fig, axes = figure("Fashion-MNIST: mười loại ảnh thật và mã hàng gốc", ncols=5, nrows=2)
    for ax, pos in zip(axes.flat, positions):
        ax.imshow(V[pos].reshape(28, 28), cmap="gray", vmin=0, vmax=1, interpolation="nearest"); ax.axis("off")
        ax.set_title(f"{yv[pos]} · {NAMES[yv[pos]]}\ntrain:{d['validation_ids'][pos]}", fontsize=13)
    save_figure(fig, args, "real_gallery", "Ảnh validation lấy từ tập train chính thức; ID đánh số từ 0. Nguồn: Fashion-MNIST, Zalando Research.")
    pos = positions[0]; pixels = np.rint(V[pos].reshape(28, 28) * 255).astype(int)
    write_csv(args.output_dir / "one_image_pixels.csv", pd.DataFrame(dict(row=np.repeat(np.arange(28), 28), column=np.tile(np.arange(28), 28), flat_index=np.arange(784), uint8=pixels.ravel(), scaled=V[pos])))
    fig, axes = figure("Một ảnh là ma trận số: flatten giữ nguyên đủ 784 pixel", ncols=2)
    axes[0, 0].imshow(pixels, cmap="gray", vmin=0, vmax=255, interpolation="nearest"); axes[0, 0].set(title=f"T-shirt/top · train:{d['validation_ids'][pos]}", xlabel="Cột c", ylabel="Hàng r")
    patch = pixels[10:16, 10:16]; ax = axes[0, 1]; ax.imshow(patch, cmap="gray", vmin=0, vmax=255)
    for r in range(6):
        for c in range(6): ax.text(c, r, str(patch[r, c]), ha="center", va="center", color="black" if patch[r, c] > 130 else "white", fontsize=14)
    ax.set(title="Phóng ô [10:16, 10:16] · giá trị uint8", xticks=range(6), xticklabels=range(10, 16), yticks=range(6), yticklabels=range(10, 16), xlabel="Cột gốc", ylabel="Hàng gốc")
    save_figure(fig, args, "real_pixels", r"$j=28r+c,\ x_j=p_{r,c}/255$. Chia 255 là phép cố định; trừ trung bình train là phép học từ dữ liệu.")
    fig, axes = figure("Cùng ảnh validation: tăng k để khôi phục thêm chi tiết", ncols=5, nrows=4)
    fig.subplots_adjust(hspace=.45)
    for row, c in enumerate([0, 4, 6, 9]):
        for col, k in enumerate([0, 2, 16, 64, 128]):
            ax = axes[row, col]; img = V[positions[c]] if k == 0 else reconstructions[k][c]
            ax.imshow(np.clip(img.reshape(28, 28), 0, 1), cmap="gray", vmin=0, vmax=1, interpolation="nearest"); ax.set_xticks([]); ax.set_yticks([])
            if row == 0: ax.set_title("Gốc" if k == 0 else f"k = {k}")
            if col == 0: ax.set_ylabel(NAMES[c], fontsize=12)
    save_figure(fig, args, "real_reconstruction", "Các ảnh dựng lại được clip về [0,1] chỉ khi vẽ; MSE chính trong báo cáo luôn tính trước clip.")
    fig, axes = figure("Chọn số chiều theo phương sai và sai số tái tạo", ncols=2)
    axes[0, 0].plot(np.arange(1, 785), cumulative, color=COLORS[0]); axes[0, 0].axhline(.9, linestyle=":", color=COLORS[3]); axes[0, 0].axvline(k90, linestyle=":", color=COLORS[2]); axes[0, 0].set(xlabel="Số PC giữ lại", ylabel="EVR cộng dồn trên train", title=f"k nhỏ nhất đạt 90%: {k90}")
    axes[0, 1].plot([r["k"] for r in rows], [r["validation_mse_pixel"] for r in rows], "o-", color=COLORS[2]); axes[0, 1].set(xlabel="k", ylabel="MSE / pixel validation (chưa clip)")
    save_figure(fig, args, "real_variance_error", "Tiêu chí phương sai không sử dụng nhãn; muốn chọn k cho phân loại cần đánh giá mô hình phân loại riêng.")
    fig, axes = figure("Mean là ảnh trung bình; PC là hướng có hệ số âm và dương", ncols=4)
    axes[0, 0].imshow(pca.mean_.reshape(28, 28), cmap="gray", vmin=0, vmax=1); axes[0, 0].set_title("Mean train")
    lim = np.abs(pca.components_[:3]).max()
    for j in range(1, 4):
        axes[0, j].imshow(pca.components_[j-1].reshape(28, 28), cmap="coolwarm", vmin=-lim, vmax=lim); axes[0, j].set_title(f"PC{j}: xanh âm, đỏ dương", fontsize=13)
    for ax in axes.flat: ax.axis("off")
    save_figure(fig, args, "real_basis", "PC không phải ảnh sản phẩm. Dấu của một PC có thể đảo; đảo cả score và hướng vẫn cho cùng ảnh tái tạo.")
    fig, axes = figure("PCA và phân loại: hai mục tiêu cần đo riêng", ncols=2)
    ax = axes[0, 0]; sc = ax.scatter(ZV[:, 0], ZV[:, 1], c=yv, cmap="tab10", vmin=-.5, vmax=9.5, s=10, alpha=.65)
    ax.set(xlabel="PC1", ylabel="PC2", title="Nhãn chỉ tô màu sau khi fit PCA")
    cb = fig.colorbar(sc, ax=ax, ticks=range(10), fraction=.045); cb.set_label("Nhãn gốc (0–9)")
    ax = axes[0, 1]; vals = [metrics_pixel["accuracy"], metrics_reduced["accuracy"]]
    bars = ax.bar(["784 pixel", "64 PC"], vals, color=COLORS[:2]); ax.bar_label(bars, labels=[f"{v:.2%}" for v in vals], padding=5); ax.set(ylim=(0, 1), ylabel="Accuracy trên cùng 3.000 ảnh validation", title="Cùng logistic C=1")
    save_figure(fig, args, "real_classification", "Một split cho thấy mức chênh cụ thể; không đủ kết luận PCA luôn giúp phân loại. Bài 09 không tính metric test.")
    return dict(split=dict(train=len(X), validation=len(V), unused_official_train=45000), duplicate_audit=d["duplicate_audit"], k90=k90, k90_evr=cumulative[k90-1], k90_previous_evr=cumulative[k90-2], reconstruction=rows, baseline_pixel=metrics_pixel, baseline_pca64=metrics_reduced, examples=examples, test_metrics_computed=False)

def main():
    args = parser(9, __doc__).parse_args(); setup(args); result = {}
    if args.mode in ("toy", "all"): result["toy"] = toy(args)
    if args.mode in ("real", "all"): result["real"] = real(args)
    finish(args, 9, result)

if __name__ == "__main__": main()

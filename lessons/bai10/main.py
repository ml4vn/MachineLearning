"""Huấn luyện MLP đầy đủ, chọn checkpoint bằng validation rồi đánh giá test."""
from pathlib import Path
import sys
if __package__ in (None, ""): sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import copy
import time
import warnings
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from threadpoolctl import threadpool_limits
from mlcourse.common import parser, setup, write_csv, write_json, finish
from mlcourse.fashion import NAMES, load_fashion, membership, fit_pixel_baseline, classification_report
from lessons.bai10.algorithms import XOR, XOR_Y, TINY_THETA, PARAM_NAMES, xor_hidden, sigmoid, bce_logits, ce_logits, finite_gradient, tiny_forward, forward, parameters
from lessons.bai10.visuals import plot_toy, plot_real

def score(logits, y):
    from lessons.bai10.algorithms import softmax
    report = classification_report(y, softmax(logits))
    report["cross_entropy"] = ce_logits(logits, y)  # CE trên logits, không clip xác suất.
    report["recall"] = np.diag(report["confusion"]) / np.sum(report["confusion"], axis=1)
    return report

def toy(args):
    H = xor_hidden(XOR); theta = np.zeros(3); delta = np.full(4, .5) - XOR_Y
    gradient = np.r_[H.T @ delta / 4, delta.mean()]; updated = theta - 8 * gradient
    target = np.array([2., -4., -1.]); tiny = tiny_forward(TINY_THETA)
    numeric = finite_gradient(lambda t: tiny_forward(t)["loss"], TINY_THETA)
    np.testing.assert_allclose(tiny["gradient"], numeric, rtol=1e-7, atol=1e-9)
    report = dict(hidden=H, gradient=gradient, next_parameters=updated, next_logits=H@updated[:2]+updated[2], next_probabilities=sigmoid(H@updated[:2]+updated[2]), initial_loss=bce_logits(np.zeros(4), XOR_Y), next_loss=bce_logits(H@updated[:2]+updated[2], XOR_Y), constructed_parameters=target, constructed_logits=H@target[:2]+target[2], constructed_loss=bce_logits(H@target[:2]+target[2], XOR_Y), tiny=tiny, numeric_gradient=numeric, max_gradient_error=float(np.max(np.abs(numeric-tiny["gradient"]))))
    write_csv(args.output_dir / "toy_xor.csv", pd.DataFrame(dict(x1=XOR[:,0], x2=XOR[:,1], y=XOR_Y, h1=H[:,0], h2=H[:,1], next_logit=report["next_logits"], next_probability=report["next_probabilities"], constructed_logit=report["constructed_logits"])))
    write_csv(args.output_dir / "toy_backprop.csv", pd.DataFrame(dict(parameter=PARAM_NAMES, before=TINY_THETA, analytic=tiny["gradient"], finite_difference=numeric, after_GD_eta_0_1=TINY_THETA-.1*tiny["gradient"])))
    write_json(args.output_dir / "toy_details.json", report)
    plot_toy(args, report)
    return report

def real(args):
    d = load_fashion(args.data_dir, args.split_seed, include_test=True)
    X, V = d["train"], d["validation"]; y, yv = d["y_train"], d["y_validation"]
    write_csv(args.output_dir / "split_membership.csv", membership(d))
    protocol = dict(train=len(X), validation=len(V), test=10000, split_seed=args.split_seed, model_seeds=list(range(args.seed,args.seed+args.runs)), primary_seed=args.seed, hidden=64, activation="relu", solver="adam", alpha=.0001, learning_rate=.001, batch_size=256, epochs=args.epochs, updates_per_epoch=int(np.ceil(len(X)/256)), pixels="uint8/255, float64", checkpoint="Minimum validation mean CE; earliest epoch on exact tie", test_status="Public benchmark previously viewed in course pilot")
    write_json(args.output_dir / "protocol_before_fit.json", protocol)
    print("Bài 10: fit lại baseline logistic trên train...", flush=True)
    baseline = fit_pixel_baseline(X, y)
    baseline_val_logits = V @ baseline.coef_.T + baseline.intercept_
    baseval = score(baseline_val_logits, yv)
    history_all, runs, all_warnings = [], [], []
    primary = None; started = time.perf_counter()
    with threadpool_limits(limits=2):
        for seed in protocol["model_seeds"]:
            model = MLPClassifier(hidden_layer_sizes=(64,), activation="relu", solver="adam", alpha=.0001, batch_size=256, learning_rate_init=.001, random_state=seed, shuffle=True, early_stopping=False)
            history, best, best_ce, best_epoch = [], None, float("inf"), None
            for epoch in range(1, args.epochs+1):
                # partial_fit giữ trạng thái Adam qua các epoch; không gọi fit nhiều lần.
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter("always"); model.partial_fit(X, y, classes=np.arange(10))
                all_warnings.extend(str(w.message) for w in captured)
                _, zt, _ = forward(X, *parameters(model)); _, zv, _ = forward(V, *parameters(model))
                val_ce = ce_logits(zv, yv)
                row = dict(seed=seed, epoch=epoch, train_ce=ce_logits(zt,y), validation_ce=val_ce, train_correct=int((zt.argmax(1)==y).sum()), validation_correct=int((zv.argmax(1)==yv).sum()))
                history.append(row); history_all.append(row)
                if val_ce < best_ce: best_ce=val_ce; best_epoch=epoch; best=copy.deepcopy(model)
                if epoch % 10 == 0 or epoch == args.epochs:
                    print(f"Seed {seed}, epoch {epoch}/{args.epochs}: validation CE={val_ce:.6f}", flush=True)
            if best_epoch != 1+int(np.argmin([row["validation_ce"] for row in history])): raise AssertionError("Checkpoint không đúng argmin.")
            _, zv, pv = forward(V, *parameters(best))
            np.testing.assert_allclose(pv, best.predict_proba(V), rtol=1e-10, atol=1e-12)
            count = sum(arr.size for arr in best.coefs_+best.intercepts_)
            if count != 50890: raise AssertionError("Số tham số sai.")
            runs.append(dict(seed=seed, selected_epoch=best_epoch, parameters=count, validation=score(zv, yv)))
            write_csv(args.output_dir / f"history_seed_{seed}.csv", history)
            if seed == args.seed: primary = best
    # Seed chính được định trước; các seed khác chỉ mô tả độ nhạy.
    write_json(args.output_dir / "frozen_before_test.json", dict(protocol=protocol, primary_seed=args.seed, selected_epoch=runs[0]["selected_epoch"], validation_runs=runs, selection_inputs="validation only"))
    W1,b1,W2,b2 = parameters(primary)
    np.savez_compressed(args.output_dir / "mlp_model.npz", W1=W1,b1=b1,W2=W2,b2=b2,baseline_W=baseline.coef_.T,baseline_b=baseline.intercept_,classes=np.arange(10))
    with threadpool_limits(limits=2):
        hval,zval,pval=forward(V,W1,b1,W2,b2)
        _,ztest,ptest=forward(d["test"],W1,b1,W2,b2)
        base_test_logits=d["test"] @ baseline.coef_.T + baseline.intercept_
    mlptest, basetest=score(ztest,d["y_test"]), score(base_test_logits,d["y_test"])
    np.testing.assert_allclose(ptest.sum(1),1,atol=1e-12)
    bpred=baseline_val_logits.argmax(1); pred=zval.argmax(1)
    for split, logits, baseline_logits in [("validation",zval,baseline_val_logits),("test",ztest,base_test_logits)]:
        source="test" if split=="test" else "train"
        write_csv(args.output_dir / f"{split}_predictions.csv", pd.DataFrame(dict(source_id=[f"{source}:{i}" for i in d[split+"_ids"]], truth=d["y_"+split], mlp=logits.argmax(1), baseline=baseline_logits.argmax(1))))
    categories = {"MLP sửa lỗi baseline": np.flatnonzero((bpred!=yv)&(pred==yv))[:3], "Cả hai cùng sai": np.flatnonzero((bpred!=yv)&(pred!=yv))[:3], "MLP sai, baseline đúng": np.flatnonzero((bpred==yv)&(pred!=yv))[:3]}
    examples=[]
    for category, positions in categories.items():
        for pos in positions: examples.append(dict(category=category, validation_position=int(pos), source_id=f"train:{int(d['validation_ids'][pos])}", truth=int(yv[pos]), baseline=int(bpred[pos]), mlp=int(pred[pos]), confidence=float(pval[pos,pred[pos]])))
    write_csv(args.output_dir / "error_examples.csv", examples)
    chosen = int(examples[0]["validation_position"]) if examples else 0
    np.save(args.output_dir / "one_image_uint8.npy", np.rint(V[chosen]*255).astype(np.uint8).reshape(28,28), allow_pickle=False)
    write_csv(args.output_dir / "one_image_probabilities.csv", pd.DataFrame(dict(label=np.arange(10), name=NAMES, logit=zval[chosen], probability=pval[chosen])))
    write_csv(args.output_dir / "one_image_hidden.csv", pd.DataFrame(dict(neuron=np.arange(64), preactivation=V[chosen]@W1+b1, activation=hval[chosen])))
    write_json(args.output_dir / "one_image_source.json", dict(source_id=f"train:{int(d['validation_ids'][chosen])}", truth=int(yv[chosen]), prediction=int(pred[chosen])))
    arrays=dict(W1=W1,b1=b1,W2=W2,b2=b2,validation_logits=zval,validation_baseline_logits=baseline_val_logits,chosen_position=np.array(chosen),history=np.array([[row[k] for k in ["seed","epoch","train_ce","validation_ce","train_correct","validation_correct"]] for row in history_all]))
    np.savez_compressed(args.output_dir / "plot_arrays.npz",**arrays)
    report=dict(protocol=protocol,duplicate_audit=d["duplicate_audit"],baseline_validation=baseval,mlp_runs=runs,baseline_test=basetest,mlp_test=mlptest,test_delta_correct=mlptest["correct"]-basetest["correct"],warnings=all_warnings,elapsed_seconds=time.perf_counter()-started,examples=examples)
    write_json(args.output_dir / "real_details.json", report)
    plot_real(args,d,report,arrays)
    return report

def main():
    p=parser(10,__doc__)
    p.add_argument("--epochs",type=int,default=50)
    p.add_argument("--runs",type=int,default=3,help="Số seed liên tiếp, seed đầu tiên là cấu hình chính")
    p.add_argument("--split-seed",type=int,default=42,help="Giữ 42 để cùng split Bài 09")
    args=p.parse_args()
    if not 1<=args.epochs<=500 or not 1<=args.runs<=10: p.error("epochs trong 1…500; runs trong 1…10.")
    setup(args); report={}
    if args.mode in ("toy","all"): report["toy"]=toy(args)
    if args.mode in ("real","all"): report["real"]=real(args)
    finish(args,10,report)

if __name__=="__main__": main()

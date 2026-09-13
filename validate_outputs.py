"""Kiểm gói kết quả mặc định cả 10 bài so với các mốc đã duyệt trong slide.

Chạy sau run_all.py --mode all, seed 42 và các tùy chọn mặc định.
Không dùng bộ kiểm tham chiếu này để đánh giá cấu hình thí nghiệm khác.
"""
from pathlib import Path
import argparse
import json
import math
import struct

ROOT=Path(__file__).resolve().parent
EXPECTED_PNG=[2,4,5,4,5,7,5,6,8,9]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,default=ROOT/"outputs")
    p.add_argument("--report",type=Path)
    args=p.parse_args(); checks=[]; data={}; allpng=[]
    def check(name,condition):
        checks.append(dict(name=name,passed=bool(condition)))
    for i in range(1,11):
        folder=args.output_dir/f"bai{i:02d}"; path=folder/"results.json"
        if not path.exists(): raise FileNotFoundError(f"Thiếu {path}; chạy đủ --mode all trước.")
        report=json.loads(path.read_text(encoding="utf-8")); data[i]=report["results"]["real"]
        check(f"B{i:02d}: mode all, seed42",report["mode"]=="all" and report["seed"]==42)
        images=list(folder.glob("*.png")); check(f"B{i:02d}: đủ PNG",len(images)==EXPECTED_PNG[i-1])
        for image in images:
            with image.open("rb") as f: header=f.read(24)
            valid=header[:8]==b"\x89PNG\r\n\x1a\n" and struct.unpack(">II",header[16:24])==(3840,2160)
            check(f"B{i:02d}: {image.name} 3840x2160",valid); allpng.append(str(image.relative_to(args.output_dir)))
    r=data
    check("B01: phim và metadata",r[1]["movies"]==9742 and len(r[1]["axes"])==19 and r[1]["candidate_pool"]==9707)
    check("B02: SMS gốc/khử trùng",r[2]["raw_rows"]==5574 and r[2]["deduplicated_rows"]==5159)
    check("B02: F1 test",math.isclose(r[2]["test_f1"],.8844621513944223,abs_tol=1e-10))
    check("B03: confusion cố định",[r[3]["base"][k] for k in ["tn","fp","fn","tp"]]==[892,12,17,111])
    check("B03: AUC",math.isclose(r[3]["roc_auc"],.9690611172566371,abs_tol=1e-10))
    check("B04: OLS hệ số",math.isclose(r[4]["ols_raw_units"]["slope_days_per_km"],.005639148533971937,abs_tol=1e-10))
    check("B04: GD gần OLS",r[4]["gd_matches_ols_at_1e_minus3"])
    check("B05: ngưỡng và chi phí",r[5]["selected_threshold"]==.1 and r[5]["test_selected"]["cost"]==16944)
    check("B06: cây và suy luận thủ công",r[6]["selected_depth"]==6 and r[6]["test_selected"]["cost"]==17359 and r[6]["manual_all_test_matches"])
    check("B07: nhãn tương lai và nhóm lặp",r[7]["approval_before_but_delivery_after_cutoff_raw"]==1490 and r[7]["shared_train_test_customers"]==363)
    check("B08: RFM",r[8]["retained_rows"]==397884 and r[8]["customers"]==4338 and r[8]["dedup_changed_customers"]==951)
    check("B08: K4 SSE",math.isclose(r[8]["experiments"][2]["inertia"],3924.4596992758034,abs_tol=1e-7))
    check("B09: k90 và test chưa dùng",r[9]["k90"]==82 and not r[9]["test_metrics_computed"])
    check("B09: hai baseline validation",r[9]["baseline_pixel"]["correct"]==2500 and r[9]["baseline_pca64"]["correct"]==2511)
    check("B10: đủ 3 seed và checkpoint",[x["selected_epoch"] for x in r[10]["mlp_runs"]]==[40,27,40] and r[10]["protocol"]["epochs"]==50)
    check("B10: test",r[10]["baseline_test"]["correct"]==8277 and r[10]["mlp_test"]["correct"]==8544)
    result=dict(passed=all(c["passed"] for c in checks),check_count=len(checks),png_count=len(allpng),checks=checks)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] else 1)

if __name__=="__main__":main()

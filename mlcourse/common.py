"""Đọc cấu hình, lưu kết quả và vẽ hình; không chứa thuật toán của bài."""
from __future__ import annotations
import argparse
import dataclasses
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Chạy được trên máy cá nhân lẫn GitHub Actions không có màn hình.
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#166A8F", "#E59A35", "#23846D", "#BF5360", "#785BA7"]

def parser(lesson: int, description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--mode", choices=["toy", "real", "all"], default="all",
                   help="toy: ví dụ nhỏ không cần tải; real: dữ liệu thật; all: cả hai")
    p.add_argument("--data-dir", type=Path, default=ROOT / "data" / "raw",
                   help="Thư mục chứa tệp dữ liệu gốc đã tải")
    p.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / f"bai{lesson:02d}")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--dpi", type=int, default=240,
                   help="240 cho hình 16×9 inch = 3840×2160 pixel")
    return p

def setup(args):
    if args.dpi < 50 or args.dpi > 600:
        raise ValueError("--dpi phải nằm trong [50,600]")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 13,
        "axes.titlesize": 17, "axes.labelsize": 13,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": plt.cycler(color=COLORS),
        "figure.facecolor": "#FAFBFD", "axes.facecolor": "#FAFBFD",
        "savefig.facecolor": "#FAFBFD",
    })

def figure(title: str, ncols=1, nrows=1):
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 9), squeeze=False)
    fig.suptitle(title, fontsize=23, weight="bold", x=.06, ha="left", y=.965)
    fig.subplots_adjust(left=.08, right=.95, top=.85, bottom=.16, wspace=.28, hspace=.35)
    return fig, axes

def save_figure(fig, args, name: str, caption: str):
    fig.text(.06, .06, caption, fontsize=11, color="#39495E", va="bottom")
    fig.text(.06, .025, "PGS.TS Nguyễn Văn Hậu · Thực hành học máy",
             fontsize=10, color="#617084")
    path = args.output_dir / f"{name}.png"
    fig.savefig(path, dpi=args.dpi)  # Không dùng bbox_inches='tight': giữ đúng 3840×2160.
    plt.close(fig)
    return path

def json_default(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return value.as_posix()
    if dataclasses.is_dataclass(value): return dataclasses.asdict(value)
    raise TypeError(type(value).__name__)

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=json_default,
                               allow_nan=False), encoding="utf-8")

def write_csv(path, records):
    df = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    df.to_csv(path, index=False, encoding="utf-8-sig")

def finish(args, lesson: int, results):
    from .teaching_visuals import recap
    recap(args, lesson)
    versions = {}
    for name in ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib"]:
        versions[name] = importlib.metadata.version(name)
    report = {"lesson": lesson, "mode": args.mode, "seed": args.seed,
              "python": platform.python_version(), "versions": versions, "results": results}
    write_json(args.output_dir / "results.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=json_default, allow_nan=False))
    print(f"Đã lưu kết quả: {args.output_dir.resolve()}")

def require_file(data_dir, name):
    path = Path(data_dir) / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Thiếu {path}. Xem README của bài hoặc chạy python -m mlcourse.data fetch --help.")
    return path

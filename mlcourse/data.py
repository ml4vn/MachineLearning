"""Tải hoặc nhập dữ liệu gốc, kiểm SHA256 trước khi dùng.

Chỉ đọc các thành viên ZIP được chỉ định trong từng bài; không giải nén tùy ý.
Không tải tự động khi import hay khi chạy chế độ toy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

REGISTRY = Path(__file__).with_name("datasets.json")
DEFAULT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def entries(dataset):
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return registry[dataset]

def verify(path, expected):
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"SHA256 khác snapshot bài giảng: {Path(path).name}. "
                         f"Nhận {actual}; cần {expected}. Không tự dùng dữ liệu đã đổi.")

def fetch(dataset, data_dir=DEFAULT_DIR, source_dir=None):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries(dataset):
        dest = data_dir / entry["name"]
        if dest.exists():
            verify(dest, entry["sha256"])
            print(f"Đã có và đúng SHA256: {dest.name}", flush=True)
            continue
        temp = dest.with_suffix(dest.suffix + ".part")
        try:
            if source_dir:
                shutil.copyfile(Path(source_dir) / entry["name"], temp)
            else:
                print(f"Đang tải {entry['name']} ...", flush=True)
                request = urllib.request.Request(entry["url"], headers={"User-Agent": "ML-teaching-labs/1.0"})
                with urllib.request.urlopen(request, timeout=60) as response, temp.open("wb") as f:
                    # Tránh ghi một phản hồi vô hạn khi endpoint thay đổi.
                    total = 0
                    while block := response.read(1024 * 1024):
                        total += len(block)
                        if total > 200 * 1024 * 1024:
                            raise ValueError("Tệp vượt giới hạn 200 MB; kiểm tra nguồn tải.")
                        f.write(block)
            verify(temp, entry["sha256"])
            temp.replace(dest)
            print(f"Đã kiểm SHA256: {dest.name}", flush=True)
        finally:
            temp.unlink(missing_ok=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fetch", help="Tải đúng snapshot hoặc nhập từ thư mục dữ liệu có sẵn")
    f.add_argument("--dataset", choices=["movielens", "sms", "olist", "retail", "fashion", "all"], required=True)
    f.add_argument("--data-dir", type=Path, default=DEFAULT_DIR)
    f.add_argument("--source-dir", type=Path, help="Nhập dữ liệu có sẵn, vẫn kiểm SHA256")
    args = p.parse_args()
    names = list(json.loads(REGISTRY.read_text(encoding="utf-8"))) if args.dataset == "all" else [args.dataset]
    for name in names: fetch(name, args.data_dir, args.source_dir)

if __name__ == "__main__": main()

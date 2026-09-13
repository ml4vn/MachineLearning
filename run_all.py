"""Chạy các bài tuần tự; dừng và báo mã lỗi nếu một bài thất bại."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import time
import json

ROOT = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["toy", "real", "all"], default="toy")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=10)
    p.add_argument("--data-dir", type=Path, default=ROOT / "data/raw")
    p.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--dpi", type=int, default=240)
    args = p.parse_args()
    if not 1 <= args.start <= args.end <= 10: p.error("Cần 1 ≤ start ≤ end ≤ 10.")
    if not 50 <= args.dpi <= 600: p.error("dpi phải trong [50,600].")
    args.output_dir = args.output_dir.resolve(); args.data_dir = args.data_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy(); env["PYTHONUTF8"] = "1"
    runs = []
    for lesson in range(args.start, args.end + 1):
        name = f"bai{lesson:02d}"; dest = args.output_dir / name; dest.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-X", "utf8", "-m", f"lessons.{name}.main", "--mode", args.mode,
                   "--data-dir", str(args.data_dir), "--output-dir", str(dest), "--seed", str(args.seed), "--dpi", str(args.dpi)]
        if lesson == 10: command.extend(["--split-seed", str(args.seed)])
        print(f"Bắt đầu {name}: {args.mode}. Log: {dest / 'run.log'}", flush=True)
        start = time.perf_counter()
        with (dest / "run.log").open("w", encoding="utf-8") as log:
            run = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        runs.append(dict(lesson=lesson, exit_code=run.returncode, seconds=round(time.perf_counter()-start, 2)))
        (args.output_dir / "run_summary.json").write_text(json.dumps(dict(mode=args.mode, seed=args.seed, runs=runs), indent=2), encoding="utf-8")
        if run.returncode:
            print((dest / "run.log").read_text(encoding="utf-8")[-6000:]); raise SystemExit(run.returncode)
        print(f"Hoàn tất {name} ({runs[-1]['seconds']:.1f} giây)", flush=True)

if __name__ == "__main__": main()

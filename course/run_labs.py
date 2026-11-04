"""Execute the  notebooks sequentially in the current Python environment."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = (1, 2, 3, 4, 5, 6, 8, 9, 10)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, choices=LESSONS, action="append",
                        help="Repeat to select lessons; default is all nine in order.")
    parser.add_argument("--audit-only", action="store_true",
                        help="Check saved scientific evidence without refitting notebooks.")
    parser.add_argument("--timeout", type=int, default=3600,
                        help="Maximum seconds for each notebook cell or audit subprocess.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    selected = sorted(set(args.lesson or LESSONS))
    output = ROOT / "outputs/"
    output.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
    os.environ.setdefault("MKL_NUM_THREADS", "2")
    os.environ.setdefault("MPLCONFIGDIR", str(output / "matplotlib"))
    os.environ.setdefault("PYTHONUTF8", "1")
    summary = {"mode": "audit-only" if args.audit_only else "notebook-and-audit",
               "python": sys.version.split()[0], "examples": []}
    for n in selected:
        folder = ROOT / "course" / f"bai{n:02d}"
        print(f"START Bai {n:02d}", flush=True)
        start = time.monotonic()
        record = {"lesson": n}
        try:
            if not args.audit_only:
                import nbformat
                from nbclient import NotebookClient

                notebook, = folder.glob("*.ipynb")
                nb = nbformat.read(notebook, as_version=4)
                for cell in nb.cells:
                    if cell.cell_type == "code":
                        cell.outputs = []
                        cell.execution_count = None
                client = NotebookClient(nb, timeout=args.timeout, kernel_name="python3",
                                        resources={"metadata": {"path": str(folder)}})
                # Use this venv, even if a different Python kernel is registered globally.
                client.create_kernel_manager()
                client.km.kernel_spec.argv[0] = sys.executable
                client.execute()
                target = output / notebook.name
                nbformat.write(nb, target)
                record["executed_notebook"] = target.relative_to(ROOT).as_posix()
                record["executed_code_cells"] = sum(c.cell_type == "code" for c in nb.cells)
            audit = folder / "source/science_audit.py"
            if audit.exists():
                completed = subprocess.run([sys.executable, str(audit)], cwd=folder,
                                           capture_output=True, text=True, encoding="utf-8",
                                           timeout=args.timeout, check=False)
                (output / f"bai{n:02d}_science_audit.log").write_text(
                    completed.stdout + completed.stderr, encoding="utf-8")
                if completed.returncode:
                    raise RuntimeError(f"Science audit failed; see outputs/bai{n:02d}_science_audit.log")
                record["independent_science_audit"] = "pass"
            else:
                record["independent_science_audit"] = "No separate audit script; checks are in the notebook/lab."
            record["status"] = "pass"
        except Exception as exc:
            record.update(status="fail", error=str(exc))
            record["seconds"] = round(time.monotonic() - start, 2)
            summary["examples"].append(record)
            (output / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            raise
        record["seconds"] = round(time.monotonic() - start, 2)
        summary["examples"].append(record)
        (output / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PASS Bai {n:02d} ({record['seconds']} seconds)", flush=True)
    print(f"PASS {len(selected)} lessons; outputs/run_summary.json", flush=True)


if __name__ == "__main__":
    main()

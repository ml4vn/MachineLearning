"""Kiểm đủ học liệu, checksum bản gốc và liên kết nội bộ trước khi đăng GitHub."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_readings import render_reading


def main() -> None:
    manifest = json.loads((ROOT / "docs/reading_manifest.json").read_text(encoding="utf-8"))
    errors = []
    copied_count = 0
    counts = {"table": 0, "figure": 0, "equation": 0, "question": 0}
    for item in manifest["lessons"]:
        number = item["lesson"]
        folder = ROOT / "readings" / f"bai{number:02d}"
        content = json.loads((folder / "content.json").read_text(encoding="utf-8"))
        if len(content["pages"]) != item["pdf_pages"] or content["lesson"] != number:
            errors.append(f"Bài {number}: số mục/trang không khớp manifest")
        if (folder / "README.md").read_text(encoding="utf-8") != render_reading(content):
            errors.append(f"Bài {number}: Markdown chưa đồng bộ content.json")
        for page in content["pages"]:
            for block in page["blocks"]:
                if block["type"] in counts:
                    counts[block["type"]] += 1
        for file in item["files"]:
            path = ROOT / file["path"]
            copied_count += 1
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != file["sha256"]:
                errors.append(f"Bản nguồn đã đổi: {file['path']}")
        for name in ["README.md", "main.py", "algorithms.py", "tests.py", "PLAN.md", "VALIDATION.md"]:
            if not (ROOT / "lessons" / f"bai{number:02d}" / name).is_file():
                errors.append(f"Thiếu Python Bài {number}: {name}")
    assert len(manifest["lessons"]) == 10
    markdowns = [ROOT / "README.md"]
    for parent in ["readings", "lessons", "docs"]:
        markdowns += list((ROOT / parent).rglob("*.md"))
    links = 0
    for path in markdowns:
        source = path.read_text(encoding="utf-8-sig")
        source = re.sub(r"```[^\n]*\n.*?```", "", source, flags=re.S)
        for target in re.findall(r"\]\(([^\n)]+)\)", source):
            target = target.strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            filename, _, anchor = target.partition("#")
            if re.match(r"[A-Za-z]:[\\/]", filename):
                errors.append(f"Liên kết chỉ dùng được trên máy biên soạn: {path.relative_to(ROOT)} → {filename}")
                continue
            linked = (path.parent / unquote(filename)).resolve() if filename else path
            links += 1
            if not linked.exists():
                errors.append(f"Liên kết thiếu: {path.relative_to(ROOT)} → {target}")
            elif anchor.startswith("muc-") and f'id="{anchor}"' not in linked.read_text(encoding="utf-8"):
                errors.append(f"Mục lục thiếu: {path.relative_to(ROOT)} → {target}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(json.dumps({"passed": True, "lessons": 10, "pdf_pages": sum(x["pdf_pages"] for x in manifest["lessons"]), "verified_files": copied_count, "local_links_checked": links, "content_blocks": counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

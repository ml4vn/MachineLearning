"""Tạo Markdown đọc trên GitHub từ content.json, không cần thư viện ngoài."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "PGS.TS. Nguyễn Văn Hậu"
AFFILIATION = "Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Kỹ thuật Hưng Yên"


def cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\r\n", "<br>").replace("\n", "<br>")


def label(value: str) -> str:
    return value.replace("[", r"\[").replace("]", r"\]")


def render_block(block: dict) -> str:
    kind = block["type"]
    if kind == "p":
        return block["text"]
    if kind == "h":
        return "### " + block["text"]
    if kind == "list":
        return "\n".join("- " + item for item in block["items"])
    if kind == "cue":
        icon = {"try": "✏️", "remember": "📌", "observe": "🔎", "warning": "⚠️"}.get(block.get("kind"), "💡")
        return "> " + icon + " " + block["text"].replace("\n", "\n> ")
    if kind == "figure":
        return f'![{label(block["caption"])}](assets/{block["name"]}.png)\n\n*{block["caption"]}*'
    if kind == "equation":
        return "```math\n" + block["tex"] + "\n```\n\n" + block["meaning"]
    if kind == "table":
        columns = len(block["head"])
        assert all(len(row) == columns for row in block["rows"]), "Bảng không đều cột"
        rows = ["| " + " | ".join(cell(v) for v in block["head"]) + " |", "| " + " | ".join(["---"] * columns) + " |"]
        rows.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in block["rows"])
        return "\n".join(rows)
    if kind == "question":
        result = f'**Câu {block["number"]}.** {block["text"]}'
        if block.get("options"):
            result += "\n\n" + "\n".join(f'- **{chr(65+i)}.** {value}' for i, value in enumerate(block["options"]))
        return result
    if kind == "link":
        return f'[{label(block["label"])}]({block["url"]})'
    raise ValueError(f"Loại nội dung chưa được xử lý: {kind}")


def render_reading(content: dict) -> str:
    lesson = content["lesson"]
    version = content.get("reading_version", "v2")
    slide_version = content.get("slide_version", "v2")
    pages = len(content["pages"])
    prefix = f"Bai{lesson:02d}_Kien_thuc_nen_tang_va_doc_truoc"
    parts = [f'# Bài {lesson:02d} · {content["title"]}', f"**{AUTHOR}**\n\n{AFFILIATION}",
             f"[← Mục lục khóa học](../../README.md) · [📄 PDF {pages} trang]({prefix}.pdf) · [📝 Word]({prefix}.docx) · [💻 Thực hành Python](../../lessons/bai{lesson:02d}/README.md)",
             f"**Tài liệu đọc trước {version} · Đối chiếu slide {slide_version}.** Python đã đồng bộ ví dụ và hướng dẫn theo cùng nguồn slide; xem [các quy ước đối chiếu](../../docs/DOI_CHIEU_HOC_LIEU.md).",
             "Đọc mục 1–8, tự làm mục 9 trước khi xem phụ lục A, dùng mục 10 để ôn tập. Phụ lục B dành cho người muốn tìm hiểu sâu hơn.",
             "## Mục lục", "\n".join(f'- [{p["title"]}](#muc-{i})' for i, p in enumerate(content["pages"], 1))]
    for i, page in enumerate(content["pages"], 1):
        parts.extend([f'<a id="muc-{i}"></a>', "## " + page["title"]])
        parts.extend(render_block(block) for block in page["blocks"])
    parts += ["## Chuyển sang thực hành", f"Mở [hướng dẫn Python Bài {lesson:02d}](../../lessons/bai{lesson:02d}/README.md), chạy ví dụ nhỏ trước rồi mới chạy dữ liệu thật. Các bảng CSV và JSON trong thư mục đọc trước lưu kết quả tham chiếu của lần biên soạn; chương trình thực hành tự tính lại và lưu kết quả mới trong `outputs/`.",
              "[Nguồn dữ liệu và điều kiện sử dụng](../../docs/DU_LIEU_VA_NGUON.md) · [Ghi chú đối chiếu tài liệu với mã](../../docs/DOI_CHIEU_HOC_LIEU.md)"]
    return "\n\n".join(parts).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Chỉ kiểm Markdown hiện tại, không ghi tệp")
    args = parser.parse_args()
    for lesson in range(1, 11):
        folder = ROOT / "readings" / f"bai{lesson:02d}"
        content = json.loads((folder / "content.json").read_text(encoding="utf-8"))
        expected = render_reading(content)
        path = folder / "README.md"
        if args.check:
            if path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Cần cập nhật {path.relative_to(ROOT)}")
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
        print(f"Bài {lesson:02d}: đủ {len(content['pages'])} mục/phụ lục")


if __name__ == "__main__":
    main()

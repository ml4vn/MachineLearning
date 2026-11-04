"""Render the complete local  prereading HTML as GitHub Markdown."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
LESSONS = (1, 2, 3, 4, 5, 6, 8, 9, 10)


def svg_assets(source: Path, check: bool = False) -> None:
    """Keep the actual vector diagrams instead of flattening their labels."""
    document = source.read_text(encoding="utf-8")
    figures = re.findall(r"<svg\b[\s\S]*?</svg>", document, flags=re.IGNORECASE)
    styles = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", document, flags=re.IGNORECASE))
    for i, svg in enumerate(figures, 1):
        if "xmlns=" not in svg.split(">", 1)[0]:
            svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        pos = svg.index(">") + 1
        svg = svg[:pos] + "<style><![CDATA[" + styles + "]]></style>" + svg[pos:]
        target = source.parent.parent / "reading_figures" / f"inline_{i:02d}.svg"
        if check:
            assert target.read_text(encoding="utf-8") == svg, f"Stale diagram: {target}"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8")


def render(source: Path) -> str:
    lesson = source.parent.parent
    tree = html.fromstring(source.read_text(encoding="utf-8"))
    svg_numbers = {svg: i for i, svg in enumerate(tree.xpath('//*[local-name()="svg"]'), 1)}

    def link(value: str) -> str:
        if value.startswith("#") or urlsplit(value).scheme:
            return value
        file, mark, anchor = value.partition("#")
        relative = (source.parent / file).resolve().relative_to(lesson.resolve())
        return quote(relative.as_posix(), safe="/") + (mark + anchor if mark else "")

    def text(value: str | None) -> str:
        return re.sub(r"\s+", " ", value or "")

    def children(node) -> str:
        return text(node.text) + "".join(node_text(c) + text(c.tail) for c in node)

    def node_text(node) -> str:
        tag = node.tag if isinstance(node.tag, str) else ""
        if tag in {"head", "script", "style", "nav"}:
            return ""
        if tag == "svg":
            return f"\n\n![Sơ đồ trực quan {svg_numbers[node]}](reading_figures/inline_{svg_numbers[node]:02d}.svg)\n\n"
        tex = node.get("data-tex")
        if tex is not None:
            display = any(set(p.get("class", "").split()) & {"equation", "eq", "formula", "math"}
                          for p in [node, *node.iterancestors()])
            if any(p.tag in {"td", "th"} for p in node.iterancestors()):
                display = False
            return "\n\n```math\n" + tex + "\n```\n\n" if display else "$" + tex + "$"
        if tag == "img":
            alt = text(node.get("alt", "Hình minh họa")).replace("[", "\\[").replace("]", "\\]")
            return "\n\n![" + alt + "](" + link(node.get("src", "")) + ")\n\n"
        if tag == "br":
            return "<br>"
        if tag in {"strong", "b"}:
            return "**" + children(node).strip() + "**"
        if tag in {"em", "i"}:
            return "*" + children(node).strip() + "*"
        if tag in {"sup", "sub"}:
            return f"<{tag}>" + children(node).strip() + f"</{tag}>"
        if tag == "code" and node.getparent().tag != "pre":
            return "`" + node.text_content() + "`"
        if tag == "pre":
            return "\n\n```text\n" + node.text_content().strip() + "\n```\n\n"
        if tag == "a":
            value = children(node).strip()
            return "[" + value + "](" + link(node.get("href", "")) + ")" if node.get("href") else value
        if tag == "table":
            rows = []
            for row in node.xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr"):
                cells = []
                for cell in row.xpath("./th|./td"):
                    value = children(cell).strip().replace("\n", " ").replace("|", "\\|")
                    cells.extend([value] + [""] * (int(cell.get("colspan", "1")) - 1))
                if cells:
                    rows.append(cells)
            if not rows:
                return ""
            width = max(map(len, rows))
            rows = [r + [""] * (width - len(r)) for r in rows]
            lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * width) + " |"]
            lines.extend("| " + " | ".join(r) + " |" for r in rows[1:])
            return "\n\n" + "\n".join(lines) + "\n\n"
        if tag in {"ul", "ol"}:
            lines = []
            for i, item in enumerate(node.xpath("./li"), 1):
                prefix = f"{i}. " if tag == "ol" else "- "
                value = children(item).strip().replace("\n", "\n  ")
                lines.append(prefix + value)
            return "\n\n" + "\n".join(lines) + "\n\n"
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            return "\n\n" + "#" * int(tag[1]) + " " + children(node).strip() + "\n\n"
        if tag == "figcaption":
            return "\n\n*" + children(node).strip() + "*\n\n"
        if tag == "summary":
            return "\n\n**" + children(node).strip() + "**\n\n"
        value = children(node)
        if tag in {"section", "div", "p", "figure", "article", "header", "footer", "details"}:
            anchor = '<a id="' + node.get("id") + '"></a>\n\n' if node.get("id") else ""
            return "\n\n" + anchor + value.strip() + "\n\n"
        return value

    body = tree.find("body")
    result = node_text(body if body is not None else tree)
    result = re.sub(r"\n[ \t]+\n", "\n\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    original = source.relative_to(lesson).as_posix()
    notice = (
        "> Bản đọc trực tiếp trên GitHub, chuyển từ đầy đủ tài liệu HTML . "
        f"[Tải bản HTML có bố cục và công thức LaTeX]({original}); "
        "mở bản HTML sau khi tải và giải nén toàn bộ repository. "
        "[Hướng dẫn bài thực hành và slide](README.md).\n\n"
    )
    return notice + result + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for n in LESSONS:
        lesson = ROOT / "course" / f"bai{n:02d}"
        source, = (lesson / "Tai_lieu_doc_truoc").glob("*.html")
        svg_assets(source, args.check)
        target = lesson / "READING.md"
        result = render(source)
        if args.check:
            assert target.read_text(encoding="utf-8") == result, f"Stale reading: {target}"
        else:
            target.write_text(result, encoding="utf-8")
        print(f"Bai {n:02d}: Markdown {'checked' if args.check else 'written'}")


if __name__ == "__main__":
    main()

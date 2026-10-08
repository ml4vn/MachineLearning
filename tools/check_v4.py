"""Check release scope, resource links, formulas, notebooks and original slides."""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from lxml import html

from build_v4_readings import LESSONS, render

ROOT = Path(__file__).resolve().parents[1]


def check_link(page: Path, ref: str) -> None:
    if not ref or ref.startswith(("#", "data:", "mailto:")) or urlsplit(ref).scheme:
        return
    name = unquote(ref.split("#")[0].split("?")[0])
    if name:
        assert (page.parent / name).is_file(), f"Missing resource {ref} in {page.relative_to(ROOT)}"


def main() -> None:
    manifest = json.loads((ROOT / "v4/source_manifest.json").read_text(encoding="utf-8"))
    assert manifest["lessons"] == list(LESSONS)
    assert not (ROOT / "v4/bai07").exists(), "Bai 7 is excluded from this release"
    # Published inputs and instructional files are immutable. Data/result products
    # can legitimately change when a student reruns the notebook.
    immutable_count = 0
    for filename, metadata in manifest["files"].items():
        path = ROOT / filename
        assert path.is_file(), filename
        mutable = "/results/" in filename or (
            "/data/" in filename and path.suffix.lower() in {".csv", ".npz", ".json"})
        if not mutable:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == metadata["published_sha256"], filename
            immutable_count += 1
        assert path.stat().st_size < 50 * 1024 * 1024, filename
    totals = dict(lessons=0, tables=0, formulas=0, figures=0, slides=0, notes=0, code_cells=0)
    for n in LESSONS:
        folder = ROOT / "v4" / f"bai{n:02d}"
        source, = (folder / "Tai_lieu_doc_truoc").glob("*.html")
        tree = html.fromstring(source.read_text(encoding="utf-8"))
        reading = (folder / "READING.md").read_text(encoding="utf-8")
        assert reading == render(source), f"Stale Markdown for Bai {n}"
        equations = tree.xpath('//*[@data-tex]/@data-tex')
        for equation in equations:
            assert equation in reading or equation.replace("|", r"\|") in reading, f"Missing formula: {equation}"
        totals["tables"] += len(tree.xpath("//table"))
        totals["formulas"] += len(equations)
        totals["figures"] += len(tree.xpath("//img|//svg"))
        assert len(tree.xpath('//h2')) >= 10, f"Incomplete prereading: {n}"
        notebook, = folder.glob("*.ipynb")
        nb = json.loads(notebook.read_text(encoding="utf-8"))
        assert all(c.get("id") for c in nb["cells"]), f"Missing notebook cell IDs: {n}"
        assert len({c["id"] for c in nb["cells"]}) == len(nb["cells"])
        cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        assert len(cells) == {1: 6, 2: 7, 3: 8}.get(n, 10), f"Missing code cells: Bai {n}"
        assert not any(output.get("output_type") == "error" for c in cells for output in c.get("outputs", []))
        for p in (folder / "source").glob("*.py"):
            compile(p.read_text(encoding="utf-8"), str(p), "exec")
        totals["code_cells"] += len(cells)
        pptx, = (folder / "PowerPoint").glob("*.pptx")
        with ZipFile(pptx) as z:
            slides = [name for name in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
            notes = [name for name in z.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)]
            plan = json.loads((folder / "source/slide_manifest.json").read_text(encoding="utf-8"))
            assert len(slides) == len(notes) == len(plan), f"Slide/notes count mismatch: Bai {n}"
            # Notes must contain explanation rather than only the slide number placeholder.
            for note in notes:
                xml = ET.fromstring(z.read(note))
                words = " ".join(xml.itertext()).strip()
                assert len(words) > 60, f"Empty explanation: {note}"
            totals["slides"] += len(slides)
            totals["notes"] += len(notes)
        for page in folder.rglob("*.html"):
            if "/source/assets/" in page.as_posix():
                # Vendor development demos are not course navigation pages.
                continue
            dom = html.fromstring(page.read_text(encoding="utf-8"))
            for ref in dom.xpath("//@href|//@src"):
                check_link(page, ref)
        totals["lessons"] += 1
    for page in list((ROOT / "v4").rglob("*.md")) + [ROOT / "README.md", ROOT / "docs/CAP_NHAT_V4.md"]:
        if "/source/assets/" in page.as_posix():
            continue
        for ref in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", page.read_text(encoding="utf-8")):
            check_link(page, ref)
    print(json.dumps({"status": "pass", "immutable_files": immutable_count, **totals}, ensure_ascii=False))


if __name__ == "__main__":
    main()

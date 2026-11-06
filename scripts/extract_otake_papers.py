#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf", "fonttools"]
# ///
"""Extract Otake's papers into data/otake_papers/*.tsv.

usage: scripts/extract_otake_papers.py <references/khitan directory>
"""
from __future__ import annotations

import csv
import glob
import hashlib
import io
import re
import sys
from pathlib import Path

import pymupdf
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).parent))
from otake_pdf import Thesis, ids  # noqa: E402

OUT = Path(__file__).parent.parent / "data" / "otake_papers"
PHONE = r"[a-zA-Zəɵʊɪıɨäöüëȫǖǟūāēīōȳůïǰčšžňľŋγχğḥʷᵘ̯̠̈̄’]"
WORD = rf"\*?{PHONE}+(?:[-=.]{PHONE}+)*\??"


def write(name: str, header: list[str], rows: list[list]) -> None:
    with open(OUT / f"{name}.tsv", "w", newline="", encoding="utf8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(name, len(rows))


def tsv(name: str) -> list[dict]:
    with open(OUT / f"{name}.tsv", encoding="utf8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


class Paper:
    """Page lines of one paper with Khitan runs written as ⟦id⟧."""

    def __init__(self, path: str, thesis: Thesis, font: str, aliases: dict[str, str], by_text: dict[str, str] | None = None):
        self.doc = pymupdf.open(path)
        self.font, self.by_text, self.aliases, self.thesis = font, by_text, aliases, thesis
        self.tables: dict[str, dict[int, str]] = {}

    def _outlines(self, base: str, xref: int) -> dict[int, str]:
        if base not in self.tables:
            font = TTFont(io.BytesIO(self.doc.extract_font(xref)[3]))
            glyphs = font.getGlyphSet()
            table = {}
            for gid, name in enumerate(font.getGlyphOrder()):
                pen = RecordingPen()
                glyphs[name].draw(pen)
                if pen.value:
                    table[gid] = hashlib.sha1(repr(pen.value).encode()).hexdigest()[:12]
            self.tables[base] = table
        return self.tables[base]

    def identify(self, outline: str) -> str:
        return self.thesis.hash_to_id.get(outline) or self.aliases.get(outline[:6]) or f"x{outline[:6]}"

    def segs(self, page: int) -> list[list[tuple[float, float, str, bool]]]:
        pno = page - 1
        glyphs = {}
        if self.by_text is None:
            bases = [(f[3], f[0]) for f in self.doc.get_page_fonts(pno) if self.font in f[3]]
            for base, xref in bases[:1]:
                table = self._outlines(base, xref)
                for span in self.doc[pno].get_texttrace():
                    if self.font in span["font"]:
                        for _, gid, origin, _ in span["chars"]:
                            if gid in table:
                                glyphs[(round(origin[0], 1), round(origin[1], 1))] = table[gid]
        lines = []
        for block in self.doc[pno].get_text("rawdict")["blocks"]:
            for raw in block.get("lines", []):
                line = []
                for span in raw["spans"]:
                    khitan = self.font in span["font"]
                    text, x, y = "", None, None
                    for c in span["chars"]:
                        if x is None:
                            x, y = c["origin"]
                        if not khitan:
                            text += c["c"]
                        elif self.by_text is not None:
                            if c["c"].strip():
                                text += f"⟦{self.by_text.get(c['c'], 'k%04X' % ord(c['c']))}⟧"
                        else:
                            outline = glyphs.get((round(c["origin"][0], 1), round(c["origin"][1], 1)))
                            if outline:
                                text += f"⟦{self.identify(outline)}⟧"
                    if text:
                        line.append((x, y, text, khitan))
                if line:
                    lines.append(line)
        lines.sort(key=lambda l: (round(l[0][1] / 3), l[0][0]))
        return lines

    def lines(self, page: int) -> list[str]:
        return ["".join(s[2] for s in line) for line in self.segs(page)]


def reference(directory: str, marker: str) -> str:
    return next(p for p in glob.glob(f"{directory}/*.pdf") if marker in p)


def pairs(text: str) -> list[tuple[str, str]]:
    return re.findall(rf"((?:⟦[^⟧]+⟧)+)-?\s*({WORD})", text)


def grid_2018(paper: Paper) -> list[list]:
    """Printed tables (4a) and (4b): values by column and row, in the slides' notation."""
    rows = []
    page = 3
    lines = paper.segs(page)
    segs = [s for line in lines for s in line]
    whole = [(line[0][0], line[0][1], "".join(p[2] for p in line).strip()) for line in lines]
    marks = {m[1]: m[2] for _, _, t in whole for m in re.finditer(r"([*]?)⟦([^⟧]+)⟧(\??)", t) if m[1] or m[3]} and {}
    for _, _, t in whole:
        for m in re.finditer(r"([*]?)⟦([^⟧]+)⟧(\??)", t):
            if m[1]:
                marks[m[2]] = "stated_unattested"
            elif m[3]:
                marks[m[2]] = "stated_tentative"
    top = next(y for x, y, t in whole if t == "ë-")
    middle = next(y for x, y, t in whole if t == "ee-")
    bottom = next(y for x, y, t in whole if t.startswith("(5)"))
    for start, end, where, pattern in ((top, middle - 6, "table (4a)", r"[aeioöuäüëʊɵı̈]{1,2}-"), (middle, bottom, "table (4b)", r"[aeioöuäü]{1,2}-")):
        columns = sorted((x, t.rstrip("-")) for x, y, t in whole if abs(y - start) < 4 and re.fullmatch(pattern, t))
        labels = []
        for x, y, t in whole:
            if start < y < end and x < 195:
                m = re.search(r"(-[a-zǰžğγňľ]+)\s*(?:⟦.*)?$", t)
                if m:
                    labels.append((y, m[1]))
                elif t.startswith("長母音"):
                    labels.append((y, "VV"))
        for x, y, text, khitan in segs:
            if not khitan or not start < y < end:
                continue
            row = min(labels, key=lambda r: abs(r[0] - y))[1]
            col = min(columns, key=lambda c: abs(c[0] - x))[1]
            value = col * 2 if row == "VV" else col + row.lstrip("-")
            for gid in ids(text):
                rows.append([gid, value, marks.get(gid, "stated"), where, page])
    return rows


def examples(paper: Paper) -> tuple[list[list], list[list], list[list]]:
    sentences, words = [], []
    current = None
    for page in range(1, len(paper.doc) + 1):
        pending = None
        for raw in paper.lines(page):
            line = raw.strip()
            if not line or re.fullmatch(r"\d+|〔.*", line) and "⟦" not in line and not line.startswith("〔"):
                continue
            if line.startswith("〔語") or line.startswith("〔資料") or line.startswith("〔グロス"):
                current = None
                continue
            start = re.match(r"^\((\d+)\)\s*(.*)", line)
            if start:
                current = {"n": int(start[1]), "translation": "", "citation": "", "note": "", "page": page}
                sentences.append(current)
                line = start[2]
            if current is None or re.match(r"^\d+\)", line) or set(line) <= set("  "):
                continue
            if "⟦" in line and not re.search(r"[「『。]", line):
                pending = {"script": line.split(), "latin": None}
                words.append([current, pending])
                continue
            if line.startswith("註"):
                current["note"] += line
                continue
            found = re.search(r"〔([A-Z][^〕]*)〕", line)
            if re.search(r"[「」『』。、]", line) or found:
                current["translation"] += re.sub(r"〔[A-Z][^〕]*〕.*", "", line).strip()
                if found:
                    current["citation"] = found[1]
                continue
            if pending and pending["latin"] is None:
                pending["latin"] = line.split()
            elif pending and "gloss" not in pending:
                pending["gloss"] = line.split()
    out_s = [[s["n"], s["citation"], s["translation"], s["note"], s["page"]] for s in sentences]
    out_w, out_l = [], []
    counters: dict[int, int] = {}
    for s, block in words:
        script, latin = block["script"], block.get("latin") or []
        line = counters[s["n"]] = counters.get(s["n"], 0) + 1
        out_l.append([s["n"], line, " ".join(latin), " ".join(block.get("gloss") or [])])
        aligned = len(script) == len(latin)
        for i, token in enumerate(script):
            word = latin[i].strip("“”,.!?") if aligned else ""
            out_w.append([s["n"], line, i + 1, " ".join(ids(token)), word])
    return out_s, out_l, out_w


def main() -> None:
    directory = sys.argv[1]
    thesis = Thesis(reference(directory, "（2020）『契丹語の歴史言語学的研究』.pdf"))
    aliases = {r["outline"]: r["grapheme"] for r in tsv("khitan_small_aliases")}
    readings, forms = [], []

    p2018 = Paper(reference(directory, "「契丹語を俯瞰する」.pdf"), thesis, "KhitanSmall", aliases)
    for gid, value, tier, where, page in grid_2018(p2018):
        readings.append(["otake2018", gid, value, tier, where, page])
    for page in range(1, len(p2018.doc) + 1):
        for line in p2018.lines(page):
            for sp, word in pairs(line):
                forms.append(["otake2018", " ".join(ids(sp)), word, "", page])
    sentences, ex_lines, words = examples(Paper(reference(directory, "例文集"), thesis, "KhitanSmall", aliases))
    write("examples", ["n", "citation", "translation", "note", "page"], sentences)
    write("example_lines", ["n", "line", "transcription", "gloss"], ex_lines)
    write("example_words", ["n", "line", "position", "spelling", "transcription"], words)

    p2024 = Paper(reference(directory, "音調"), thesis, "KhitanSmall", aliases)
    for page in range(1, len(p2024.doc) + 1):
        for line in p2024.lines(page):
            for sp, word in pairs(line):
                forms.append(["otake2024", " ".join(ids(sp)), word, "", 84 + page])

    by_text = {chr(int(r["text_layer_codepoint"], 16)): r["grapheme"] for r in tsv("kss_gengokenkyu_glyphs") if r["grapheme"]}
    p2015 = Paper(reference(directory, "（2015）"), thesis, "KSS", aliases, by_text)
    for page, where in ((8, "表6"), (10, "表9")):
        text = "\n".join(p2015.lines(page))
        block = text[text.index(where):]
        block = block[:block.index("2.1.1." if page == 8 else "CV 型字素の母音も")]
        for sp, word in pairs(block):
            if len(ids(sp)) == 1:
                readings.append(["otake2015", ids(sp)[0], word, "stated", where, 80 + page])
    for page in range(1, len(p2015.doc) + 1):
        for line in p2015.lines(page):
            for sp, word in pairs(line):
                forms.append(["otake2015", " ".join(ids(sp)), word, "", 80 + page])

    for r in tsv("otake2025_tables"):
        readings.append(["otake2025", r["grapheme"], r["value"], "stated", "TABLE " + r["table"], 10])
    write("readings", ["source", "grapheme", "value", "tier", "location", "page"], readings)
    seen, unique = set(), []
    for row in forms:
        key = (row[0], row[1], row[2])
        if key not in seen and not re.fullmatch(r"[A-Z]+|e\.g|cf|MM", row[2]):
            seen.add(key)
            unique.append(row)
    write("forms", ["source", "spelling", "form", "gloss", "page"], unique)


if __name__ == "__main__":
    main()

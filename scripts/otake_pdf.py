"""Decode the Khitan small-script text of Otake (2020) into catalogue numbers.

The dissertation sets Khitan in a legacy font whose text layer cannot be read
directly. Glyphs are identified by outline, across the font's subsets, against
the grapheme table on printed pp.28-30. The font itself is never exported.
"""
from __future__ import annotations

import hashlib
import io
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache

import pymupdf
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

logging.getLogger("fontTools").setLevel(logging.ERROR)

CATALOGUE_PDF_PAGES = (40, 41, 42)
PRINTED_OFFSET = 12  # printed page = PDF page - 12 from chapter 1 onwards
NUMBER = re.compile(r"^(?:\d{3}[D?]?|C\d\d)$")


@dataclass
class Seg:
    x: float
    y: float
    text: str
    khitan: bool
    italic: bool = False
    size: float = 0.0


@dataclass
class Line:
    segs: list[Seg] = field(default_factory=list)

    @property
    def x(self) -> float:
        return self.segs[0].x

    @property
    def y(self) -> float:
        return self.segs[0].y

    @property
    def text(self) -> str:
        return "".join(s.text for s in self.segs)


class Thesis:
    def __init__(self, path: str):
        self.doc = pymupdf.open(path)
        self.outlines: dict[str, dict[int, str]] = {}
        self.catalogue: dict[str, list[str]] = {}
        self.catalogue_note: dict[str, str] = {}
        self.hash_to_id: dict[str, str] = {}
        self._load_catalogue()

    def _subset(self, pno: int) -> str | None:
        for f in self.doc.get_page_fonts(pno):
            if "KhitanSmall" in f[3]:
                tag = f[3].split("+")[0]
                if tag not in self.outlines:
                    self._load_subset(tag, f[0])
                return tag
        return None

    def _load_subset(self, tag: str, xref: int) -> None:
        _, _, _, data = self.doc.extract_font(xref)
        font = TTFont(io.BytesIO(data))
        glyphs = font.getGlyphSet()
        table: dict[int, str] = {}
        for gid, name in enumerate(font.getGlyphOrder()):
            pen = RecordingPen()
            glyphs[name].draw(pen)
            if pen.value:
                table[gid] = hashlib.sha1(repr(pen.value).encode()).hexdigest()[:12]
        self.outlines[tag] = table

    def _glyphs(self, pno: int) -> dict[tuple[float, float], str]:
        tag = self._subset(pno)
        if tag is None:
            return {}
        found = {}
        for span in self.doc[pno].get_texttrace():
            if "KhitanSmall" not in span["font"]:
                continue
            for _, gid, origin, _ in span["chars"]:
                outline = self.outlines[tag].get(gid)
                if outline:
                    found[(round(origin[0], 1), round(origin[1], 1))] = outline
        return found

    def _load_catalogue(self) -> None:
        for page in CATALOGUE_PDF_PAGES:
            pno = page - 1
            glyphs = self._glyphs(pno)
            words = self.doc[pno].get_text("words")
            for w in words:
                x0, y0, x1, y1, text = w[:5]
                if not NUMBER.match(text):
                    continue
                row = sorted(
                    (x, h) for (x, y), h in glyphs.items() if abs(y - y1) < 6 and x1 - 1 < x < x1 + 50
                )
                self.catalogue[text] = [h for _, h in row]
                self.catalogue_note[text] = " ".join(
                    v[4]
                    for v in words
                    if abs((v[1] + v[3]) / 2 - (y0 + y1) / 2) < 5
                    and x1 - 1 < v[0] < x1 + 60
                    and not NUMBER.match(v[4])
                )
        for number, row in self.catalogue.items():
            if len(row) == 1:
                self.hash_to_id[row[0]] = number

    def glyph_id(self, outline: str) -> str:
        return self.hash_to_id.get(outline) or f"x{outline[:6]}"

    @lru_cache(maxsize=None)
    def lines(self, page: int) -> tuple[Line, ...]:
        """Lines of a 1-based PDF page, Khitan runs written as ⟦id⟧."""
        pno = page - 1
        glyphs = self._glyphs(pno)
        out: list[Line] = []
        for block in self.doc[pno].get_text("rawdict")["blocks"]:
            for raw in block.get("lines", []):
                line = Line()
                for span in raw["spans"]:
                    khitan = "KhitanSmall" in span["font"]
                    italic = "Italic" in span["font"]
                    text = ""
                    x = y = None
                    for c in span["chars"]:
                        if x is None:
                            x, y = c["origin"]
                        if khitan:
                            key = (round(c["origin"][0], 1), round(c["origin"][1], 1))
                            outline = glyphs.get(key)
                            if outline:
                                text += f"⟦{self.glyph_id(outline)}⟧"
                            continue
                        text += c["c"]
                    if text:
                        line.segs.append(Seg(x, y, text, khitan, italic, span["size"]))
                if line.segs:
                    out.append(line)
        out.sort(key=lambda l: (round(l.y / 3), l.x))
        return tuple(out)

    def text(self, page: int) -> str:
        return "\n".join(l.text for l in self.lines(page))

    def rows(self, page: int, tolerance: float = 5.0) -> list[list[Line]]:
        """Lines grouped into visual rows by baseline, left to right."""
        rows: list[list[Line]] = []
        for line in sorted(self.lines(page), key=lambda l: l.y):
            if rows and abs(rows[-1][0].y - line.y) <= tolerance:
                rows[-1].append(line)
            else:
                rows.append([line])
        for row in rows:
            row.sort(key=lambda l: l.x)
        return rows


def printed(page: int) -> int:
    return page - PRINTED_OFFSET


def ids(spelling: str) -> list[str]:
    return re.findall(r"⟦([^⟧]+)⟧", spelling)

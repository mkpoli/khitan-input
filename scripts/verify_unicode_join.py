#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf", "fonttools", "numpy", "pillow"]
# ///
"""Rank Unicode characters against each catalogue glyph by shape.

usage: scripts/verify_unicode_join.py <dissertation.pdf> <noto.ttf> <out.json>
Writes the top candidates for every catalogue grapheme. Rasters stay in memory;
the dissertation's font is never written out.
"""
import io
import json
import sys
from pathlib import Path

import numpy as np
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from otake_pdf import Thesis  # noqa: E402

SIZE = 56


class Flat(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.contours = []

    def _moveTo(self, p):
        self.contours.append([p])

    def _lineTo(self, p):
        self.contours[-1].append(p)

    def _curveToOne(self, a, b, c):
        p0 = self.contours[-1][-1]
        for t in np.linspace(0.1, 1, 10):
            u = 1 - t
            self.contours[-1].append(tuple(u**3 * np.array(p0) + 3 * u * u * t * np.array(a) + 3 * u * t * t * np.array(b) + t**3 * np.array(c)))

    def _closePath(self):
        pass


def raster(contours):
    pts = np.array([p for c in contours for p in c])
    lo, hi = pts.min(0), pts.max(0)
    scale = (SIZE * 4 - 8) / max(hi - lo)
    pad = (SIZE * 4 - (hi - lo) * scale) / 2
    canvas = Image.new("L", (SIZE * 4, SIZE * 4), 0)
    for c in contours:
        layer = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(layer).polygon([((x - lo[0]) * scale + pad[0], SIZE * 4 - ((y - lo[1]) * scale + pad[1])) for x, y in c], fill=255)
        canvas = ImageChops.logical_xor(canvas.convert("1"), layer.convert("1")).convert("L")
    small = canvas.resize((SIZE, SIZE), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    v = np.array(small, dtype=float).ravel()
    v -= v.mean()
    return v / (np.linalg.norm(v) or 1)


def glyph_vector(font, name):
    gs = font.getGlyphSet()
    pen = Flat(gs)
    gs[name].draw(pen)
    return raster(pen.contours) if pen.contours else None


def main():
    thesis_path, noto_path, out = sys.argv[1:4]
    t = Thesis(thesis_path)
    noto = TTFont(noto_path)
    cmap = noto.getBestCmap()
    uni = {}
    for cp, name in cmap.items():
        if 0x18B00 <= cp <= 0x18CFF:
            v = glyph_vector(noto, name)
            if v is not None:
                uni[f"{cp:05X}"] = v
    names = list(uni)
    matrix = np.array([uni[c] for c in names])
    tag_page = {}
    for pno in range(len(t.doc)):
        for f in t.doc.get_page_fonts(pno):
            if "KhitanSmall" in f[3] and f[3].split("+")[0] not in tag_page:
                tag_page[f[3].split("+")[0]] = f[0]
    # the catalogue subset holds every grapheme
    tag = t._subset(39)
    data = t.doc.extract_font(tag_page[tag])[3]
    subset = TTFont(io.BytesIO(data))
    order = subset.getGlyphOrder()
    hash_gid = {h: g for g, h in t.outlines[tag].items()}
    result = {}
    for number, row in t.catalogue.items():
        if len(row) != 1:
            continue
        v = glyph_vector(subset, order[hash_gid[row[0]]])
        scores = matrix @ v
        best = np.argsort(-scores)[:6]
        result[number] = [[names[i], round(float(scores[i]), 3)] for i in best]
    Path(out).write_text(json.dumps(result, indent=0))


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0", "fonttools==4.68.0", "brotli==1.2.0"]
# ///
"""Build the pen lines the drawing pad compares a drawing with.

Every Khitan small-script character Noto Serif Khitan Small Script draws is rendered from its outline at
96 px, cropped to its ink, fitted to a 32×32 square and thinned to a one-cell line along the pen,
then packed as 128 bytes of bits. The file is a little-endian u32 header length, the header as UTF-8
JSON (format, size, font, sha256 and the sequences in order), then the masks back to back. The page
normalises a drawing the same way.
"""
import hashlib
import json
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'app/public/fonts/NotoSerifKhitanSmallScript-Regular.woff2'
OUT = ROOT / 'app/public/data/shapes.bin'
SIZE = 32
FIT = 30
THIN_SCALE = 3
RENDER = 96
THRESHOLD = 96


class PolygonPen(BasePen):
    """A glyph's contours as polygons."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.polygons = []
        self.contour = []

    def _moveTo(self, point):
        self.contour = [point]

    def _lineTo(self, point):
        self.contour.append(point)

    def _curveToOne(self, a, b, c, steps=8):
        start = self.contour[-1]
        for i in range(1, steps + 1):
            t = i / steps
            x = (1 - t) ** 3 * start[0] + 3 * (1 - t) ** 2 * t * a[0] + 3 * (1 - t) * t ** 2 * b[0] + t ** 3 * c[0]
            y = (1 - t) ** 3 * start[1] + 3 * (1 - t) ** 2 * t * a[1] + 3 * (1 - t) * t ** 2 * b[1] + t ** 3 * c[1]
            self.contour.append((x, y))

    def _closePath(self):
        if len(self.contour) > 2:
            self.polygons.append(self.contour)
        self.contour = []

    _endPath = _closePath


def area(polygon):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(polygon, polygon[1:] + polygon[:1])) / 2


def render(glyph_set, name, scale):
    """The glyph's ink. Contours wound like the largest one are ink; the others are counters."""
    pen = PolygonPen(glyph_set)
    glyph_set[name].draw(pen)
    if not pen.polygons:
        return None
    xs = [x for polygon in pen.polygons for x, _ in polygon]
    ys = [y for polygon in pen.polygons for _, y in polygon]
    left, top = min(xs), max(ys)
    pad = 8
    width = int((max(xs) - left) * scale) + 2 * pad
    height = int((top - min(ys)) * scale) + 2 * pad
    canvas = Image.new('L', (max(1, width), max(1, height)), 0)
    draw = ImageDraw.Draw(canvas)
    outer = area(max(pen.polygons, key=lambda polygon: abs(area(polygon)))) > 0
    place = lambda polygon: [((x - left) * scale + pad, (top - y) * scale + pad) for x, y in polygon]
    for polygon in pen.polygons:
        if (area(polygon) > 0) == outer:
            draw.polygon(place(polygon), fill=255)
    for polygon in pen.polygons:
        if (area(polygon) > 0) != outer:
            draw.polygon(place(polygon), fill=0)
    return canvas


def mask_of(canvas):
    """The ink of a rendered glyph as a pen line of packed bits, fitted to the square."""
    box = canvas.point(lambda v: 255 if v >= THRESHOLD else 0).getbbox()
    if not box:
        return None
    ink = canvas.crop(box)
    width, height = ink.size
    size = SIZE * THIN_SCALE
    fit = FIT * THIN_SCALE
    scale = fit / max(width, height, 1)
    w = max(1, round(width * scale))
    h = max(1, round(height * scale))
    fitted = ink.resize((w, h), Image.Resampling.LANCZOS)
    square = Image.new('L', (size, size), 0)
    square.paste(fitted, ((size - w) // 2, (size - h) // 2))
    pixels = square.load()
    cells = {(x, y) for y in range(size) for x in range(size) if pixels[x, y] >= THRESHOLD // 4}
    cells = {(x // THIN_SCALE, y // THIN_SCALE) for x, y in thinner(cells)}
    bits = bytearray(SIZE * SIZE // 8)
    for x, y in cells:
        index = y * SIZE + x
        bits[index >> 3] |= 1 << (index & 7)
    return bits


def thinner(ink):
    """Zhang-Suen thinning: the filled glyph reduced to a one-cell-wide line along its pen."""
    ink = set(ink)
    while True:
        removed = 0
        for step in (0, 1):
            marks = []
            for x, y in ink:
                p = (0 if (x, y - 1) not in ink else 1, 0 if (x + 1, y - 1) not in ink else 1,
                     0 if (x + 1, y) not in ink else 1, 0 if (x + 1, y + 1) not in ink else 1,
                     0 if (x, y + 1) not in ink else 1, 0 if (x - 1, y + 1) not in ink else 1,
                     0 if (x - 1, y) not in ink else 1, 0 if (x - 1, y - 1) not in ink else 1)
                if not 2 <= sum(p) <= 6:
                    continue
                if sum(1 for k in range(8) if p[k] == 0 and p[(k + 1) % 8] == 1) != 1:
                    continue
                if step == 0 and (p[0] * p[2] * p[4] or p[2] * p[4] * p[6]):
                    continue
                if step == 1 and (p[0] * p[2] * p[6] or p[0] * p[4] * p[6]):
                    continue
                marks.append((x, y))
            for cell in marks:
                ink.discard(cell)
            removed += len(marks)
        if not removed:
            return ink


def main():
    font = TTFont(FONT)
    glyph_set = font.getGlyphSet()
    scale = RENDER / font['head'].unitsPerEm
    cmap = font.getBestCmap()
    chars = []
    packed = bytearray()
    for point in sorted(cmap):
        if not 0x18B00 <= point <= 0x18CFF:
            continue
        canvas = render(glyph_set, cmap[point], scale)
        mask = mask_of(canvas) if canvas else None
        if mask is None:
            continue
        chars.append(chr(point))
        packed += mask
    document = {'format': 'khitan-input/shapes', 'size': SIZE, 'font': 'Noto Serif Khitan Small Script',
                'fontSha256': hashlib.sha256(FONT.read_bytes()).hexdigest(), 'chars': chars}
    header = json.dumps(document, ensure_ascii=False, separators=(',', ':')).encode()
    OUT.write_bytes(len(header).to_bytes(4, 'little') + header + bytes(packed))
    print(f'{len(chars)} glyphs, {OUT.stat().st_size} bytes -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

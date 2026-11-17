# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "brotli==1.2.1",
#   "fonttools==4.68.0",
#   "numpy==2.5.5",
#   "pillow==13.0.0",
#   "scikit-image==0.26.0",
#   "scipy==1.18.1",
#   "skan==0.13.1",
# ]
# ///
"""Build the pilot seal typeface from the sixteen-block reference drawing.

`reference.png` holds the sixteen abstracted blocks in four rows and four columns. Each cell is
reduced to a one-pixel skeleton, the branches are traced as polylines, and the strokes are drawn
with a 30-unit round pen on a 1024-unit em. The pen and the em follow Sealie; the forms follow the
drawing.

    uv run scripts/build_seal_font.py

The sixteen glyphs stand at page-local U+E700-U+E70F.
"""
from __future__ import annotations

import json
import math
import re
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skan import Skeleton
from skimage.morphology import remove_small_objects, skeletonize

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple

ROOT = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'data/seal/font/reference.png'
OVERRIDES = ROOT / 'data/seal/font/overrides.json'
FORMS = ROOT / 'data/seal/font/forms.json'
TTF = ROOT / 'fonts/QinglingSeal-Regular.ttf'
WOFF2 = ROOT / 'fonts/QinglingSeal-Regular.woff2'
WEB = ROOT / 'app/public/fonts/QinglingSeal-Regular.woff2'
SPECIMEN = ROOT / 'docs/seal-font-specimen.png'

EM = 1024
ASCENT = 832
DESCENT = -192
ADVANCE = 1024
RADIUS = 15
BASELINE = 60
INK = 760


def rdp(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Ramer-Douglas-Peucker simplification of one polyline."""
    if len(points) < 3:
        return points

    def distance(point, start, end):
        ax, ay = start
        bx, by = end
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.dist(point, start)
        t = max(0.0, min(1.0, ((point[0] - ax) * dx + (point[1] - ay) * dy) / (dx * dx + dy * dy)))
        return math.dist(point, (ax + t * dx, ay + t * dy))

    farthest, index = 0.0, 0
    for i in range(1, len(points) - 1):
        d = distance(points[i], points[0], points[-1])
        if d > farthest:
            farthest, index = d, i
    if farthest > tolerance:
        left = rdp(points[:index + 1], tolerance)
        right = rdp(points[index:], tolerance)
        return left[:-1] + right
    return [points[0], points[-1]]


def chaikin(points: list[tuple[float, float]], rounds: int = 2) -> list[tuple[float, float]]:
    """Round a polyline by corner cutting."""
    for _ in range(rounds):
        if len(points) < 3:
            break
        smoothed = [points[0]]
        for a, b in zip(points, points[1:]):
            smoothed.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            smoothed.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        smoothed.append(points[-1])
        points = smoothed
    return points


def trace(cell: Image.Image) -> list[list[tuple[float, float]]]:
    """Turn one cell's dark strokes into centreline polylines."""
    mask = np.asarray(cell.convert('L')) < 120
    mask = remove_small_objects(mask, max_size=24)
    skeleton = skeletonize(mask)
    if not skeleton.any():
        raise ValueError('no stroke in the cell')
    branches = Skeleton(skeleton)
    paths = []
    for index in range(branches.n_paths):
        coords = branches.path_coordinates(index)
        if len(coords) < 8:
            continue
        points = [(float(x), float(y)) for y, x in coords]
        length = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
        if length < 8:
            continue
        paths.append(chaikin(rdp(points, 1.5), 2))
    return paths


def normalise(paths: list[list[tuple[float, float]]], centre: int = 512) -> list[list[list[float]]]:
    """Scale a block to the em, centre it, and put its foot on the baseline."""
    points = [point for path in paths for point in path]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    if not points:
        raise ValueError('the cell produced no centreline')
    scale = INK / max(max(xs) - min(xs), max(ys) - min(ys), 1)
    cx = (min(xs) + max(xs)) / 2
    bottom = max(ys)
    return [[[round(centre + (x - cx) * scale, 2), round(BASELINE + (bottom - y) * scale, 2)]
             for x, y in path] for path in paths]


def _rectangle(pen: TTGlyphPen, start, end, radius: float) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    nx, ny = -dy / length * radius, dx / length * radius
    pen.moveTo((start[0] + nx, start[1] + ny))
    pen.lineTo((end[0] + nx, end[1] + ny))
    pen.lineTo((end[0] - nx, end[1] - ny))
    pen.lineTo((start[0] - nx, start[1] - ny))
    pen.closePath()


def _disk(pen: TTGlyphPen, centre, radius: float) -> None:
    """Sixteen quadratic arcs approximate a round cap."""
    cx, cy = centre
    control = radius / math.cos(math.pi / 16)
    pen.moveTo((cx + radius, cy))
    for index in range(16):
        middle = -(index + 0.5) * math.pi / 8
        end = -(index + 1) * math.pi / 8
        endpoint = (cx + radius, cy) if index == 15 else (
            cx + radius * math.cos(end), cy + radius * math.sin(end))
        pen.qCurveTo((cx + control * math.cos(middle), cy + control * math.sin(middle)), endpoint)
    pen.closePath()


def glyph(paths: list[list[list[float]]]):
    """Expand centreline polylines into a TrueType glyph with a round pen."""
    pen = TTGlyphPen(None)
    for path in paths:
        for start, end in zip(path, path[1:]):
            _rectangle(pen, start, end, RADIUS)
        for point in path:
            _disk(pen, point, RADIUS)
    result = pen.glyph()
    if result.numberOfContours:
        result.flags[0] |= flagOverlapSimple
    return result


def load_overrides() -> dict[str, list[list[list[float]]]]:
    """Parse the manual M/L/Q redraws into font-unit paths."""
    if not OVERRIDES.exists():
        return {}
    data = json.loads(OVERRIDES.read_text(encoding='utf-8'))
    out = {}
    for name, strokes in data['glyphs'].items():
        paths = []
        for stroke in strokes:
            tokens = re.sub(r'([MLQ])', r' \1 ', stroke).replace(',', ' ').split()
            points = []
            current = (0.0, 0.0)
            i = 0
            while i < len(tokens):
                command = tokens[i]
                if command in ('M', 'L'):
                    current = (float(tokens[i + 1]), float(tokens[i + 2]))
                    points.append(current)
                    i += 3
                elif command == 'Q':
                    control = (float(tokens[i + 1]), float(tokens[i + 2]))
                    end = (float(tokens[i + 3]), float(tokens[i + 4]))
                    for step in range(1, 11):
                        t = step / 10
                        points.append((
                            (1 - t) ** 2 * current[0] + 2 * (1 - t) * t * control[0] + t * t * end[0],
                            (1 - t) ** 2 * current[1] + 2 * (1 - t) * t * control[1] + t * t * end[1]))
                    current = end
                    i += 5
                else:
                    raise SystemExit(f'{name}: unknown command {command}')
            paths.append([[round(132 + x * 7.6, 2), round(820 - y * 7.6, 2)] for x, y in points])
        out[name] = paths
    return out


def build(record: dict) -> None:
    """Write the font, the WOFF2 copies and the specimen."""
    order = ['.notdef']
    outlines = {'.notdef': glyph([[[80, 0], [944, 0], [944, 760], [80, 760], [80, 0]]])}
    widths = {'.notdef': (ADVANCE, 60)}
    cmap = {}
    for index, form in enumerate(record['forms']):
        name = f"uE7{index:02X}"
        order.append(name)
        outlines[name] = glyph(form['paths'])
        widths[name] = (ADVANCE, 0)
        cmap[0xE700 + index] = name

    builder = FontBuilder(EM, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(outlines)
    builder.setupHorizontalMetrics(widths)
    builder.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    builder.setupNameTable({
        'copyright': 'Reference drawing abstracted for the Khitan Input project from the Xuanyi '
                     'cover photograph (Tonyxy1992, Wikimedia Commons, CC BY-SA 4.0). The 30-unit '
                     'round pen and 1024-unit em follow Sealie (SIL OFL 1.1).',
        'familyName': 'Qingling Seal',
        'styleName': 'Regular',
        'uniqueFontIdentifier': 'QinglingSeal-Regular;1.100;2026',
        'fullName': 'Qingling Seal Regular',
        'version': 'Version 1.100',
        'psName': 'QinglingSeal-Regular',
        'designer': 'Drawn for the Khitan Input project',
        'description': '16 abstracted seal-script blocks from the cover of Empress Xuanyi\'s '
                       'Qingling 哀册, at page-local code points U+E700-U+E70F.',
        'licenseDescription': 'The glyphs derive from a CC BY-SA 4.0 photograph and are offered '
                              'under CC BY-SA 4.0. The stroke system follows Sealie, SIL OFL 1.1.',
        'licenseInfoURL': 'https://github.com/mkpoli/khitan-input/blob/main/data/seal/font/README.md',
        'vendorURL': 'https://commons.wikimedia.org/wiki/File:Epitaph_of_Empress_Xuanyi_of_Liao.jpg',
        'designerURL': 'https://khitan.mkpo.li/',
    })
    builder.setupOS2(
        sTypoAscender=ASCENT, sTypoDescender=DESCENT, sTypoLineGap=0,
        usWinAscent=ASCENT, usWinDescent=-DESCENT,
        sxHeight=512, sCapHeight=700, achVendID='MKPO', fsType=0)
    builder.setupPost()
    TTF.parent.mkdir(parents=True, exist_ok=True)
    builder.save(TTF)
    builder.font.flavor = 'woff2'
    builder.save(WOFF2)
    WEB.parent.mkdir(parents=True, exist_ok=True)
    WEB.write_bytes(WOFF2.read_bytes())
    (WEB.parent / TTF.name).write_bytes(TTF.read_bytes())
    print(f'{TTF.relative_to(ROOT)}: {len(order)} glyphs, {TTF.stat().st_size} bytes')
    print(f'{WOFF2.relative_to(ROOT)}: {WOFF2.stat().st_size} bytes')
    draw_specimen(record)


def draw_specimen(record: dict) -> None:
    """Draw the reference and the sixteen font glyphs on one sheet."""
    label = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 26)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    glyph_font = ImageFont.truetype(str(TTF), 96)
    canvas = Image.new('RGB', (1000, 610), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 24), 'Qingling Seal · 16 abstracted blocks', font=title, fill='black')
    draw.text((30, 60), 'Reference drawing above; 30-unit round pen below. A draft; the Daozong cover is not drawn.',
              font=small, fill=(90, 90, 90))
    reference = Image.open(REFERENCE).convert('RGB').resize((420, 420), Image.LANCZOS)
    canvas.paste(reference, (30, 95))
    for index, form in enumerate(record['forms']):
        column, row = index % 4, index // 4
        x = 490 + column * 125
        y = 95 + row * 125
        draw.text((x, y), chr(0xE700 + index), font=glyph_font, fill='black')
        draw.text((x, y + 88), form['id'], font=label, fill=(90, 90, 90))
    canvas.save(SPECIMEN, optimize=True)
    print(f'{SPECIMEN.relative_to(ROOT)}: {canvas.width}x{canvas.height}')


def main() -> None:
    reference = Image.open(REFERENCE).convert('L')
    width, height = reference.size
    overrides = load_overrides()
    forms = []
    for index in range(16):
        column, row = index % 4, index // 4
        left, right = round(column * width / 4), round((column + 1) * width / 4)
        top, bottom = round(row * height / 4), round((row + 1) * height / 4)
        cell = reference.crop((left, top, right, bottom))
        name = f'XY-{index + 1:02d}'
        paths = overrides.get(name) or normalise(trace(cell))
        forms.append({'id': name, 'col': column + 1, 'row': row + 1, 'paths': paths})
    record = {
        'source': {
            'drawing': 'reference.png',
            'basis': 'Tonyxy1992, Epitaph of Empress Xuanyi of Liao, Wikimedia Commons, 2015-08-05',
            'licence': 'CC BY-SA 4.0',
        },
        'font': {
            'family': 'Qingling Seal', 'em': EM, 'ascent': ASCENT, 'descent': DESCENT,
            'advance': ADVANCE, 'stroke_radius': RADIUS, 'licence': 'CC BY-SA 4.0',
            'stroke_system': 'Sealie, SIL OFL 1.1',
        },
        'forms': forms,
    }
    FORMS.write_text(json.dumps(record, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{FORMS.relative_to(ROOT)}: {len(forms)} forms')
    build(record)


if __name__ == '__main__':
    main()

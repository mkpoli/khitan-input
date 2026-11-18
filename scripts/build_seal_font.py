# /// script
# requires-python = ">=3.12"
# dependencies = ["brotli==1.2.1", "fonttools==4.68.0", "pillow==13.0.0", "shapely==2.1.2"]
# ///
"""Build the pilot seal typeface and its gallery.

`data/seal/font/forms.json` is the vector source: the drawn forms, each a list of centreline paths
in font units. This script expands them with a 30-unit round pen on a 1024-unit em, writes the TTF
and WOFF2, and draws `docs/seal-gallery.png`.

    uv run scripts/build_seal_font.py
"""
from __future__ import annotations

import json
import math
import pathlib

from PIL import Image, ImageDraw, ImageFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from shapely.geometry import LineString
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).resolve().parents[1]
FORMS = ROOT / 'data/seal/font/forms.json'
CORRESPONDENCES = ROOT / 'data/seal/correspondences.json'
TTF = ROOT / 'fonts/QinglingSeal-Regular.ttf'
WOFF2 = ROOT / 'fonts/QinglingSeal-Regular.woff2'
WEB = ROOT / 'app/public/fonts/QinglingSeal-Regular.woff2'
GALLERY = ROOT / 'docs/seal-gallery.png'

EM = 1024
ASCENT = 832
DESCENT = -192
ADVANCE = 1024
RADIUS = 15


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


def _area(points: list[tuple[float, float]]) -> float:
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1])) / 2


def glyph(paths: list[list[list[float]]]):
    """Union the round-pen strokes into one clean outline per glyph."""
    shapes = []
    for path in paths:
        points = [tuple(point) for point in path]
        if len(points) < 2:
            continue
        shapes.append(LineString(points).buffer(RADIUS, cap_style='round', join_style='round', resolution=12))
    shape = unary_union(shapes)
    polygons = list(shape.geoms) if hasattr(shape, 'geoms') else [shape]
    pen = TTGlyphPen(None)
    for polygon in polygons:
        rings = [polygon.exterior] + list(polygon.interiors)
        for index, ring in enumerate(rings):
            points = list(ring.coords)
            if len(points) < 3:
                continue
            # TrueType fills clockwise exteriors, counter-clockwise holes.
            clockwise = _area(points) < 0
            if (index == 0) != clockwise:
                points.reverse()
            pen.moveTo(points[0])
            for point in points[1:]:
                pen.lineTo(point)
            pen.closePath()
    result = pen.glyph()
    if result.numberOfContours:
        result.flags[0] |= flagOverlapSimple
    return result


def fit(record: dict) -> None:
    """Put every glyph on one baseline at one height, centred in the em."""
    for form in record['forms']:
        points = [point for path in form['paths'] for point in path]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        scale = min(700 / max(height, 1), 860 / max(width, 1))
        cx = (min(xs) + max(xs)) / 2
        bottom = min(ys)
        form['paths'] = [[[round(512 + (x - cx) * scale, 2), round(80 + (y - bottom) * scale, 2)]
                          for x, y in path] for path in form['paths']]


def build(record: dict) -> None:
    """Write the font at the Khitan code points, plus the WOFF2 copies and gallery."""
    mapping = json.loads(CORRESPONDENCES.read_text(encoding='utf-8'))
    correspondences = mapping['blocks']
    order = ['.notdef']
    outlines = {'.notdef': glyph([[[80, 0], [944, 0], [944, 760], [80, 760], [80, 0]]])}
    widths = {'.notdef': (ADVANCE, 60)}
    cmap = {}
    alternates = []
    for form in record['forms']:
        code = int(correspondences[form['id']]['unicode'][2:], 16)
        name = f'uni{code:04X}'
        if code in cmap:
            alternate = f'{name}.alt'
            order.append(alternate)
            outlines[alternate] = glyph(form['paths'])
            widths[alternate] = (ADVANCE, 0)
            alternates.append((name, alternate))
            continue
        order.append(name)
        outlines[name] = glyph(form['paths'])
        widths[name] = (ADVANCE, 0)
        cmap[code] = name

    for alias, primary in mapping['unicode_aliases'].items():
        cmap[int(alias[2:], 16)] = cmap[int(primary[2:], 16)]

    builder = FontBuilder(EM, isTTF=True)
    builder.font['head'].fontRevision = 2.1
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(outlines)
    if alternates:
        rules = ' '.join(f'sub {base} by {alt};' for base, alt in alternates)
        addOpenTypeFeaturesFromString(builder.font, f'feature ss01 {{ {rules} }} ss01;')
    builder.setupHorizontalMetrics(widths)
    builder.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    builder.setupNameTable({
        'copyright': 'Vector glyphs drawn for the Khitan Input project after the Qingling cover '
                     'photographs (Tonyxy1992, CC BY-SA 4.0 and 红烧腰果, CC BY 4.0). The 30-unit round '
                     'pen and 1024-unit em follow Sealie (SIL OFL 1.1).',
        'familyName': 'Qingling Seal',
        'styleName': 'Regular',
        'uniqueFontIdentifier': 'QinglingSeal-Regular;2.100;2026',
        'fullName': 'Qingling Seal Regular',
        'version': 'Version 2.100',
        'psName': 'QinglingSeal-Regular',
        'designer': 'Drawn for the Khitan Input project',
        'description': 'Seal-script forms from the Daozong and Xuanyi Qingling covers, '
                       'at their Khitan small-script code points.',
        'licenseDescription': 'The glyphs derive from CC BY and CC BY-SA 4.0 photographs and are offered '
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
    draw_gallery(record)


def draw_gallery(record: dict) -> None:
    """Draw every glyph at display size on one sheet."""
    label = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 28)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    glyph_font = ImageFont.truetype(str(TTF), 168)
    correspondences = json.loads(CORRESPONDENCES.read_text(encoding='utf-8'))['blocks']
    canvas = Image.new('RGB', (1100, 150 + math.ceil(len(record['forms']) / 4) * 225), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 28), f"Qingling Seal · {len(record['forms'])} vector glyphs", font=title, fill='black')
    draw.text((42, 68), 'Khitan Small Script · 1024-unit em · 30-unit round pen', font=small, fill=(90, 90, 90))
    for index, form in enumerate(record['forms']):
        column, row = index % 4, index // 4
        x = 40 + column * 265
        y = 110 + row * 225
        draw.text((x, y), chr(int(correspondences[form['id']]['unicode'][2:], 16)), font=glyph_font, fill='black',
                  features=['ss01'] if form['id'] == 'XY-05' else [])
        draw.text((x, y + 170), f"{form['id']}  {correspondences[form['id']]['unicode']}", font=label, fill=(90, 90, 90))
    canvas.save(GALLERY, optimize=True)
    print(f'{GALLERY.relative_to(ROOT)}: {canvas.width}x{canvas.height}')


def main() -> None:
    record = json.loads(FORMS.read_text(encoding='utf-8'))
    fit(record)
    build(record)


if __name__ == '__main__':
    main()

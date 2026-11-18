# /// script
# requires-python = ">=3.12"
# dependencies = ["brotli==1.2.1", "fonttools==4.68.0", "pillow==13.0.0"]
# ///
"""Build the pilot seal typeface and its gallery.

`data/seal/font/forms.json` is the vector source: the drawn forms, each a list of centreline paths
in font units. This script expands them with a variable round pen (30 units at regular weight) on a 1024-unit em, writes the TTF
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
from fontTools.ttLib.tables.TupleVariation import TupleVariation

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


# Each segment has a clockwise contour with two semicircular caps. Keeping these
# contours separate preserves point correspondence as strokes meet at heavier weights.
def glyph(paths: list[list[list[float]]], radius: float):
    pen = TTGlyphPen(None)
    for path in paths:
        for start, end in zip(path, path[1:]):
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = math.hypot(dx, dy)
            if not length:
                continue
            tx, ty = radius * dx / length, radius * dy / length
            nx, ny = -ty, tx
            pen.moveTo((start[0] + nx, start[1] + ny))
            pen.lineTo((end[0] + nx, end[1] + ny))
            # TrueType quadratic arcs, four per semicircle.
            for centre, sign in ((end, 1), (start, -1)):
                x, y = centre
                if sign == -1:
                    pen.lineTo((x - nx, y - ny))
                for i in range(4):
                    angle = (i + 1) * math.pi / 4
                    mid = angle - math.pi / 8
                    scale = sign / math.cos(math.pi / 8)
                    endpoint = (x + sign * (nx * math.cos(angle) + tx * math.sin(angle)),
                                y + sign * (ny * math.cos(angle) + ty * math.sin(angle)))
                    if i == 3:
                        endpoint = (x - sign * nx, y - sign * ny)
                    pen.qCurveTo(
                        (x + scale * (nx * math.cos(mid) + tx * math.sin(mid)),
                         y + scale * (ny * math.cos(mid) + ty * math.sin(mid))),
                        endpoint)
            pen.closePath()
    result = pen.glyph()
    result.flags[0] |= flagOverlapSimple
    return result


def heavy_paths(paths, terminals):
    """Move facing tips apart at weight 800, holding the far ends in place."""
    adjusted = paths.copy()
    for terminal in terminals:
        index = terminal['path']
        points = paths[index]
        distances = [0.0]
        for start, end in zip(points, points[1:]):
            distances.append(distances[-1] + math.dist(start, end))
        dx, dy = terminal['offset']
        moved = []
        for (x, y), distance in zip(points, distances):
            fraction = distance / distances[-1]
            if terminal['terminal'] == 'start':
                fraction = 1 - fraction
            moved.append((x + dx * fraction ** 2, y + dy * fraction ** 2))
        adjusted[index] = moved
    return adjusted


def weight_variations(paths, regular, terminals):
    variations = []
    for support, radius in (((-1, -1, 0), 9), ((0, 1, 1), 28)):
        extreme = glyph(heavy_paths(paths, terminals) if radius > RADIUS else paths, radius)
        if extreme.endPtsOfContours != regular.endPtsOfContours:
            raise ValueError('Weight masters must have matching contour endpoints')
        deltas = [(x - a, y - b) for (x, y), (a, b) in
                  zip(extreme.coordinates, regular.coordinates, strict=True)]
        # Four phantom points keep the origin and fixed advance constant.
        variations.append(TupleVariation({'wght': support}, deltas + [(0, 0)] * 4))
    return variations


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
    order = ['.notdef']
    paths = {'.notdef': [[[80, 0], [944, 0], [944, 760], [80, 760], [80, 0]]]}
    cmap = {}
    alternates = []
    terminals = {}
    for form in record['forms']:
        code = int(form['unicode'][2:], 16)
        name = f'uni{code:04X}'
        if form.get('alternate'):
            alternate = f'{name}.alt'
            order.append(alternate)
            paths[alternate] = form['paths']
            terminals[alternate] = form.get('heavy_terminals', [])
            alternates.append((name, alternate))
            continue
        order.append(name)
        paths[name] = form['paths']
        terminals[name] = form.get('heavy_terminals', [])
        cmap[code] = name

    for alias, primary in mapping['unicode_aliases'].items():
        cmap[int(alias[2:], 16)] = cmap[int(primary[2:], 16)]

    builder = FontBuilder(EM, isTTF=True)
    builder.font['head'].fontRevision = 3.4
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    outlines = {name: glyph(strokes, RADIUS) for name, strokes in paths.items()}
    builder.setupGlyf(outlines)
    if alternates:
        rules = ' '.join(f'sub {base} by {alt};' for base, alt in alternates)
        addOpenTypeFeaturesFromString(builder.font, f'feature ss01 {{ {rules} }} ss01;')
    builder.setupHorizontalMetrics({name: (ADVANCE, outline.xMin) for name, outline in outlines.items()})
    builder.font['head'].flags |= 2
    builder.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    builder.setupNameTable({
        'copyright': 'Vector glyphs drawn for the Khitan Input project after the Qingling cover '
                     'photographs (Tonyxy1992, CC BY-SA 4.0 and 红烧腰果, CC BY 4.0). The 30-unit round '
                     'pen and 1024-unit em follow Sealie (SIL OFL 1.1).',
        'familyName': 'Qingling Seal',
        'styleName': 'Regular',
        'uniqueFontIdentifier': 'QinglingSeal-Regular;3.400;2026',
        'fullName': 'Qingling Seal Regular',
        'version': 'Version 3.400',
        'psName': 'QinglingSeal-Regular',
        'designer': 'Drawn for the Khitan Input project',
        'description': 'Seal-script forms from the Daozong and Xuanyi Qingling covers, '
                       'with modern designs based on their stroke forms.',
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
    weights = [(200, 'ExtraLight'), (400, 'Regular'), (700, 'Bold'), (800, 'ExtraBold')]
    builder.setupFvar([('wght', 200, 400, 800, 'Weight')], [
        {'location': {'wght': weight}, 'stylename': name} for weight, name in weights
    ])
    builder.setupStat([{'tag': 'wght', 'name': 'Weight', 'values': [
        {'value': weight, 'name': name, 'flags': 2 if weight == 400 else 0}
        for weight, name in weights
    ]}])
    builder.setupGvar({name: weight_variations(strokes, outlines[name], terminals.get(name, []))
                       for name, strokes in paths.items()})
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
    canvas = Image.new('RGB', (1100, 150 + math.ceil(len(record['forms']) / 4) * 225), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 28), f"Qingling Seal · {len(record['forms'])} vector glyphs", font=title, fill='black')
    draw.text((42, 68), 'Khitan Small Script · 1024-unit em · 30-unit round pen', font=small, fill=(90, 90, 90))
    for index, form in enumerate(record['forms']):
        column, row = index % 4, index // 4
        x = 40 + column * 265
        y = 110 + row * 225
        draw.text((x, y), chr(int(form['unicode'][2:], 16)), font=glyph_font, fill='black',
                  features=['ss01'] if form.get('alternate') else [])
        draw.text((x, y + 170), f"{form['id']}  {form['unicode']}", font=label, fill=(90, 90, 90))
    canvas.save(GALLERY, optimize=True)
    print(f'{GALLERY.relative_to(ROOT)}: {canvas.width}x{canvas.height}')


def main() -> None:
    record = json.loads(FORMS.read_text(encoding='utf-8'))
    mapping = json.loads(CORRESPONDENCES.read_text(encoding='utf-8'))
    blocks = mapping['blocks']
    for form in record['forms']:
        form['unicode'] = blocks[form['id']]['unicode']
        form['alternate'] = form['id'] in mapping['font_alternates']
    designs = json.loads((FORMS.parent / 'analogues.json').read_text(encoding='utf-8'))
    record['forms'].extend({**design, 'id': 'Design'} for design in designs)
    fit(record)
    build(record)


if __name__ == '__main__':
    main()

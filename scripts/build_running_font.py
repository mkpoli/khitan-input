# /// script
# requires-python = ">=3.12"
# dependencies = ["brotli==1.2.1", "fonttools==4.68.0"]
# ///
"""Build the Nova N 176 running-script face from the traced forms.

Each cut form is a glyph at its page-local code point U+E600 onward. The four forms of the state
name that Zaytsev identifies also answer at BabelStone's Private Use points, so text keyed to the
large-script face can reach them.

    uv run scripts/build_running_font.py
"""
from __future__ import annotations

import calendar
import gzip
import json
import pathlib

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/running/forms.json.gz'
TTF = ROOT / 'fonts/NovaN176Running-Regular.ttf'
WOFF2 = ROOT / 'fonts/NovaN176Running-Regular.woff2'

TIMESTAMP = calendar.timegm((2026, 11, 8, 0, 0, 0)) + 2082844800
ASCENT = 836
DESCENT = -146
ADVANCE = 1000
NOTDEF = [
    ['M', 60, 0], ['L', 940, 0], ['L', 940, 820], ['L', 60, 820], ['Z'],
    ['M', 140, 80], ['L', 140, 740], ['L', 860, 740], ['L', 860, 80], ['Z'],
]


def glyph(outline: list[list], glyph_set) -> object:
    """Convert a normalised outline to a quadratic TrueType glyph."""
    pen = TTGlyphPen(glyph_set)
    quad = Cu2QuPen(pen, max_err=0.5, all_quadratic=True)
    for command in outline:
        operator, *values = command
        if operator == 'M':
            quad.moveTo(tuple(values))
        elif operator == 'L':
            quad.lineTo(tuple(values))
        elif operator == 'C':
            quad.curveTo(tuple(values[:2]), tuple(values[2:4]), tuple(values[4:6]))
        elif operator == 'Z':
            quad.closePath()
        else:
            raise ValueError(f'unknown command {operator}')
    return pen.glyph()


def left_side(outline: list[list]) -> int:
    """The leftmost x of an outline, used as the glyph's side bearing."""
    values = []
    for operator, *points in outline:
        if operator in 'ML':
            values.append(points[0])
        elif operator == 'C':
            values.extend([points[0], points[2], points[4]])
    return round(min(values))


def main() -> None:
    """Write the TTF and WOFF2 from the traced form record."""
    record = json.load(gzip.open(DATA, 'rt', encoding='utf-8'))
    metrics = record.get('metrics', {})
    if metrics.get('unitsPerEm', ADVANCE) != ADVANCE or metrics.get('advance', ADVANCE) != ADVANCE:
        raise SystemExit('the builder assumes a 1000-unit em and a 1000-unit advance')

    order = ['.notdef']
    drawings = {'.notdef': NOTDEF}
    widths = {'.notdef': (ADVANCE, 60)}
    cmap = {}
    aliases = []
    for form in record['forms']:
        name = f"u{form['pua']}"
        order.append(name)
        drawings[name] = form['outline']
        widths[name] = (ADVANCE, left_side(form['outline']))
        cmap[int(form['pua'], 16)] = name
        for alias in form.get('aliases', []):
            code = int(alias, 16)
            if code in cmap:
                raise SystemExit(f'{alias} would be mapped twice')
            cmap[code] = name
            aliases.append((alias, form['pua'], form.get('identification')))

    glyph_set = {}
    glyphs = {name: glyph(outline, glyph_set) for name, outline in drawings.items()}
    builder = FontBuilder(ADVANCE, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(widths)
    builder.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)
    builder.setupNameTable({
        'copyright': 'Forms traced from a public-domain photograph of Nova N 176 folio 9 '
                     '(V. P. Zaytsev 2011, fig. 4); the photograph is PD-scan (PD-old-100).',
        'familyName': 'Nova N 176 Running',
        'styleName': 'Regular',
        'uniqueFontIdentifier': 'NovaN176Running-Regular;1.000;2026',
        'fullName': 'Nova N 176 Running Regular',
        'version': 'Version 1.000',
        'psName': 'NovaN176Running-Regular',
        'designer': 'Traced for the Khitan Input project',
        'description': '96 running-script forms cut from folio 9 of the Khitan large-script '
                       'manuscript Nova N 176. The forms stand at page-local Private Use code '
                       'points U+E600-U+E65F in reading order; four identified forms also answer '
                       'at BabelStone points U+E05A, U+E28F, U+E396 and U+E03C.',
        'licenseDescription': 'The source photograph is public domain. The traced outlines are '
                              'derived from it.',
        'licenseInfoURL': 'https://github.com/mkpoli/khitan-input/blob/main/data/running/README.md',
        'vendorURL': 'https://commons.wikimedia.org/wiki/File:Nova_N_176_folio_9.jpg',
        'designerURL': 'https://khitan.mkpo.li/',
    })
    builder.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=-DESCENT,
        sxHeight=500,
        sCapHeight=700,
        achVendID='MKPO',
        fsType=0,
    )
    builder.setupPost()
    builder.font['head'].created = TIMESTAMP
    builder.font['head'].modified = TIMESTAMP
    TTF.parent.mkdir(parents=True, exist_ok=True)
    builder.save(TTF)
    builder.font.flavor = 'woff2'
    builder.save(WOFF2)
    print(f'{TTF.relative_to(ROOT)}: {len(order)} glyphs, {TTF.stat().st_size} bytes')
    print(f'{WOFF2.relative_to(ROOT)}: {WOFF2.stat().st_size} bytes')
    print('aliases:', ', '.join(f'{alias}->{pua} ({name})' for alias, pua, name in aliases))


if __name__ == '__main__':
    main()

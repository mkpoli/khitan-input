# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.2.6", "pillow==11.3.0", "scipy==1.18.1"]
# ///
"""Draw the specimen for the Nova N 176 running-script face.

    uv run scripts/build_running_specimen.py
"""
from __future__ import annotations

import gzip
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
CUTS = ROOT / 'data/running/cuts.json'
FORMS = ROOT / 'data/running/forms.json.gz'
FONT = ROOT / 'fonts/NovaN176Running-Regular.ttf'
SOURCE = ROOT / 'cache/running/Nova_N_176_folio_9.jpg'
OUT = ROOT / 'docs/running-specimen.png'

WIDTH, HEIGHT = 1800, 2000
PAPER = (247, 245, 239)
INK = (28, 28, 26)
MUTED = (112, 108, 100)
RED = (176, 48, 40)


def main() -> None:
    """Render the source page, the seven anchors and every cut form."""
    if not SOURCE.exists():
        raise SystemExit(f'{SOURCE.relative_to(ROOT)} is missing; run scripts/build_running_forms.py first')
    cuts = json.loads(CUTS.read_text(encoding='utf-8'))
    record = json.load(gzip.open(FORMS, 'rt', encoding='utf-8'))
    source = Image.open(SOURCE).convert('RGB')
    cut_font = ImageFont.truetype(str(FONT), 104)
    grid_font = ImageFont.truetype(str(FONT), 46)
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 46)
    subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    label_font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 17)
    small_font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 13)
    index_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)

    canvas = Image.new('RGB', (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 48), 'Nova N 176, folio 9', font=title_font, fill=INK)
    draw.text((62, 112), 'Running-script Khitan large script · 96 forms cut from one page',
              font=subtitle_font, fill=MUTED)

    scale = 860 / source.height
    page = source.resize((round(source.width * scale), 860), Image.LANCZOS)
    canvas.paste(page, (60, 190))
    draw.rectangle([60, 190, 60 + page.width, 190 + page.height], outline=(198, 192, 180))

    anchors = [form for form in record['forms'] if form.get('identification')]
    for number, form in enumerate(anchors, start=1):
        x, y, w, h = form['box']
        x0, y0 = 60 + x * scale, 190 + y * scale
        x1, y1 = x0 + w * scale, y0 + h * scale
        draw.rectangle([x0, y0, x1, y1], outline=RED, width=3)
        draw.text((x0 + 3, max(192, y0 - 20)), str(number), font=label_font, fill=RED)

    draw.text((790, 196), 'The state name at the head of column 6', font=subtitle_font, fill=MUTED)
    draw.text((790, 226), 'Seven forms; 大, 契, 丹 and 國 also answer at BabelStone points.',
              font=small_font, fill=MUTED)
    for number, form in enumerate(anchors, start=1):
        column = (number - 1) % 4
        row = (number - 1) // 4
        x = 800 + column * 245
        y = 280 + row * 225
        draw.text((x, y), chr(int(form['pua'], 16)), font=cut_font, fill=INK)
        name = (form.get('identification') or '').replace('ʤ', 'j')
        alias = form['aliases'][0] if form['aliases'] else ''
        caption = f"U+{form['pua']}  {name}"
        if alias:
            caption += f"  ·  U+{alias}"
        draw.text((x, y + 125), caption, font=label_font, fill=MUTED)
        draw.text((x, y + 149), f'{number}. column 6', font=small_font, fill=MUTED)

    draw.text((60, 1120), 'Every cut form, in reading order', font=subtitle_font, fill=MUTED)
    columns = 12
    cell_w, cell_h = 140, 80
    for index, form in enumerate(record['forms']):
        column = index % columns
        row = index // columns
        x = 60 + column * cell_w
        y = 1140 + row * cell_h
        draw.text((x + 20, y), chr(int(form['pua'], 16)), font=grid_font, fill=INK)
        draw.text((x + 20, y + 50), f"U+{form['pua']}", font=index_font, fill=MUTED)

    draw.text((60, 1955),
              'Source: Nova N 176 folio 9, photograph from V. P. Zaytsev (2011), fig. 4; public domain. '
              'Boxes and traced outlines: data/running/.',
              font=small_font, fill=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, optimize=True)
    print(f'{OUT.relative_to(ROOT)}: {canvas.width}x{canvas.height}, {OUT.stat().st_size} bytes')


if __name__ == '__main__':
    main()

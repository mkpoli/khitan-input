# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.5.5", "pillow==13.0.0", "scipy==1.18.1", "scikit-image==0.26.0"]
# ///
"""Write one centred colour cut and one ink mask for each Xuanyi block.

The cuts are for redrawing or vectorising outside this repository: each is a 512-square image with
the block centred on black, a 12 per cent margin, and no neighbour strokes.

    uv run scripts/build_seal_cuts.py
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import closing, disk, remove_small_objects

ROOT = pathlib.Path(__file__).resolve().parents[1]
CUTS = ROOT / 'data/seal/font/cuts.json'
OUT = ROOT / 'data/seal/font/cuts'
SHEET = ROOT / 'docs/seal-cuts.png'
SIZE = 512


def ink_mask(cell: Image.Image, stone: np.ndarray, paint: np.ndarray, projection: float) -> np.ndarray:
    """Paint on black, keeping the largest connected cluster."""
    values = np.asarray(cell).astype(float)
    direction = paint - stone
    t = ((values - stone) * direction).sum(axis=2) / (direction * direction).sum()
    mask = t > projection
    mask = remove_small_objects(mask, max_size=99)
    mask = closing(mask, disk(1))
    labels, count = ndimage.label(mask, np.ones((3, 3)))
    if count:
        areas = ndimage.sum(mask, labels, range(1, count + 1))
        main = int(np.argmax(areas)) + 1
        ys, xs = np.where(labels == main)
        left, right = xs.min() - 12, xs.max() + 12
        top, bottom = ys.min() - 12, ys.max() + 12
        keep = np.zeros(count + 1, bool)
        for index in range(1, count + 1):
            ys, xs = np.where(labels == index)
            if xs.max() < left or xs.min() > right or ys.max() < top or ys.min() > bottom:
                continue
            keep[index] = True
        mask = keep[labels]
    return mask


def square(image: Image.Image) -> Image.Image:
    """Fit an image into a SIZE square on black with a small margin."""
    scale = min((SIZE - 24) / image.width, (SIZE - 24) / image.height)
    resized = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)
    canvas = Image.new('RGB', (SIZE, SIZE), 'black')
    canvas.paste(resized, ((SIZE - resized.width) // 2, (SIZE - resized.height) // 2))
    return canvas


def main() -> None:
    cuts = json.loads(CUTS.read_text(encoding='utf-8'))
    cover = Image.open(ROOT / 'app/public' / cuts['cover'].lstrip('/')).convert('RGB')
    panel = cover.transform((800, 800), Image.QUAD,
                            [*cuts['rectify'][0], *cuts['rectify'][3],
                             *cuts['rectify'][2], *cuts['rectify'][1]], resample=Image.BICUBIC)
    pixels = np.asarray(panel).astype(float).reshape(-1, 3)
    stone = np.percentile(pixels, 10, axis=0)
    paint = np.percentile(pixels, 99, axis=0)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'masks').mkdir(exist_ok=True)
    label = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 26)
    sheet = Image.new('RGB', (1200, 1250), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    draw.text((30, 24), 'Qingling Seal · 16 cut blocks', font=title, fill='white')
    draw.text((30, 58), 'Colour above, ink mask below; each block centred on black.', font=label, fill=(190, 190, 190))
    for index, form in enumerate(cuts['forms']):
        x0, y0, x1, y1 = form['box']
        colour = panel.crop((x0, y0, x1, y1))
        mask = ink_mask(colour, stone, paint, cuts['projection'])
        ys, xs = np.where(mask)
        if len(xs):
            pad = 10
            left, right = max(0, xs.min() - pad), min(mask.shape[1], xs.max() + pad)
            top, bottom = max(0, ys.min() - pad), min(mask.shape[0], ys.max() + pad)
            colour = colour.crop((left, top, right, bottom))
            mask = mask[top:bottom, left:right]
        colour = square(colour)
        ink = Image.fromarray((mask * 255).astype(np.uint8)).convert('RGB')
        ink = square(ink)
        colour.save(OUT / f"{form['id']}.png")
        ink.save(OUT / 'masks' / f"{form['id']}.png")
        column, row = index % 4, index // 4
        cell_x, cell_y = 30 + column * 290, 95 + row * 285
        sheet.paste(colour.resize((250, 250), Image.LANCZOS), (cell_x, cell_y))
        draw.text((cell_x, cell_y + 255), form['id'], font=label, fill=(220, 220, 220))
    sheet.save(SHEET, optimize=True)
    print(f'{OUT.relative_to(ROOT)}: 16 colour cuts, masks/ optional')
    print(f'{SHEET.relative_to(ROOT)}: {sheet.width}x{sheet.height}')


if __name__ == '__main__':
    main()

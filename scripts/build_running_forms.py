# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy==2.2.6",
#   "pillow==11.3.0",
#   "potracer==0.0.4",
#   "scipy==1.18.1",
# ]
# ///
"""Cut and trace the running-script forms of Nova N 176 folio 9.

`data/running/cuts.json` holds the reviewed character boxes: six ruled columns, one box per
written character, and the state name at the head of column 6 corrected by hand. This script
fetches the public-domain photograph once into `cache/running/`, separates the ink from the
paper, drops the ruled lines and neighbouring strokes at the box edges, traces each form with
potrace, and writes `data/running/forms.json.gz`.

    uv run scripts/build_running_forms.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import pathlib
import urllib.request

import numpy as np
import potrace
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[1]
CUTS = ROOT / 'data/running/cuts.json'
OUT = ROOT / 'data/running/forms.json.gz'
CACHE = ROOT / 'cache/running'

EM = 1000
INK = 880
CENTER_X = 500
CENTER_Y = 372
# The box is cut this far inside the column's ruled edges, which keeps the rules out of the mask.
LEFT = 8
RIGHT = 8
MIN_HALF_WIDTH = 70
Y_TRIM = 3


def fetch(source: dict) -> Image.Image:
    """Read the page photograph, downloading it once and checking its digest."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / source['image']
    if not path.exists():
        request = urllib.request.Request(
            source['url'], headers={'User-Agent': 'khitan-input/0.1 (https://khitan.mkpo.li/)'})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != source['sha256']:
            raise SystemExit(f'{path.name}: expected {source["sha256"]}, downloaded {digest}')
        path.write_bytes(data)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != source['sha256']:
        path.unlink()
        raise SystemExit(f'{path.name}: expected {source["sha256"]}, read {digest}')
    image = Image.open(path)
    if image.size != (source['width'], source['height']):
        raise SystemExit(f'{path.name}: expected {source["width"]}x{source["height"]}, read {image.size}')
    return image.convert('L')


def otsu(values: np.ndarray) -> float:
    """The threshold that best separates ink from paper in a greyscale array."""
    histogram, _ = np.histogram(values, bins=256, range=(0, 1))
    probability = histogram.astype(np.float64)
    probability /= probability.sum()
    omega = np.cumsum(probability)
    mu = np.cumsum(probability * np.arange(256))
    total = mu[-1]
    denominator = omega * (1 - omega)
    with np.errstate(divide='ignore', invalid='ignore'):
        variance = np.where(denominator > 0, (total * omega - mu) ** 2 / denominator, -1)
    variance[~np.isfinite(variance)] = -1
    return (int(np.argmax(variance)) + 0.5) / 256


def mask_for(inkness: np.ndarray, column: dict, box: list[int]) -> np.ndarray | None:
    """The ink of one character, without the ruled edge or the neighbour's strokes."""
    centre = box[0] + box[2] / 2
    half = max(MIN_HALF_WIDTH, box[2] / 2 + 20)
    x0 = max(column['x0'] + LEFT, round(centre - half))
    x1 = min(column['x1'] - RIGHT, round(centre + half))
    y0 = max(0, box[1] + Y_TRIM)
    y1 = box[1] + box[3] - Y_TRIM
    crop = inkness[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    mask = crop > max(0.20, otsu(crop))
    # The crop's own edge holds the rule line and the neighbour's strokes; neither is the glyph.
    mask[:, :3] = False
    mask[:, -3:] = False
    mask[:2, :] = False
    mask[-2:, :] = False
    labelled, count = ndimage.label(mask, np.ones((3, 3)))
    if count == 0:
        return None
    sizes = ndimage.sum(mask, labelled, range(1, count + 1))
    centroids = ndimage.center_of_mass(mask, labelled, range(1, count + 1))
    height, width = mask.shape
    main = int(np.argmax(sizes)) + 1
    main_ys, main_xs = np.where(labelled == main)
    main_area = sizes[main - 1]
    top, bottom = max(0, main_ys.min() - height * 0.02), min(height, main_ys.max() + height * 0.02)
    left, right = max(0, main_xs.min() - width * 0.02), min(width, main_xs.max() + width * 0.02)
    keep = np.zeros(count + 1, bool)
    for index in range(1, count + 1):
        if sizes[index - 1] < 25:
            continue
        cy, cx = centroids[index - 1]
        # A fleck far from the character's main strokes is a neighbour or a speck of the paper.
        if sizes[index - 1] < 0.015 * main_area and not (top <= cy <= bottom and left <= cx <= right):
            continue
        # A neighbour's stroke sits at the top or bottom edge; the character's own strokes do not.
        if not 0.08 * height <= cy <= 0.92 * height:
            continue
        ys, xs = np.where(labelled == index)
        component_h = ys.max() - ys.min() + 1
        component_w = xs.max() - xs.min() + 1
        # A ruled line at the column edge, broken by the crop into short segments.
        if component_h > 0.5 * height and component_w < 7 and (xs.min() <= 1 or xs.max() >= width - 2):
            continue
        keep[index] = True
    if not keep.any():
        keep[1:] = sizes > 25
    return keep[labelled]


def trace(mask: np.ndarray, upscale: int = 8) -> list[list]:
    """Trace a mask with potrace and return path commands in pixels."""
    mask = ndimage.gaussian_filter(mask.astype(np.float32), 1.0) > 0.5
    image = Image.fromarray((mask * 255).astype(np.uint8))
    image = image.resize((image.width * upscale, image.height * upscale), Image.LANCZOS)
    bitmap = potrace.Bitmap(~(np.asarray(image) > 127))
    path = bitmap.trace(turdsize=20, alphamax=1.3, opticurve=True, opttolerance=0.4)
    commands: list[list] = []
    for curve in path:
        start = curve.start_point
        commands.append(['M', start.x, start.y])
        for segment in curve:
            if segment.is_corner:
                commands.append(['L', segment.c.x, segment.c.y])
                commands.append(['L', segment.end_point.x, segment.end_point.y])
            else:
                commands.append(['C', segment.c1.x, segment.c1.y, segment.c2.x, segment.c2.y,
                                 segment.end_point.x, segment.end_point.y])
        commands.append(['Z'])
    return commands


def normalise(commands: list[list]) -> list[list]:
    """Fit a traced path into the em box and flip the image's y axis."""
    xs = [point for command in commands for point in command[1::2]]
    ys = [point for command in commands for point in command[2::2]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = INK / max(x1 - x0, y1 - y0, 1)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for command in commands:
        operator, values = command[0], command[1:]
        mapped = []
        for index in range(0, len(values), 2):
            mapped.append(round(CENTER_X + (values[index] - mx) * scale))
            mapped.append(round(CENTER_Y + (my - values[index + 1]) * scale))
        out.append([operator, *mapped])
    return out


def validate(cuts: dict, image: Image.Image) -> None:
    """Check the reviewed boxes before any outline is written."""
    width, height = image.size
    columns = {column['col'] for column in cuts['columns']}
    if columns != set(range(1, 7)):
        raise SystemExit(f'columns must be 1..6, read {sorted(columns)}')
    seen = set()
    for index, form in enumerate(cuts['forms']):
        expected = f'E{0x600 + index:03X}'
        if form['pua'] != expected:
            raise SystemExit(f"form {index}: expected {expected}, read {form['pua']}")
        if form['col'] not in columns:
            raise SystemExit(f"{form['pua']}: column {form['col']} is not on the page")
        x, y, w, h = form['box']
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > width or y + h > height:
            raise SystemExit(f"{form['pua']}: box {form['box']} leaves the {width}x{height} page")
        key = (form['col'], x, y, w, h)
        if key in seen:
            raise SystemExit(f"{form['pua']}: duplicate box {form['box']}")
        seen.add(key)


def main() -> None:
    """Write data/running/forms.json.gz from the reviewed boxes and the photograph."""
    cuts = json.loads(CUTS.read_text(encoding='utf-8'))
    image = fetch(cuts['source'])
    validate(cuts, image)
    grey = np.asarray(image, dtype=np.float32) / 255
    paper = ndimage.gaussian_filter(ndimage.grey_closing(grey, size=(61, 61)), 25)
    inkness = np.clip(1 - grey / np.maximum(paper, 1e-3), 0, 1)
    columns = {column['col']: column for column in cuts['columns']}

    forms = []
    dropped = []
    for cut in cuts['forms']:
        mask = mask_for(inkness, columns[cut['col']], cut['box'])
        if mask is None or mask.sum() < 80:
            dropped.append(cut['pua'])
            continue
        commands = trace(mask)
        if not commands:
            dropped.append(cut['pua'])
            continue
        forms.append({
            **cut,
            'outline': normalise(commands),
            'ink': round(float((inkness[cut['box'][1]:cut['box'][1] + cut['box'][3],
                                       cut['box'][0]:cut['box'][0] + cut['box'][2]] > 0.3).mean()), 3),
            'mask_pixels': int(mask.sum()),
        })
    if dropped:
        raise SystemExit(f'{len(dropped)} boxes traced nothing: {dropped}')
    if len(forms) != len(cuts['forms']):
        raise SystemExit(f'expected {len(cuts["forms"])} forms, traced {len(forms)}')

    record = {
        'source': cuts['source'],
        'metrics': {'unitsPerEm': EM, 'advance': 1000, 'ink': INK,
                    'center': [CENTER_X, CENTER_Y]},
        'columns': cuts['columns'],
        'forms': forms,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, 'wt', encoding='utf-8', compresslevel=9) as handle:
        json.dump(record, handle, ensure_ascii=False, separators=(',', ':'))
    print(f'{OUT.relative_to(ROOT)}: {len(forms)} forms, {OUT.stat().st_size} bytes')


if __name__ == '__main__':
    main()

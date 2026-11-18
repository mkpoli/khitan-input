# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==11.3.0"]
# ///
"""Cut the two seal-script covers from their Commons photographs.

`data/seal/cuts.json` holds the two photographs, the rectangles that hold the covers, and one
locator box for each block. This script fetches each photograph once into `cache/seal/`, checks
its digest, crops the cover, writes the WebP the page displays, and stores the locator boxes as
fractions of that crop in `data/seal/records.json`.

The boxes place a block on the cover; they are not traced outlines. Xuanyi blocks carry the Unicode
correspondence from `data/seal/correspondences.json`; Daozong blocks remain unidentified.

    uv run scripts/build_seal_images.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
CUTS = ROOT / 'data/seal/cuts.json'
OUT = ROOT / 'data/seal/records.json'
CORRESPONDENCES = ROOT / 'data/seal/correspondences.json'
CACHE = ROOT / 'cache/seal'
PUBLIC = ROOT / 'app/public/seal'


def fetch(source: dict) -> Image.Image:
    """Read a source photograph, downloading it once and checking its digest."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{source['id']}.jpg"
    if not path.exists():
        request = urllib.request.Request(
            source['image'], headers={'User-Agent': 'khitan-input/0.1 (https://khitan.mkpo.li/)'})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != source['sha256']:
            raise SystemExit(f"{path.name}: expected {source['sha256']}, downloaded {digest}")
        path.write_bytes(data)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != source['sha256']:
        path.unlink()
        raise SystemExit(f"{path.name}: expected {source['sha256']}, read {digest}")
    image = Image.open(path)
    if image.size != (source['width'], source['height']):
        raise SystemExit(f"{path.name}: expected {source['width']}x{source['height']}, read {image.size}")
    return image.convert('RGB')


def validate(cuts: dict) -> None:
    """Check the reviewed layout before anything is written."""
    sources = {source['id'] for source in cuts['sources']}
    inscriptions = {inscription['id']: inscription for inscription in cuts['inscriptions']}
    if len(inscriptions) != len(cuts['inscriptions']):
        raise SystemExit('inscription ids must be unique')
    for inscription in cuts['inscriptions']:
        if inscription['source'] not in sources:
            raise SystemExit(f"{inscription['id']}: unknown source {inscription['source']}")
        x, y, right, bottom = inscription['crop']
        if not (0 <= x < right and 0 <= y < bottom):
            raise SystemExit(f"{inscription['id']}: bad crop {inscription['crop']}")
        columns = {form['col'] for form in cuts['forms'] if form['inscription'] == inscription['id']}
        if columns != set(range(1, inscription['columns'] + 1)):
            raise SystemExit(f"{inscription['id']}: columns are not 1..{inscription['columns']}")
    seen = set()
    for form in cuts['forms']:
        if form['id'] in seen:
            raise SystemExit(f"duplicate form id {form['id']}")
        seen.add(form['id'])
        inscription = inscriptions.get(form['inscription'])
        if inscription is None:
            raise SystemExit(f"{form['id']}: unknown inscription")
        if not 1 <= form['col'] <= inscription['columns']:
            raise SystemExit(f"{form['id']}: column out of range")
        if not 1 <= form['row'] <= inscription['rows']:
            raise SystemExit(f"{form['id']}: row out of range")


def main() -> None:
    """Write the cover images and the page record."""
    cuts = json.loads(CUTS.read_text(encoding='utf-8'))
    validate(cuts)
    sources = {source['id']: source for source in cuts['sources']}
    images = {}
    PUBLIC.mkdir(parents=True, exist_ok=True)

    inscriptions = []
    for inscription in cuts['inscriptions']:
        source = sources[inscription['source']]
        if source['id'] not in images:
            images[source['id']] = fetch(source)
        left, top, right, bottom = inscription['crop']
        cover = images[source['id']].crop((left, top, right, bottom))
        width = inscription['image_width']
        height = round(cover.height * width / cover.width)
        if height != inscription['image_height']:
            raise SystemExit(
                f"{inscription['id']}: expected {inscription['image_width']}x{inscription['image_height']}, "
                f"the crop makes {width}x{height}")
        cover = cover.resize((width, height), Image.LANCZOS)
        path = PUBLIC / pathlib.Path(inscription['image']).name
        cover.save(path, 'WEBP', quality=86, method=6)
        inscriptions.append({
            **inscription,
            'source_record': source,
            'image_bytes': path.stat().st_size,
        })

    correspondences = json.loads(CORRESPONDENCES.read_text(encoding='utf-8'))['blocks']
    forms = []
    for form in cuts['forms']:
        match = correspondences.get(form['id'])
        if match:
            forms.append({**form, **match, 'identification': match['character']})
        else:
            forms.append({
                **form,
                'identification': None,
                'unicode': None,
                'status': 'unidentified',
                'basis': 'No block of the Daozong cover has been assigned a reading here. '
                         'The Xuanyi blocks are matched to BabelStone Khitan Small Seal.',
            })

    record = {
        'sources': cuts['sources'],
        'inscriptions': inscriptions,
        'forms': forms,
        'counts': {
            'inscriptions': len(inscriptions),
            'forms': len(forms),
            'identified': sum(1 for form in forms if form['identification']),
        },
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{OUT.relative_to(ROOT)}: {len(forms)} forms, {sum(1 for f in forms if f["identification"])} identified')
    for inscription in inscriptions:
        print(f"  {inscription['image']}: {inscription['image_width']}x{inscription['image_height']}, "
              f"{inscription['image_bytes']} bytes")


if __name__ == '__main__':
    main()

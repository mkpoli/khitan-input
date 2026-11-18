# /// script
# requires-python = ">=3.12"
# dependencies = ["brotli==1.2.1", "fonttools==4.68.0", "pillow==13.0.0"]
# ///
"""Check the shipped variable faces for lost apertures at specimen sizes."""
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def topology(image):
    """Count ink islands and enclosed white spaces at half pixel coverage."""
    mask = image.point(lambda value: 255 if value >= 128 else 0)
    pixels = mask.load()
    regions = {0: 0, 255: 0}
    for y in range(mask.height):
        for x in range(mask.width):
            value = pixels[x, y]
            if value in regions:
                regions[value] += 1
                ImageDraw.floodfill(mask, (x, y), 128)
    return regions[255], regions[0] - 1  # Exclude the white margin.


def check(path, size):
    font = TTFont(path)
    glyphs = [(chr(code), False) for code in font.getBestCmap()]
    glyphs.append((chr(0x18C64), True))
    font.flavor = None  # FreeType in Pillow accepts sfnt input for both formats.
    data = BytesIO()
    font.save(data)
    data.seek(0)
    face = ImageFont.truetype(data, size)
    regular = {}
    for weight in (400, 500, 600, 700, 750, 800):
        face.set_variation_by_axes([weight])
        for char, alternate in glyphs:
            image = Image.new('L', (size + 20, size + 20))
            ImageDraw.Draw(image).text((8, 8 + .83 * size), char, anchor='ls',
                                       font=face, features=['ss01'] if alternate else [], fill=255)
            actual = topology(image)
            key = (char, alternate)
            if weight == 400:
                regular[key] = actual
            elif actual != regular[key]:
                raise AssertionError(f'{path.name} U+{ord(char):05X} ss01={alternate} '
                                     f'{size}px wght={weight}: {actual} vs regular {regular[key]}')


if __name__ == '__main__':
    for name in ('QinglingSeal-Regular.ttf', 'QinglingSeal-Regular.woff2'):
        for size in (76, 128):
            check(ROOT / 'fonts' / name, size)
        print(f'{name}: apertures verified at six weights and two sizes')

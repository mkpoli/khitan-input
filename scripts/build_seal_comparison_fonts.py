# /// script
# dependencies = ["fonttools[woff]"]
# ///
"""Build the comparison webfonts from the pinned Sealie and Zhuque sources."""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("sealie", type=Path)
parser.add_argument("zhuque", type=Path)
args = parser.parse_args()
rows = json.loads((ROOT / "data/seal/font/analogues.json").read_text())
for family, source, digest, points in [
    ("Sealie", args.sealie, "81b448889d484731ecc803a9514fd6888a29678bc28584fa11bfc540048e3581",
     {int(row["smallSeal"][2:], 16) for row in rows}),
    ("Zhuque", args.zhuque, "5cb9aca8a85825a204ba58c9e975d8298e7370494b845694ee8a6882d0d6ed37",
     {ord(row["han"]) for row in rows}),
]:
    if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        parser.error(f"unexpected {family} source checksum")
    font = TTFont(source, recalcTimestamp=False)
    if points.difference(font.getBestCmap()):
        parser.error(f"{family} is missing a comparison character")
    options = subset.Options()
    options.name_IDs = ["*"]
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=points)
    subsetter.subset(font)
    name = "Khitan Comparison " + family
    for record in font["name"].names:
        if record.nameID in (1, 3, 4, 6, 16):
            value = name.replace(" ", "") if record.nameID == 6 else name
            record.string = value.encode(record.getEncoding())
    font.flavor = "woff2"
    font.save(ROOT / f"app/public/fonts/Comparison{family}.woff2")

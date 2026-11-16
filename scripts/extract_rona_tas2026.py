#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf"]
# ///
"""Róna-Tas (2026) 19.1, the Höhhot list of KSS glyphs revised, into data/unicode/rona_tas2026_list.tsv.

usage: scripts/extract_rona_tas2026.py <volume two PDF>

The list numbers graphemes by the CWJ (2017) index and sets each glyph in the Menksoft Khitan font,
whose Private Use code points follow that index. A whole number is the 1985 number, so West's mapping
gives its code point. Additions with a decimal number, and the two places where CWJ swaps the 1985
forms, were matched by eye and are kept in data/unicode/rona_tas2026_visual.tsv.
"""
import csv
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "unicode" / "rona_tas2026_list.tsv"
FIRST_PAGE = 803  # printed page of the list's first page
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = {"a": "ᵃ", "e": "ᵉ", "i": "ⁱ", "o": "ᵒ", "u": "ᵘ"}
# Two values whose small type is set off its line in 19.1, as the book's own index (19.2) prints them.
MISSET = {"236": "ur₂", "240.1": "parᵒ"}
ENTRY = re.compile(r"(\d{2,3}(?:\.\d+)?)\s+([-])\s*([^\s-]*(?:\s+n\.i\.?)?)")


def list_pages(doc: pymupdf.Document) -> range:
    first = next(i for i in range(20, len(doc)) if "HÖHHOT LIST OF KSS GLYPHS REVISED" in doc[i].get_text())
    last = next(i for i in range(first, len(doc)) if "19.2 ALPHABETICAL LIST" in doc[i].get_text())
    return range(first, last + 1)


def rows_of(page: pymupdf.Page) -> list[str]:
    """Lines of the page rebuilt by baseline. Small type below the baseline is a homophone index, small
    letters above it are part of the value, and small digits above it are footnote calls."""
    spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()]
    rows: list[dict] = []
    for s in sorted((s for s in spans if s["size"] >= 10), key=lambda s: s["origin"][1]):
        if rows and abs(rows[-1]["y"] - s["origin"][1]) < 3:
            rows[-1]["spans"].append(s)
        else:
            rows.append({"y": s["origin"][1], "spans": [s]})
    for s in spans:
        if s["size"] < 10 and rows:
            row = min(rows, key=lambda r: abs(r["y"] - s["origin"][1]))
            if abs(row["y"] - s["origin"][1]) < 6:
                row["spans"].append(s)
    out = []
    for row in rows:
        text, right = "", None
        for s in sorted(row["spans"], key=lambda s: s["bbox"][0]):
            piece = s["text"].replace("\t", " ")
            if s["size"] < 10:
                lowered = s["origin"][1] - row["y"] > 0.5
                if lowered:
                    piece = piece.translate(SUB)
                elif piece.strip().isdigit():
                    piece = ""
                else:
                    piece = "".join(SUP.get(c, c) for c in piece.strip())
            elif right is not None and s["bbox"][0] - right > 2:
                text += " "
            text += piece
            right = s["bbox"][2]
        out.append(text)
    return out


def west_1985() -> dict[str, str]:
    numbers: dict[str, str] = {}
    with open(ROOT / "data" / "unicode" / "kss_mappings.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for n in re.split(r"[;,/ ]+", r["chinggeltei1985"] or ""):
                if n.strip():
                    numbers.setdefault(n.strip().lstrip("0"), r["codepoint"])
    return numbers


def main() -> None:
    doc = pymupdf.open(sys.argv[1])
    pages = list_pages(doc)
    with open(ROOT / "data" / "unicode" / "rona_tas2026_visual.tsv", encoding="utf-8") as f:
        visual = {r["menksoft"]: r for r in csv.DictReader(f, delimiter="\t")}
    west = west_1985()
    entries: dict[str, list] = {}
    for index in pages:
        for line in rows_of(doc[index]):
            for m in ENTRY.finditer(line):
                number, glyph, printed = m.groups()
                menksoft = f"{ord(glyph):04X}"
                if menksoft in entries:
                    continue
                not_initial = bool(re.search(r"n\.i", printed))
                value = re.sub(r",?\s*n\.i\.?$", "", printed).strip(" ,.")
                # A repeated list number means the glyph has no reading yet.
                if re.fullmatch(r"[\d.]+", value):
                    value = ""
                value = MISSET.get(number, value)
                if menksoft in visual:
                    codepoint, method = visual[menksoft]["codepoint"], "visual" if visual[menksoft]["codepoint"] else ""
                else:
                    codepoint, method = west.get(number.lstrip("0"), ""), "west_1985_number"
                entries[menksoft] = [number, menksoft, codepoint, method, value, int(not_initial), FIRST_PAGE + index - pages.start]
    rows = sorted(entries.values(), key=lambda r: float(r[0]))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["cwj_no", "menksoft", "codepoint", "unicode_method", "value", "not_initial", "page"])
        w.writerows(rows)
    print(f"{len(rows)} graphemes, {sum(1 for r in rows if r[2])} with a code point, {sum(1 for r in rows if r[4])} with a value")


if __name__ == "__main__":
    main()

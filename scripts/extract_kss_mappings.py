#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf"]
# ///
"""Code point to catalogue numbers, from West's KSS_Mappings.pdf.

usage: scripts/extract_kss_mappings.py cache/web/KSS_Mappings.pdf > data/unicode/kss_mappings.tsv
"""
import csv
import re
import sys

import pymupdf

COLUMNS = {
    "n4725r": 160, "n3820": 250, "n3918": 299, "chinggeltei1985": 351, "chinggeltei2002": 400,
    "chinggeltei2010": 449, "jishi1996": 498, "jishi2012": 547, "kane2009": 596, "liu2009": 645,
    "liu2014": 694, "jiruhe_wu2009": 742, "wu_janhunen2010": 794, "takeuchi2012": 847,
    "liu_kang2014": 897, "aisin_gioro2012": 942,
}


def main() -> None:
    doc = pymupdf.open(sys.argv[1])
    out = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    out.writerow(["codepoint", *COLUMNS])
    seen = set()
    for page in doc:
        words = page.get_text("words")
        codes = sorted((w for w in words if re.fullmatch(r"1[6-8][0-9A-F]{3}", w[4]) and w[0] < 90), key=lambda w: w[1])
        if not codes:
            continue
        mids = [(a[1] + b[1]) / 2 for a, b in zip(codes, codes[1:])]
        for i, code in enumerate(codes):
            if code[4] in seen:  # later pages cite code points in their notes
                continue
            seen.add(code[4])
            top = mids[i - 1] if i else code[1] - 16
            bottom = mids[i] if i < len(mids) else code[1] + 16
            cells: dict[str, list[str]] = {k: [] for k in COLUMNS}
            for w in sorted(words, key=lambda w: (w[1], w[0])):
                if not top <= (w[1] + w[3]) / 2 < bottom or w[0] < 130:
                    continue
                name = min(COLUMNS, key=lambda k: abs(COLUMNS[k] - ((w[0] + w[2]) / 2 - 8)))
                if abs(COLUMNS[name] - ((w[0] + w[2]) / 2 - 8)) < 24 and re.search(r"[\dA-Za-z]", w[4]):
                    cells[name].append(w[4])
            out.writerow([code[4], *(" ".join(cells[k]) for k in COLUMNS)])


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf"]
# ///
"""Readings from N4725R Table 6 and West's HTML lists into data/.

usage: scripts/extract_web_layers.py   (reads cache/web/)
"""
import csv
import html
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).parent.parent
WEB = ROOT / "cache" / "web"
COLS = {"liu2009": 110, "liu2014": 158, "chinggeltei2010": 206, "kane2009": 261, "wu_janhunen2010": 330,
        "jishi2012": 399, "takeuchi2012": 454, "relation": 516}


HEADER = {"Liu", "2009", "2010", "2012", "2014", "Ching.", "Kane", "Wu", "&", "Jan.", "Jishi", "Takeuchi", "Relation-", "ship"}


def write(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(path.name, len(rows))


def table6() -> None:
    doc = pymupdf.open(WEB / "16113r-n4725r-khitan-small-script.pdf")
    rows = []
    pua = {}
    for i in range(78, 104):
        page = doc[i]
        words = page.get_text("words")
        nums = sorted((w for w in words if w[0] < 62 and re.fullmatch(r"\d{1,3}", w[4]) and w[1] > 95), key=lambda w: w[1])
        mids = [(a[1] + b[1]) / 2 for a, b in zip(nums, nums[1:])]
        for k, n in enumerate(nums):
            top = mids[k - 1] if k else n[1] - 22
            bottom = mids[k] if k < len(mids) else n[1] + 26
            cells = {c: [] for c in COLS}
            for w in sorted(words, key=lambda w: (w[1], w[0])):
                y = (w[1] + w[3]) / 2
                if not max(top, 97) <= y < bottom:
                    continue
                if 66 < w[0] < 100 and re.search(r"[-]", w[4]):
                    pua[w[4]] = int(n[4])
                    continue
                if w[0] < 100 or (not k and w[4] in HEADER):
                    continue
                col = max((c for c in COLS if COLS[c] <= w[0] + 2), key=lambda c: COLS[c], default=None)
                if col:
                    cells[col].append(w[4])
            rows.append([int(n[4]), *(" ".join(cells[c]) for c in COLS)])
    fixed = []
    for row in rows:
        rel = row[-1]
        row[-1] = re.sub(r"[-]", lambda m: f"#{pua[m[0]]}" if m[0] in pua else "#?", rel)
        fixed.append(row)
    write(ROOT / "data" / "unicode" / "n4725r_table6.tsv", ["n4725r", *COLS], fixed)


def clean(cell: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()


def kane() -> None:
    text = (WEB / "Kane2009List.html").read_text(encoding="utf8")
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", text, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 3:
            continue
        glyph = clean(tds[1])
        cps = " ".join(f"{ord(c):05X}" for c in glyph if 0x18B00 <= ord(c) <= 0x18CFF)
        rows.append([clean(tds[0]), cps, clean(tds[2]), clean(tds[3]) if len(tds) > 3 else ""])
    write(ROOT / "data" / "unicode" / "kane2009_index.tsv", ["kane_no", "codepoints", "value", "notes"], rows)


def liu_wang() -> None:
    text = (WEB / "LiuWang2004.html").read_text(encoding="utf8")
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", text, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 5:
            continue
        pua = " ".join(re.findall(r"/([0-9A-F]{4,5})\.png", tds[1]))
        rows.append([clean(tds[0]), pua, clean(tds[2]), clean(tds[3]), clean(tds[4])])
    write(ROOT / "data" / "large" / "liu_wang2004.tsv", ["number", "babelstone_pua", "reconstruction", "chinese_transcription", "meaning"], rows)


if __name__ == "__main__":
    table6()
    kane()
    liu_wang()

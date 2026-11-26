#!/usr/bin/env python3
"""Read Andrew West's survey of Khitan seals into data/seal/large/west2012.json.

`seals` has one record per seal: the fields the survey labels, and the sentences in which it reads
the whole seal face. `characters` is its table of ninefold seal-script characters. Khitan
characters stay on BabelStone's Private Use code points, as in the survey.

usage: scripts/extract_west_seals.py   (reads cache/web/babelstone/khitan-seals.html)
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PAGE = "https://www.babelstone.co.uk/Blog/2012/10/khitan-seals.html"
LABELS = {"References": "references", "Found at": "found", "Present Location": "held", "Description": "description", "Inscription": "inscription"}
READING = re.compile(r"thus means|can be translated as|has read the inscription on this seal as")


def text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def sentence(paragraph: str, at: int) -> str:
    """The sentence around `at`: from the last full stop before it to the first after it that ends a clause."""
    start = max(paragraph.rfind(". ", 0, at) + 2, 0) if ". " in paragraph[:at] else 0
    end = re.compile(r'[)"”]\.(?= |$)|\.(?= [A-Z]|$)').search(paragraph, at)
    return paragraph[start:end.end() if end else len(paragraph)].strip()


def seals(page: str) -> list[dict]:
    out = []
    parts = re.split(r'<h4 id="(Seal_[AB]\d+[A-C]?)">(.*?)</h4>', page)
    for anchor, title, body in zip(parts[1::3], parts[2::3], parts[3::3]):
        body = re.split(r"<h3|<hr", body)[0] if "<h3" in body else body
        body = re.sub(r'<(p|span) class="khitan_seals[^>]*>.*?</\1>', "", body, flags=re.S)  # the seal face, set in a face of its own
        paragraphs = [text(p) for p in re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", body, re.S)]
        row = {"id": text(title).removeprefix("Seal "), "kind": "ninefold" if anchor.startswith("Seal_A") else "other",
               "plate": "", "references": "", "found": "", "held": "", "description": "", "inscription": "", "reading": "", "remark": "", "url": f"{PAGE}#{anchor}"}
        loose = []
        for p in paragraphs:
            m = re.match(r"(References|Found at|Present Location|Description|Inscription)\s*:?\s*(.*)", p)
            if m and (":" in p[:len(m[1]) + 3] or m[1] == "Found at"):
                row[LABELS[m[1]]] = m[2].strip()
            elif p and p != "Interpretation":
                loose.append(p)
        captions = [p for p in loose if re.search(r"\b(p\.|plate|vol\.) ?\d+\.?$", p) and len(p) < 80]
        row["plate"] = captions[0].rstrip(".") if captions else ""
        readings = [sentence(p, m.start()) for p in loose for m in [READING.search(p)] if m]
        row["reading"] = " ".join(dict.fromkeys(readings))
        if row["kind"] == "other":  # the B seals carry a remark in place of labelled fields
            row["remark"] = " ".join(p for p in loose if len(p) > 80 and not READING.search(p))  # shorter ones caption the pictures
        out.append(row)
    return out


def characters(page: str) -> list[dict]:
    """One row per row of the survey's table; a cell spanning several rows is repeated on each."""
    table = page[page.index('id="Table"'):]
    table = table[:table.index("</table>")]
    out, carried = [], {}  # column -> (rows still covered, cell)
    for tr in re.findall(r"<tr>(.*?)</tr>", table, re.S)[1:]:
        cells = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
        row, column = [], 0
        while cells or column in carried:
            if column in carried:
                left, cell = carried[column]
                carried[column] = (left - 1, cell)
                if left == 1:
                    del carried[column]
            else:
                attrs, cell = cells.pop(0)
                span = re.search(r'rowspan="(\d+)"', attrs)
                if span and int(span[1]) > 1:
                    carried[column] = (int(span[1]) - 1, cell)
            row.append(cell)
            column += 1
        if len(row) != 7:
            raise SystemExit(f"the character table has a row of {len(row)} cells")
        glyphs = [g for c in row[:5] for g in re.findall(r"Seal/U_00(F[0-9A-F]{3})\.png", c)]
        out.append({"seal_glyphs": " ".join(glyphs), "standard": text(row[5]), "meaning": text(row[6])})
    return out


def main() -> None:
    page = (ROOT / "cache/web/babelstone/khitan-seals.html").read_text(encoding="utf8")
    rows, table = seals(page), characters(page)
    if len(rows) != 25 or not all(r["found"] or r["held"] or r["references"] or r["remark"] for r in rows):
        raise SystemExit(f"the survey's layout has changed: {len(rows)} seals")
    target = ROOT / "data/seal/large/west2012.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"source": {"id": "west2012_seals", "author": "Andrew West", "title": "Khitan Seals", "site": "BabelStone Blog", "date": "2012-10-16", "url": PAGE},
              "seals": [{k: v for k, v in r.items() if v} for r in rows], "characters": table}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
    print(len(rows), "seals,", len(table), "table rows")


if __name__ == "__main__":
    main()

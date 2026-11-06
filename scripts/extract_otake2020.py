#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf", "fonttools"]
# ///
"""Extract the structured data of Otake (2020) into data/otake2020/*.tsv.

usage: scripts/extract_otake2020.py <dissertation.pdf>
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from otake_pdf import Thesis, ids, printed  # noqa: E402

OUT = Path(__file__).parent.parent / "data" / "otake2020"
PAGES_DOCUMENTS = range(17, 37)
PAGES_RHYMES = range(463, 484)
PAGES_COGNATES = range(484, 535)
PAGES_LOANS = range(535, 587)
PAGES_BIBLIOGRAPHY = range(587, 614)
PAGES_APPENDIX_READINGS = range(122, 134)
PAGES_BODY = range(13, 463)

PHONE = r"[a-zəɵʊɪıäöüǰčšžňľŋγχğḥʷāēīōūȳāɵ̈A-Z]"
VALUE = re.compile(rf"\*?{PHONE}+(?:\?|\(\?\))?")
LABEL = r"(?:\d{3}[D?]?|C\d\d)"


def write(name: str, header: list[str], rows: list[list]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.tsv", "w", newline="", encoding="utf8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)}")


def spelling(text: str) -> str:
    return " ".join(ids(text))


def graphemes(t: Thesis) -> None:
    rows = []
    for number, row in t.catalogue.items():
        note = t.catalogue_note[number].strip()
        if len(row) == 1:
            status, target = "current", ""
        elif len(row) == 2:
            status, target = "sequence", " ".join(t.glyph_id(h) for h in row)
        elif "→" in note:
            status, target = "renumbered", note.replace("→", "").strip()
        elif "＝" in note:
            status, target = "variant", note.replace("＝", "").strip()
        else:
            status, target = "void", ""
        origin = "otake" if number.startswith("C") else ("derived" if number.endswith("D") else "1985")
        rows.append([number, status, target, origin, printed(40) if number < "084" else ""])
    rows.sort()
    write("graphemes", ["id", "status", "target", "number_origin", "printed_page"], [r[:4] for r in rows])


def seg_cells(t: Thesis, page: int):
    return [s for l in t.lines(page) for s in l.segs]


def table_v(t: Thesis) -> list[list]:
    rows = t.rows(113)
    head = next(r for r in rows if r[0].text.strip() == "əə")
    cells = next(r for r in rows if r[0].y > head[0].y and "⟦" in r[0].text)
    out = []
    for h, c in zip(head, cells):
        found = re.match(r"⟦([^⟧]+)⟧\s*(\S+)", c.text)
        out.append([found[1], h.text.strip(), "V", printed(113), "table 3.4.7.1", ""])
    return out


def table_grid(t: Thesis, page: int, columns: dict[str, float], kind: str, where: str, y_min: float, y_max: float):
    segs = seg_cells(t, page)
    labels = []
    for s in segs:
        if y_min < s.y < y_max:
            m = re.search(r"(-[a-zǰžğŋγʷň ľ]+)", s.text)
            if m:
                labels.append((s.y, m[1].strip()))
    # one label per visual row
    labels.sort()
    merged: list[tuple[float, str]] = []
    for y, text in labels:
        if not merged or abs(merged[-1][0] - y) > 8:
            merged.append((y, text))
    names = sorted(columns.items(), key=lambda kv: kv[1])
    out = []
    for s in segs:
        if not s.khitan or not (y_min < s.y < y_max):
            continue
        for gid in ids(s.text):
            near = min(merged, key=lambda m: abs(m[0] - s.y))
            if abs(near[0] - s.y) > 10:
                continue
            col = min(names, key=lambda kv: abs(kv[1] - s.x))
            out.append([gid, col[0].rstrip("-") + near[1].lstrip("-"), kind, printed(page), where, ""])
    return out


def table_cv(t: Thesis) -> list[list]:
    out = []
    for s_line in t.lines(116):
        for m in re.finditer(rf"⟦([^⟧]+)⟧ ({LABEL})\s+({VALUE.pattern})", s_line.text):
            if s_line.y < 240:
                out.append([m[1], m[3], "CV", printed(116), "table 3.4.7.4", ""])
    return out


def readings(t: Thesis) -> None:
    rows = table_v(t)
    vc = dict(zip("əə ə a o u i e ö ü".split(), [183 + 34 * i for i in range(9)]))
    vc = {k + "-": v + 6 for k, v in vc.items()}
    rows += table_grid(t, 114, vc, "VC", "table 3.4.7.2", 170, 600)
    vcc = dict(zip("ə a o u i ä e ö ü".split(), [209 + 34 * i for i in range(9)]))
    vcc = {k + "-": v for k, v in vcc.items()}
    rows += table_grid(t, 115, vcc, "VCC", "table 3.4.7.3", 305, 575)
    rows += table_cv(t)
    # 補遺1: "⟦247⟧ 247 əəd"
    for page in PAGES_APPENDIX_READINGS:
        for line in t.lines(page):
            m = re.match(rf"⟦([^⟧]+)⟧ ({LABEL}) ({VALUE.pattern})\d*\)?\s*", line.text)
            if m:
                kind = "VCC" if re.search(r"[aəouieäöüʊɵ](nd|nz|ŋg|ŋgʷ|ŋγ|ŋγʷ|rd|rǰ|ld|lz|wǰ|yl)$", m[3]) else "VC"
                rows.append([m[1], m[3], kind, printed(page), "補遺1", ""])
    # corrections stated next to the table, p.102
    for gid, value in (("372", "uğʷ"), ("090", "ʊğʷ"), ("274", "äğ")):
        rows.append([gid, value, "VC", 102, "text below table 3.4.7.2", "final"])
    for gid, value in (("172", "ugʷ?"), ("246", "ʊgʷ?")):
        rows.append([gid, value, "VC", 102, "note 80", "tentative"])
    # every other "glyph number value" in the body
    seen = {(r[0], r[1]) for r in rows}
    for page in PAGES_BODY:
        for line in t.lines(page):
            for m in re.finditer(rf"⟦([^⟧]+)⟧ ?({LABEL})\s+({VALUE.pattern})(?![\w-])", line.text):
                if m[1] != m[2] or (m[1], m[3]) in seen or len(m[3]) > 7:
                    continue
                seen.add((m[1], m[3]))
                rows.append([m[1], m[3], "", printed(page), "body text", ""])
    write("readings", ["grapheme", "value", "type", "printed_page", "where", "note"], rows)


def rhymes(t: Thesis) -> None:
    rows = []
    doc = lines = stanza = ""
    for page in PAGES_RHYMES:
        for row in t.rows(page):
            cols: dict[str, str] = {}
            for line in row:
                for seg in line.segs:
                    x = seg.x
                    key = "doc" if x < 128 else "line" if x < 164 else "stanza" if x < 186 else "verse" if x < 208 else "spelling" if x < 279 else "reading" if x < 336 else "note"
                    cols[key] = cols.get(key, "") + seg.text
            if "表記" in cols.get("spelling", "") or "spelling" not in cols and "reading" not in cols:
                continue
            if not cols.get("verse", "").strip().isdigit():
                continue
            cell = cols.get("doc", "").strip()
            both = re.match(r"^(\S+)\s+(\d[\d–-]*)$", cell)
            if both:
                doc, lines = both[1], both[2]
            else:
                doc = cell or doc
                lines = cols.get("line", lines).strip() or lines
            stanza = cols.get("stanza", stanza).strip() or stanza
            rows.append([doc, lines, stanza, cols["verse"].strip(), spelling(cols.get("spelling", "")),
                         cols.get("reading", "").strip(), cols.get("note", "").strip(), printed(page)])
    write("rhymes", ["document", "lines", "stanza", "verse", "spelling", "reading", "note", "printed_page"], rows)


HEAD = re.compile(r"^(?P<form>[^［〔\[]{1,60})［(?P<spell>[^］]*)］(?:〔(?P<pos>[^〕]*)〕)?(?:《(?P<gloss>[^》]*)》)?(?:〔(?P<cit>[^〕]*)〕)?")


REFLEX = r"(MM|WM|OT|Mong\.|Dag\.|Bur\.|Kalm\.|Jur\.|Ma\.)"


def cognates(t: Thesis) -> None:
    entries = []
    current = None
    for page in PAGES_COGNATES:
        for row in t.rows(page):
            text = " ".join(line.text.strip() for line in row).strip()
            start = re.match(r"^\[(\d+)\]\s*(.*)", text) if row[0].x < 115 else None
            if start:
                current = {"n": int(start[1]), "head": start[2], "page": printed(page), "cf": [], "reflex": [], "state": "head"}
                entries.append(current)
            elif current is not None:
                if re.fullmatch(r"(附録.*|\d+)?", text):
                    continue
                if re.match(rf"^{REFLEX}\s", text):
                    current["reflex"].append(text)
                    current["state"] = "reflex"
                elif text.startswith("Cf."):
                    current["cf"].append(text[3:].strip())
                    current["state"] = "cf"
                elif text.startswith("【備考】"):
                    current["state"] = "remark"
                elif current["state"] == "head":
                    current["head"] += text
                elif current["state"] == "reflex":
                    current["reflex"][-1] += " " + text
                elif current["state"] == "cf":
                    current["cf"][-1] += text
    out, reflexes = [], []
    for e in entries:
        m = HEAD.match(e["head"])
        if m:
            spell = " ~ ".join(spelling(p) for p in m["spell"].split("~"))
            out.append([e["n"], m["form"].strip(), spell, m["pos"] or "", m["gloss"] or "", m["cit"] or "", " ; ".join(e["cf"]), e["page"]])
        else:
            out.append([e["n"], e["head"], spelling(e["head"]), "", "", "", " ; ".join(e["cf"]), e["page"]])
        for r in e["reflex"]:
            for chunk in re.split(rf"[,，]\s*(?={REFLEX.replace('(', '(?:', 1)}\s)", r):
                lang = re.match(rf"{REFLEX}\s*(.*)", chunk)
                if lang:
                    reflexes.append([e["n"], lang[1].rstrip("."), lang[2].strip()])
    write("cognates", ["n", "form", "spelling", "pos", "gloss", "attestations", "cf", "printed_page"], out)
    write("cognate_reflexes", ["n", "language", "text"], reflexes)


def loans(t: Thesis) -> None:
    rows, examples = [], []
    section = ""
    hanzi = ""
    current = None
    for page in PAGES_LOANS:
        for row in t.rows(page, tolerance=6):
            cols = {"hanzi": "", "glyph": "", "translit": "", "use": ""}
            for line in row:
                for seg in line.segs:
                    x = seg.x
                    key = "hanzi" if x < 116 else "glyph" if x < 162 else "translit" if x < 203 else "use"
                    cols[key] += seg.text
            joined = "".join(cols.values()).strip()
            sec = re.match(r"^(4\.\d+\.\d+)\s*(.+)", joined)
            if sec and not cols["glyph"]:
                section = f"{sec[1]} {sec[2].strip()}"
                continue
            if re.match(r"^\s*漢字", cols["hanzi"]) or re.fullmatch(r"(附録.*|\d+)", joined) or not joined:
                continue
            if cols["hanzi"].strip():
                hanzi = cols["hanzi"].strip()
            if "⟦" in cols["glyph"]:
                current = [section, hanzi, spelling(cols["glyph"]), cols["translit"].strip(), printed(page)]
                rows.append(current)
                if cols["use"].strip():
                    examples.append([len(rows), cols["use"].strip()])
            elif cols["use"].strip() and rows:
                # continuation of the use column
                if examples and examples[-1][0] == len(rows) and not re.search(r"〕\s*[，,：]?\s*$", examples[-1][1]):
                    examples[-1][1] += cols["use"].strip()
                else:
                    examples.append([len(rows), cols["use"].strip()])
    write("loan_spellings", ["id", "section", "hanzi", "spelling", "transliteration", "printed_page"],
          [[i + 1, *r] for i, r in enumerate(rows)])
    write("loan_uses", ["spelling_id", "use"], examples)


DOC = re.compile(r"^\((KS|KL|Ch)(\d+)\)\s*(.+)")


def documents(t: Thesis) -> None:
    text = []
    for page in PAGES_DOCUMENTS:
        text += [(l.text.strip(), page) for l in t.lines(page)]
    rows = []
    current = None
    for line, page in text:
        m = DOC.match(line)
        if m:
            current = dict(id=m[1] + m[2], script={"KS": "small", "KL": "large", "Ch": "chinese"}[m[1]], head=m[3], page=printed(page), body="")
            rows.append(current)
        elif current is not None:
            current["body"] += line
    out = []
    for r in rows:
        whole = r["head"] + r["body"]
        abbr = re.search(r"〔([^〕]+)〕", whole)
        title = re.match(r"『([^』]+)』", r["head"])
        name = title[1] if title else re.sub(r"〔.*", "", r["head"]).strip()
        date = re.search(r"［([^］]+)］", whole)
        year = re.search(r"（(\d{3,4})(?:[–-]\d+)?）", (date[1] if date else whole.split("．")[0]))
        date_text = date[1] if date else re.split(r"[．。]", r["body"])[0][:40]
        cf = re.search(r"Cf\.\s*([^(（]*(?:（[^）]*）[，、,]?\s*)*)", r["body"])
        lines = re.search(r"契丹文\s*(\d+)\s*行", r["body"])
        out.append([r["id"], r["script"], abbr[1] if abbr else "", name, date_text, year[1] if year else "",
                    lines[1] if lines else "", cf[1].strip() if cf else "", r["page"]])
    write("documents", ["id", "script", "abbreviation", "title", "date_text", "year", "khitan_lines", "cf", "printed_page"], out)


def bibliography(t: Thesis) -> None:
    rows = []
    section = ""
    for page in PAGES_BIBLIOGRAPHY:
        for line in t.lines(page):
            text = line.text.strip()
            if re.fullmatch(r"\d+|参考文献|", text):
                continue
            if re.fullmatch(r"【.+】", text):
                section = text.strip("【】")
                continue
            if line.x < 95 and rows is not None:
                rows.append([section, text, printed(page)])
            elif rows:
                rows[-1][1] += text
    write("bibliography", ["section", "entry", "printed_page"], rows)


SEG = rf"(?:[\(\)\*\?\[\]-]|{PHONE}|̈)+"
FORM = re.compile(
    rf"(?P<sp>(?:⟦[^⟧]+⟧)+)-?\s+(?P<seg>{SEG})(?:\s{{1,3}}(?P<word>{SEG}))?\s*"
    r"(?:《(?P<gloss>[^》]+)》)?\s*(?:（(?P<note>[^）]{1,14})）)?\s*(?:〔(?P<cit>[A-Z][^〕]{1,60})〕)?"
)


def forms(t: Thesis) -> None:
    rows, aligned = [], []
    for page in PAGES_BODY:
        for line in t.text(page).split("\n"):
            for m in FORM.finditer(line):
                glyphs = ids(m["sp"])
                parts = m["seg"].strip("-").split("-")
                if len(glyphs) > 1 and "-" not in m["seg"]:
                    continue
                if not re.search(r"[a-zəɵʊäöü]", m["seg"]):
                    continue
                rows.append([" ".join(glyphs), m["seg"], m["word"] or "", m["gloss"] or "", m["note"] or "", m["cit"] or "", printed(page)])
                if len(parts) == len(glyphs):
                    for g, value in zip(glyphs, parts):
                        if value:
                            aligned.append([g, value, " ".join(glyphs), m["seg"], printed(page)])
    write("forms", ["spelling", "segmentation", "form", "gloss", "note", "citation", "printed_page"], rows)
    write("segment_values", ["grapheme", "value", "spelling", "segmentation", "printed_page"], aligned)


def errata(t: Thesis) -> None:
    rows = []
    for page in PAGES_BODY:
        text = t.text(page)
        for m in re.finditer(rf"⟦([^⟧]+)⟧ ?({LABEL})\b", text):
            if m[1] != m[2] and not m[1].startswith("x"):
                rows.append(["label", m[1], m[2], printed(page)])
        for m in re.finditer(r"⟦(x[^⟧]+)⟧", text):
            rows.append(["uncatalogued", m[1], "", printed(page)])
    for page in list(PAGES_RHYMES) + list(PAGES_COGNATES) + list(PAGES_LOANS):
        for m in re.finditer(r"⟦(x[^⟧]+)⟧", t.text(page)):
            rows.append(["uncatalogued", m[1], "", printed(page)])
    write("errata", ["kind", "glyph", "printed_label", "printed_page"], rows)


def main() -> None:
    t = Thesis(sys.argv[1])
    graphemes(t); readings(t); rhymes(t); cognates(t); loans(t); documents(t); bibliography(t); forms(t); errata(t)


if __name__ == "__main__":
    main()

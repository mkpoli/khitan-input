#!/usr/bin/env python3
"""Build dist/khitan.sqlite from the TSV files in data/.

usage: python3 scripts/build_db.py
"""
from __future__ import annotations

import csv
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
OTAKE = DATA / "otake2020"
SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf8")
VOWEL = "aəɵʊɪıɨäöüoueiāēīōūȳ"
CITATION_ITEM = re.compile(r"([A-Z][A-Z.]*[A-Z]|[A-Z]{2,})\s*(\d[\d–-]*)?")


def tsv(path: Path) -> list[dict]:
    with open(path, encoding="utf8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def characters() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in open(ROOT / "cache/web/UnicodeData.txt", encoding="ascii"):
        cp, name = line.split(";")[:2]
        if "KHITAN SMALL SCRIPT" in name:
            out[cp] = {"codepoint": cp, "name": name, "radical": None, "jurchen": 0}
    radical = None
    jurchen = False
    for line in open(ROOT / "cache/web/NamesList.txt", encoding="utf8"):
        if line.startswith("@@\t"):
            radical, jurchen = None, False
        elif line.startswith("@\t\t"):
            title = line.strip("@\t\n ")
            jurchen = "Jurchen" in title
            radical = title if title.startswith(("Radical", "Khitan")) or "Radical" in title else radical
        else:
            m = re.match(r"([0-9A-F]{5})\t", line)
            if m and m[1] in out:
                out[m[1]]["radical"] = radical
                out[m[1]]["jurchen"] = int(jurchen or m[1] == "18C3E")
    return out


def assign_unicode() -> dict[str, tuple[str, str, str]]:
    """grapheme -> (codepoint, method, confidence)."""
    by_1985: dict[str, str] = {}
    for row in tsv(DATA / "unicode/kss_mappings.tsv"):
        for n in row["chinggeltei1985"].split():
            if n.isdigit():
                by_1985[f"{int(n):03d}"] = row["codepoint"]
    assigned = {}
    graphemes = tsv(OTAKE / "graphemes.tsv")
    for g in graphemes:
        if g["id"] in by_1985:
            assigned[g["id"]] = (by_1985[g["id"]], "west_1985_number", "high")
    for g in graphemes:  # 005 -> 004D: the old number's code point is the new grapheme's
        if g["status"] == "renumbered" and g["id"] in by_1985 and g["target"] not in assigned:
            assigned[g["target"]] = (by_1985[g["id"]], "west_1985_renumbered", "high")
    for row in tsv(DATA / "unicode/catalogue_additions.tsv"):
        assigned[row["grapheme"]] = (row["codepoint"], "visual", row["confidence"])
    return assigned


def clean_value(value: str) -> str:
    return re.sub(r"[()]", "", value).strip("-")


def is_phonetic(value: str) -> bool:
    return bool(re.search(f"[{VOWEL}]", value)) and not re.search(r"[A-Z]|[0-9]|tš|dž|^.$", value.replace("?", ""))


def kind_of(value: str) -> str:
    if re.search(r"[A-Z]{2,}", value):
        return "semantic"
    if re.search("[̉ảẻỉỏủỷẩểổửởẳ]", value):
        return "mnemonic"
    return "phonetic"


RANK = {"text below table 3.4.7.2": 0, "補遺1": 1, "table 3.4.7.1": 2, "table 3.4.7.2": 2, "table 3.4.7.3": 2, "table 3.4.7.4": 2, "note 80": 5}


def main() -> None:
    target = ROOT / "dist" / "khitan.sqlite"
    target.parent.mkdir(exist_ok=True)
    target.unlink(missing_ok=True)
    db = sqlite3.connect(target)
    db.executescript(SCHEMA)

    for s in tsv(DATA / "sources.tsv"):
        db.execute("INSERT INTO source VALUES (?,?,?,?,?,?)", tuple(s.values()))

    chars = characters()
    west = {r["codepoint"]: r for r in tsv(DATA / "unicode/kss_mappings.tsv")}
    for cp, c in chars.items():
        db.execute("INSERT INTO character VALUES (?,?,?,?,?)", (cp, chr(int(cp, 16)), c["name"], c["radical"], c["jurchen"]))
        for scheme, value in west.get(cp, {}).items():
            if scheme != "codepoint" and value:
                db.execute("INSERT INTO catalogue_number VALUES (?,?,?)", (cp, scheme, value))

    assigned = assign_unicode()
    catalogue = tsv(OTAKE / "graphemes.tsv")
    unresolved = {r["grapheme"]: r for r in tsv(DATA / "unicode/catalogue_unresolved.tsv")}
    for g in catalogue:
        cp, method, conf = assigned.get(g["id"], (None, None, None))
        if g["status"] != "current" and g["status"] != "variant":
            cp, method, conf = None, None, None
        cand = unresolved.get(g["id"], {}).get("candidate") or None
        db.execute("INSERT INTO grapheme VALUES (?,?,?,?,?,?,?,?)", (g["id"], g["status"], g["target"] or None, g["number_origin"], cp, method, conf, cand))
    for gid in sorted({r["glyph"] for r in tsv(OTAKE / "errata.tsv") if r["kind"] == "uncatalogued"}):
        db.execute("INSERT INTO grapheme VALUES (?,?,?,?,?,?,?,?)", (gid, "uncatalogued", None, "otake", None, None, None, None))
    known = {r[0] for r in db.execute("SELECT id FROM grapheme")}

    def to_text(spelling: str) -> str | None:
        out = []
        for gid in spelling.replace("~", " ").split():
            cp = assigned.get(gid, (None,))[0]
            if cp is None:
                return None
            out.append(chr(int(cp, 16)))
        return "".join(out)

    # Otake's values, explicit statements first
    explicit: dict[str, list[dict]] = defaultdict(list)
    for r in tsv(OTAKE / "readings.tsv"):
        if r["grapheme"] not in known:
            continue
        if r["where"] == "body text" and not is_phonetic(r["value"]):
            continue
        explicit[r["grapheme"]].append(r)
    segments: dict[str, Counter] = defaultdict(Counter)
    seg_page: dict[tuple, str] = {}
    for r in tsv(OTAKE / "segment_values.tsv"):
        if r["grapheme"] not in known or not re.fullmatch(rf"[\(\)\*a-zəɵʊɪɨıäöüǰčšžňľŋγχğḥʷ{VOWEL}]+\??", r["value"]):
            continue
        segments[r["grapheme"]][r["value"]] += 1
        seg_page.setdefault((r["grapheme"], r["value"]), r["printed_page"])
    singles: dict[str, Counter] = defaultdict(Counter)
    for table, field in (("rhymes", "reading"), ("loan_spellings", "transliteration")):
        for r in tsv(OTAKE / f"{table}.tsv"):
            if r["spelling"] and " " not in r["spelling"] and r["spelling"] in known and r[field] not in ("", "?"):
                singles[r["spelling"]][r[field]] += 1
    n = 0
    for gid in sorted(known):
        rows = []
        for r in sorted(explicit.get(gid, []), key=lambda r: RANK.get(r["where"], 4)):
            value = r["value"]
            tier = "stated"
            if value.startswith("*"):
                tier = "stated_unattested"
            elif value.endswith("?") or r["note"] == "tentative":
                tier = "stated_tentative"
            rows.append((value.lstrip("*").rstrip("?"), r["type"] or None, tier, r["where"], r["printed_page"]))
        for value, count in singles.get(gid, Counter()).most_common():
            rows.append((value.rstrip("?"), None, "single_grapheme_word", f"{count} rows", None))
        for value, count in segments.get(gid, Counter()).most_common():
            if clean_value(value):
                rows.append((clean_value(value), None, "aligned_spelling", f"{count} aligned spellings", seg_page[(gid, value)]))
        seen = set()
        for rank, (value, vtype, tier, where, page) in enumerate(rows):
            if (value, tier) in seen:
                continue
            seen.add((value, tier))
            db.execute("INSERT INTO reading VALUES (?,?,?,?,?,?,?,?,?)", (gid, assigned.get(gid, (None,))[0], "otake2020", value, "phonetic", vtype, tier, where, page))
            n += 1
    papers = tsv(DATA / "otake_papers/readings.tsv")
    for gid in sorted({r["grapheme"] for r in papers if r["grapheme"].startswith("x") or r["grapheme"].startswith("k")}):
        raise SystemExit(f"unidentified grapheme in a table: {gid}")
    for r in papers:
        db.execute("INSERT INTO reading VALUES (?,?,?,?,?,?,?,?,?)", (r["grapheme"], assigned.get(r["grapheme"], (None,))[0], r["source"], r["value"].lstrip("*").rstrip("?"), "phonetic", None, r["tier"], r["location"], r["page"]))
    # Primary, in the dissertation's notation: the 2025 tables, then the dissertation by evidence
    db.executescript("""
    INSERT INTO primary_reading
    SELECT grapheme, value, tier, source, page FROM (
      SELECT grapheme, value, tier, source, page,
             row_number() OVER (PARTITION BY grapheme ORDER BY source = 'otake2025' DESC, rowid) rn
      FROM reading WHERE source IN ('otake2020', 'otake2025')
    ) WHERE rn = 1;
    """)

    # Other scholars, keyed by code point
    n4725 = {r["n4725r"]: r["codepoint"] for r in tsv(DATA / "unicode/kss_mappings.tsv") if r["n4725r"]}
    by_cp = {}
    for gid, (cp, _, _) in assigned.items():
        by_cp.setdefault(cp, gid)
    for row in tsv(DATA / "unicode/n4725r_table6.tsv"):
        cp = n4725.get(row["n4725r"])
        if cp is None:
            continue
        for scheme in ("liu2009", "liu2014", "chinggeltei2010", "wu_janhunen2010", "jishi2012", "takeuchi2012"):
            if row[scheme].strip():
                db.execute("INSERT INTO reading VALUES (?,?,?,?,?,?,?,?,?)", (by_cp.get(cp), cp, "n4725r:" + scheme, row[scheme].strip(), kind_of(row[scheme]), None, "scholar_via_n4725r", "Table 6", None))
        for m in re.finditer(r"([~<>=+])#(\d+)", row["relation"]):
            other = n4725.get(m[2])
            if other:
                db.execute("INSERT INTO relation VALUES (?,?,?,?)", (cp, m[1], other, "n4725r"))
    for row in tsv(DATA / "unicode/kane2009_index.tsv"):
        for cp in row["codepoints"].split()[:1]:
            value = row["value"].strip()
            if value and cp in chars:
                db.execute("INSERT INTO reading VALUES (?,?,?,?,?,?,?,?,?)", (by_cp.get(cp), cp, "kane2009", value, kind_of(value), None, "scholar", "Index of Graphs " + row["kane_no"], None))

    # Documents
    abbreviations = set()
    for d in tsv(OTAKE / "documents.tsv"):
        db.execute("INSERT INTO document VALUES (?,?,?,?,?,?,?,?,?)", tuple(d[k] or None for k in ("id", "script", "abbreviation", "title", "date_text", "year", "khitan_lines", "cf", "printed_page")))
        if d["abbreviation"]:
            abbreviations.add(d["abbreviation"])

    def attest(kind: str, rid: int, text: str) -> None:
        current = None
        for part in re.split(r"[,，;、]\s*", text):
            m = re.match(r"\s*([A-Z][A-Za-z.]*)\s*([\d–-]*)", part)
            if m and m[1] in abbreviations:
                current = m[1]
                if m[2]:
                    db.execute("INSERT INTO attestation VALUES (?,?,?,?)", (kind, rid, current, m[2]))
            elif current and re.fullmatch(r"\s*[\d–-]+\s*", part):
                db.execute("INSERT INTO attestation VALUES (?,?,?,?)", (kind, rid, current, part.strip()))

    for i, r in enumerate(tsv(OTAKE / "rhymes.tsv"), 1):
        db.execute("INSERT INTO rhyme VALUES (?,?,?,?,?,?,?,?,?,?)", (i, r["document"], r["lines"], r["stanza"], r["verse"], r["spelling"], to_text(r["spelling"]), r["reading"], r["note"] or None, r["printed_page"]))
    for r in tsv(OTAKE / "cognates.tsv"):
        db.execute("INSERT INTO cognate VALUES (?,?,?,?,?,?,?,?)", (r["n"], r["form"], r["spelling"], to_text(r["spelling"].split("~")[0]) if r["spelling"] else None, r["pos"] or None, r["gloss"] or None, r["cf"] or None, r["printed_page"]))
        attest("cognate", int(r["n"]), r["attestations"])
    for r in tsv(OTAKE / "cognate_reflexes.tsv"):
        db.execute("INSERT INTO cognate_reflex VALUES (?,?,?)", (r["n"], r["language"], r["text"]))
    uses = defaultdict(list)
    for r in tsv(OTAKE / "loan_uses.tsv"):
        uses[int(r["spelling_id"])].append(r["use"])
    for r in tsv(OTAKE / "loan_spellings.tsv"):
        rid = int(r["id"])
        db.execute("INSERT INTO loan_spelling VALUES (?,?,?,?,?,?,?)", (rid, r["section"], r["hanzi"], r["spelling"], to_text(r["spelling"]), r["transliteration"], r["printed_page"]))
        for use in uses[rid]:
            db.execute("INSERT INTO loan_use VALUES (?,?)", (rid, use))
            for cit in re.findall(r"〔([^〕]+)〕", use):
                attest("loan", rid, cit)
    for i, r in enumerate(tsv(OTAKE / "forms.tsv"), 1):
        db.execute("INSERT INTO form VALUES (?,?,?,?,?,?,?,?,?)", (i, "otake2020", r["spelling"], to_text(r["spelling"]), r["segmentation"], r["form"] or None, r["gloss"] or None, r["note"] or None, r["printed_page"]))
        attest("form", i, r["citation"])
    next_form = db.execute("SELECT max(id) FROM form").fetchone()[0]
    for r in tsv(DATA / "otake_papers/forms.tsv"):
        if re.search(r"(^| )[xk][0-9A-Fa-f]", r["spelling"]):
            continue
        next_form += 1
        db.execute("INSERT INTO form VALUES (?,?,?,?,?,?,?,?,?)", (next_form, r["source"], r["spelling"], to_text(r["spelling"]), None, r["form"], r["gloss"] or None, None, r["page"]))
    for r in tsv(DATA / "otake_papers/examples.tsv"):
        db.execute("INSERT INTO example VALUES (?,?,?,?,?,?)", (r["n"], "otake2018", r["citation"], r["translation"], r["note"] or None, r["page"]))
    for r in tsv(DATA / "otake_papers/example_lines.tsv"):
        db.execute("INSERT INTO example_line VALUES (?,?,?,?)", (r["n"], r["line"], r["transcription"], r["gloss"]))
    for r in tsv(DATA / "otake_papers/example_words.tsv"):
        db.execute("INSERT INTO example_word VALUES (?,?,?,?,?,?)", (r["n"], r["line"], r["position"], r["spelling"], to_text(r["spelling"]) if not re.search(r"(^| )x", r["spelling"]) else None, r["transcription"] or None))
    for r in tsv(OTAKE / "bibliography.tsv"):
        db.execute("INSERT INTO bibliography VALUES (?,?,?)", (r["section"], r["entry"], r["printed_page"]))
    for r in tsv(OTAKE / "errata.tsv"):
        if r["kind"] == "label":
            db.execute("INSERT INTO erratum VALUES (?,?,?)", (r["glyph"], r["printed_label"], r["printed_page"]))
    for r in tsv(DATA / "large/liu_wang2004.tsv"):
        db.execute("INSERT INTO large_reading VALUES (?,?,?,?,?,?)", (int(r["number"]), r["babelstone_pua"], r["reconstruction"], r["chinese_transcription"] or None, r["meaning"] or None, "liu_wang2004"))
    db.commit()
    for name in ("character", "grapheme", "reading", "primary_reading", "catalogue_number", "relation", "document", "rhyme", "cognate", "cognate_reflex", "loan_spelling", "loan_use", "form", "attestation", "bibliography", "erratum", "large_reading", "example", "example_line", "example_word"):
        print(f"{name}: {db.execute(f'SELECT count(*) FROM {name}').fetchone()[0]}")
    db.close()


if __name__ == "__main__":
    main()

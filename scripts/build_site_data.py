#!/usr/bin/env python3
"""Export dist/khitan.sqlite to app/public/data/khitan.json for the site.

usage: python3 scripts/build_site_data.py
"""
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent


def rows(db, sql):
    return [dict(r) for r in db.execute(sql)]


def compact(d):
    return {k: v for k, v in d.items() if v not in (None, "", [])}


def main():
    db = sqlite3.connect(ROOT / "dist" / "khitan.sqlite")
    db.row_factory = sqlite3.Row
    readings = defaultdict(list)
    for r in rows(db, "SELECT rowid, * FROM reading ORDER BY rowid"):
        key = r["grapheme"] or "U+" + r["codepoint"]
        readings[key].append(compact({"s": r["source"], "v": r["value"], "k": r["kind"], "t": r["tier"], "l": r["location"], "p": r["page"]}))
    primary = {r["grapheme"]: r for r in rows(db, "SELECT * FROM primary_reading")}
    chars = {r["codepoint"]: r for r in rows(db, "SELECT * FROM character")}
    numbers = defaultdict(dict)
    for r in rows(db, "SELECT * FROM catalogue_number"):
        numbers[r["codepoint"]][r["scheme"]] = r["value"]
    relation = defaultdict(list)
    for r in rows(db, "SELECT * FROM relation"):
        relation[r["codepoint"]].append([r["type"], r["other"]])

    graphemes, used = [], set()
    for g in rows(db, "SELECT * FROM grapheme"):
        if g["status"] not in ("current", "variant", "uncatalogued"):
            continue
        cp = g["codepoint"]
        used.add(cp)
        c = chars.get(cp, {})
        p = primary.get(g["id"], {})
        types = {r["value_type"] for r in rows(db, f"SELECT value_type FROM reading WHERE grapheme='{g['id']}' AND source='otake2020' AND value_type IS NOT NULL")}
        graphemes.append(compact({
            "id": g["id"], "cp": cp, "st": g["status"], "tg": g["target"], "um": g["unicode_method"], "uc": g["unicode_confidence"],
            "cand": g["unicode_candidate"], "v": p.get("value"), "vt": p.get("tier"), "vs": p.get("source"), "vp": p.get("page"),
            "ty": sorted(types)[0] if types else None, "rad": c.get("radical_group"), "jur": c.get("jurchen_tentative") or None,
            "rs": readings.get(g["id"]), "num": numbers.get(cp), "rel": relation.get(cp),
        }))
    for cp, c in chars.items():
        if cp not in used:
            key = "U+" + cp
            graphemes.append(compact({"id": key, "cp": cp, "st": "unicode", "rad": c["radical_group"], "jur": c["jurchen_tentative"] or None,
                                      "rs": readings.get(key), "num": numbers.get(cp), "rel": relation.get(cp)}))

    atts = defaultdict(list)
    for a in rows(db, "SELECT * FROM attestation"):
        atts[(a["kind"], a["ref"])].append(f'{a["document"]} {a["line"]}')
    words = []
    reflex = defaultdict(list)
    for r in rows(db, "SELECT * FROM cognate_reflex"):
        reflex[r["n"]].append([r["language"], r["text"]])
    for r in rows(db, "SELECT * FROM cognate"):
        words.append(compact({"k": "cognate", "sp": r["spelling"], "x": r["text"], "f": r["form"], "g": r["gloss"], "pos": r["pos"], "src": "otake2020", "p": r["page"], "at": atts[("cognate", r["n"])], "cf": r["cf"], "rf": reflex[r["n"]]}))
    uses = defaultdict(list)
    for r in rows(db, "SELECT * FROM loan_use"):
        uses[r["spelling_id"]].append(r["use"])
    for r in rows(db, "SELECT * FROM loan_spelling"):
        words.append(compact({"k": "loan", "sp": r["spelling"], "x": r["text"], "f": r["transliteration"], "h": r["hanzi"], "sec": r["section"], "src": "otake2020", "p": r["page"], "uses": uses[r["id"]]}))
    seen = set()
    for r in rows(db, "SELECT * FROM form"):
        form = r["transcription"] or r["segmentation"]
        key = (r["source"], r["spelling"], form, r["gloss"])
        if key in seen or not form:
            continue
        seen.add(key)
        words.append(compact({"k": "form", "sp": r["spelling"], "x": r["text"], "f": form, "sg": r["segmentation"], "g": r["gloss"], "src": r["source"], "p": r["page"], "at": atts[("form", r["id"])] if r["source"] == "otake2020" else None}))
    rhyme = {}
    for r in rows(db, "SELECT * FROM rhyme WHERE spelling <> ''"):
        key = (r["spelling"], r["reading"])
        entry = rhyme.setdefault(key, compact({"k": "rhyme", "sp": r["spelling"], "x": r["text"], "f": r["reading"], "src": "otake2020", "p": r["page"], "at": []}))
        entry.setdefault("at", []).append(f'{r["document"]} {r["lines"]}')
    words += list(rhyme.values())

    examples = []
    for e in rows(db, "SELECT * FROM example ORDER BY n"):
        lines = []
        for l in rows(db, f"SELECT * FROM example_line WHERE n={e['n']} ORDER BY line"):
            ws = rows(db, f"SELECT * FROM example_word WHERE n={e['n']} AND line={l['line']} ORDER BY position")
            lines.append(compact({"tr": l["transcription"], "gl": l["gloss"], "w": [compact({"sp": w["spelling"], "x": w["text"], "t": w["transcription"]}) for w in ws]}))
        examples.append(compact({"n": e["n"], "cit": e["citation"], "tr": e["translation"], "note": e["note"], "src": e["source"], "p": e["page"], "lines": lines}))

    documents = [compact({"id": d["id"], "s": d["script"], "a": d["abbreviation"], "t": re.sub(r"⟦[^⟧]*⟧", "□", d["title"] or ""), "d": d["date_text"], "y": d["year"], "n": d["khitan_lines"], "p": d["page"]}) for d in rows(db, "SELECT * FROM document")]
    data = {
        "graphemes": graphemes, "words": words, "examples": examples, "documents": documents,
        "sources": [compact({"id": s["id"], "c": s["citation"], "u": s["url"], "t": s["terms"], "n": s["note"]}) for s in rows(db, "SELECT * FROM source")],
        "large": [compact({"n": r["number"], "pua": r["babelstone_pua"], "r": r["reconstruction"], "c": r["chinese_transcription"], "m": r["meaning"]}) for r in rows(db, "SELECT * FROM large_reading")],
    }
    out = ROOT / "app" / "public" / "data" / "khitan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print({k: len(v) for k, v in data.items()}, out.stat().st_size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read Wikipedia's two lists of Khitan inscriptions into data/inscriptions/inscriptions.tsv.

The English and Chinese lists hold the same rows in the same order; each row is joined by its
position in its section and checked by its coordinates.

usage: scripts/extract_wikipedia_inscriptions.py   (reads cache/web/wikipedia/{en,zh}.wikitext)
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "cache/web/wikipedia"
SECTIONS = {
    "Monumental inscriptions in the Khitan large script": ("large", "monument"),
    "Other inscriptions in the Khitan large script": ("large", "other"),
    "Khitan large script seals": ("large", "seal"),
    "Monumental inscriptions in the Khitan small script": ("small", "monument"),
    "Other inscriptions in the Khitan small script": ("small", "other"),
    "Khitan small script seals": ("small", "seal"),
    "契丹大字墓志铭": ("large", "monument"),
    "其他契丹大字铭文": ("large", "other"),
    "契丹大字印章": ("large", "seal"),
    "契丹小字墓志铭": ("small", "monument"),
    "其他契丹小字铭文": ("small", "other"),
    "契丹小字印章": ("small", "seal"),
}
HEADERS = {
    "Monument": "name", "Object": "name", "Image": "image", "Date": "date", "Place of discovery": "place",
    "Year of discovery": "found", "Current Location": "held", "Description": "description",
    "碑文": "name", "物件": "name", "图像": "image", "日期": "date", "发现地": "place", "发现年": "found", "现藏于": "held", "描述": "description",
}
ENGLISH_ONLY = {("small", "other"): {6}}  # the second fish-shaped tally has no row in the Chinese list
FIELDS = ("id", "script", "kind", "name_en", "name_zh", "date", "place_en", "place_zh", "latitude", "longitude", "found_en", "found_zh",
          "held_en", "held_zh", "description_en", "description_zh", "image", "note_en", "references_en", "references_zh")


def balanced(text: str, start: int, opener: str = "{{", closer: str = "}}") -> int:
    """Index just past the template opening at `start`."""
    depth, i = 0, start
    while i < len(text):
        if text.startswith(opener, i):
            depth, i = depth + 1, i + 2
        elif text.startswith(closer, i):
            depth, i = depth - 1, i + 2
            if depth == 0:
                return i
        else:
            i += 1
    raise ValueError("unbalanced template")


def template_args(body: str) -> tuple[str, list[str], dict[str, str]]:
    """Split `name|a|k=v` at top-level pipes."""
    parts, depth, current, i = [], 0, "", 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "[["):
            depth, current, i = depth + 1, current + two, i + 2
        elif two in ("}}", "]]"):
            depth, current, i = depth - 1, current + two, i + 2
        elif body[i] == "|" and depth == 0:
            parts.append(current)
            current, i = "", i + 1
        else:
            current, i = current + body[i], i + 1
    parts.append(current)
    positional, named = [], {}
    for part in parts[1:]:
        key, eq, value = part.partition("=")
        if eq and re.fullmatch(r"[\w\- ]+", key.strip()):
            named[key.strip()] = value.strip()
        else:
            positional.append(part.strip())
    return parts[0].strip(), positional, named


def plain(text: str) -> str:
    """Wikitext to plain text; references and coordinates are taken out before this."""
    while True:
        m = re.search(r"\{\{", text)
        if not m:
            break
        end = balanced(text, m.start())
        name, positional, named = template_args(text[m.start() + 2:end - 2])
        key = name.lower()
        if key == "sort":
            value = positional[1]
        elif key in ("lang", "lang-zh", "zh", "nowrap", "nobr"):
            value = positional[-1] if positional else ""
        elif key in ("rp", "clear", "coord"):
            value = ""
        else:
            raise SystemExit(f"unhandled template: {text[m.start():end]}")
        text = text[:m.start()] + value + text[end:]
    text = re.sub(r"\[\[(?:File|Image):[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", text)
    text = re.sub(r"-\{(.*?)\}-", r"\1", text)
    text = re.sub(r"<br\s*/?>", ", ", text)
    text = re.sub(r"</?(small|nowiki|span|sup|sub)[^>]*>", "", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r",[ ,]+", ", ", re.sub(r" ,", ",", text)).strip(", ")


def citation(body: str) -> str:
    """One reference as a short line."""
    out = []
    i = 0
    while i < len(body):
        if body.startswith("{{", i):
            end = balanced(body, i)
            name, positional, named = template_args(body[i + 2:end - 2])
            key = name.lower()
            if key in ("harvnb", "harv", "sfn"):
                pages = named.get("p") or named.get("pp")
                out.append(" and ".join(positional[:-1]) + " " + positional[-1] + (f": {pages}" if pages else ""))
            elif key.startswith("cite") or key == "citation":
                authors = []
                for n in ("", *map(str, range(1, 10))):
                    who = named.get("author" + n) or named.get("last" + n)
                    if who and who not in authors:
                        authors.append(who + (", " + named["first" + n] if named.get("first" + n) and not named.get("author" + n) else ""))
                title = named.get("script-title") or named.get("title") or ""
                title = re.sub(r"^[a-z]{2}:", "", title)
                where = (named.get("journal") or named.get("publisher") or named.get("website") or "").split("｜")[0]
                issue = "".join(x for x in (named.get("volume", ""), f"({named['issue']})" if named.get("issue") else "") if x)
                pages = named.get("pages") or named.get("page")
                year = named.get("year") or named.get("date") or ""
                line = ", ".join(authors) + (f" ({year})" if year else "") + (f", {plain(title)}" if title else "")
                line += (f", {plain(where)}" if where else "") + (f" {issue}" if issue else "") + (f": {pages}" if pages else "")
                url = named.get("url")
                out.append(plain(line) + (f" <{url}>" if url else ""))
            elif key == "lang":
                out.append(plain(positional[-1]))
            elif key != "dead link":
                raise SystemExit(f"unhandled reference template: {body[i:end]}")
            i = end
        else:
            j = body.find("{{", i)
            j = len(body) if j < 0 else j
            out.append(plain(re.sub(r"<[^>]+>", "", body[i:j])))
            i = j
    return " ".join(x for x in out if x).strip()


def take_refs(text: str, named: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """Remove references and notes from a cell; return the rest, the references and the notes."""
    refs, notes = [], []
    while True:  # explanatory notes written as {{#tag:ref|…|group=note}} or {{efn|…}}
        m = re.search(r"\{\{(#tag:ref|efn)\s*\|", text)
        if not m:
            break
        start = m.start()
        end = balanced(text, start)
        body = text[m.end():end - 2]
        body = re.sub(r"\|\s*group\s*=\s*note\s*$", "", body.strip())
        body, inner, _ = take_refs(body, named)
        notes.append(plain(body))
        refs += inner
        text = text[:start] + text[end:]

    page = r"(?:\{\{rp\|([^}]*)\}\})?"  # the Chinese list gives the page after the reference

    def full(m: re.Match) -> str:
        body = citation(m[2])
        name = re.search(r'name\s*=\s*"?([^">/]+)"?', m[1] or "")
        if name:
            named[name[1].strip()] = body
            if m[3]:
                named["page of " + name[1].strip()] = m[3]
        refs.append(body + (f": {m[3]}" if m[3] else ""))
        return ""

    def short(m: re.Match) -> str:
        refs.append("@" + m[1].strip() + "\t" + (m[2] or ""))
        return ""

    text = re.sub(r"<ref([^>/]*)>(.*?)</ref>" + page, full, text, flags=re.S)
    text = re.sub(r'<ref\s+name\s*=\s*"?([^">/]+)"?\s*/>' + page, short, text)
    return text, refs, notes


def resolve(ref: str, named: dict[str, str]) -> str:
    if not ref.startswith("@"):
        return ref
    name, page = ref[1:].split("\t")
    page = page or named.get("page of " + name)  # a bare reuse keeps the page given where the reference is defined
    return named[name] + (f": {page}" if page else "")


def tables(wikitext: str) -> dict[tuple[str, str], list[dict]]:
    out, named, pending = {}, {}, []
    take_refs(wikitext[:wikitext.index("\n==")], named)  # the lead defines named references
    for heading, body in re.findall(r"^==([^=\n]+)==\n(.*?)(?=^==[^=])", wikitext, flags=re.S | re.M):
        key = SECTIONS.get(heading.strip())
        if key is None:
            continue
        table = body[body.index("{|"):body.index("\n|}")]
        chunks = re.split(r"\n\|-[^\n]*", table)
        header = next(c for c in chunks if c.lstrip().startswith("!"))
        columns = [HEADERS[re.sub(r"^.*\|", "", h).strip()] for h in header.strip().lstrip("!").split("!!")]
        rows = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk.startswith("|") or chunk.startswith("|}"):
                continue
            cells = [c.strip() for c in re.split(r"\|\|", chunk[1:])]
            if len(cells) == 1 and not cells[0]:
                continue
            if len(cells) != len(columns):
                raise SystemExit(f"{heading}: {len(cells)} cells for {len(columns)} columns: {chunk[:80]}")
            row = {"refs": [], "notes": []}
            for column, cell in zip(columns, cells):
                if column == "image":
                    m = re.search(r"\[\[(?:File|Image):([^|\]]+)", cell)
                    row["image"] = m[1].strip() if m else ""
                    continue
                cell, refs, notes = take_refs(cell, named)
                row["refs"] += refs
                row["notes"] += notes
                m = re.search(r"\{\{coord\|([\d.]+)\|([\d.]+)\|", cell)
                if m:
                    row["latitude"], row["longitude"] = m[1], m[2]
                row[column] = plain(cell)
            rows.append(row)
            pending.append(row)
        out[key] = rows
    for row in pending:
        row["refs"] = [resolve(r, named) for r in row["refs"]]
    return out


def main() -> None:
    en = tables((SOURCE / "en.wikitext").read_text(encoding="utf8"))
    zh = tables((SOURCE / "zh.wikitext").read_text(encoding="utf8"))
    target = ROOT / "data/inscriptions/inscriptions.tsv"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for (script, kind), rows in en.items():
            other = list(zh[(script, kind)])
            for n in sorted(ENGLISH_ONLY.get((script, kind), ())):
                other.insert(n - 1, {"name": "", "place": "", "found": "", "held": "", "description": "", "refs": []})
            if len(rows) != len(other):
                raise SystemExit(f"{script} {kind}: {len(rows)} English rows, {len(other)} Chinese rows")
            for n, (e, z) in enumerate(zip(rows, other), 1):
                if "latitude" in e and "latitude" in z and (e["latitude"], e["longitude"]) != (z["latitude"], z["longitude"]):
                    raise SystemExit(f"{script} {kind} {n}: coordinates differ between the lists: {e['name']} / {z['name']}")
                w.writerow({
                    "id": f"{script}-{kind}-{n:02d}", "script": script, "kind": kind,
                    "name_en": e["name"], "name_zh": z["name"], "date": e.get("date", ""),
                    "place_en": e["place"], "place_zh": z["place"], "latitude": e.get("latitude", ""), "longitude": e.get("longitude", ""),
                    "found_en": e["found"], "found_zh": z["found"], "held_en": e["held"], "held_zh": z["held"],
                    "description_en": e["description"], "description_zh": z["description"], "image": e["image"] if "image" in e else "",
                    "note_en": " ".join(e["notes"]),
                    "references_en": " | ".join(dict.fromkeys(e["refs"])), "references_zh": " | ".join(dict.fromkeys(z["refs"])),
                })
            print(f"{script} {kind}: {len(rows)}", file=sys.stderr)


if __name__ == "__main__":
    main()

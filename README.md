# Khitan Input

A site for entering the Khitan scripts, and the database behind it: <https://khitan.mkpo.li/>. It holds the small script's graphemes, Unicode code
points, readings by scholar, attested spellings and source documents, and what can so far be
gathered for the large script.

Grapheme values follow 大竹昌巳 (2020, 2025). Other scholars' values sit beside them under their own names.

## Finding a grapheme

- **Find**: one box for pasted Khitan, a reading, a catalogue number, a code point, a meaning or a Chinese word.
- **Syllabary**: Otake's values, vowels across and codas down.
- **Graphemes**: every grapheme, by Unicode group or catalogue number.
- **Draw**: a drawing pad ranked by shape against Noto Serif Khitan Small Script.
- **Reading**: an input method over readings, with phonetic letters or plain ones.
- **Words** and **Sentences**: attested words with their evidence, and interlinear sentences.
- **Blocks**: the text being written, set as blocks in columns running right to left.
- **Large script**: reconstructions on BabelStone's Private Use code points.

## Build

```sh
mkdir -p cache/web    # downloads listed in docs/materials.md
scripts/extract_otake2020.py <dissertation.pdf>
scripts/extract_otake_papers.py <directory of the papers>
scripts/extract_kss_mappings.py cache/web/KSS_Mappings.pdf > data/unicode/kss_mappings.tsv
scripts/extract_web_layers.py
python3 scripts/build_db.py          # dist/khitan.sqlite
python3 -m unittest discover tests
python3 scripts/build_site_data.py   # app/public/data/khitan.json
bun install
bun run dev
```

`scripts/build_shapes.py` builds the pen lines the drawing pad compares with. `scripts/messages.py` writes the five interface languages to `messages/`.

The tables are described in [`docs/database.md`](docs/database.md) and the sources in
[`docs/materials.md`](docs/materials.md). `data/sources.tsv` states every source's terms.

## Deployment

A push to `main` runs the tests, type check and build, then deploys to <https://khitan.mkpo.li/>. It needs the repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

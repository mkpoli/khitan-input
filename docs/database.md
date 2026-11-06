# Database

`dist/khitan.sqlite`, built from the TSV files in `data/`. The schema is `scripts/schema.sql`.

## Keys

A **grapheme** is a number in 大竹昌巳 (2020)'s catalogue, itself the numbering of 契丹文字研究小組
(1985) with `D` forms and `C` additions. A **character** is a Unicode code point. They differ: the
catalogue holds 368 current graphemes, Unicode 477 code points. Spellings are stored as grapheme
numbers, with Unicode text alongside when every grapheme has a code point.

| Grapheme status | Rows | Meaning |
| --- | --- | --- |
| `current` | 368 | a grapheme in Otake's inventory |
| `variant` | 12 | a catalogue number now counted as a variant of `target`; it keeps its own code point |
| `renumbered` | 14 | replaced by the number in `target` |
| `sequence` | 4 | two graphemes, listed in `target` |
| `void` | 31 | a number with no grapheme behind it |
| `uncatalogued` | 2 | set in the dissertation's text, absent from its table |

## Grapheme to code point

`unicode_method` says how each link was made:

- `west_1985_number`: the 1985 number in West, Zaytsev and Everson's mapping table.
- `west_1985_renumbered`: the same, through an old number (005 → 004D).
- `visual`: judged by eye against Noto Serif Khitan Small Script, with `unicode_confidence`.

Twelve graphemes have no code point: 002D, 211D, C03, C05, C09, C13, C15, C16, C19, C20, C21, C29.
Four have a weak match in `unicode_candidate`, which is not used for text. The glyphs of 275, 276 and
277 in the dissertation have a left-hand element that Noto's forms at West's code points lack.

## Readings

`reading.tier` grades each value:

| Tier | Evidence |
| --- | --- |
| `stated` | printed as the grapheme's value in Otake's tables, 補遺 or text |
| `stated_tentative` | the same, marked with a question mark |
| `stated_unattested` | the same, marked `*` |
| `single_grapheme_word` | a one-grapheme word in the rhyme list or loan table; may be a whole word |
| `aligned_spelling` | a segment in a segmented spelling; onset use and logograms are not separated |
| `scholar` | another scholar's value, from their own list |
| `scholar_via_n4725r` | another scholar's value, as reported in N4725R Table 6 |

Otake's papers use different notations, kept as printed: 2015 writes `tā` and `qā`, and 2018 writes `e`,
`ee` and `ä` for the dissertation's `ə`, `əə` and `e`. `kind` separates `phonetic` values from Kane's `semantic` glosses (ABOVE, NORTH) and `mnemonic`
readings. `primary_reading` holds one value per grapheme in the dissertation's notation: the 2025 tables first,
then the dissertation by tier.

## Availability

`source.terms` gives each source's terms. The dissertation's full text is not public, and `rhyme`, `cognate`,
`loan_spelling`, `document`, `bibliography` and rows of `form` with source `otake2020` come from it.

## Attested material

| Table | Rows | Content |
| --- | --- | --- |
| `document` | 146 | 43 small-script, 13 large-script and 90 Chinese inscriptions |
| `rhyme` | 795 | rhyme words by document, line, stanza and verse |
| `cognate`, `cognate_reflex` | 178, 799 | Khitan words with Mongolic and other comparanda |
| `loan_spelling`, `loan_use` | 702, 1490 | Chinese words in the small script, by rhyme group |
| `form` | 1010 | spellings with transcription, harvested from running text, by `source` |
| `example`, `example_line`, `example_word` | 13, 36, 249 | interlinear sentences from Otake (2018), with citation; glosses by line because one gloss can cover two written words |
| `attestation` | 5825 | document and line for the above |
| `bibliography` | 460 | the dissertation's references |
| `erratum` | 9 | places where a glyph and its printed number disagree |

Rows in `form` come from a pattern over running text and include noise. Remarks in the appendices are
left out.

## Large script

Unencoded, so `large_reading` keys on BabelStone's Private Use code points and holds Liu and Wang's
189 reconstructions. No catalogue table exists yet.

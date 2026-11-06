# Materials

Every source used, every one found while looking, and what is still missing. Retrieved 2026-11-06.
"Opened" means the file or page was read here; the rest comes from search results or citations.

## In use

Citations and terms are in `data/sources.tsv`.

| Source | Gives | Terms |
| --- | --- | --- |
| 大竹昌巳 (2020), dissertation, Kyoto University, 甲第22174号. [KURENAI](https://hdl.handle.net/2433/253009) | grapheme inventory and values, forms, rhyme list, cognates, loan spellings, documents, bibliography | abstracts only are public (学位規則第9条第2項); [NDL](https://dl.ndl.go.jp/pid/11492485) on-site only |
| 大竹昌巳 (2025), 『2025年蒙古学研究国际学术研讨会论文集』9–14 | long vowels and VC graphemes before coronals (TABLE I, II), read by eye from a scan | published |
| 大竹昌巳 (2024), [『言語研究』165](https://doi.org/10.11435/gengo.165.0_85) | spellings with transcriptions | published |
| 大竹昌巳 (2018), 「契丹語を俯瞰する」 and its 例文集, [project site](https://sites.google.com/view/ilcaa-mongolic/) | grapheme grids, spellings, 13 interlinear sentences | password-protected download; none stated |
| 大竹昌巳 (2015), [『言語研究』148](https://www.jstage.jst.go.jp/article/gengo/148/0/148_81/_article/-char/ja) | V and CV graphemes (表6, 表9), spellings | free on J-STAGE |
| [Unicode 18.0 UCD](https://www.unicode.org/Public/18.0.0/ucd/) | code points, names, radical groups | Unicode License V3 |
| [KSS_Mappings](https://babelstone.co.uk/Khitan/KSS_Mappings.pdf), West, Zaytsev and Everson, 2020 | code point to 16 catalogue numberings | none stated |
| [N4725R](https://www.unicode.org/L2/L2016/16113r-n4725r-khitan-small-script.pdf) Table 6, 2016 | values by six scholars, relations between characters | none stated |
| [Kane 2009 index](https://babelstone.co.uk/Khitan/Kane2009List.html), transcribed by West | values and glosses | Brill's book; page states none |
| [Liu and Wang 2004 list](https://babelstone.co.uk/Khitan/LiuWang2004.html), transcribed by West | 189 large-script reconstructions | none stated |
| [BabelStone Khitan Large Glyphs](https://www.babelstone.co.uk/Fonts/KhitanLarge.html) v1.012, 2023 | the face of the Large script page; 1,469 Private Use glyphs, unordered and experimental | redistributable, not for sale alone |
| [Noto Serif Khitan Small Script](https://github.com/notofonts/khitan-small-script) | shapes compared by eye; 470 of the block, plus the filler, without U+18CD6–18CDA and U+18CFF | OFL 1.1 |

Otake's fonts, `KhitanSmall` and `KSS-Gengokenkyu`, identify glyphs during extraction and are never
written out. Font revisions between the papers changed some outlines; `data/otake_papers/` records how each
such glyph was identified, and five stay unidentified.

大竹昌巳 (2018) 「日本契丹学小史」 gives the history of the field and no data. 大竹昌巳 (2013) is the
predecessor of the 2015 paper; its text layer is OCR and has lost the Khitan.

## How the script is encoded

Unicode encodes graphemes, not blocks. Characters run left to right, then top to bottom within a
block. U+16FE4 KHITAN SMALL SCRIPT FILLER selects the layout with one grapheme on the first line
([Core Spec ch.18](https://www.unicode.org/versions/latest/core-spec/chapter-18/),
[N5002](https://www.unicode.org/L2/L2018/18213-n5002-khitan-small-ad-hoc.pdf); the filler's exact
effect is read from these and Wikipedia). NamesList marks U+18C3E and U+18CD6–18CDA as tentatively
Jurchen Small Script; `character.jurchen_tentative` carries that. Noto Serif Khitan Small Script forms these blocks in its own shaping. U+18CFF is the blank.

## Found, not used yet

- [BabelStone Khitan Small](https://www.babelstone.co.uk/Fonts/KhitanSmall.html) v16.000, 2024: covers U+18CFF. Free for use, with no explicit redistribution grant. Not downloaded.
- [N4631](https://www.unicode.org/L2/L2014/14234-n4631-khitan.pdf), China, 2014: 2,218 large-script characters with a document survey. PDF only; its tables are not parsed.
- [N5319](https://www.unicode.org/wg2/docs/n5319-KhitanLargeScriptEncoding.pdf), 2025: replaces N4631. [N5323](https://www.unicode.org/L2/L2025/25166-wg2-n5323.pdf) (West, Zaytsev) criticises it as a glyph encoding without source references. Repertoire not checked.
- [吉本智慧子 (Aisin Gioro) 2012](http://www.ritsumei.ac.jp/acd/cg/lt/rb/627/627PDF/yosimoto.pdf), 立命館文學 627: reading notes, and who first proposed each value. Cited by N4725R; not opened. The largest missing layer.
- 大竹昌巳 (2025) TABLE IV–XIII: about 100 cognates with glyphs, in a scan. Not yet transcribed.
- Ōtake 2017, [AOASH 70(2)](https://real.mtak.hu/56021/): not read.
- [ja.wiktionary per-character pages](https://ja.wiktionary.org/wiki/%F0%98%AC%AD): copies of N4725R Table 6. [en.wiktionary Module:zkt-translit/data](https://en.wiktionary.org/wiki/Module:zkt-translit/data): source not stated. Neither adds evidence.
- [Xebec33 Rime schemas](https://github.com/Xebec33/khitan_small_script_wubi), GPL-3.0: one author's Wubi codes, in the Private Use Area and built around CCAMC fonts. A design reference at most.
- CCAMC: not used, by this site's policy.
- [Brett-Khitan-Script-Decoder](https://github.com/nbbulk-dotcom/Brett-Khitan-Script-Decoder): excluded. Its decoding claim has no support.

## Missing

- A transcribed corpus. No full inscription text in Unicode was found; the database has cited forms and 13 sentences.
- A large-script catalogue with source references. West and Zaytsev hold an unpublished spreadsheet of N4631, according to N5323.
- Input codes for the small script from an open source.

# Qingling Seal (draft)

A pilot typeface for the seal-script titles of the Daozong and Xuanyi 哀册 covers, at their Khitan
small-script code points on a 1024-unit em with a variable round pen. The OpenType `wght` axis runs from 200 to 800. Regular (400) has a 30-unit stroke, with 18-unit strokes at 200 and 56-unit strokes at 800. The two Xuanyi blocks for U+18C64
share one code point. The `ss01` feature selects XY-05, the joined diagonal of XY-11, and the stepped, unbranched XY-12. The default forms for U+18CA6 and U+18C9C follow DZ-31 and DZ-17 respectively.

`forms.json` is the vector source: 39 drawings, each a list of centreline paths in font units.
`scripts/build_seal_font.py` expands them with the round pen and writes the TTF, WOFF2 and the full
gallery. The glyphs are redrawn after the photographs.

The pen, the em and the fixed advance follow [Sealie](https://github.com/iebb/sealie), the Small
Seal typeface by ieb (SIL OFL 1.1).

The 36 distinct characters on the covers use 38 Unicode code points in the font. The `unicode_aliases` table in `correspondences.json` follows West’s two alternative identifications: U+18C04 shares the roof form at U+18C39, and U+18C32 shares the form at U+18C7F. The Daozong drawings use the first occurrence of each of the 21 additional characters. Repeated characters share an outline.

At heavier weights, the inner legs of XY-06 and XY-14 shorten under the crossbar, and the two ends of the DZ-07 canopy draw apart. DZ-14 and DZ-29 also have extra clearance beside their uprights. The offsets in `heavy_terminals` are in fitted font units at weight 800. They taper along each stroke and interpolate from zero at 400.

## Proposed forms

Sixteen proposed characters bring the font to 54 code points. These modern designs preserve the stroke count and joins of the regular Khitan glyphs in Noto Serif Khitan Small Script. DZ-27 supplies the projecting central stem and DZ-28 the stacked crossbars with a detached upper bar. The flush joins in the proposed designs follow the regular Khitan forms. Their crossbars, pen widths and fixed advance carry through to the proposed forms.

| Khitan | Daozong model | Zhuque Fangsong | Sealie | Construction |
| --- | --- | --- | --- | --- |
| U+18B03 | DZ-28 | 干 | U+3D664 | Open lower stem and horizontal head. The Chinese seal head forks. |
| U+18B04 | DZ-28 | 王 | U+3D068 | Three bars with a flush stem. |
| U+18B36 | DZ-27 | 十 | U+3D67E | A single crossbar on a projecting upright. |
| U+18B54 | DZ-27 | 土 | U+3F859 | One crossbar and a wider foot. |
| U+18B76 | DZ-07 | 大 | U+3EDB1 | Crossbar over the forked legs of DZ-07. The upright projects above the bar. |
| U+18B29 | DZ-07 | 天 | U+3D003 | Cap the upright with a second, shorter bar above the forked legs. |
| U+18B46 | DZ-31 | 木 | U+3DFA9 | Paired oblique limbs join the central upright below a free crossbar. |
| U+18B47 | DZ-31 | 本 | U+3E04A | Add a short foot flush with the bottom of the upright. The Khitan foot sits below both oblique limbs. |
| U+18B3A | DZ-13 | 中 | U+3D119 | A projecting upright crosses an open bowl. A separate horizontal passes through the upright above the bowl tips. |
| U+18B9D | DZ-13 | 山 | U+3EA5A | Two raised side stems turn into a common foot. The central stem ends on the foot. |
| U+18BA2 | DZ-13 | 出 | U+3E19B | Two stacked open bowls share a tall upright. The gap between bowls keeps their four side stems distinct. |
| U+18BC2 | DZ-10 | 目 | U+3D97F | A tall rounded enclosure with two interior bars attached to the left wall. Both tips stop short of the right wall. |
| U+18BCC | DZ-10 | 由 | U+3F60C | One short internal crossbar on a central stem. The stem rises above the enclosure and meets its base. |
| U+18C4C | DZ-01 | 乂 | U+3F552 | Use the crossing curves inside the split canopy of DZ-01, with the left entry lower than the right. |
| U+18C52 | DZ-01 | 文 | U+3E9C6 | A detached slant above a horizontal. Only the descending right-hand entry of the crossing pair meets the horizontal. |
| U+18C28 | DZ-07 | 八 | U+3D323 | Two separate, outward-falling strokes. The right entry rises higher and the inner gap stays open. |

The Han columns illustrate changes of stroke treatment. Their pairings use `kSEAL_MCJK` in the [ids-input SealSources data](https://github.com/mkpoli/ids-input/blob/dbb49a933f301ee710dc88d580d77aee3456785d/data/seal-sources.txt.gz). The Han comparison uses [Zhuque Fangsong](https://github.com/mkpoli/ids-input/blob/dbb49a933f301ee710dc88d580d77aee3456785d/fonts/ZhuqueFangsong-Regular.woff2) and [Sealie](https://github.com/iebb/sealie/tree/303bf0b3c506bb3f1c39a868fe63d1e422a91d24/fonts). Each web subset contains the comparison characters listed above. The Khitan drawings use independent centrelines in `analogues.json`.

## Record

- `forms.json` — the vector centrelines in font units.
- `cuts/` — centred colour cuts and optional masks of the stone blocks, for redrawing outside the
  repository.

## Sources and licences

- **Daozong photograph.** 红烧腰果, 2019-07-14, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Funeral_Epitaph_in_Khitan_Script_and_Its_Cover_of_Emperor_Daozong_of_Liao_Dynasty.jpg), CC BY 4.0. The Daozong glyphs are vector redrawings of this photograph.
- **Xuanyi photograph.** Tonyxy1992, 2015-08-05, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Epitaph_of_Empress_Xuanyi_of_Liao.jpg), CC BY-SA 4.0. The vector glyphs redraw this photograph; they and the font are offered under CC BY-SA 4.0.
- **Sealie.** ieb, [Sealie](https://github.com/iebb/sealie), SIL OFL 1.1. Model for the 30-unit round pen, the 1024-unit em and the fixed advance.
- **Inscription.** 王靜如 (1931), 「遼道宗及宣懿皇后契丹國字哀冊初釋」, 《中央研究院歷史語言研究所集刊》第三本第四分, 467–478, plate 3.
- **Code points.** Andrew West, [BabelStone Khitan Small Seal](https://www.babelstone.co.uk/Fonts/KhitanSmallSeal.html), v13.000, 2023.
- **Cover reading.** Andrew Shimunek, “Toward a decipherment and linguistic reconstruction of the 1101 A.D. Kitan Eulogy for Empress Xuanyi”, *Acta Orientalia Academiae Scientiarum Hungaricae* 70.2 (2017), 253–272.

## Rebuilding

```sh
uv run scripts/build_seal_font.py
uv run scripts/build_seal_comparison_fonts.py path/to/Sealie.woff path/to/ZhuqueFangsong-Regular.woff2
uv run tests/seal_gaps.py
```

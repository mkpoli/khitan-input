# Qingling Seal (draft)

A pilot typeface for the seal-script titles of the Daozong and Xuanyi 哀册 covers, at their Khitan
small-script code points on a 1024-unit em with a variable round pen. The OpenType `wght` axis runs from 200 to 800. Regular (400) has a 30-unit stroke, with 18-unit strokes at 200 and 56-unit strokes at 800. The two Xuanyi blocks for U+18C64
share one code point; the second carving is the `ss01` alternate.

`forms.json` is the vector source: 37 drawings, each a list of centreline paths in font units.
`scripts/build_seal_font.py` expands them with the round pen and writes the TTF, WOFF2 and the full
gallery. The glyphs are redrawn after the photographs.

The pen, the em and the fixed advance follow [Sealie](https://github.com/iebb/sealie), the Small
Seal typeface by ieb (SIL OFL 1.1).

The 36 distinct characters on the covers use 38 Unicode code points in the font. The `unicode_aliases` table in `correspondences.json` follows West’s two alternative identifications: U+18C04 shares the roof form at U+18C39, and U+18C32 shares the form at U+18C7F. The Daozong drawings use the first occurrence of each of the 21 additional characters. Repeated characters share an outline.

## Proposed forms

Four additional Unicode characters bring the font to 42 code points. These modern designs preserve the stroke count and joins of the regular Khitan glyphs in Noto Serif Khitan Small Script. DZ-27 supplies the projecting central stem and DZ-28 the flush join. Their crossbars, pen widths and fixed advance carry through to the proposed forms.

| Khitan | Daozong model | Zhuque Fangsong | Sealie | Construction |
| --- | --- | --- | --- | --- |
| U+18B03 | DZ-28 | 干 | U+3D664 | Open lower stem and horizontal head. The Chinese seal head forks. |
| U+18B04 | DZ-28 | 王 | U+3D068 | Three bars with a flush stem. |
| U+18B36 | DZ-27 | 十 | U+3D67E | A single crossbar on a projecting upright. |
| U+18B54 | DZ-27 | 土 | U+3F859 | One crossbar and a wider foot. |

The Han columns illustrate changes of stroke treatment. Their pairings use `kSEAL_MCJK` in the [ids-input SealSources data](https://github.com/mkpoli/ids-input/blob/dbb49a933f301ee710dc88d580d77aee3456785d/data/seal-sources.txt.gz). The Han comparison uses [Zhuque Fangsong](https://github.com/mkpoli/ids-input/blob/dbb49a933f301ee710dc88d580d77aee3456785d/fonts/ZhuqueFangsong-Regular.woff2) and [Sealie](https://github.com/iebb/sealie/tree/303bf0b3c506bb3f1c39a868fe63d1e422a91d24/fonts). Each web subset contains the four comparison characters. The Khitan drawings use independent centrelines in `analogues.json`.

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
```

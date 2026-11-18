# Qingling Seal (draft)

A pilot typeface for the seal-script titles of the Daozong and Xuanyi 哀册 covers, at their Khitan
small-script code points on a 1024-unit em with a 30-unit round pen. The two Xuanyi blocks for U+18C64
share one code point; the second carving is the `ss01` alternate.

`forms.json` is the vector source: 37 drawings, each a list of centreline paths in font units.
`scripts/build_seal_font.py` expands them with the round pen and writes the TTF, WOFF2 and the full
gallery. The glyphs are redrawn after the photographs.

The pen, the em and the fixed advance follow [Sealie](https://github.com/iebb/sealie), the Small
Seal typeface by ieb (SIL OFL 1.1).

The font covers 36 Unicode characters. The Daozong drawings use the first occurrence of each of the 21 additional characters. Repeated characters share an outline.

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

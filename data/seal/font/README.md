# Qingling Seal (draft)

A pilot typeface for the sixteen seal-script blocks of the Xuanyi 哀册 cover: U+E700–U+E70F on a
1024-unit em with a 30-unit round pen.

The glyphs are not traced from the stone photograph. `reference.png` is an abstracted drawing of
the sixteen blocks; the builder traces its dark strokes to centrelines, smooths them, and expands
them with the round pen. The drawing keeps the block order of the cover: four columns, top to
bottom, right to left.

The pen, the em and the fixed advance follow [Sealie](https://github.com/iebb/sealie), the Small
Seal typeface by ieb (SIL OFL 1.1).

This is a **draft** of the sixteen Xuanyi blocks. The Daozong cover (30 blocks) is not drawn, and
the abstraction is simplified.

## Record

- `reference.png` — the sixteen-block drawing.
- `forms.json` — the traced centrelines in font units.
- `cuts/` — centred colour cuts and optional masks of the stone blocks, for redrawing outside the
  repository.

## Sources and licences

- **Photograph.** Tonyxy1992, 2015-08-05, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Epitaph_of_Empress_Xuanyi_of_Liao.jpg), CC BY-SA 4.0. The drawing abstracts this photograph; the glyphs and font are offered under CC BY-SA 4.0.
- **Sealie.** ieb, [Sealie](https://github.com/iebb/sealie), SIL OFL 1.1. Model for the 30-unit round pen, the 1024-unit em and the fixed advance.
- **Inscription.** 王靜如 (1931), 「遼道宗及宣懿皇后契丹國字哀冊初釋」, 《中央研究院歷史語言研究所集刊》第三本第四分, 467–478, plate 3.

## Rebuilding

```sh
uv run scripts/build_seal_font.py
```

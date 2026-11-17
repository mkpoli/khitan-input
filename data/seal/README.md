# Seal-script covers of the Qingling 哀册

The stone covers of the Daozong and Xuanyi 哀册 carry their titles in a squared seal script: 30
blocks in six columns of five on the Daozong cover, 16 in four columns of four on the Xuanyi cover.
The photographs are of the stones in the Liaoning Provincial Museum.

王靜如 (1931) identifies the inscriptions and reads the first line of each epitaph text. The 16
Xuanyi blocks correspond to characters of that title, `宣懿皇后哀冊`, as read by Shimunek (2017);
the 30 Daozong blocks remain `unidentified`.

## Record

`records.json` holds the two inscriptions and 46 block records:

| field | meaning |
| --- | --- |
| `id` | `DZ-01`–`DZ-30`, `XY-01`–`XY-16`, in reading order |
| `inscription` | `daozong` or `xuanyi` |
| `n` | position in reading order |
| `col` | the column, 1 on the right |
| `row` | the row, 1 at the top |
| `identification` | the regular Khitan character, or null |
| `unicode` | its code point, or null |
| `status` | `identified` or `unidentified` |
| `confidence` | `probable` where the shape match is editorial |
| `basis` | the evidence for the correspondence |

`correspondences.json` holds the sixteen Xuanyi matches, keyed by block id. The builder merges them
into `records.json`; Daozong blocks stay unidentified.

Each inscription also carries its title, object, person, date, plate number, photograph source and
display image. `sources` holds the two Commons photographs and the 1931 article, with author, date,
licence and terms.

## Sources and licences

- **Daozong cover.** Photograph by 红烧腰果, 2019-07-14, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Funeral_Epitaph_in_Khitan_Script_and_Its_Cover_of_Emperor_Daozong_of_Liao_Dynasty.jpg), CC BY 4.0. The image is cropped to the cover; the WebP is derived from it and offered under CC BY 4.0.
- **Xuanyi cover.** Photograph by Tonyxy1992, 2015-08-05, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Epitaph_of_Empress_Xuanyi_of_Liao.jpg), CC BY-SA 4.0. The image is cropped to the cover; the WebP is derived from it and offered under CC BY-SA 4.0.
- **王靜如 (1931).** 「遼道宗及宣懿皇后契丹國字哀冊初釋」《中央研究院歷史語言研究所集刊》第三本第四分，467–478頁，圖版一至四。 [PDF](https://www1.ihp.sinica.edu.tw/storage/w2_file/5017YcdiByr.pdf), [article page](https://www1.ihp.sinica.edu.tw/Publications/Bulletin/856/Article/1167). No reuse licence stated. Used for the inscriptions, dates and plates; its plates are not reproduced.
- **BabelStone Khitan Small Seal.** Andrew West, [BabelStone Fonts](https://www.babelstone.co.uk/Fonts/KhitanSmallSeal.html), version 13.000. Maps 38 seal-script characters from the two covers to Unicode; the Xuanyi shapes were matched against this repertoire. Free to use and redistribute, not to be sold on its own.
- **Shimunek (2017).** Andrew Shimunek, “Toward a decipherment and linguistic reconstruction of the 1101 A.D. Kitan Eulogy for Empress Xuanyi”, *Acta Orientalia Academiae Scientiarum Hungaricae* 70.2, 253–272. [PDF](http://real.mtak.hu/56024/1/062.2017.70.2.6.pdf). Reads the opening title `s.ÿê.n i.i nou.e omo.n g.en.eñ č.ai w.un`, corresponding to `宣懿皇后哀冊`.

## Rebuilding

```sh
uv run scripts/build_seal_images.py
```

The builder downloads each photograph once into `cache/`, checks its SHA-256, crops the cover, writes
`app/public/seal/daozong-cover.webp` and `xuanyi-cover.webp`, and writes `records.json`. The page
reads `records.json` directly.

// What the script itself decides: how graphemes stack into a block, and how a reading is typed.

export const FILLER = '\u{16FE4}'
export const MARK = '\u{18BA7}'

const isKhitan = (/** @type {number} */ cp) => (cp >= 0x18b00 && cp <= 0x18cff)

/** @param {string} text */
export const hasKhitan = text => [...text].some(ch => isKhitan(ch.codePointAt(0) ?? 0))

/** @param {string} cp a code point in hex */
export const fromHex = cp => String.fromCodePoint(parseInt(cp, 16))

/** @param {string} ch */
export const hexOf = ch => (ch.codePointAt(0) ?? 0).toString(16).toUpperCase().padStart(4, '0')

/**
 * Rows of a block: pairs read left to right, then top to bottom, an odd last grapheme centred. A
 * filler after the first grapheme sets it alone on the first row.
 * @template T @param {T[]} items @param {boolean} [single] @returns {T[][]}
 */
export function blockRows(items, single = false) {
  const rows = []
  let at = 0
  if (single && items.length) { rows.push([items[0]]); at = 1 }
  for (; at < items.length; at += 2) rows.push(items.slice(at, at + 2))
  return rows
}

/** A written word as its graphemes and its layout. @param {string} word */
export function parseWord(word) {
  const chars = [...word]
  const single = chars[1] === FILLER
  return { chars: chars.filter(ch => ch !== FILLER), single }
}

/** Plain letters for a phonetic value, so a reading can be typed on any keyboard. @param {string} value */
export function fold(value) {
  return value.normalize('NFD').toLowerCase()
    .replace(/[̀-ͯ]/g, '')
    .replace(/[ʷᵘ’'*?()\[\]]/g, '')
    .replace(/ə/g, 'e').replace(/ɵ/g, 'o').replace(/ʊ/g, 'u').replace(/[ıɨɪ]/g, 'i')
    .replace(/ǰ/g, 'j').replace(/ŋ/g, 'ng').replace(/[γğ]/g, 'g').replace(/χ/g, 'x')
    .replace(/ɲ/g, 'n').replace(/[ʧʨ]/g, 'c').replace(/[ʂʃ]/g, 's')
}

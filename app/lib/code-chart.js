// The code chart: every mapped grapheme by code point, in pages of 16-code rows, with the counts
// the inventory, the block, the statuses and the mappings add up to.

export const BLOCK_START = 0x18b00
export const BLOCK_END = 0x18cff
export const FILLER = 0x16fe4
export const PAGE_SIZE = 256
export const COLUMNS = 16
/** The bundled Noto Serif Khitan Small Script 1.000 stops at U+18CD5; these cells stay code-only. */
export const NO_GLYPH = new Set([0x18CD6, 0x18CD7, 0x18CD8, 0x18CD9, 0x18CDA, 0x18CFF])

/** @param {number} cp */
const hex = cp => cp.toString(16).toUpperCase().padStart(4, '0')

/** @param {number} cp */
export const codePointLabel = cp => `U+${hex(cp)}`

/** @param {{ start: number, end: number }} range */
export const rangeLabel = range => `${codePointLabel(range.start)}–${codePointLabel(range.end)}`

/**
 * Every mapped grapheme, the block's pages with an empty slot for each unassigned code point,
 * and the counts for the page.
 * @param {any[]} graphemes
 */
export function codeChart(graphemes) {
  const mapped = graphemes
    .filter(g => g.cp)
    .sort((a, b) => parseInt(a.cp, 16) - parseInt(b.cp, 16))
  /** @type {Map<number, any>} */
  const byCp = new Map()
  for (const g of mapped) {
    const cp = parseInt(g.cp, 16)
    if (byCp.has(cp)) throw new Error(`Two graphemes share U+${cp.toString(16).toUpperCase()}`)
    byCp.set(cp, g)
  }

  const pages = []
  for (let start = BLOCK_START; start <= BLOCK_END; start += PAGE_SIZE) {
    const cells = Array.from({ length: PAGE_SIZE }, (_, i) => {
      const g = byCp.get(start + i)
      return g ? { ...g, drawn: !NO_GLYPH.has(start + i) } : null
    })
    pages.push({ start, end: start + PAGE_SIZE - 1, cells, filled: cells.filter(Boolean).length })
  }

  /** @type {Record<string, number>} */
  const status = {}
  for (const g of graphemes) status[g.st] = (status[g.st] ?? 0) + 1

  const confidence = { high: 0, medium: 0, none: 0 }
  for (const g of mapped) {
    if (g.uc === 'high') confidence.high++
    else if (g.uc === 'medium') confidence.medium++
    else confidence.none++
  }

  const block = mapped.filter(g => {
    const cp = parseInt(g.cp, 16)
    return cp >= BLOCK_START && cp <= BLOCK_END
  }).length

  return {
    graphemes: graphemes.length,
    codePoints: mapped.length,
    withoutCodePoint: graphemes.length - mapped.length,
    block,
    filler: byCp.has(FILLER) ? 1 : 0,
    status,
    confidence,
    pages,
  }
}

// The records, and the indexes every page reads. Filled once, when the file arrives.
import { fold, fromHex } from './script.js'

export const ix = {
  /** @type {any[]} */ graphemes: [],
  /** @type {Map<string, any>} */ byId: new Map(),
  /** @type {Map<string, any>} */ byChar: new Map(),
  /** @type {any[]} */ words: [],
  /** @type {any[]} */ examples: [],
  /** @type {any[]} */ documents: [],
  /** @type {any[]} */ sources: [],
  /** @type {any[]} */ large: [],
  /** @type {Map<string, any>} */ source: new Map(),
  /** @type {{ key: string, g: any, rank: number }[]} */ readings: [],
}

/** Otake's values rank above other scholars', stated values above inferred ones. @param {any} r */
function rankOf(r) {
  if (r.s === 'otake2025') return 0
  if (r.s === 'otake2020') return r.t?.startsWith('stated') ? 0 : r.t === 'single_grapheme_word' ? 1 : 2
  if (r.s?.startsWith('otake')) return 3
  return 4
}

/** @param {any} data */
export function fill(data) {
  Object.assign(ix, { graphemes: data.graphemes, words: data.words, examples: data.examples, documents: data.documents, sources: data.sources, large: data.large })
  for (const g of ix.graphemes) {
    g.char = g.cp ? fromHex(g.cp) : ''
    ix.byId.set(g.id, g)
    if (g.char) ix.byChar.set(g.char, g)
    for (const r of g.rs ?? []) if (r.k !== 'semantic' && r.k !== 'mnemonic') ix.readings.push({ key: fold(r.v), g, rank: rankOf(r) })
  }
  for (const s of ix.sources) ix.source.set(s.id, s)
  for (const w of ix.words) w.search = [w.f, w.f && fold(w.f), w.g, w.h, w.sg].filter(Boolean).join(' ').toLowerCase()
}

/** Graphemes whose reading matches, best first. @param {string} query */
export function searchReadings(query) {
  const key = fold(query.trim())
  if (!key) return []
  /** @type {Map<any, number>} */
  const best = new Map()
  for (const r of ix.readings) {
    const exact = r.key === key
    if (!exact && !r.key.startsWith(key)) continue
    const score = r.rank + (exact ? 0 : 10)
    if (!best.has(r.g) || /** @type {number} */ (best.get(r.g)) > score) best.set(r.g, score)
  }
  return [...best].sort((a, b) => a[1] - b[1] || a[0].id.localeCompare(b[0].id)).map(([g]) => g)
}

/** The value a reading search matched, which may not be the primary one. @param {any} g @param {string} query */
export function matchedReading(g, query) {
  const key = fold(query.trim())
  const values = (g.rs ?? []).filter((/** @type {any} */ r) => r.k !== 'semantic' && r.k !== 'mnemonic')
  const hit = values.find((/** @type {any} */ r) => fold(r.v) === key) ?? values.find((/** @type {any} */ r) => key && fold(r.v).startsWith(key))
  return hit?.v ?? g.v
}

/** Words whose form, gloss, Chinese or segmentation holds the query. @param {string} query @param {string} [kind] */
export function searchWords(query, kind = '') {
  const q = query.trim().toLowerCase()
  const folded = fold(q)
  return ix.words.filter(w => (!kind || w.k === kind) && (!q || w.search.includes(q) || w.search.includes(folded)))
}

/** A grapheme by catalogue number or code point. @param {string} query */
export function lookup(query) {
  const q = query.trim()
  const cp = /^u\+?([0-9a-f]{4,5})$/i.exec(q)
  if (cp) return ix.graphemes.filter(g => g.cp === cp[1].toUpperCase())
  const number = /^(\d{1,3})([dD]?\??)$|^([cC]\d{2})$/.exec(q)
  if (!number) return []
  const id = number[3] ? number[3].toUpperCase() : number[1].padStart(3, '0') + number[2].toUpperCase()
  const hit = ix.byId.get(id)
  return hit ? [hit] : []
}

/** Words whose spelling holds a grapheme. @param {string} id */
export const wordsWith = id => ix.words.filter(w => w.sp && w.sp.replace(/~/g, ' ').split(/\s+/).includes(id))

/** The primary reading of a character, for transcription. @param {string} ch */
export const readingOf = ch => ix.byChar.get(ch)?.v ?? ''

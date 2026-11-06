// The text being written: one per browser, kept in local storage. Every finder inserts at the caret.
import { hexOf } from './script.js'
import { readingOf } from './data.js'

const KEY = 'khitan-input:text'

export const text = $state({
  value: (typeof localStorage !== 'undefined' && localStorage.getItem(KEY)) || '',
  start: -1,
  end: -1,
})

function save() {
  try { localStorage.setItem(KEY, text.value) } catch { /* storage may be full or blocked */ }
}

/** @param {string} value */
export function setText(value) {
  text.value = value
  save()
}

/** @param {HTMLTextAreaElement} field */
export function remember(field) {
  text.start = field.selectionStart
  text.end = field.selectionEnd
}

/** @param {string} chars */
export function insert(chars) {
  const length = text.value.length
  const start = text.start < 0 || text.start > length ? length : text.start
  const end = text.end < 0 || text.end > length ? length : Math.max(start, text.end)
  text.value = text.value.slice(0, start) + chars + text.value.slice(end)
  text.start = text.end = start + chars.length
  save()
}

/** @param {string} value */
export const asCodePoints = value => [...value].filter(ch => !/\s/.test(ch)).map(ch => `U+${hexOf(ch)}`).join(' ')

/** @param {string} value */
export const asReadings = value => value.split(/\s+/).filter(Boolean).map(word => [...word].map(ch => readingOf(ch) || '?').join('-')).join(' ')

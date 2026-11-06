// Toasts, the phone's card sheet, the theme, and the two things every finder does with a grapheme.
import { open } from './route.svelte.js'
import { insert } from './text.svelte.js'
import { t } from './i18n.svelte.js'

const THEME = 'khitan-input:theme'

export const toast = $state({ message: '', id: 0 })
export const ui = $state({
  sheet: false,
  theme: /** @type {'auto' | 'light' | 'dark'} */ ((typeof localStorage !== 'undefined' && localStorage.getItem(THEME)) || 'auto'),
})

/** @param {string} message */
export function say(message) {
  toast.message = message
  const id = ++toast.id
  setTimeout(() => { if (toast.id === id) toast.message = '' }, 1800)
}

/** @param {string} value @param {string} [label] */
export async function copy(value, label = value) {
  try {
    await navigator.clipboard.writeText(value)
    say(t('toast.copied', { what: label }))
  } catch {
    say(t('toast.clipboard'))
  }
}

/** @param {string} id */
export function choose(id) {
  open(id)
  if (matchMedia('(max-width: 900px)').matches) ui.sheet = true
}

/** @param {string} chars */
export function put(chars) {
  if (!chars) return
  insert(chars)
  say(t('toast.added', { char: chars }))
}

export function applyTheme() {
  if (ui.theme === 'auto') delete document.documentElement.dataset.theme
  else document.documentElement.dataset.theme = ui.theme
}

/** @param {'auto' | 'light' | 'dark'} theme */
export function setTheme(theme) {
  ui.theme = theme
  applyTheme()
  try { localStorage.setItem(THEME, theme) } catch { /* the choice lasts this visit */ }
}

/** @param {HTMLElement} node */
export function autofocus(node) {
  if (!matchMedia('(pointer: coarse)').matches) queueMicrotask(() => node.focus())
}

// What each page says about itself outside the page: the title a tab and a search result show, the
// one-line description under it, and the address the page answers at. The worker reads this to
// answer a crawler without running the app, and the app reads it to keep the head in step when a
// reader moves between pages without a page load. Titles and descriptions are catalogue keys, so
// the worker speaks English and the app speaks the reader's language.
import en from '../../messages/en.json' with { type: 'json' }
import { OTHER, PAGES } from './pages.js'

export const SITE = { name: 'Khitan Input', url: 'https://khitan.mkpo.li' }

/** The finder's description, which the page's own text has no line for. */
const HOME_DESCRIPTION = 'Find a Khitan small-script grapheme by its reading, number or meaning, read its record, and write Khitan in blocks.'

/** @type {Record<string, { title: string, description: string }>} */
const KEYS = {
  syllabary: { title: 'nav.syllabary', description: 'syllabary.intro' },
  graphemes: { title: 'nav.graphemes', description: 'graphemes.intro' },
  draw: { title: 'nav.draw', description: 'draw.intro' },
  reading: { title: 'nav.reading', description: 'reading.intro' },
  words: { title: 'nav.words', description: 'words.intro' },
  sentences: { title: 'nav.sentences', description: 'sentences.intro' },
  blocks: { title: 'nav.blocks', description: 'blocks.intro' },
  large: { title: 'nav.large', description: 'large.intro' },
  jurchen: { title: 'jurchen.title', description: 'jurchen.lead' },
  seal: { title: 'nav.seal', description: 'seal.intro' },
  codes: { title: 'nav.codes', description: 'nav.codes.hint' },
  documents: { title: 'nav.documents', description: 'documents.intro' },
  about: { title: 'nav.about', description: 'about.intro' },
}

/** The paths of the pages that have a head of their own, the finder's empty path first. */
export const SEO_PATHS = ['', ...Object.keys(KEYS)]

/** @param {string} key */
const english = key => /** @type {Record<string, string>} */ (en)[key]

/**
 * The page a pathname names, or null when no page answers there. A trailing slash is the same page.
 * @param {string} path a pathname
 * @returns {string | null}
 */
export function pageOf(path) {
  const clean = path.replace(/^\/+|\/+$/g, '')
  return [...PAGES.map(page => page.path), ...OTHER].includes(clean) ? clean : null
}

/**
 * The title, description and canonical address of a page.
 * @param {string} page
 * @param {(key: string) => string} [say] the reader's language; English when left out
 */
export function seoOf(page, say = english) {
  const url = `${SITE.url}/${page}`
  const keys = Object.hasOwn(KEYS, page) ? KEYS[page] : undefined
  if (!keys) return { title: SITE.name, description: HOME_DESCRIPTION, url }
  return { title: `${say(keys.title)} · ${SITE.name}`, description: say(keys.description), url }
}

/**
 * Put a page's title, description and canonical address into the document.
 * @param {string} page
 * @param {(key: string) => string} [say] the reader's language; English when left out
 */
export function applySeo(page, say = english) {
  if (typeof document === 'undefined') return
  const { title, description, url } = seoOf(page, say)
  document.title = title
  /** @param {string} selector @param {string} value @param {string} [attribute] */
  const set = (selector, value, attribute = 'content') => {
    document.head.querySelector(selector)?.setAttribute(attribute, value)
  }
  set('meta[name="description"]', description)
  set('link[rel="canonical"]', url, 'href')
  set('meta[property="og:title"]', title)
  set('meta[property="og:description"]', description)
  set('meta[property="og:url"]', url)
}

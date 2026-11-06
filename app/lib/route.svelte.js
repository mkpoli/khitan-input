// Where the reader is: the page in the path, the open grapheme in `?g=`, the page's query in `?q=`.
export const PAGES = /** @type {const} */ ([
  { path: '', label: 'nav.find', hint: 'nav.find.hint' },
  { path: 'syllabary', label: 'nav.syllabary', hint: 'nav.syllabary.hint' },
  { path: 'graphemes', label: 'nav.graphemes', hint: 'nav.graphemes.hint' },
  { path: 'draw', label: 'nav.draw', hint: 'nav.draw.hint' },
  { path: 'reading', label: 'nav.reading', hint: 'nav.reading.hint' },
  { path: 'words', label: 'nav.words', hint: 'nav.words.hint' },
  { path: 'sentences', label: 'nav.sentences', hint: 'nav.sentences.hint' },
  { path: 'blocks', label: 'nav.blocks', hint: 'nav.blocks.hint' },
  { path: 'large', label: 'nav.large', hint: 'nav.large.hint' },
])

const OTHER = ['documents', 'about']

function read() {
  const path = location.pathname.replace(/^\/+|\/+$/g, '')
  const page = [...PAGES.map(p => p.path), ...OTHER].includes(path) ? path : ''
  const params = new URLSearchParams(location.search)
  return { page, q: params.get('q') ?? '', g: params.get('g') ?? '' }
}

export const route = $state(read())

/** @param {{ page: string, q: string, g: string }} next */
function href(next) {
  const params = new URLSearchParams()
  if (next.q) params.set('q', next.q)
  if (next.g) params.set('g', next.g)
  const search = params.toString()
  return `/${next.page}${search ? `?${search}` : ''}`
}

/** @param {string} page @param {string} [q] */
export function go(page, q = '') {
  route.page = page
  route.q = q
  history.pushState(null, '', href(route))
  scrollTo(0, 0)
}

/** @param {string} id */
export function open(id) {
  route.g = id
  history.replaceState(null, '', href(route))
}

/** @param {string} q */
export function setQuery(q) {
  route.q = q
  history.replaceState(null, '', href(route))
}

/** @param {string} page @param {string} [q] */
export const link = (page, q = '') => href({ page, q, g: route.g })

addEventListener('popstate', () => Object.assign(route, read()))

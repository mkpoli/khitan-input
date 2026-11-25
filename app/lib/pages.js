// The pages the app renders: the tabs, then the pages reached from elsewhere. The route reads the
// list to place the reader, and the worker reads it to tell an app path from a mistyped address.
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
  { path: 'jurchen', label: 'nav.jurchen', hint: 'nav.jurchen.hint' },
  { path: 'seal', label: 'nav.seal', hint: 'nav.seal.hint' },
  { path: 'codes', label: 'nav.codes', hint: 'nav.codes.hint' },
])

// Reached from links and the footer rather than the tabs.
export const OTHER = ['documents', 'about']

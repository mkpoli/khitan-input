import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { OTHER, PAGES } from '../app/lib/pages.js'
import { SEO_PATHS, SITE, pageOf, seoOf } from '../app/lib/seo.js'
import en from '../messages/en.json'
import ja from '../messages/ja.json'

const read = (/** @type {string} */ path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')

describe('page SEO', () => {
  test('gives every page its own title, description and address', () => {
    const entries = SEO_PATHS.map(page => seoOf(page))
    for (const key of ['title', 'description', 'url'])
      expect(new Set(entries.map(entry => entry[key])).size, key).toBe(entries.length)
  })
  test('takes each page’s text from the catalogue', () => {
    expect(seoOf('syllabary')).toEqual({
      title: 'Syllabary · Khitan Input',
      description: en['syllabary.intro'],
      url: 'https://khitan.mkpo.li/syllabary',
    })
    expect(seoOf('jurchen').title).toBe('Jurchen script · Khitan Input')
    expect(seoOf('about').url).toBe('https://khitan.mkpo.li/about')
  })
  test('speaks the reader’s language when asked to', () => {
    const say = (/** @type {string} */ key) => /** @type {Record<string, string>} */ (ja)[key]
    expect(seoOf('words', say).title).toBe(`${ja['nav.words']} · Khitan Input`)
  })
  test('names the page a path belongs to', () => {
    expect(pageOf('/')).toBe('')
    expect(pageOf('/syllabary')).toBe('syllabary')
    expect(pageOf('/syllabary/')).toBe('syllabary')
    expect(pageOf('//about')).toBe('about')
    for (const path of ['/nope', '/about/extra', '/toString', '/__proto__']) expect(pageOf(path), path).toBeNull()
  })
  test('covers the pages the app renders and nothing else', () => {
    expect(new Set(SEO_PATHS)).toEqual(new Set([...PAGES.map(page => page.path), ...OTHER]))
  })
  test('runs the worker first for every page path so navigations get its head', () => {
    const config = JSON.parse(read('wrangler.jsonc').replace(/^\s*\/\/.*$/gm, ''))
    const first = new Set(config.assets.run_worker_first)
    for (const page of SEO_PATHS) {
      expect(first.has(`/${page}`), `/${page}`).toBe(true)
      if (page) expect(first.has(`/${page}/`), `/${page}/`).toBe(true)
    }
  })
})

describe('served head', () => {
  const html = read('app/index.html')
  test('holds the tags the worker rewrites', () => {
    for (const tag of ['<title>', '<meta name="description"', '<link rel="canonical"', '<meta property="og:title"', '<meta property="og:description"', '<meta property="og:url"'])
      expect(html).toContain(tag)
  })
  test('describes the finder as the page SEO does', () => {
    const { title, description, url } = seoOf('')
    expect(html).toContain(`<title>${title}</title>`)
    expect(html).toContain(`<meta name="description" content="${description}">`)
    expect(html).toContain(`<link rel="canonical" href="${url}">`)
    expect(html).toContain(`<meta property="og:url" content="${url}">`)
  })
})

describe('crawler files', () => {
  test('lists a page of the app for every address', () => {
    const locs = [...read('app/public/sitemap.xml').matchAll(/<loc>(.*?)<\/loc>/g)].map(match => match[1])
    expect(new Set(locs).size).toBe(locs.length)
    for (const loc of locs) expect(pageOf(new URL(loc).pathname), loc).not.toBeNull()
    expect(locs.every(loc => loc.startsWith(`${SITE.url}/`))).toBe(true)
  })
})

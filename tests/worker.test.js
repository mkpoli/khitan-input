import { describe, expect, test } from 'bun:test'
import worker from '../worker/index.js'
import { SEO_PATHS, seoOf } from '../app/lib/seo.js'

const HTML = `<!doctype html><html><head>
<link rel="canonical" href="https://khitan.mkpo.li/">
<title>Khitan Input</title>
<meta name="description" content="Find a Khitan grapheme.">
<meta property="og:title" content="Khitan Input">
<meta property="og:description" content="Find a Khitan grapheme.">
<meta property="og:url" content="https://khitan.mkpo.li/">
</head><body>app</body></html>`
// Every path opens the app, as the single-page-application fallback does; a file keeps its own type.
const env = {
  ASSETS: {
    /** @param {Request} request */
    async fetch(request) {
      const { pathname } = new URL(request.url)
      if (pathname.endsWith('.svg')) return new Response('<svg/>', { status: 200, headers: { 'content-type': 'image/svg+xml' } })
      return new Response(request.method === 'HEAD' ? null : HTML, { status: 200, headers: { 'content-type': 'text/html', etag: '"index"' } })
    },
  },
}

/** @param {string} path @param {RequestInit} [init] */
const fetch = (path, init) => worker.fetch(new Request(`https://khitan.mkpo.li${path}`, init), env)

describe('worker', () => {
  test('serves each page with its own head', async () => {
    for (const page of SEO_PATHS) {
      const html = await (await fetch(`/${page}`)).text()
      const { title, url } = seoOf(page)
      expect(html, page).toContain(`<title>${title}</title>`)
      expect(html, page).toContain(`<link rel="canonical" href="${url}">`)
      expect(html, page).toContain(`<meta property="og:url" content="${url}">`)
    }
  })
  test('escapes the description into its attribute', async () => {
    const html = await (await fetch('/words')).text()
    expect(html).toContain('Words cited in Otake&#39;s work.')
  })
  test('reads a trailing slash as the same page', async () => {
    expect(await (await fetch('/syllabary/')).text()).toContain('<link rel="canonical" href="https://khitan.mkpo.li/syllabary">')
  })
  test('sends the new body without the old length or tag', async () => {
    const response = await fetch('/about')
    expect(response.headers.get('etag')).toBeNull()
    expect(response.headers.get('content-length')).toBeNull()
  })
  test('answers HEAD without a body', async () => {
    const response = await fetch('/about', { method: 'HEAD' })
    expect(response.status).toBe(200)
    expect(await response.text()).toBe('')
  })
  test('leaves other paths and files as the assets answer them', async () => {
    expect(await (await fetch('/nope')).text()).toBe(HTML)
    const file = await fetch('/favicon.svg')
    expect(file.headers.get('content-type')).toBe('image/svg+xml')
    expect(await file.text()).toBe('<svg/>')
  })
  test('does not rewrite a write', async () => {
    expect(await (await fetch('/about', { method: 'POST' })).text()).toBe(HTML)
  })
})

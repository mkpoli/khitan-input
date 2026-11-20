import { describe, expect, test } from 'bun:test'
import worker from '../worker/index.js'
import { SEO_PATHS, pageOf, seoOf } from '../app/lib/seo.js'

const HTML = `<!doctype html><html><head>
<link rel="canonical" href="https://khitan.mkpo.li/">
<title>Khitan Input</title>
<meta name="description" content="Find a Khitan grapheme.">
<meta property="og:title" content="Khitan Input">
<meta property="og:description" content="Find a Khitan grapheme.">
<meta property="og:url" content="https://khitan.mkpo.li/">
</head><body>app</body></html>`
// The assets hold index.html and one file; every other path is a 404, as `not_found_handling: none` answers.
const env = {
  ASSETS: {
    /** @param {Request} request */
    async fetch(request) {
      const { pathname } = new URL(request.url)
      if (pathname === '/index.html') {
        if (request.headers.get('if-none-match') === '"index"') return new Response(null, { status: 304 })
        return new Response(request.method === 'HEAD' ? null : HTML, { status: 200, headers: { 'content-type': 'text/html', etag: '"index"' } })
      }
      if (pathname === '/favicon.svg') return new Response('<svg/>', { status: 200, headers: { 'content-type': 'image/svg+xml' } })
      return new Response('missing', { status: 404, headers: { 'content-type': 'text/plain' } })
    },
  },
}

/** @param {string} path @param {RequestInit} [init] */
const fetch = (path, init) => worker.fetch(new Request(`https://khitan.mkpo.li${path}`, init), env)
const asPage = { headers: { accept: 'text/html' } }

describe('worker', () => {
  test('serves each page with its own head', async () => {
    for (const page of SEO_PATHS.filter(Boolean)) {
      const response = await fetch(`/${page}`, asPage)
      expect(response.status, page).toBe(200)
      const html = await response.text()
      const { title, url } = seoOf(page)
      expect(html, page).toContain(`<title>${title}</title>`)
      expect(html, page).toContain(`<link rel="canonical" href="${url}">`)
      expect(html, page).toContain(`<meta property="og:url" content="${url}">`)
    }
  })
  test('serves a page to a client that names no type', async () => {
    expect((await fetch('/syllabary')).status).toBe(200)
  })
  test('reads a trailing slash as the same page', async () => {
    const html = await (await fetch('/syllabary/', asPage)).text()
    expect(html).toContain('<link rel="canonical" href="https://khitan.mkpo.li/syllabary">')
  })
  test('serves an unknown address as a noindex 404 with no address of its own', async () => {
    const response = await fetch('/nope', asPage)
    expect(response.status).toBe(404)
    const html = await response.text()
    expect(html).toContain('<title>Khitan Input</title>')
    expect(html).toContain('<meta name="robots" content="noindex, nofollow">')
    expect(html).not.toContain('rel="canonical"')
    expect(html).not.toContain('og:url')
  })
  test('does not let a matching ETag turn a page or the 404 view into 304', async () => {
    const headers = { accept: 'text/html', 'if-none-match': '"index"' }
    expect((await fetch('/nope', { headers })).status).toBe(404)
    expect((await fetch('/about', { headers })).status).toBe(200)
  })
  test('keeps a miss that is not for a page a plain 404', async () => {
    const response = await fetch('/nope', { headers: { accept: 'application/json' } })
    expect(response.status).toBe(404)
    expect(await response.text()).toBe('missing')
  })
  test('answers HEAD for a page and for a miss', async () => {
    const known = await fetch('/about', { method: 'HEAD', ...asPage })
    expect(known.status).toBe(200)
    expect(await known.text()).toBe('')
    expect((await fetch('/nope', { method: 'HEAD', ...asPage })).status).toBe(404)
  })
  test('sends the new body without the old length or tag', async () => {
    const response = await fetch('/about', asPage)
    expect(response.headers.get('etag')).toBeNull()
    expect(response.headers.get('content-length')).toBeNull()
  })
  test('leaves files and writes as the assets answer them', async () => {
    expect(await (await fetch('/favicon.svg')).text()).toBe('<svg/>')
    expect((await fetch('/about', { method: 'POST' })).status).toBe(404)
  })
})

describe('app paths', () => {
  test('answers the home page from the assets', async () => {
    expect(await (await fetch('/index.html')).text()).toBe(HTML)
  })
  test('names no page for a path the app does not render', () => {
    for (const path of ['/nope', '/about/extra', '/data/missing.json']) expect(pageOf(path), path).toBeNull()
  })
})

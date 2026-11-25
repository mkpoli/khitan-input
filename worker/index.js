// Serves the built app and writes each page's own head into the HTML it sends, so a crawler that
// runs no script reads the right title and address for /radicals as well as for /.
import { pageOf, seoOf } from '../app/lib/seo.js'

/** @param {string} text */
const escaped = text => String(text).replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char] ?? char)

/**
 * The app's page with the head of the page its address names.
 * @param {string} html the served index.html
 * @param {string} page
 */
export function withSeo(html, page) {
  const { title, description, url } = seoOf(page)
  /** @type {[RegExp, string][]} */
  const head = [
    [/<title>[\s\S]*?<\/title>/, `<title>${escaped(title)}</title>`],
    [/<meta name="description"[^>]*>/, `<meta name="description" content="${escaped(description)}">`],
    [/<link rel="canonical"[^>]*>/, `<link rel="canonical" href="${escaped(url)}">`],
    [/<meta property="og:title"[^>]*>/, `<meta property="og:title" content="${escaped(title)}">`],
    [/<meta property="og:description"[^>]*>/, `<meta property="og:description" content="${escaped(description)}">`],
    [/<meta property="og:url"[^>]*>/, `<meta property="og:url" content="${escaped(url)}">`],
  ]
  return head.reduce((out, [pattern, tag]) => out.replace(pattern, () => tag), html)
}

export default {
  /**
   * @param {Request} request
   * @param {{ ASSETS: { fetch: (request: Request) => Promise<Response> } }} env
   * @returns {Promise<Response>}
   */
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request)
    const reads = request.method === 'GET' || request.method === 'HEAD'
    if (!reads || response.status !== 200 || !(response.headers.get('content-type') ?? '').includes('text/html')) return response
    const page = pageOf(new URL(request.url).pathname)
    if (page === null) return response
    const html = await response.text()
    const headers = new Headers(response.headers)
    // The rewritten head is a different body, so its original length and tag no longer apply.
    headers.delete('content-length')
    headers.delete('content-encoding')
    headers.delete('etag')
    return new Response(request.method === 'HEAD' ? null : withSeo(html, page), { status: 200, headers })
  },
}

// Where a page says it lives. The one HTML file serves every path, so the address can only be set here.
const SITE = 'https://khitan.mkpo.li'

/** @param {string} page the page's path, without its leading slash */
export function applyCanonical(page) {
  const url = `${SITE}/${page}`
  let link = document.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.append(link)
  }
  link.setAttribute('href', url)
  let meta = document.querySelector('meta[property="og:url"]')
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute('property', 'og:url')
    document.head.append(meta)
  }
  meta.setAttribute('content', url)
}

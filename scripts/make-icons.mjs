#!/usr/bin/env bun
// Draw the icons and the share card from `app/public/favicon.svg`, the one place the mark is drawn.
// Chromium is already a dependency of the screenshots, and it renders the SVG exactly as a browser
// does, so the 32-pixel icon and the 1200-pixel card cannot drift apart.
//
//   bun scripts/make-icons.mjs
import { chromium } from 'playwright-core'
import { readFileSync, readdirSync, existsSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

const ROOT = new URL('..', import.meta.url).pathname
const PUBLIC = join(ROOT, 'app/public')
const mark = readFileSync(join(PUBLIC, 'favicon.svg'), 'utf8')

/** The mark without its background square, for a maskable icon and the card. */
const glyph = mark
  .replace(/<rect[^>]*\/>/, '')

const INK = '#1f2412'
const PAPER = '#eef0e2'
const ACCENT = '#566b0f'

function browserPath() {
  const cache = join(homedir(), '.cache/ms-playwright')
  for (const dir of readdirSync(cache).filter(name => name.startsWith('chromium-')).sort().reverse()) {
    for (const candidate of [join(cache, dir, 'chrome-linux64/chrome'), join(cache, dir, 'chrome-linux/chrome')]) {
      if (existsSync(candidate)) return candidate
    }
  }
  throw new Error('no Chromium under ~/.cache/ms-playwright; run a shoot script once')
}

const svg = (/** @type {string} */ body, /** @type {number} */ size) =>
  `data:image/svg+xml;base64,${Buffer.from(body).toString('base64')}`

const browser = await chromium.launch({ executablePath: browserPath() })
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 })

/** @param {string} html @param {number} width @param {number} height @param {boolean} [transparent] */
async function shot(html, width, height, transparent = false) {
  await page.setViewportSize({ width, height })
  await page.setContent(`<body style="margin:0;width:${width}px;height:${height}px;overflow:hidden">${html}</body>`)
  await page.waitForTimeout(120)
  return page.screenshot({ clip: { x: 0, y: 0, width, height }, omitBackground: transparent })
}

/** @param {number} size @param {boolean} [opaque] */
const icon = (size, opaque = false) =>
  shot(`<img src="${svg(mark, size)}" width="${size}" height="${size}" style="display:block;${opaque ? `background:${PAPER}` : ''}">`, size, size, !opaque)

writeFileSync(join(PUBLIC, 'icon-32.png'), await icon(32))
writeFileSync(join(PUBLIC, 'icon-192.png'), await icon(192))
writeFileSync(join(PUBLIC, 'icon-512.png'), await icon(512))
writeFileSync(join(PUBLIC, 'apple-touch-icon.png'), await icon(180, true))
// A maskable icon is cropped to a circle on some launchers, so the mark keeps a wide margin.
writeFileSync(join(PUBLIC, 'icon-maskable-512.png'), await shot(
  `<div style="display:grid;place-items:center;width:512px;height:512px;background:${ACCENT}">
     <img src="${svg(glyph, 512)}" width="300" height="300"></div>`, 512, 512))

const face = readFileSync(join(ROOT, 'app/public/fonts/NotoSerifKhitanSmallScript-Regular.woff2')).toString('base64')
const card = await shot(`
  <style>
    @font-face{font-family:"Noto Serif Khitan Small Script";src:url(data:font/woff2;base64,${face}) format("woff2")}
    body{background:${PAPER};color:${INK};font-family:"DejaVu Serif",Georgia,serif;display:grid;
      grid-template-columns:720px 1fr;align-items:center;padding:0 72px;gap:24px;box-sizing:border-box}
    .copy{width:720px}
    h1{margin:0;font-size:60px;line-height:1.12;letter-spacing:-.01em}
    .mark{display:flex;align-items:center;gap:18px;margin-bottom:26px}
    .mark img{width:76px;height:76px;border-radius:14px}
    .lead{margin:18px 0 0;font-size:27px;line-height:1.4;color:#434a2c;max-width:19em;font-family:system-ui,sans-serif}
    .glyphs{font-family:"Noto Serif Khitan Small Script";font-size:104px;line-height:1.1;color:${ACCENT};
      display:grid;grid-template-columns:repeat(2,1em);gap:0 10px;justify-content:center}
    .glyphs span{display:block;width:2em;margin-inline:-.5em;text-align:center}
  </style>
  <div class="copy">
    <div class="mark"><img src="${svg(mark, 76)}"><span style="font-size:30px;letter-spacing:.02em">Khitan Input</span></div>
    <h1>Enter a Khitan<br>grapheme.</h1>
    <p class="lead">By reading, number, meaning or the shape you draw, with each scholar's value under their name.</p>
  </div>
  <div class="glyphs"><span>\u{18BA7}</span><span>\u{18BFA}</span><span>\u{18C64}</span><span>\u{18C0A}</span></div>
`, 1200, 630)
writeFileSync(join(PUBLIC, 'og.png'), card)

await browser.close()
console.log('icons and og.png written to app/public')

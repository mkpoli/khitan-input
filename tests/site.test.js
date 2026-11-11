import { describe, expect, test } from 'bun:test'
import { matchedReading } from '../app/lib/data.js'
import { readFileSync } from 'node:fs'
import { indexShapes, parseShapes, rankShapes, rasterize, SIZE } from '../app/lib/shape.js'
import { blockRows, fold, parseWord, FILLER } from '../app/lib/script.js'
import { BLOCK_START, FILLER as FILLER_CP, NO_GLYPH, PAGE_SIZE, codeChart, codePointLabel, rangeLabel } from '../app/lib/code-chart.js'
import en from '../messages/en.json'
import ja from '../messages/ja.json'
import zhHans from '../messages/zh-Hans.json'
import zhHant from '../messages/zh-Hant.json'
import ko from '../messages/ko.json'

test('a block pairs graphemes and centres an odd last one', () => {
  expect(blockRows([1, 2, 3])).toEqual([[1, 2], [3]])
  expect(blockRows([1, 2, 3, 4])).toEqual([[1, 2], [3, 4]])
})

test('a filler after the first grapheme sets it alone', () => {
  const { chars, single } = parseWord(`\u{18B01}${FILLER}\u{18B02}\u{18B06}`)
  expect(single).toBe(true)
  expect(blockRows(chars, single).map(row => row.length)).toEqual([1, 2])
})

test('readings can be typed in plain letters', () => {
  expect(fold('əəd')).toBe('eed')
  expect(fold('ǰaw')).toBe('jaw')
  expect(fold('χaa')).toBe('xaa')
  expect(fold('uŋγʷ')).toBe('ungg')
  expect(fold('*əəg')).toBe('eeg')
})

test('every language has every message', () => {
  const keys = Object.keys(en).sort()
  for (const catalogue of [ja, zhHans, zhHant, ko]) expect(Object.keys(catalogue).sort()).toEqual(keys)
})

const codeData = JSON.parse(readFileSync('app/public/data/khitan.json', 'utf8'))
const chart = codeChart(codeData.graphemes)

test('the code chart pages the block in runs of sixteen', () => {
  expect(chart.pages).toHaveLength(2)
  for (const page of chart.pages) expect(page.cells).toHaveLength(PAGE_SIZE)
  expect(chart.pages[0].start).toBe(BLOCK_START)
  expect(chart.pages[0].cells[0].cp).toBe('18B00')
  expect(chart.pages[1].cells[255].cp).toBe('18CFF')
  expect(chart.pages.flatMap(page => page.cells).filter(Boolean)).toHaveLength(476)
  expect(chart.pages[1].cells.slice(219, 255).every(cell => cell === null)).toBe(true)
  expect(codePointLabel(FILLER_CP)).toBe('U+16FE4')
  expect(rangeLabel(chart.pages[0])).toBe('U+18B00–U+18BFF')
})

test('marks the code points the bundled face does not draw', () => {
  const cells = chart.pages.flatMap(page => page.cells).filter(Boolean)
  for (const cp of NO_GLYPH) expect(cells.find(g => parseInt(g.cp, 16) === cp)?.drawn).toBe(false)
  expect(cells.filter(g => !g.drawn)).toHaveLength(NO_GLYPH.size)
})

test('the code chart counts the inventory and its statuses', () => {
  expect(chart.graphemes).toBe(491)
  expect(chart.codePoints).toBe(477)
  expect(chart.withoutCodePoint).toBe(14)
  expect(chart.block).toBe(476)
  expect(chart.filler).toBe(1)
  expect(chart.status).toEqual({ current: 368, variant: 12, unicode: 109, uncatalogued: 2 })
  expect(chart.confidence).toEqual({ high: 362, medium: 6, none: 109 })
})

describe('drawing search', () => {
  const index = indexShapes(parseShapes(new Uint8Array(readFileSync('app/public/data/shapes.bin'))))

  test('covers the characters the face draws', () => {
    expect(index.chars.length).toBeGreaterThan(460)
  })

  test('a lone tap stays in the middle of the square', () => {
    const mask = rasterize([[[0.3, 0.7]]])
    const cells = [...mask.keys()].filter(c => mask[c]).map(c => [c % SIZE, Math.floor(c / SIZE)])
    expect(cells.length).toBeGreaterThan(0)
    for (const [x, y] of cells) {
      expect(Math.abs(x - SIZE / 2)).toBeLessThanOrEqual(2)
      expect(Math.abs(y - SIZE / 2)).toBeLessThanOrEqual(2)
    }
  })

  test('a drawing means the same at any scale', () => {
    const stroke = [[[0.1, 0.2], [0.9, 0.25]], [[0.5, 0.1], [0.45, 0.9]]]
    const scaled = stroke.map(s => s.map(([x, y]) => [x * 340, y * 340]))
    expect([...rasterize(scaled)]).toEqual([...rasterize(stroke)])
  })

  test('a glyph drawn as its own line ranks first', () => {
    let first = 0
    index.chars.forEach((char, at) => {
      const drawn = new Uint8Array(SIZE * SIZE)
      for (const cell of index.inks[at]) drawn[cell] = 1
      if (rankShapes(index, drawn, { limit: 1 })[0].char === char) first++
    })
    expect(first / index.chars.length).toBeGreaterThan(0.95)
  })
})

describe('the reading a search matched', () => {
  const g = { v: 'ard', rs: [{ v: 'ard', k: 'phonetic' }, { v: 'aard', k: 'phonetic' }, { v: 'ABOVE', k: 'semantic' }] }

  test('is the value that matched, not the primary one', () => {
    expect(matchedReading(g, 'aa')).toBe('aard')
    expect(matchedReading(g, 'ard')).toBe('ard')
  })

  test('prefers an exact match over an earlier prefix', () => {
    expect(matchedReading({ v: 'aar', rs: [{ v: 'aar', k: 'phonetic' }, { v: 'aa', k: 'phonetic' }] }, 'aa')).toBe('aa')
  })

  test('falls back to the primary value when no reading matched', () => {
    expect(matchedReading(g, '339')).toBe('ard')
    expect(matchedReading(g, 'above')).toBe('ard')
  })
})

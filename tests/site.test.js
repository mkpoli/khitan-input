import { describe, expect, test } from 'bun:test'
import { matchedReading } from '../app/lib/data.js'
import { readFileSync } from 'node:fs'
import { indexShapes, parseShapes, rankShapes, rasterize, SIZE } from '../app/lib/shape.js'
import { blockRows, fold, parseWord, FILLER } from '../app/lib/script.js'
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

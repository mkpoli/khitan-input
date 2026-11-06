import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { indexShapes, parseShapes, rankShapes, SIZE } from '../app/lib/shape.js'
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

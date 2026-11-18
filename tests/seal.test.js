import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'

const record = JSON.parse(readFileSync(new URL('../data/seal/records.json', import.meta.url), 'utf8'))
const forms = record.forms
const inscriptions = record.inscriptions

test('two inscriptions and 52 blocks, counted from the covers', () => {
  expect(inscriptions.map(inscription => inscription.id)).toEqual(['daozong', 'xuanyi'])
  expect(forms).toHaveLength(52)
  expect(record.counts).toEqual({ inscriptions: 2, forms: 52, identified: 52 })
  expect(inscriptions.map(inscription => [inscription.columns, inscription.rows])).toEqual([[6, 6], [4, 4]])
  expect(forms.filter(form => form.inscription === 'daozong')).toHaveLength(36)
  expect(forms.filter(form => form.inscription === 'xuanyi')).toHaveLength(16)
})

test('each inscription carries the first line of its epitaph text', () => {
  expect(inscriptions.map(inscription => inscription.reading)).toEqual(['仁聖大孝文皇帝哀冊文', '宣懿皇后哀冊文'])
  expect(inscriptions.every(inscription => inscription.reading_source === 'Wang 1931, 471')).toBe(true)
})

test('the blocks are numbered in reading order, columns right to left and rows top to bottom', () => {
  for (const inscription of inscriptions) {
    const own = forms.filter(form => form.inscription === inscription.id)
    let previous = { col: 1, row: 0 }
    for (const form of own) {
      expect(form.col).toBeGreaterThanOrEqual(1)
      expect(form.col).toBeLessThanOrEqual(inscription.columns)
      expect(form.row).toBeGreaterThanOrEqual(1)
      expect(form.row).toBeLessThanOrEqual(inscription.rows)
      if (form.col !== previous.col) {
        expect(form.col).toBe(previous.col + 1)
        expect(form.row).toBe(1)
      } else {
        expect(form.row).toBe(previous.row + 1)
      }
      previous = form
    }
    expect(own[0]).toMatchObject({ col: 1, row: 1 })
    expect(own.at(-1)).toMatchObject({ col: inscription.columns, row: inscription.rows })
  }
})

test('block ids are unique and in reading order', () => {
  expect(new Set(forms.map(form => form.id)).size).toBe(forms.length)
  const ids = forms.map(form => form.id)
  expect(ids.slice(0, 36)).toEqual(Array.from({ length: 36 }, (_, index) => `DZ-${String(index + 1).padStart(2, '0')}`))
  expect(ids.slice(36)).toEqual(Array.from({ length: 16 }, (_, index) => `XY-${String(index + 1).padStart(2, '0')}`))
})

test('every block records its identification status', () => {
  for (const form of forms) {
    expect(form.status).toBe('identified')
    expect(form.confidence).toBe('probable')
    expect(form.identification).toBe(String.fromCodePoint(parseInt(form.unicode.slice(2), 16)))
    expect(form.basis).toContain('BabelStone')
  }
})

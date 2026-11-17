// The seal-script covers: two inscriptions, 46 blocks; the 16 Xuanyi blocks carry their Khitan characters.
import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'

const record = JSON.parse(readFileSync(new URL('../data/seal/records.json', import.meta.url), 'utf8'))
const forms = record.forms
const inscriptions = record.inscriptions

test('two inscriptions and 46 blocks, counted from the covers', () => {
  expect(inscriptions.map(inscription => inscription.id)).toEqual(['daozong', 'xuanyi'])
  expect(forms).toHaveLength(46)
  expect(record.counts).toEqual({ inscriptions: 2, forms: 46, identified: 16 })
  expect(inscriptions.map(inscription => [inscription.columns, inscription.rows])).toEqual([[6, 5], [4, 4]])
  expect(forms.filter(form => form.inscription === 'daozong')).toHaveLength(30)
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
  expect(ids.slice(0, 30)).toEqual(Array.from({ length: 30 }, (_, index) => `DZ-${String(index + 1).padStart(2, '0')}`))
  expect(ids.slice(30)).toEqual(Array.from({ length: 16 }, (_, index) => `XY-${String(index + 1).padStart(2, '0')}`))
})

test('every block records its identification status', () => {
  const xuanyi = forms.filter(form => form.inscription === 'xuanyi')
  const daozong = forms.filter(form => form.inscription === 'daozong')
  expect(xuanyi).toHaveLength(16)
  expect(daozong).toHaveLength(30)
  for (const form of xuanyi) {
    expect(form.status).toBe('identified')
    expect([...form.identification]).toHaveLength(1)
    expect(form.unicode).toMatch(/^U\+18[BC][0-9A-F]{2}$/)
    expect(form.basis).toContain('BabelStone')
  }
  for (const form of daozong) {
    expect(form.identification).toBeNull()
    expect(form.status).toBe('unidentified')
    expect(form.basis).toContain('Daozong')
  }
})

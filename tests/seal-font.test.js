import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'

const record = JSON.parse(readFileSync(new URL('../data/seal/font/forms.json', import.meta.url), 'utf8'))
const forms = record.forms
const correspondences = JSON.parse(readFileSync(new URL('../data/seal/correspondences.json', import.meta.url), 'utf8'))

test('the font covers both inscriptions and preserves the Xuanyi alternate', () => {
  expect(forms).toHaveLength(37)
  expect(forms.slice(0, 16).map(form => form.id)).toEqual(Array.from({ length: 16 }, (_, index) => `XY-${String(index + 1).padStart(2, '0')}`))
  expect(record.font).toMatchObject({ family: 'Qingling Seal', em: 1024, ascent: 832, descent: -192, advance: 1024, stroke_radius: 15 })
  expect(record.font.licence).toBe('CC BY-SA 4.0')
  expect(record.font.stroke_system).toContain('Sealie')
  expect(Object.keys(correspondences.blocks)).toHaveLength(52)
  expect(new Set(Object.values(correspondences.blocks).map(block => block.unicode)).size).toBe(36)
  expect(new Set(forms.map(form => correspondences.blocks[form.id].unicode))).toEqual(
    new Set(Object.values(correspondences.blocks).map(block => block.unicode))
  )
  for (const block of Object.values(correspondences.blocks)) expect(block.unicode).toMatch(/^U\+18[BC][0-9A-F]{2}$/)
})

test('the Xuanyi and Daozong plates distinguish the upper bar and the hooked upright', () => {
  const { blocks, unicode_aliases: aliases } = correspondences
  expect(blocks['XY-06'].unicode).toBe('U+18C57')
  expect(blocks['DZ-02'].unicode).toBe('U+18C8C')
  expect([blocks['XY-13'], blocks['DZ-19'], blocks['DZ-33']].map(block => block.unicode))
    .toEqual(Array(3).fill('U+18CBD'))
  expect(aliases).toEqual({ 'U+18C04': blocks['XY-14'].unicode, 'U+18C32': blocks['DZ-07'].unicode })
  const primary = new Set(Object.values(blocks).map(block => block.unicode))
  expect(new Set([...primary, ...Object.keys(aliases)]).size).toBe(38)
})

test('every block has centre lines inside the em box', () => {
  for (const form of forms) {
    expect(form.paths.length).toBeGreaterThanOrEqual(2)
    for (const path of form.paths) {
      expect(path.length).toBeGreaterThanOrEqual(2)
      for (const [x, y] of path) {
        expect(x).toBeGreaterThanOrEqual(0)
        expect(x).toBeLessThanOrEqual(1024)
        expect(y).toBeGreaterThanOrEqual(0)
        expect(y).toBeLessThanOrEqual(832)
      }
    }
  }
})

test('the built faces and the specimen are in the repository', () => {
  const ttf = readFileSync(new URL('../fonts/QinglingSeal-Regular.ttf', import.meta.url))
  const woff2 = readFileSync(new URL('../fonts/QinglingSeal-Regular.woff2', import.meta.url))
  const web = readFileSync(new URL('../app/public/fonts/QinglingSeal-Regular.woff2', import.meta.url))
  expect([0x00010000, 0x74727565]).toContain(ttf.readUInt32BE(0))
  expect(woff2.subarray(0, 4).toString('latin1')).toBe('wOF2')
  expect(web.equals(woff2)).toBe(true)
  expect(ttf.length).toBeGreaterThan(10_000)
  expect(existsSync(new URL('../docs/seal-gallery.png', import.meta.url))).toBe(true)
  expect(existsSync(new URL('../data/seal/font/README.md', import.meta.url))).toBe(true)
})

test('the vector source and its licence are recorded', () => {
  expect(record.source.drawing).toBe('forms.json')
  expect(record.source.basis).toContain('Vector')
  expect(record.source.licence).toBe('CC BY-SA 4.0')
  expect(existsSync(new URL('../data/seal/font/forms.json', import.meta.url))).toBe(true)
})

test('the distributed TTF exposes continuous weight variation with fixed glyph origins', () => {
  const font = readFileSync(new URL('../fonts/QinglingSeal-Regular.ttf', import.meta.url))
  const tables = new Map()
  for (let i = 0; i < font.readUInt16BE(4); i++) {
    const record = 12 + i * 16
    tables.set(font.toString('ascii', record, record + 4), font.readUInt32BE(record + 8))
  }
  expect(tables.has('gvar')).toBe(true)
  const axis = tables.get('fvar') + font.readUInt16BE(tables.get('fvar') + 4)
  expect(font.toString('ascii', axis, axis + 4)).toBe('wght')
  expect([4, 8, 12].map(offset => font.readInt32BE(axis + offset) / 65536)).toEqual([200, 400, 800])
  expect(font.readUInt16BE(tables.get('head') + 16) & 2).toBe(2)
})

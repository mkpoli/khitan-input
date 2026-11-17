// The pilot seal typeface: 16 Xuanyi blocks at U+E700-U+E70F.
import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'

const record = JSON.parse(readFileSync(new URL('../data/seal/font/forms.json', import.meta.url), 'utf8'))
const forms = record.forms

test('the pilot holds the sixteen Xuanyi blocks at U+E700-U+E70F', () => {
  expect(forms).toHaveLength(16)
  expect(forms.map(form => form.id)).toEqual(Array.from({ length: 16 }, (_, index) => `XY-${String(index + 1).padStart(2, '0')}`))
  expect(record.font).toMatchObject({ family: 'Qingling Seal', em: 1024, ascent: 832, descent: -192, advance: 1024, stroke_radius: 15 })
  expect(record.font.licence).toBe('CC BY-SA 4.0')
  expect(record.font.stroke_system).toContain('Sealie')
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
  expect(ttf.length).toBeGreaterThan(100_000)
  expect(existsSync(new URL('../docs/seal-font-specimen.png', import.meta.url))).toBe(true)
  expect(existsSync(new URL('../data/seal/font/README.md', import.meta.url))).toBe(true)
})

test('the reference drawing and its licence are recorded', () => {
  expect(record.source.basis).toContain('Wikimedia Commons')
  expect(record.source.licence).toBe('CC BY-SA 4.0')
  expect(existsSync(new URL('../data/seal/font/reference.png', import.meta.url))).toBe(true)
})

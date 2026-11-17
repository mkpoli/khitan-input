// The running-script face: 96 forms cut from Nova N 176 folio 9, one glyph at each page-local
// code point, with four identified forms also reachable at BabelStone points.
import { expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'

const record = JSON.parse(gunzipSync(readFileSync(new URL('../data/running/forms.json.gz', import.meta.url))).toString())
const cuts = JSON.parse(readFileSync(new URL('../data/running/cuts.json', import.meta.url), 'utf8'))
const forms = record.forms

test('the record holds 96 forms in reading order, one at each page-local code point', () => {
  expect(forms).toHaveLength(96)
  expect(record.metrics.unitsPerEm).toBe(1000)
  expect(record.metrics.advance).toBe(1000)
  expect(cuts.forms).toHaveLength(96)
  const codePoints = forms.map(form => Number.parseInt(form.pua, 16))
  expect(codePoints).toEqual(Array.from({ length: 96 }, (_, index) => 0xE600 + index))
  expect(new Set(codePoints).size).toBe(96)
  expect(forms.map(form => form.col)).toEqual(cuts.forms.map(form => form.col))
})

test('the page is six columns, cut right to left and top to bottom', () => {
  expect(new Set(forms.map(form => form.col))).toEqual(new Set([1, 2, 3, 4, 5, 6]))
  let previous = { col: 0, y: -1 }
  for (const form of forms) {
    if (form.col !== previous.col) {
      expect(form.col).toBe(previous.col + 1)
      previous = { col: form.col, y: -1 }
    }
    expect(form.box[1]).toBeGreaterThanOrEqual(previous.y)
    previous.y = form.box[1]
  }
})

test('every box lies on the 1543x1964 photograph', () => {
  for (const form of forms) {
    const [x, y, w, h] = form.box
    expect(x).toBeGreaterThanOrEqual(0)
    expect(y).toBeGreaterThanOrEqual(0)
    expect(w).toBeGreaterThan(0)
    expect(h).toBeGreaterThan(0)
    expect(x + w).toBeLessThanOrEqual(1543)
    expect(y + h).toBeLessThanOrEqual(1964)
  }
})

test('the seven state-name forms are identified, and four answer at BabelStone points', () => {
  const identified = forms.filter(form => form.identification)
  expect(identified.map(form => form.identification)).toEqual(['大', '中', '央', 'hulʤi', '契', '丹', '國'])
  expect(identified.map(form => form.pua)).toEqual(['E652', 'E653', 'E654', 'E655', 'E656', 'E657', 'E658'])
  const aliases = identified.flatMap(form => form.aliases.map(alias => [alias, form.identification]))
  expect(aliases).toEqual([['E05A', '大'], ['E28F', '契'], ['E396', '丹'], ['E03C', '國']])
  for (const form of identified) {
    expect(form.identification_basis).toContain('Zaytsev 2011')
  }
})

test('each outline is a closed path inside the em box', () => {
  for (const form of forms) {
    expect(form.outline[0][0]).toBe('M')
    expect(form.outline.at(-1)[0]).toBe('Z')
    const operands = { M: 2, L: 2, C: 6, Z: 0 }
    for (const [operator, ...points] of form.outline) {
      expect(points).toHaveLength(operands[operator])
      for (let index = 0; index < points.length; index += 2) {
        expect(points[index]).toBeGreaterThanOrEqual(0)
        expect(points[index]).toBeLessThanOrEqual(1000)
        expect(points[index + 1]).toBeGreaterThan(-146)
        expect(points[index + 1]).toBeLessThan(900)
      }
    }
  }
})

test('the source and its digest are recorded', () => {
  expect(record.source.sha256).toBe('057931c5a99e7a9a7c07aebd62b1442579539565d65f4596194e84ba69732157')
  expect(record.source.width).toBe(1543)
  expect(record.source.height).toBe(1964)
  expect(record.source.terms).toContain('Public domain')
})

test('the built face and its specimen are in the repository', () => {
  const ttf = readFileSync(new URL('../fonts/NovaN176Running-Regular.ttf', import.meta.url))
  const woff2 = readFileSync(new URL('../fonts/NovaN176Running-Regular.woff2', import.meta.url))
  expect(ttf.length).toBeGreaterThan(250_000)
  expect([0x00010000, 0x74727565]).toContain(ttf.readUInt32BE(0))
  expect(woff2.subarray(0, 4).toString('latin1')).toBe('wOF2')
  expect(existsSync(new URL('../docs/running-specimen.png', import.meta.url))).toBe(true)
  expect(existsSync(new URL('../data/running/README.md', import.meta.url))).toBe(true)
})

import { expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

const survey = JSON.parse(readFileSync(new URL('../data/seal/large/west2012.json', import.meta.url), 'utf8'))

test('the survey lists eighteen ninefold seals and seven others', () => {
  expect(survey.seals.map(seal => seal.id)).toEqual([
    'A1', 'A2a', 'A2b', 'A3', 'A4a', 'A4b', 'A5a', 'A5b', 'A5c', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14',
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
  expect(survey.seals.filter(seal => seal.kind === 'ninefold')).toHaveLength(18)
})

test('a reading is the survey’s own sentence, Khitan on Private Use code points', () => {
  const a2a = survey.seals.find(seal => seal.id === 'A2a')
  expect(a2a.reading).toBe('The seal inscription  can be translated as "Seal of the Headquarters of the Commander-in-chief" (Chinese dūtǒngfǔ zhīyìn 都統府之印).')
  expect(a2a.url).toEndWith('#Seal_A02A')
  expect(survey.seals.find(seal => seal.id === 'A7').reading).toStartWith('Liu Fengzhu has read the inscription')
})

test('the character table keeps a row for each row of the survey', () => {
  expect(survey.characters).toHaveLength(44)
  expect(survey.characters[2]).toEqual({ seal_glyphs: 'F003 F004 F005 F02C F037', standard: '', meaning: 'Genitive particle *-un for stems with a u vowel or ending in w (Chinese 之).' })
})

test('no field keeps markup', () => {
  for (const seal of survey.seals) for (const value of Object.values(seal)) expect(value).not.toMatch(/[<>]|&[a-z]+;/)
})

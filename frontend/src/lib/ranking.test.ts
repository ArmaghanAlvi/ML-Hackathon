// C7 ranking tests driven by shared/ranking_test_vectors.json. Skipped while `cases` is empty.
// Owner: Stream D · Roadmap: Stage 5e
import { describe, expect, it } from 'vitest'
import vectors from '@shared/ranking_test_vectors.json'
import { topKLists, type RankInput, type RankOutput } from './ranking'

interface VectorCase {
  name: string
  input: { candidates: RankInput[]; weight?: number }
  expected: RankOutput
}

const cases = (vectors as unknown as { cases: VectorCase[] }).cases
const TOL_DIGITS = 6 // toBeCloseTo(x, 6) ≈ 1e-6 tolerance

describe.skipIf(cases.length === 0)('C7 ranking test vectors', () => {
  for (const c of cases) {
    it(c.name, () => {
      const out = topKLists(c.input.candidates, c.input.weight ?? 0.5)
      for (const [id, val] of Object.entries(c.expected.adjusted_rating)) {
        expect(out.adjusted_rating[id]).toBeCloseTo(val, TOL_DIGITS)
      }
      expect(out.top_cheapest).toEqual(c.expected.top_cheapest)
      expect(out.top_rated).toEqual(c.expected.top_rated)
      expect([...out.frontier].sort()).toEqual([...c.expected.frontier].sort())
      expect(out.best_value).toEqual(c.expected.best_value)
    })
  }
})

// Keeps the file a valid suite while the vectors are empty.
it('loads the ranking test vectors file', () => {
  expect(Array.isArray(cases)).toBe(true)
})

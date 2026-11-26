// Contract C7 ranking (see docs/contracts.md): client-side mirror of backend/app/services/ranking.py,
// used by the ValueScatter weight slider. Must pass shared/ranking_test_vectors.json.
// Owner: Stream D · Roadmap: Stage 5e
// STUB: not implemented yet.
//
// Pool: candidates with match_label identical|similar, non-null price, (rating lists) non-null rating.

export interface RankInput {
  id: string
  price: number
  rating: number | null
  review_count: number | null
}

export interface RankOutput {
  adjusted_rating: Record<string, number>
  top_cheapest: string[]
  top_rated: string[]
  frontier: string[]
  best_value: string[]
}

/** adj = (v/(v+m))·R + (m/(v+m))·C; v = review_count (null → 0), C = pool mean rating, m = pool median review count (min 1). */
export function bayesianAverage(candidates: RankInput[]): Record<string, number> {
  void candidates
  throw new Error('STUB: TODO Stage 5e (bayesianAverage)')
}

/** Ids not dominated: A dominates B if price_A <= price_B and adj_A >= adj_B, at least one strict. */
export function paretoFrontier(candidates: RankInput[], adjusted: Record<string, number>): string[] {
  void candidates
  void adjusted
  throw new Error('STUB: TODO Stage 5e (paretoFrontier)')
}

/** w·norm(adj) + (1−w)·(1 − norm(log(price))); norm = min-max over pool, 0.5 if all equal. */
export function weightedValue(
  candidates: RankInput[],
  adjusted: Record<string, number>,
  weight = 0.5,
): Record<string, number> {
  void candidates
  void adjusted
  void weight
  throw new Error('STUB: TODO Stage 5e (weightedValue)')
}

/** top_cheapest: 3 lowest prices; top_rated: 3 highest adj (ties → higher v); best_value: 3 highest weightedValue. */
export function topKLists(candidates: RankInput[], weight = 0.5, k = 3): RankOutput {
  void candidates
  void weight
  void k
  throw new Error('STUB: TODO Stage 5e (topKLists)')
}

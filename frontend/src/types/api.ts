// Contract C1 (Search API): TypeScript mirror of backend/app/schemas.py. See docs/contracts.md.
// Owner: Shared contract (consumed by Stream D) · Roadmap: Stage 0d
// CONTRACT FILE: must stay in sync with backend/app/schemas.py. Do not change without team approval.

export type MatchLabel = 'identical' | 'similar' | 'none'

/** Normalized box: x, y = top-left in [0, 1]; w, h in (0, 1]. */
export interface Box {
  x: number
  y: number
  w: number
  h: number
  label: string
  score: number
}

/** Exactly one of image_base64 / image_url must be set. */
export interface SearchRequest {
  image_base64?: string | null
  image_url?: string | null
  text?: string | null // e.g. "yellow version"
  box?: Box | null // user-selected box; null = auto
}

export interface Candidate {
  id: string
  title: string
  description?: string | null
  price?: number | null
  currency: string // default "USD"
  rating?: number | null // 0..5
  review_count?: number | null // >= 0
  adjusted_rating?: number | null // Bayesian (C7)
  trust_rating?: number | null // review-model weighted (Stream B)
  source: string // store name
  link: string
  image_url: string
  match_label: MatchLabel
  match_score: number // 0..1
  top_reviews: string[]
}

export interface SearchResponse {
  query_id: string
  detections: Box[]
  selected_box?: Box | null
  candidates: Candidate[]
  top_cheapest: string[] // candidate ids, max 3
  top_rated: string[]
  best_value: string[]
  frontier: string[] // Pareto-optimal candidate ids
  cached: boolean
  timings_ms: Record<string, number>
}

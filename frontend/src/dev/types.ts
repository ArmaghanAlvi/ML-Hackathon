import type { Candidate, SearchResponse } from '../types/api'

export interface DevCandidate extends Candidate {
  reviews_scanned?: number
}

export interface Suggestion {
  keyword: string
  candidate_ids: string[]
}

export interface DevSearchResponse extends Omit<SearchResponse, 'candidates'> {
  candidates: DevCandidate[]
  suggestions?: Suggestion[]
}

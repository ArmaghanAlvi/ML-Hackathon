import mock from '@shared/mocks/search_response.json'
import type { SearchResponse } from '../types/api'
import type { DevCandidate, Suggestion } from './types'

const mockResponse = mock as SearchResponse

export const sampleNoneCandidates: DevCandidate[] = mockResponse.candidates
  .filter((candidate) => candidate.match_label === 'none')
  .slice(0, 2)
  .map((candidate, index) => ({
    ...candidate,
    reviews_scanned: [18, 11][index],
  }))

export const sampleSuggestions: Suggestion[] = [
  { keyword: 'insulated water bottle', candidate_ids: ['c1', 'c2'] },
  { keyword: 'vacuum bottle with straw lid', candidate_ids: ['c4', 'c5'] },
]

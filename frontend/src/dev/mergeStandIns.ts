import { sampleNoneCandidates, sampleSuggestions } from './sampleData'
import type { DevSearchResponse } from './types'
import type { SearchResponse } from '../types/api'

export function mergeStandIns(response: SearchResponse | DevSearchResponse): DevSearchResponse {
  const standInsById = new Map(sampleNoneCandidates.map((candidate) => [candidate.id, candidate]))
  const candidates = response.candidates.map((candidate) => {
    const standIn = standInsById.get(candidate.id)
    const reviewsScanned = 'reviews_scanned' in candidate ? candidate.reviews_scanned : undefined
    if (reviewsScanned != null || standIn?.reviews_scanned == null) return candidate

    return { ...candidate, reviews_scanned: standIn.reviews_scanned }
  })
  const candidateIds = new Set(candidates.map((candidate) => candidate.id))
  const candidatesWithNoneStandIns = [
    ...candidates,
    ...sampleNoneCandidates.filter((candidate) => !candidateIds.has(candidate.id)),
  ]
  const suggestions = 'suggestions' in response ? response.suggestions : undefined

  return {
    ...response,
    candidates: candidatesWithNoneStandIns,
    suggestions: suggestions ?? sampleSuggestions,
  }
}

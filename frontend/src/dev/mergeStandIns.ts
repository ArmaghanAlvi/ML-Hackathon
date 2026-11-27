import { sampleNoneCandidates, sampleSuggestions } from './sampleData'
import type { DevSearchResponse } from './types'

export function mergeStandIns(response: DevSearchResponse): DevSearchResponse {
  const standInsById = new Map(sampleNoneCandidates.map((candidate) => [candidate.id, candidate]))
  const candidates = response.candidates.map((candidate) => {
    const standIn = standInsById.get(candidate.id)
    if (candidate.reviews_scanned != null || standIn?.reviews_scanned == null) return candidate

    return { ...candidate, reviews_scanned: standIn.reviews_scanned }
  })

  return {
    ...response,
    candidates,
    suggestions: response.suggestions ?? sampleSuggestions,
  }
}
